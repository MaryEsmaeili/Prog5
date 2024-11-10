import os
from sqlalchemy import create_engine
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, concat_ws
from pyspark import StorageLevel
from pyspark.sql.types import FloatType

# Function to load MySQL credentials from the .my.cnf file
def load_mysql_credentials():
    """
    Load MySQL credentials from the .my.cnf file.
    """
    credentials = {}
    with open(os.path.expanduser("~/.my.cnf"), encoding='utf-8') as config_file:
        for line in config_file:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                credentials[key.strip()] = value.strip()
    return credentials

# Load credentials
creds = load_mysql_credentials()

# Initialize the SQLAlchemy engine (optional, for verifying credentials)
connection_string = (f"mysql+pymysql://{creds['user']}:{creds['password']}@"
                     f"mariadb.bin.bioinf.nl/{creds['database']}")
engine = create_engine(connection_string)
conn = engine.connect()

# Set up Spark session with increased memory, JDBC driver, and retry configuration
spark = SparkSession.builder \
    .appName("NSF SNP Analysis") \
    .master("local[16]") \
    .config("spark.executor.memory", "4g") \
    .config("spark.ui.port", "4060") \
    .config("spark.port.maxRetries", "5") \
    .config("spark.jars", "mysql-connector-java-8.0.13.jar") \
    .config("spark.sql.debug.maxToStringFields", "10000") \
    .getOrCreate()

# Path to the gzipped file
file_path = "/data/datasets/dbNSFP/snpEff/data/dbNSFP4.9a.txt.gz"

# JDBC URL for MySQL connection
jdbc_url = f"jdbc:mysql://mariadb.bin.bioinf.nl:3306/{creds['database']}?useSSL=false&allowPublicKeyRetrieval=true"
jdbc_properties = {
    "driver": "com.mysql.cj.jdbc.Driver",
    "user": creds["user"],
    "password": creds["password"]
}

# Read the gzipped file directly with sampling for memory efficiency
df = spark.read.csv(file_path, sep="\t", header=True).sample(fraction=0.1)

# Rename columns with special characters for compatibility with MySQL
df = df.withColumnRenamed("#chr", "chr") \
       .withColumnRenamed("pos(1-based)", "pos_1_based")

# Define required columns
columns_needed = [
    "chr", "pos_1_based", "Ensembl_proteinid",
    "SIFT_score", "Polyphen2_HDIV_score", "MutationTaster_score",
    "FATHMM_score", "PROVEAN_score"
]

# Select and filter required columns
df = df.sample(fraction=0.1)
df = df.select(*columns_needed)

# Cast columns to appropriate data types to match MySQL table schema
df = df.withColumn("MutationTaster_score", col("MutationTaster_score").cast(FloatType())) \
       .withColumn("SIFT_score", col("SIFT_score").cast(FloatType())) \
       .withColumn("Polyphen2_HDIV_score", col("Polyphen2_HDIV_score").cast(FloatType())) \
       .withColumn("FATHMM_score", col("FATHMM_score").cast(FloatType())) \
       .withColumn("PROVEAN_score", col("PROVEAN_score").cast(FloatType()))


# Count predictions made by each classifier
classifier_columns = [
    "SIFT_score", "Polyphen2_HDIV_score", "MutationTaster_score",
    "FATHMM_score", "PROVEAN_score"
]

# # Step 3: Count non-NULL values for each classifier column to identify significant columns
# non_null_counts = {col: df.filter(df[col].isNotNull()).count() for col in classifier_columns}
# significant_columns = [col for col, count in non_null_counts.items() if count > 0]

# # Step 4: Proceed with analysis for significant columns
# # (Here, we only found MutationTaster_score with meaningful data)
# if "MutationTaster_score" in significant_columns:
#     # Summary statistics for MutationTaster_score
#     df.select("MutationTaster_score").describe().show()

#     # Top 5 highest MutationTaster_score rows
#     highest_score_df = df.orderBy(df["MutationTaster_score"].desc()).select(
#         "chr", "pos_1_based", "Ensembl_proteinid", "MutationTaster_score"
#     )
#     highest_score_df.show(5)

#     # Filtering scores above 0.5 as an example of additional analysis
#     significant_scores_df = df.filter(df["MutationTaster_score"] > 0.5)
#     significant_scores_df.select("chr", "pos_1_based", "Ensembl_proteinid", "MutationTaster_score").show(5)


predictions_count = {col: df.filter(df[col].isNotNull()).count() for col in classifier_columns}

# List all columns containing "score" in their name
# score_columns = [col for col in df.columns if "score" in col]

# Continue analysis with chosen classifier columns
# for col in classifier_columns:
#     df.select(col).describe().show()

# Top five classifiers
top_five_classifiers = sorted(predictions_count, key=predictions_count.get, reverse=True)[:5]
df = df.select("chr", "pos_1_based", "Ensembl_proteinid", *top_five_classifiers)

# Create a unique identifier for each genome position
df = df.withColumn("genome_position_id", concat_ws(":", col("chr"), col("pos_1_based")))

# Identify the position with the most predictions
most_predictions_position = df.groupBy("genome_position_id").count().orderBy("count", ascending=False).first()

# Identify the protein with the most predictions
most_predictions_protein = df.groupBy("Ensembl_proteinid").count().orderBy("count", ascending=False).first()

# Output answers to questions based on the processed data
print("1. Number of predictions each classifier makes:")
print(predictions_count)

print("\n2. Top five classifiers by prediction count:")
print(top_five_classifiers)

print("\n3. Unique genome position identifier created: 'genome_position_id' column")

print("\n4. Position with the most predictions:")
print(f"Position: {most_predictions_position['genome_position_id']}, Count: {most_predictions_position['count']}")

print("\n5. Protein (Ensembl_proteinid) with the most predictions:")
print(f"Protein: {most_predictions_protein['Ensembl_proteinid']}, Count: {most_predictions_protein['count']}")

df.printSchema()
df.show(5)

# Save the DataFrame to MySQL with overwrite mode
df.write \
   .format("jdbc") \
   .option("url", jdbc_url) \
   .option("dbtable", "nsf_predictions") \
   .option("user", creds["user"]) \
   .option("password", creds["password"]) \
   .option("driver", "com.mysql.cj.jdbc.Driver") \
   .option("truncate", "true") \
   .option("batchsize", "500") \
   .mode("overwrite") \
   .save()

# Stop Spark session
spark.stop()
