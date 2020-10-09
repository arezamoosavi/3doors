from __future__ import print_function, division, unicode_literals

from functools import partial

from pyspark.sql import SparkSession
from pyspark.sql.functions import expr, split
from pyspark.sql.functions import from_json
from pyspark.sql.types import *

# we want to change spark logging level

url = "jdbc:postgresql://postgres:5432/atmdb"


def postgres_sink(df, epoch_id, table_name):
    properties = {
        "driver": "org.postgresql.Driver",
        "user": "admin",
        "password": "admin",
    }

    df.persist()

    # 2- Write on postgres
    df.write.jdbc(url=url, table=table_name, mode="append", properties=properties)

    # 1- Save on hdfs
    #
    # df.write.format("csv").option("header", True).mode("overwrite").option(
    #     "path",
    #     "hdfs://namenode:8020/transactions",
    # ).option(
    #     "checkpointLocation",
    #     "hdfs://namenode:8020/transactions/checkpoint",
    # ).save()

    df.unpersist()


def parse_data_from_kafka_message(sdf, schema):

    assert sdf.isStreaming == True, "DataFrame doesn't receive streaming data"
    col = split(sdf["value"], ",")  # split attributes to nested array in one Column
    # now expand col to multiple top-level columns
    for idx, field in enumerate(schema):
        sdf = sdf.withColumn(field.name, col.getItem(idx).cast(field.dataType))
    return sdf.select([field.name for field in schema])


def main():
    TOPIC_NAME = "atm_transactions"
    brokerAddresses = "kafka:9092"

    # Creating stream.
    spark = SparkSession.builder.appName("ATM_Streaming").getOrCreate()

    sdf_transactions = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", brokerAddresses)
        .option("subscribe", TOPIC_NAME)
        .option("startingOffsets", "earliest")
        .load()
        .selectExpr("CAST(value AS STRING)")
    )

    sdf_transactions_schema = StructType(
        [
            StructField("ATM_Name", StringType()),
            StructField("Transaction_Date", TimestampType()),
            StructField("No_Of_XYZ_Card_Withdrawals", IntegerType()),
            StructField("No_Of_Other_Card_Withdrawals", IntegerType()),
            StructField("Total_amount_Withdrawn", LongType()),
            StructField("Amount_withdrawn_XYZ_Card", LongType()),
            StructField("Amount_withdrawn_Other_Card", LongType()),
            StructField("Weekday", StringType()),
            StructField("Festival_Religion", StringType()),
            StructField("Working_Day", StringType()),
            StructField("Holiday_Sequence", StringType()),
        ]
    )

    sdf_transactions_data = parse_data_from_kafka_message(
        sdf_transactions, sdf_transactions_schema
    )
    # sdf_transactions_data = sdf_transactions.select(
    #     from_json("value", sdf_transactions_schema).alias("a")
    # ).select("a.*")

    # Apply watermarks on event-time columns
    sdf_transactions_data = sdf_transactions_data.withWatermark(
        "Transaction_Date", "5 seconds"
    )

    sdf_transactions_data.writeStream.outputMode("append").format("csv").foreachBatch(
        partial(postgres_sink, table_name="atm_data")
    ).start().awaitTermination()


if __name__ == "__main__":
    main()
