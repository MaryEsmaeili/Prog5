import pyspark
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.functions import col, count, when

# تنظیمات Spark Session
spark = SparkSession.builder \
    .appName("SNP_Data_Exploration") \
    .master("local[*]") \
    .getOrCreate()

# مسیر فایل داده‌ها
data_path = '/data/datasets/dbNSFP/snpEff/data/dbNSFP4.9a.txt.gz.SMALL'

# بارگذاری داده‌ها با schema اولیه برای بررسی
df = spark.read.csv(data_path, sep='\t', header=True, inferSchema=True)

# df.show(5)
# df.printSchema()


# # نمایش schema داده‌ها
# print("Schema of the DataFrame:")
# df.printSchema()

# # نمایش نمونه‌ای از داده‌ها
# print("Sample data:")
# df.show(5)

# # شمارش تعداد کل سطرها و ستون‌ها
# print(f"Total rows: {df.count()}, Total columns: {len(df.columns)}")

# # بررسی تعداد مقادیر Null در هر ستون
# print("Count of NULL values in each column:")
# null_counts = df.select([F.count(F.when(F.col(c).isNull(), c)).alias(c) for c in df.columns])
# null_counts.show()

# 1
# Count SNPs per chromosome and find the chromosome with the maximum count
# Counting SNPs per chromosome
chromosome_counts = df.groupBy(col("#chr")).agg(count("*").alias("snp_count"))
top_chromosome = chromosome_counts.orderBy(col("snp_count").desc()).first()

# Show the distinct chromosomes and their SNP counts
# chromosome_counts = df.groupBy("#chr").count().orderBy("count", ascending=False)
# chromosome_counts.show()

# Print the result
print(f"Chromosome with the most annotated SNPs: {top_chromosome['#chr']}, Count: {top_chromosome['snp_count']}")

# 2
# Count rows where the hg18 and hg19 positions differ

# differing_positions_count = df.filter(
#     (df["hg18_pos(1-based)"].isNotNull()) & 
#     (df["hg19_pos(1-based)"].isNotNull()) & 
#     (df["hg18_pos(1-based)"] != df["hg19_pos(1-based)"])
# ).count()
diff_position_count = df.filter(F.col("hg18_pos(1-based)") != F.col("hg19_pos(1-based)")).count()
print("Number of SNPs with differing positions between hg18 and hg19:", diff_position_count)

# 3
# Models with no predictions
prediction_columns = ["SIFT_score", "Polyphen2_HDIV_score", "MutationTaster_score", "FATHMM_score", "PROVEAN_score"]

# Replace dots with nulls in prediction columns and cast as double
for col_name in prediction_columns:
    df = df.withColumn(col_name, when(col(col_name) == '.', None).otherwise(col(col_name).cast("double")))

# Calculate the number of rows in the dataframe
total_rows = df.count()

# Identify models with no predictions
null_counts = df.select([count(when(col(c).isNull(), c)).alias(c) for c in prediction_columns])
no_prediction_models = [col for col, null_count in null_counts.collect()[0].asDict().items() if null_count == total_rows]

# Output the result for models with no predictions
print("Models with no predictions at all:", no_prediction_models)
print("Number of models with no predictions:", len(no_prediction_models))

# 4
# Check if `aaref` column exists before proceeding
if "aaref" in df.columns:
    avg_score_per_aaref = df.groupBy("aaref").agg(
        F.mean(F.coalesce("SIFT_score", F.lit(0)) +
               F.coalesce("Polyphen2_HDIV_score", F.lit(0)) +
               F.coalesce("MutationTaster_score", F.lit(0)) +
               F.coalesce("FATHMM_score", F.lit(0)) +
               F.coalesce("PROVEAN_score", F.lit(0))
              ).alias("average_score")
    )

    # Find the amino acid with the highest average score
    highest_avg_score = avg_score_per_aaref.orderBy(F.desc("average_score")).first()
    if highest_avg_score:
        print(f"Amino acid with the highest average score: {highest_avg_score['aaref']}, Score: {highest_avg_score['average_score']}")
    else:
        print("No amino acid found with predictor scores.")
else:
    print("The 'aaref' column is not available in the dataset.")

# Stop Spark session
spark.stop()