import sys
from pyspark.sql import SparkSession

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Assignment4_Schema_Preview") \
    .master("spark://spark.bin.bioinf.nl:7077") \
    .getOrCreate()

# Set the Spark context
sc = spark.sparkContext

# Function to process the XML file and load it into a DataFrame
def load_pubmed_xml(file_path):
    # Load the first 1000 rows of the XML file into a DataFrame
    df = spark.read.format("xml") \
        .option("rowTag", "PubmedArticle") \
        .load(file_path)

    # Limit the DataFrame to the first 1000 rows
    df = df.limit(1000)

    return df

# Main function to load the file and print schema
def main(input_file):
    # Load the XML data
    df = load_pubmed_xml(input_file)

    # Print the schema of the DataFrame to understand its structure
    df.printSchema()

if __name__ == "__main__":
    # Path to the XML file
    input_file = "/data/datasets/NCBI/PubMed/pubmed21n0562.xml"

    # Run the main function
    main(input_file)
# Stop Spark session
spark.stop()