import os
from sqlalchemy import create_engine
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, concat_ws
from pyspark import StorageLevel

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
connection_string = (f"mysql+mysqldb://{creds['user']}:{creds['password']}@"
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
    .config("spark.jars", "mysql-connector-java.jar") \
    .config("spark.sql.debug.maxToStringFields", "1000") \
    .getOrCreate()

# Path to the gzipped file
file_path = "/data/datasets/dbNSFP/snpEff/data/dbNSFP4.9a.txt.gz"

# Read the gzipped file directly with sampling for memory efficiency
df = spark.read.csv(file_path, sep="\t", header=True).limit(1000)

# Define required columns
columns_needed = [
    "#chr", "pos(1-based)", "Ensembl_proteinid",
    "SIFT_score", "Polyphen2_HDIV_score", "MutationTaster_score",
    "FATHMM_score", "PROVEAN_score"
]
df = df.sample(fraction=0.1)
df = df.select(*columns_needed)

# Count predictions made by each classifier
classifier_columns = [
    "SIFT_score", "Polyphen2_HDIV_score", "MutationTaster_score",
    "FATHMM_score", "PROVEAN_score"
]
predictions_count = {col: df.filter(df[col].isNotNull()).count() for col in classifier_columns}

# Top five classifiers
top_five_classifiers = sorted(predictions_count, key=predictions_count.get, reverse=True)[:5]
df = df.select("#chr", "pos(1-based)", "Ensembl_proteinid", *top_five_classifiers)

# Create a unique identifier for each genome position
df = df.withColumn("genome_position_id", concat_ws(":", col("#chr"), col("pos(1-based)")))

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

# JDBC URL for MySQL connection
jdbc_url = f"jdbc:mysql://mariadb.bin.bioinf.nl:3306/{creds['database']}?useSSL=false&allowPublicKeyRetrieval=true"
jdbc_properties = {
    "driver": "com.mysql.cj.jdbc.Driver",
    "user": creds["user"],
    "password": creds["password"]
}

# Save the DataFrame to MySQL with overwrite mode
df.write \
   .format("jdbc") \
   .option("url", jdbc_url) \
   .option("dbtable", "nsf_predictions") \
   .option("user", creds["user"]) \
   .option("password", creds["password"]) \
   .option("driver", "com.mysql.cj.jdbc.Driver") \
   .mode("overwrite") \
   .save()

# Stop Spark session
spark.stop()
