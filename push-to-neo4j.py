import sys
from operator import add

from pyspark.sql import SparkSession

if __name__ == "__main__":
    spark = SparkSession \
        .builder \
        .appName("push-to-neo4j") \
        .getOrCreate()

    df = spark.createDataFrame([("John Doe", 32), ("Jane Doe", 42)], ["name", "age"])

    df.write.format("org.neo4j.spark.DataSource") \
        .mode("append") \
        .option("url", "neo4j://10.103.209.48:7687") \
        .option("authentication.basic.username", "neo4j") \
        .option("authentication.basic.password", "passw0rd") \
        .option("labels", ":Person") \
        .save()

    spark.stop()
