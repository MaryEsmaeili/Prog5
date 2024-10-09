from pyspark.sql import SparkSession
from pyspark.sql.functions import year, explode
import pandas as pd
import matplotlib.pyplot as plt
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, ArrayType
import random, sys, time
from pyspark.sql import SparkSession

# Initialize Spark Session
def create_spark_session():
    spark = SparkSession.builder \
        .appName("assignment4_yourname") \
        .master("local[16]") \
        .config("spark.jars.packages", "com.databricks:spark-xml_2.12:0.15.0") \
        .getOrCreate()
    return spark
spark, sc =create_spark_session()
# Function to load and process the XML files (fixed to handle correct paths)
def load_data(spark, schema, file_path_list):
    return spark.read.format("xml") \
        .option("rootTag", "PubmedArticleSet") \
        .option("rowTag", "PubmedArticle") \
        .schema(schema) \
        .load(file_path_list)

# Function to answer question 1: Average number of co-authors per article
def q1(df):
    return df.selectExpr("size(authors) as num_authors").groupBy().avg("num_authors").first()[0]

# Function to answer question 2: Co-authorship in citations
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

# Function to answer question 3: Distribution of citations over time
def q3(df):
    df_with_year = df.withColumn("year", year(df["pub_date"]))
    df_citations = df.withColumn("citation", explode(df["citations"]))
    citation_distribution = df_citations.groupBy("year").count()
    return citation_distribution

# Function to answer question 4: Correlation between shared keywords and citations
def q4(df):
    df_keywords = df.withColumn("keyword", explode("keywords"))
    shared_keywords = df_keywords.alias("a").join(
        df_keywords.alias("b"),
        F.col("a.keyword") == F.col("b.keyword") & (F.col("a.title") != F.col("b.title")),
        how="inner"
    ).select(F.col("a.title").alias("paper1"), F.col("b.title").alias("paper2"))

    df_citation = df.withColumn("citation", explode(df["citations"]))
    citation_with_keywords = shared_keywords.join(
        df_citation.alias("c"),
        F.col("paper1") == F.col("c.title") & F.col("paper2").isin(F.col("c.citation")),
        how="left"
    ).groupBy("paper1", "paper2").count()
    return citation_with_keywords

# Function to answer question 5: Most-cited papers and keyword correlation
def q5(df):
    df_citation = df.withColumn("citation", explode(df["citations"]))
    most_cited = df_citation.groupBy("title").count().orderBy("count", ascending=False).limit(100)
    return most_cited

# Plot citation distribution over time
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

    # Define the schema
    schema = StructType([
        StructField("title", StringType(), True),
        StructField("authors", ArrayType(StringType()), True),
        StructField("citations", ArrayType(StringType()), True),
        StructField("keywords", ArrayType(StringType()), True),
        StructField("pub_date", StringType(), True)
    ])
    
    # Load the data (make sure your path is correct)
    df = load_data(spark, schema, "/data/datasets/NCBI/PubMed/file1.xml")
    
    
    # # List of 5 specific XML files (adjust these paths according to your environment)
    # file_path_list = [
    #     "/data/datasets/NCBI/PubMed/file1.xml"
        # "/data/datasets/NCBI/PubMed/file2.xml",
        # "/data/datasets/NCBI/PubMed/file3.xml",
        # "/data/datasets/NCBI/PubMed/file4.xml",
        # "/data/datasets/NCBI/PubMed/file5.xml"
    # ]

    # # Load data
    # df = load_data(spark, schema, "/data/datasets/NCBI/PubMed/file1.xml")

    # Perform analysis for each question
    avg_coauthors = q1(df)
    # coauthor_citation_ratio = q2(df)
    # citation_distribution = q3(df)
    # citation_with_keywords = q4(df)
    # most_cited = q5(df)

    # # Plot citation distribution
    # plot_citation_distribution(df)

    # Collect all results
    results = {
        "Average number of co-authors": avg_coauthors,
        # "Co-author citation ratio": coauthor_citation_ratio,
        # "Citation Distribution": citation_distribution.collect(),
        # "Citation with Shared Keywords": citation_with_keywords.collect(),
        # "Most-cited Papers": most_cited.collect()
    }

    # Save the results to CSV
    pd.DataFrame.from_dict(results, orient='index').to_csv("assignment4_answers.csv")

if __name__ == "__main__":
    main()
