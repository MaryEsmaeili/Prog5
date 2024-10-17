import random, sys, time
sys.path.append('/opt/spark/python/lib/py4j-0.10.9.7-src.zip')
sys.path.append('/opt/spark/python')
from pyspark.sql import SparkSession
from pyspark.sql.functions import year, explode
from pyspark.sql.functions import col, substring, desc, countDistinct
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, ArrayType

# Initialize Spark Session
def create_spark_session():
    spark = SparkSession.builder\
    .appName("assignment4_Maryam")\
    .master("spark://spark.bin.bioinf.nl:7077")\
    .config("spark.jars.packages", "com.databricks:spark-xml_2.12:0.15.0")\
    .getOrCreate()
    return spark
# def create_spark_session():
#     spark = SparkSession.builder \
#         .appName("assignment4_Maryam") \
#         .master("spark://spark.bin.bioinf.nl:7077") \
#         .config("spark.executor.memory", "4g") \
#         .config("spark.executor.cores", "2") \
#         .config("spark.driver.memory", "4g") \
#         .config("spark.ui.port", "4051") \
#         .config("spark.jars.packages", "com.databricks:spark-xml_2.12:0.15.0") \
#         .getOrCreate()
#     return spark
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
    # Explode authors and citations to create individual rows
    df_exploded = df.withColumn("author", explode("authors")) \
                    .withColumn("citation", explode("citations"))
    
    # Perform a self-join to find matching authors between citing and cited papers
    coauthored_citations = df_exploded.alias("citing").join(
        df_exploded.alias("cited"),
        (F.col("citing.citation") == F.col("cited.title")) &  # Match citations with titles
        (F.col("citing.author") == F.col("cited.author")),    # Match authors between citing and cited
        how="inner"
    ).select(
        F.col("citing.title").alias("citing_paper"),
        F.col("citing.author").alias("common_author"),
        F.col("cited.title").alias("cited_paper")
    )
    
    # Calculate the total number of citations and the number of co-authored citations
    total_citations = df_exploded.select("citation").distinct().count()
    coauthored_citations_count = coauthored_citations.distinct().count()
    
    # Calculate the ratio of co-authored citations to total citations
    coauthor_citation_ratio = coauthored_citations_count / total_citations if total_citations > 0 else 0
    
    return coauthor_citation_ratio


# Function to answer question 3: Distribution of citations over time
def q3(df):
    # Step 1: Extract the year from the pub_date column
    df_with_year = df.withColumn("year", substring("pub_date", 1, 4))
    
    # Step 2: Explode the citations array to create individual rows for each citation
    df_citations = df_with_year.withColumn("citation", explode("citations"))
    
    # Step 3: General citation distribution over time
    general_citation_distribution = df_citations.groupBy("year").count().orderBy("year")
    
    # Step 4: Identify papers with the highest number of citations
    most_cited_papers = df_citations.groupBy("title").count().orderBy(desc("count")).limit(10)
    
    # Step 5: Filter the citation data for the most cited papers
    most_cited_titles = [row["title"] for row in most_cited_papers.collect()]
    most_cited_distribution = df_citations.filter(col("title").isin(most_cited_titles)) \
                                          .groupBy("year").count().orderBy("year")
    
    # Step 6: Return both distributions
    return general_citation_distribution, most_cited_distribution


# Function to answer question 4: Correlation between shared keywords and citations
def q4(df):
    # Step 1: Explode the keywords and citations columns to create individual rows
    df_keywords = df.withColumn("keyword", explode("keywords"))
    df_citations = df.withColumn("citation", explode("citations"))
    
    # Step 2: Find papers that share keywords
    shared_keywords = df_keywords.alias("a").join(
        df_keywords.alias("b"),
        (F.col("a.keyword") == F.col("b.keyword")) & (F.col("a.title") != F.col("b.title")),
        how="inner"
    ).select(
        F.col("a.title").alias("paper1"),
        F.col("b.title").alias("paper2"),
        F.col("a.keyword").alias("shared_keyword")
    )
    
    # Step 3: Count the number of shared keywords between each pair of papers
    shared_keywords_count = shared_keywords.groupBy("paper1", "paper2") \
                                           .agg(countDistinct("shared_keyword").alias("shared_keyword_count"))
    
    # Step 4: Find pairs of papers where one cites the other
    citation_pairs = df_citations.alias("a").join(
        df.alias("b"),
        F.col("a.citation") == F.col("b.title"),
        how="inner"
    ).select(
        F.col("a.title").alias("citing_paper"),
        F.col("b.title").alias("cited_paper")
    ).distinct()
    
    # Step 5: Join the shared keyword count with the citation pairs
    correlation_data = shared_keywords_count.join(
        citation_pairs,
        (shared_keywords_count.paper1 == citation_pairs.citing_paper) & 
        (shared_keywords_count.paper2 == citation_pairs.cited_paper),
        how="inner"
    ).select("shared_keyword_count")
    
    # Step 6: Calculate the correlation between the number of shared keywords and citations
    total_citation_pairs = citation_pairs.count()
    citation_with_shared_keywords = correlation_data.count()
    correlation_ratio = citation_with_shared_keywords / total_citation_pairs if total_citation_pairs > 0 else 0
    
    return correlation_ratio

