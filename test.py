from pyspark.sql import SparkSession
from pyspark.sql.functions import year, explode, col
from pyspark.sql.types import StructType, StructField, StringType, ArrayType
import pandas as pd

# Initialize Spark Session
def create_spark_session():
    spark = SparkSession.builder \
        .appName("assignment4") \
        .master("spark://spark.bin.bioinf.nl:7077") \
        .config("spark.jars.packages", "com.databricks:spark-xml_2.12:0.15.0") \
        .getOrCreate()
    return spark

# Function to load and process the XML file
def load_data(spark, schema, file_path):
    return spark.read.format("xml") \
        .option("rootTag", "PubmedArticleSet") \
        .option("rowTag", "PubmedArticle") \
        .schema(schema) \
        .load(file_path)

# Function to answer question 1: Average number of co-authors per article
def q1(df):
    return df.selectExpr("size(authors) as num_authors").groupBy().avg("num_authors").first()[0]

# Function to answer question 2: Co-authorship in citations
def q2(df):
    df_authors = df.withColumn("author", explode("authors"))
    df_citations = df.withColumn("citation", explode("citations"))
    coauthor_citations = df_authors.alias("a").join(
        df_authors.alias("b"),
        (col("a.citation") == col("b.title")) & (col("a.author") == col("b.author")),
        how="inner"
    ).select(col("a.title").alias("citing_paper"), col("a.author").alias("author"), col("a.citation").alias("cited_paper"))
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
        col("a.keyword") == col("b.keyword") & (col("a.title") != col("b.title")),
        how="inner"
    ).select(col("a.title").alias("paper1"), col("b.title").alias("paper2"))

    df_citation = df.withColumn("citation", explode(df["citations"]))
    citation_with_keywords = shared_keywords.join(
        df_citation.alias("c"),
        col("paper1") == col("c.title") & col("paper2").isin(col("c.citation")),
        how="left"
    ).groupBy("paper1", "paper2").count()
    return citation_with_keywords

# Function to answer question 5: Most-cited papers and keyword correlation
def q5(df):
    df_citation = df.withColumn("citation", explode(df["citations"]))
    most_cited = df_citation.groupBy("title").count().orderBy("count", ascending=False).limit(100)
    return most_cited

# Main function to test all functions
def main():
    spark = create_spark_session()

    # Define the schema to match the structure of your XML
    schema = StructType([
        StructField("title", StringType(), True),
        StructField("authors", ArrayType(StringType()), True),
        StructField("citations", ArrayType(StringType()), True),
        StructField("keywords", ArrayType(StringType()), True),
        StructField("pub_date", StringType(), True)
    ])
    
    # Single file path for testing
    file_path = "/data/datasets/NCBI/PubMed/file1.xml"
    
    # Load the XML file
    df = load_data(spark, schema, file_path)
    
    # Test each function and print the results
    avg_coauthors = q1(df)
    print(f"Average number of co-authors: {avg_coauthors}")

    coauthor_citation_ratio = q2(df)
    print(f"Co-author citation ratio: {coauthor_citation_ratio}")

    citation_distribution = q3(df)
    print(f"Citation distribution over time:")
    citation_distribution.show()

    shared_keywords = q4(df)
    print(f"Shared keywords between papers:")
    shared_keywords.show()

    most_cited = q5(df)
    print(f"Most-cited papers:")
    most_cited.show()

if __name__ == "__main__":
    main()
