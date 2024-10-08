from pyspark.sql import SparkSession
from pyspark.sql.functions import year, explode
import pandas as pd
import matplotlib.pyplot as plt
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, ArrayType

# Initialize Spark Session
def create_spark_session():
    spark = SparkSession.builder.appName("assignment4").master("spark://spark.bin.bioinf.nl:7077").getOrCreate()
    return spark
def create_spark_session():
    spark = SparkSession.builder \
        .appName("assignment4") \
        .master("spark://spark.bin.bioinf.nl:7077") \
        .config("spark.jars.packages", "com.databricks:spark-xml_2.12:0.15.0") \
        .getOrCreate()
    return spark
# Function to load and process exactly 5 XML files
def load_data(spark, schema, file_path_list):
    return spark.read.format("xml") \
        .option("rootTag", "PubmedArticleSet") \
        .option("rowTag", "PubmedArticle") \
        .schema(schema) \
        .load(file_path_list)

# Function to answer question 1
def q1(df):
    return df.selectExpr("size(authors) as num_authors").groupBy().avg("num_authors").first()[0]

# Function to answer question 2
def q2(df):
    df_authors = df.withColumn("author", explode("authors"))
    df_citations = df.withColumn("citation", explode("citations"))
    coauthor_citations = df_authors.alias("a").join(
        df_authors.alias("b"),
        (F.col("a.citation") == F.col("b.title")) & (F.col("a.author") == F.col("b.author")),
        how="inner"
    ).select(F.col("a.title").alias("citing_paper"), F.col("a.author").alias("author"), F.col("a.citation").alias("cited_paper"))
    total_citations = df_citations.count()
    coauthor_citations_count = coauthor_citations.count()
    coauthor_citation_ratio = coauthor_citations_count / total_citations if total_citations > 0 else 0
    return coauthor_citation_ratio

# Function to plot citation distribution over time
def plot_citation_distribution(df):
    citation_counts = df.groupBy("year").count().orderBy("year").toPandas()
    plt.figure(figsize=(10, 6))
    plt.plot(citation_counts["year"], citation_counts["count"], marker='o')
    plt.title("Citation Distribution Over Time")
    plt.xlabel("Year")
    plt.ylabel("Number of Citations")
    plt.grid(True)
    plt.savefig("citation_distribution_over_time.png")

# Main function to run all analyses and save results
def main():

    spark = create_spark_session()
    schema = StructType([
        StructField("title", StringType(), True),
        StructField("authors", ArrayType(StringType()), True),
        StructField("citations", ArrayType(StringType()), True),
        StructField("keywords", ArrayType(StringType()), True),
        StructField("pub_date", StringType(), True)
    ])
    
    file_path_list = [
        "/data/datasets/NCBI/PubMed/pubmed21n0002.xml",
        "/data/datasets/NCBI/PubMed/pubmed21n0012.xml",
        "/data/datasets/NCBI/PubMed/pubmed21n0032.xml",
        "/data/datasets/NCBI/PubMed/pubmed21n0042.xml",
        "/data/datasets/NCBI/PubMed/pubmed21n0052.xml"
    ]
    
    df = load_data(spark, schema, file_path_list)
    
    avg_coauthors = q1(df)
    coauthor_citation_ratio = q2(df)
    
    # Plot citation distribution over time
    plot_citation_distribution(df)
    
    # Collect results
    results = {
        "Average number of co-authors": avg_coauthors,
        "Co-author citation ratio": coauthor_citation_ratio
    }
    
    # Save the results to CSV
    pd.DataFrame.from_dict(results, orient='index').to_csv("assignment4_answers.csv")

if __name__ == "__main__":
    main()