# Function to answer question 5: Most-cited papers and keyword correlation
def q5(df, cutoff=100):
    # Step 1: Explode the keywords and citations columns to create individual rows
    df_keywords = df.withColumn("keyword", explode("keywords"))
    df_citations = df.withColumn("citation", explode("citations"))
    
    # Step 2: Identify the most-cited papers based on the cutoff
    most_cited_papers = df_citations.groupBy("title").count().orderBy(desc("count")).limit(cutoff)
    most_cited_titles = [row["title"] for row in most_cited_papers.collect()]
    
    # Step 3: Find papers that share keywords
    shared_keywords = df_keywords.alias("a").join(
        df_keywords.alias("b"),
        (F.col("a.keyword") == F.col("b.keyword")) & (F.col("a.title") != F.col("b.title")),
        how="inner"
    ).select(
        F.col("a.title").alias("paper1"),
        F.col("b.title").alias("paper2"),
        F.col("a.keyword").alias("shared_keyword")
    )
    
    # Step 4: Count the number of shared keywords between each pair of papers
    shared_keywords_count = shared_keywords.groupBy("paper1", "paper2") \
                                           .agg(countDistinct("shared_keyword").alias("shared_keyword_count"))
    
    # Step 5: Filter for pairs where one paper is among the most-cited
    shared_keywords_most_cited = shared_keywords_count.filter(
        col("paper1").isin(most_cited_titles) | col("paper2").isin(most_cited_titles)
    )
    
    # Step 6: Find citation pairs where the citing or cited paper is among the most-cited
    citation_pairs_most_cited = df_citations.alias("a").join(
        df.alias("b"),
        F.col("a.citation") == F.col("b.title"),
        how="inner"
    ).filter(
        F.col("a.title").isin(most_cited_titles) | F.col("b.title").isin(most_cited_titles)
    ).select(
        F.col("a.title").alias("citing_paper"),
        F.col("b.title").alias("cited_paper")
    ).distinct()
    
    # Step 7: Join the shared keyword counts with the filtered citation pairs
    correlation_data_most_cited = shared_keywords_most_cited.join(
        citation_pairs_most_cited,
        (shared_keywords_most_cited.paper1 == citation_pairs_most_cited.citing_paper) & 
        (shared_keywords_most_cited.paper2 == citation_pairs_most_cited.cited_paper),
        how="inner"
    ).select("shared_keyword_count")
    
    # Step 8: Calculate the correlation for the most-cited papers
    total_citation_pairs_most_cited = citation_pairs_most_cited.count()
    citation_with_shared_keywords_most_cited = correlation_data_most_cited.count()
    correlation_ratio_most_cited = citation_with_shared_keywords_most_cited / total_citation_pairs_most_cited if total_citation_pairs_most_cited > 0 else 0
    
    return correlation_ratio_most_cited

