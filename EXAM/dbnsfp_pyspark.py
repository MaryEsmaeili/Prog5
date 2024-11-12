import sys
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, avg, min, max, when, concat, lit, count
from pyspark.sql.types import FloatType

# Setup Spark
sys.path.append('/opt/spark/python')
sys.path.append('/opt/spark/python/lib/py4j-0.10.9.7-src.zip')

spark = SparkSession.builder.appName("dbNSFP_exam") \
    .config("spark.ui.enabled", "false") \
    .config("spark.executor.memory", "8g") \
    .config("spark.driver.memory", "8g") \
    .master("local[8]").getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

# Load data
data_path = "/data/datasets/dbNSFP/snpEff/data/dbNSFP4.9a.txt.gz.SMALL"
df = spark.read.csv(data_path, header=True, sep="\t")

# Define the function to clean data
def clean_column(df: DataFrame, column_name: str) -> DataFrame:
    """
    Replaces '.', ';', or '.;' with None in the specified column and casts it to FloatType.
    
    Parameters:
    - df (DataFrame): The input DataFrame
    - column_name (str): The column name to be cleaned and cast
    
    Returns:
    - DataFrame: The DataFrame with the specified column cleaned and cast to FloatType
    """
    return df.withColumn(
        column_name,
        when(
            col(column_name).rlike(r"^\.;?$"),
            None
        ).otherwise(col(column_name).cast(FloatType()))
    )

# Question 1: Calculate average, minimum, and maximum SIFT_score
def question1(df):
    # Clean the column SIFT_score
    df_cleaned = clean_column(df, 'SIFT_score')
    
    # Calculate statistics
    result = df_cleaned.select(
        avg(col("SIFT_score")).alias("mean_SIFT_score"),
        min(col("SIFT_score")).alias("min_SIFT_score"),
        max(col("SIFT_score")).alias("max_SIFT_score")
    )
    
    # Display result (for debugging purposes)
    result.show()

    # Answer: mean, min, and max of SIFT_score
    return result.collect()

# Question 2: Merge hg19_chr and hg19_pos(1-based) into hg19_chr_pos and remove the originals
def question2(df):
    # Create the new column by concatenating hg19_chr and hg19_pos(1-based)
    df = df.withColumn("hg19_chr_pos", concat(col("hg19_chr"), lit("_"), col("hg19_pos(1-based)")))
    
    # Drop the original hg19_chr and hg19_pos(1-based) columns
    df = df.drop("hg19_chr", "hg19_pos(1-based)")

    # Return the modified DataFrame
    return df

# Question 3: Find the most common codon position
def question3(df):
    """
    Determines the codon position ('codonpos') with the most predicted effects across all SNPs in the file.
    Args:
        df (DataFrame): The input DataFrame.

    Returns:
        tuple: The most common codon position and its count.
    """
    # Count the occurrences of each "codonpos" value
    codonpos_counts = df.groupBy("codonpos").agg(count("*").alias("count")).orderBy(col("count").desc())

    # Fetch the codon position with the highest count
    most_common_codonpos = codonpos_counts.first()

    return most_common_codonpos

# Run the questions
question1(df)
df = question2(df)
df.select("hg19_chr_pos").show()
print("Most common codon position:", question3(df))

# Stop Spark session
spark.stop()
