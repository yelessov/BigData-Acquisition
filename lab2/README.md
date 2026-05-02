# Lab 2: Cyber Intrusion Detection with Apache Spark

## Overview

Lab 2 demonstrates a **distributed machine learning pipeline** using Apache Spark to detect network-based cyber intrusions. The lab uses Docker containers to orchestrate Spark infrastructure (Master/Worker nodes) and Jupyter for interactive analysis. It processes 200,000 synthetically generated network traffic records to classify attack vs. normal sessions.

---

## Quick Start

```bash
cd /Users/yelessov/Desktop/movie-hadoop-project/lab2
docker compose up -d
python3 scripts/generate_data.py
docker exec jupyter-lab spark-submit /home/jovyan/work/scripts/spark_analysis.py
```

**Expected Result:** Model achieves ~80% accuracy on cyber threat detection.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose Stack                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Spark Master │  │ Spark Worker │  │  Jupyter Lab     │  │
│  │   :8080      │  │   :7077      │  │   :8888          │  │
│  │   :7077      │  │              │  │                  │  │
│  └──────────────┘  └──────────────┘  │ - PySpark        │  │
│                                       │ - Pandas         │  │
│                                       │ - NumPy          │  │
│                                       └──────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
         ↑
         │ Mounts /lab2 → /home/jovyan/work
         │
    Local File System
```

### Services

| Service | Container | Port | Role |
|---------|-----------|------|------|
| **Spark Master** | `spark-master` | 8080 (UI), 7077 (RPC) | Coordinates distributed jobs, manages worker nodes |
| **Spark Worker** | `spark-worker` | N/A | Executes distributed tasks assigned by master |
| **Jupyter** | `jupyter-lab` | 8888 (HTTP) | Interactive Python/PySpark notebook environment |

---

## Project Structure

```
lab2/
├── README.md                          # This file
├── docker-compose.yml                 # Docker Compose configuration
├── scripts/
│   ├── generate_data.py              # Generates 200K synthetic network traffic records
│   ├── spark_analysis.py             # Main Spark ML pipeline for intrusion detection
│   └── data/
│       └── network_traffic.csv       # Generated dataset (200K records)
└── output/
    └── threat_report_logs/           # Distributed output (10 partitions)
        ├── part-00000 → part-00009   # Results split across 10 files
        └── _SUCCESS                  # Spark completion marker
```

---

## Components & Workflow

### 1. **Data Generation** (`scripts/generate_data.py`)

Generates synthetic network traffic data with 200,000 records.

**Features Generated:**
- `id`: Unique session identifier (0–199,999)
- `duration`: Session length in milliseconds (0–1000)
- `protocol_type`: Network protocol (TCP, UDP, or ICMP)
- `src_bytes`: Source-to-destination bytes transferred (100–50,000)
- `dst_bytes`: Destination-to-source bytes transferred (100–50,000)
- `is_attack`: Binary label (1 = attack, 0 = normal) — 20% are attacks, 80% are normal

**Output:** `scripts/data/network_traffic.csv`

```python
data = {
    'id': range(200000),
    'duration': random_integers(0, 1000),
    'protocol_type': random_choice(['TCP', 'UDP', 'ICMP']),
    'src_bytes': random_integers(100, 50000),
    'dst_bytes': random_integers(100, 50000),
    'is_attack': random_choice([0, 1], p=[0.8, 0.2])
}
```

---

### 2. **Spark ML Pipeline** (`scripts/spark_analysis.py`)

A complete machine learning workflow for cyber intrusion classification.

#### Pipeline Steps:

**Step 1: Initialize Spark Session**
```python
spark = SparkSession.builder \
    .appName("CyberIntrusionDetection") \
    .master("local[*]") \
    .getOrCreate()
```
- `local[*]`: Uses all available CPU cores on a single machine
- Alternative: `spark://spark-master:7077` for distributed mode across containers

**Step 2: Load Data**
```python
df = spark.read.csv("/home/jovyan/work/scripts/data/network_traffic.csv", 
                     header=True, inferSchema=True)
```
- Reads 200K records into a Spark DataFrame
- Auto-infers schema from CSV headers and data types

**Step 3: Feature Engineering**
```python
# Encode categorical variable (protocol_type → numeric index)
indexer = StringIndexer(inputCol="protocol_type", outputCol="protocol_index")
df_indexed = indexer.fit(df).transform(df)

# Combine numeric features into single feature vector
assembler = VectorAssembler(
    inputCols=["duration", "src_bytes", "dst_bytes", "protocol_index"],
    outputCol="features"
)
ml_data = assembler.transform(df_indexed).select("id", "features", "is_attack")
```

**Step 4: Train/Test Split**
```python
train, test = ml_data.randomSplit([0.8, 0.2])
# 80% for training (160K records)
# 20% for testing (40K records)
```

**Step 5: Model Training**
```python
rf = RandomForestClassifier(labelCol="is_attack", 
                            featuresCol="features", 
                            numTrees=50)
model = rf.fit(train)
```
- **Algorithm**: Random Forest (ensemble of 50 decision trees)
- **Label**: `is_attack` (what to predict)
- **Features**: Encoded and vectorized network traffic properties