# Main function to run all analyses and save results
def main():
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("ERROR")
    
    # Define the schema for the nested XML structure
    schema = StructType([
        StructField("MedlineCitation", StructType([
            StructField("Article", StructType([
                StructField("ArticleTitle", StringType(), True),
                StructField("AuthorList", StructType([
                    StructField("Author", ArrayType(StructType([
                        StructField("ForeName", StringType(), True),
                        StructField("LastName", StringType(), True),
                        StructField("Initials", StringType(), True)
                    ])), True)
                ]), True),
                StructField("Journal", StructType([
                    StructField("JournalIssue", StructType([
                        StructField("PubDate", StructType([
                            StructField("Year", StringType(), True),
                            StructField("Month", StringType(), True),
                            StructField("Day", StringType(), True)
                        ]), True)
                    ]), True),
                    StructField("Title", StringType(), True)
                ]), True),
                StructField("Abstract", StructType([
                    StructField("AbstractText", ArrayType(StructType([
                        StructField("_VALUE", StringType(), True)
                    ])), True)
                ]), True)
            ]), True),
            StructField("KeywordList", StructType([
                StructField("Keyword", ArrayType(StructType([
                    StructField("_VALUE", StringType(), True)
                ])), True)
            ]), True)
        ]), True),
        StructField("PubmedData", StructType([
            StructField("ArticleIdList", StructType([
                StructField("ArticleId", ArrayType(StructType([
                    StructField("_VALUE", StringType(), True)
                ])), True)
            ]), True)
        ]), True)
    ])

    # Load the data with the defined schema
    df = load_data(spark, schema, "/data/datasets/NCBI/PubMed/pubmed21n0562.xml")

    # Extract relevant fields using the schema
    df_extracted = df.select(
        F.col("MedlineCitation.Article.ArticleTitle").alias("title"),
        F.col("MedlineCitation.Article.AuthorList.Author.ForeName").alias("authors"),
        F.col("MedlineCitation.Article.Journal.JournalIssue.PubDate.Year").alias("pub_date"),
        F.col("MedlineCitation.KeywordList.Keyword._VALUE").alias("keywords"),
        F.col("PubmedData.ArticleIdList.ArticleId._VALUE").alias("citations")
    )
    df_extracted = df_extracted.limit(1000)
    # Perform analysis for each question
    avg_coauthors = q1(df_extracted)
    coauthor_citation_ratio = q2(df_extracted)
    general_citation_distribution, most_cited_distribution = q3(df_extracted)
    citation_with_keywords = q4(df_extracted)
    correlation_most_cited = q5(df_extracted)

    # Collect results for citation distributions
    general_citation_data = general_citation_distribution.collect()
    most_cited_data = most_cited_distribution.collect()

    # # Plot citation distribution
    # plot_citation_distribution(general_citation_distribution)

    # Print the results
    print("Average number of co-authors:", avg_coauthors)
    print("Co-author citation ratio:", coauthor_citation_ratio)
    print("Correlation ratio for shared keywords:", citation_with_keywords)
    print("Correlation for most-cited papers:", correlation_most_cited)

    # Collect all results
    results = {
        "Average number of co-authors": avg_coauthors,
        "Co-author citation ratio": coauthor_citation_ratio,
        "General Citation Distribution": general_citation_data,
        "Most Cited Distribution": most_cited_data,
        "Correlation with Shared Keywords": citation_with_keywords,
        "Correlation for Most-Cited Papers": correlation_most_cited
    }

    # Save the results to CSV
    pd.DataFrame.from_dict(results, orient='index').to_csv("assignment4_answers.csv")

if __name__ == "__main__":
    main()


    # Show the extracted DataFrame
    # df_extracted.show(truncate=False)
    
    # # List of 5 specific XML files (adjust these paths according to your environment)
    # file_path_list = [
    #     "/data/datasets/NCBI/PubMed/file1.xml"
        # "/data/datasets/NCBI/PubMed/file2.xml",
        # "/data/datasets/NCBI/PubMed/file3.xml",
        # "/data/datasets/NCBI/PubMed/file4.xml",
        # "/data/datasets/NCBI/PubMed/file5.xml"
    # ]

    # Load the data (make sure your path is correct)
    # df = load_data(spark, schema, "/data/datasets/NCBI/PubMed/pubmed21n0562.xml")
    # df.show()
    # check if my file exists???
    # import os
    # print(os.path.exists("/data/datasets/NCBI/PubMed/pubmed21n0562.xml"))

    # Test without schema
    # df = spark.read.format("xml") \
    #     .option("rootTag", "PubmedArticleSet") \
    #     .option("rowTag", "PubmedArticle") \
    #     .load("/data/datasets/NCBI/PubMed/pubmed21n0562.xml")

    # df.show()
    # df.printSchema()