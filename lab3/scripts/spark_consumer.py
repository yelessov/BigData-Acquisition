from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, avg, round
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType

# 1. Initialize Spark Structured Streaming
spark = SparkSession.builder \
    .appName("SmartCityTrafficMonitor") \
    .getOrCreate()

# Disable noisy logging
spark.sparkContext.setLogLevel("WARN")

# 2. Define the JSON schema of our incoming IoT data
schema = StructType([
    StructField("Vehicle_ID", StringType(), True),
    StructField("Highway_ID", StringType(), True),
    StructField("Speed_KMH", IntegerType(), True),
    StructField("Timestamp", TimestampType(), True)
])

print("📡 Connecting to Kafka 'highway-telemetry' stream...")

# 3. Read the real-time stream from Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "highway-telemetry") \
    .option("startingOffsets", "latest") \
    .option("failOnDataLoss", "false") \
    .load()

# 4. Parse the raw Kafka bytes into a readable Spark DataFrame
parsed_df = df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

# 5. Perform the 10-Second Tumbling Window Aggregation
traffic_monitor = parsed_df \
    .withWatermark("Timestamp", "10 seconds") \
    .groupBy(
        window(col("Timestamp"), "10 seconds"),
        col("Highway_ID")
    ) \
    .agg(round(avg("Speed_KMH"), 2).alias("Average_Speed_KMH"))

# 6. Output the live dashboard to the console
query = traffic_monitor.writeStream \
    .outputMode("update") \
    .format("console") \
    .option("truncate", "false") \
    .start()

query.awaitTermination()