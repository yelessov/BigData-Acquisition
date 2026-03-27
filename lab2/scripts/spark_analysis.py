from pyspark.sql import SparkSession
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

# 1. Spark Infrastructure (Connect to Master)
spark = SparkSession.builder \
    .appName("CyberIntrusionDetection") \
    .master("local[*]") \
    .getOrCreate()

# ✅ Data Loading (200K records)
df = spark.read.csv("/home/jovyan/work/scripts/data/network_traffic.csv", header=True, inferSchema=True)

# ✅ Data Preprocessing
indexer = StringIndexer(inputCol="protocol_type", outputCol="protocol_index")
df_indexed = indexer.fit(df).transform(df)

assembler = VectorAssembler(
    inputCols=["duration", "src_bytes", "dst_bytes", "protocol_index"], 
    outputCol="features"
)
ml_data = assembler.transform(df_indexed).select("id", "features", "is_attack")

# ✅ Model Training: Random Forest with 50 trees
train, test = ml_data.randomSplit([0.8, 0.2])
rf = RandomForestClassifier(labelCol="is_attack", featuresCol="features", numTrees=50)
model = rf.fit(train)

# ✅ Model Evaluation: Accuracy
predictions = model.transform(test)
evaluator = MulticlassClassificationEvaluator(labelCol="is_attack", metricName="accuracy")
accuracy = evaluator.evaluate(predictions)
print("\n" + "="*30)
print("LAB 2 RESULTS: Model Accuracy: {:.2f}%".format(accuracy * 100))
print("="*30 + "\n")

# ✅ RDD Operations (DataFrame -> RDD)
# Move from high-level tables to low-level transformations
results_rdd = predictions.select("id", "prediction").rdd

# ✅ Map Transformation
# Custom formatting for the output text file
formatted_log = results_rdd.map(lambda x: "SessionID: {} | ThreatDetected: {}".format(int(x[0]), bool(x[1])))

# ✅ Data Persistence & Distributed Processing (10 partitions)
# Force the data into exactly 10 shards across the cluster
output_path = "/home/jovyan/work/output/threat_report_logs"
import shutil, os
if os.path.exists(output_path): shutil.rmtree(output_path)

formatted_log.repartition(10).saveAsTextFile(output_path)

spark.stop()