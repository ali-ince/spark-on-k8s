import sys
from operator import add

from pyspark.sql import SparkSession

if __name__ == "__main__":
    spark = SparkSession \
        .builder \
        .appName("push-to-neo4j") \
        .getOrCreate()

    # load suppliers
    suppliers = spark.read.jdbc(
        "jdbc:postgresql://data-import-experiment-postgres.cgzrnuxjdpso.us-east-1.rds.amazonaws.com:5432/northwind",
        "suppliers",
        numPartitions=5,
        properties={"user": "postgres", "password": "mypassword", "driver": "org.postgresql.Driver"})
    suppliers.show()

    # create suppliers nodes
    suppliers \
        .select("supplierid", "companyname", "address", "city", "region", "postalcode", "country") \
        .withColumnsRenamed(
        {"supplierid": "id", "companyname": "name", "address": "address", "city": "city", "region": "region",
         "postalcode": "postalcode", "country": "country"}) \
        .write \
        .format("org.neo4j.spark.DataSource") \
        .mode("overwrite") \
        .option("url", "neo4j://my-neo4j-release:7687") \
        .option("authentication.basic.username", "neo4j") \
        .option("authentication.basic.password", "passw0rd") \
        .option("labels", ":Supplier") \
        .option("node.keys", "id") \
        .option("schema.optimization.type", "NODE_CONSTRAINTS") \
        .save()

    # load products table
    products = spark.read.jdbc(
        "jdbc:postgresql://data-import-experiment-postgres.cgzrnuxjdpso.us-east-1.rds.amazonaws.com:5432/northwind",
        "products",
        numPartitions=5,
        properties={"user": "postgres", "password": "mypassword", "driver": "org.postgresql.Driver"})
    products.show()

    # create products nodes
    products.select("productid", "productname", "unitprice", "discontinued") \
        .withColumnsRenamed(
        {"productid": "id", "productname": "name", "unitprice": "price", "discontinued": "discontinued"}) \
        .write \
        .format("org.neo4j.spark.DataSource") \
        .mode("overwrite") \
        .option("url", "neo4j://my-neo4j-release:7687") \
        .option("authentication.basic.username", "neo4j") \
        .option("authentication.basic.password", "passw0rd") \
        .option("labels", ":Product") \
        .option("node.keys", "id") \
        .option("schema.optimization.type", "NODE_CONSTRAINTS") \
        .save()

    # create Supplies relationship
    products \
        .select("productid", "supplierid") \
        .repartition(1) \
        .write \
        .format("org.neo4j.spark.DataSource") \
        .mode("overwrite") \
        .option("url", "neo4j://my-neo4j-release:7687") \
        .option("authentication.basic.username", "neo4j") \
        .option("authentication.basic.password", "passw0rd") \
        .option("relationship", "SUPPLIES") \
        .option("relationship.save.strategy", "keys") \
        .option("relationship.source.labels", ":Supplier") \
        .option("relationship.source.save.mode", "match") \
        .option("relationship.source.node.keys", "supplierid:id") \
        .option("relationship.target.labels", ":Product") \
        .option("relationship.target.save.mode", "match") \
        .option("relationship.target.node.keys", "productid:id") \
        .save()

    spark.stop()
