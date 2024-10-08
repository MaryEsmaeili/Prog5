import random, sys, time
sys.path.append('/opt/spark/python')
sys.path.append('/opt/spark/python/lib/py4j-0.10.9.7-src.zip')
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("assignment4_yourname").master("spark://spark.bin.bioinf.nl:7077").getOrCreate()
sc = spark.sparkContext