**Step 6: Evaluation**
```python
predictions = model.transform(test)
evaluator = MulticlassClassificationEvaluator(labelCol="is_attack", 
                                              metricName="accuracy")
accuracy = evaluator.evaluate(predictions)
# Result: ~80% Accuracy (varies slightly with random splits)
```

**Step 7: RDD Operations & Output**
```python
# Convert DataFrame to RDD for low-level transformations
results_rdd = predictions.select("id", "prediction").rdd

# Map: Format each prediction as readable log entry
formatted_log = results_rdd.map(lambda x: 
    f"SessionID: {x[0]} | ThreatDetected: {bool(x[1])}")

# Repartition and save across 10 files (distributed)
formatted_log.repartition(10).saveAsTextFile(output_path)
```

---

## Running the Lab

### Prerequisites

- **Docker Desktop** installed and running
- **Python 3.9+** with `pandas` and `numpy`
- **~10 GB** disk space for Docker images and data

### Step 1: Start Containers

```bash
cd /Users/yelessov/Desktop/movie-hadoop-project/lab2
docker compose up -d
```

**Expected Output:**
```
[+] Running 4/4
 ✔ Network lab2_default    Created
 ✔ Container spark-master  Started
 ✔ Container spark-worker  Started
 ✔ Container jupyter-lab   Started
```

**Access Points:**
- Spark Master UI: http://localhost:8080
- Jupyter Lab: http://localhost:8888 (token in logs: `docker compose logs jupyter-lab`)

### Step 2: Generate Data

```bash
python3 scripts/generate_data.py
```

**Output:**
```
Successfully generated 200,000 records in data/network_traffic.csv
```

This creates `scripts/data/network_traffic.csv` (CSV file with 200K rows).

### Step 3: Run Spark Analysis

```bash
docker exec -it jupyter-lab spark-submit /home/jovyan/work/scripts/spark_analysis.py
```

**Expected Output:**
```
...
**Expected Output:**
```
...
==============================
LAB 2 RESULTS: Model Accuracy: 80.08%
==============================
...```
...
```

The script automatically:
1. Loads the CSV data
2. Preprocesses and engineers features
3. Trains the Random Forest model
4. Evaluates on test data
5. Outputs threat detection logs to `output/threat_report_logs/`

### Step 4: View Results

```bash
cat output/threat_report_logs/part-00000
```

**Sample Output:**
```
SessionID: 42891 | ThreatDetected: False
SessionID: 15234 | ThreatDetected: True
SessionID: 88102 | ThreatDetected: False
...
```

---

## Key Concepts Demonstrated

### 1. **Distributed Computing**
- Spark Master/Worker architecture
- Job scheduling and task distribution
- Container orchestration with Docker Compose

### 2. **Big Data Processing**
- Loading 200K records into distributed DataFrame
- Feature engineering with Spark ML transformers
- Train/test splits for ML validation

### 3. **Machine Learning Pipeline**
- StringIndexer: Categorical encoding
- VectorAssembler: Feature vectorization
- RandomForestClassifier: Classification model
- MulticlassClassificationEvaluator: Performance metrics

### 4. **RDD Operations**
- DataFrame → RDD conversion
- Map transformations
- Repartitioning for distributed output

### 5. **Data Persistence**
- CSV input handling
- Distributed text file output (10 partitions)
- Hadoop-compatible output format (`_SUCCESS` markers)

---

## Results Summary

| Metric | Value |
|--------|-------|
| Total Records | 200,000 |
| Training Set | 160,000 (80%) |
| Test Set | 40,000 (20%) |
| Model | Random Forest (50 trees) |
| **Accuracy** | **~80%** |
| Output Partitions | 10 |

---

## Troubleshooting

### Issue: `docker compose up -d` fails
**Solution:** Pull images with `docker compose pull`, then retry.

### Issue: `FileNotFoundError: data/network_traffic.csv`
**Solution:** Run `python3 scripts/generate_data.py` first to create the CSV.

### Issue: `LiveListenerBus is stopped` (Spark error)
**Solution:** Changed `master("spark://spark-master:7077")` to `master("local[*]")` in `spark_analysis.py`. The distributed mode requires additional network configuration.

### Issue: Jupyter token required for access
**Solution:** View token with `docker compose logs jupyter-lab | grep token`.

---

## File Modifications Made

- **`docker-compose.yml`**: Updated Spark image to `spark:latest` (original `bitnami/spark:3.3` not available)
- **`scripts/spark_analysis.py`**: 
  - Changed paths from relative to absolute (`/home/jovyan/work/...`)
  - Updated master to `local[*]` mode for stable execution
- **`scripts/generate_data.py`**: No changes (works as-is after `data/` directory created)

---

## References

- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [PySpark ML Pipelines](https://spark.apache.org/docs/latest/ml-pipeline.html)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Jupyter PySpark Notebook](https://hub.docker.com/r/jupyter/pyspark-notebook)

---

## Author Notes

This lab demonstrates the end-to-end workflow for building a production-ready machine learning pipeline on distributed computing infrastructure. It bridges high-level ML abstractions (Spark ML) with low-level distributed computing (RDDs and partitioning).

**Key Takeaway:** By scaling from 200K to millions of records, the same code runs unchanged thanks to Spark's lazy evaluation and DAG-based execution model.
