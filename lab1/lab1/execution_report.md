Lab 1 Execution Report: Hadoop MapReduce Movie Analytics
Execution Date: 2026-03-23
Execution Mode: Hadoop Pseudo-Distributed (Docker Compose)
Application: Dataset Join & Average Calculation (MapReduce Streaming)

📥 INPUTS

1. Infrastructure

Docker Containers:

namenode (Hadoop 3.2.1) - Port 9870 (Web UI), 8020 (HDFS)

datanode (Hadoop 3.2.1) - Port 9864

resourcemanager (YARN) - Port 8088

Hadoop Version: 3.2.1 (bde2020 image)

Dependencies: Python 3.5 (Manually provisioned via Debian Stretch archives)

OS: Linux (Container host)

2. Dataset

Files: movies.csv and ratings.csv (MovieLens Small Dataset)

Source Location: Local project directory (lab1/)

HDFS Location: /input/

Data Structure: movies.csv contains ID and Title; ratings.csv contains ID and User Ratings.

3. Application Code

Framework: Hadoop Streaming

Scripts:

Mapper: join_mapper.py (Tags and emits data)

Reducer: join_reducer.py (Aggregates and calculates averages)

Orchestration: run.sh (Automates cleanup, ingestion, and job execution)

Language: Python 3

4. Job Configuration

Goal: Perform a Reduce-Side Join on movieId to calculate the mathematical average rating for every movie in the dataset.

Input: hdfs://namenode:8020/input/*

Output: hdfs://namenode:8020/output

⚙️ EXECUTION FLOW

Phase 1: Environment Provisioning & Data Ingestion

Booted cluster via docker-compose up -d.

Paused for 45 seconds to allow DataNode registration.

Cleaned previous HDFS directories (hdfs dfs -rm -r -f /input /output).

Copied local files to the namenode container (docker cp).

Ingested datasets into HDFS (hdfs dfs -put).

Verified: Successfully copied to namenode:/movies.csv

Phase 2: Job Execution (MapReduce Join)

Plaintext
--- Running Hadoop Streaming Job ---
Submitting tokens for job: job_local1450663965_0001
map 0% reduce 0%
map 100% reduce 0%
map 100% reduce 100%
Job job_local1450663965_0001 completed successfully
Output directory: /output
📤 OUTPUTS

1. Sample Results (/output/part-00000)

Plaintext
Toy Story (1995)            3.92
Jumanji (1995)              3.43
Grumpier Old Men (1995)     3.26
Waiting to Exhale (1995)    2.36
Father of the Bride Part II 3.07
2. Artifacts

Processed output is successfully stored in the HDFS /output directory and can be viewed via hdfs dfs -cat /output/part-00000.

🔍 KEY OBSERVATIONS & REASONING

1. Infrastructure Networking

Result: The initial cluster boot resulted in 0 datanode(s) running, causing the pipeline to fail because HDFS had zero capacity.

Reasoning: The bde2020 DataNode container requires explicit instructions on where to find the NameNode. We updated docker-compose.yml to inject the CORE_CONF_fs_defaultFS=hdfs://namenode:8020 environment variable, immediately restoring cluster health.

2. Container Dependency Limits

Result: The MapReduce job initially crashed with a Cannot run program "python3" error.

Reasoning: Lightweight Docker images do not include Python by default. Furthermore, the underlying Debian "Stretch" OS had archived its package repositories. We successfully bypassed this by running apt-get -o Acquire::Check-Valid-Until=false update against the archive servers and manually installing Python 3 inside the running NameNode.

3. Code Compatibility

Result: Python scripts were refactored to use "{}\t{}".format() instead of modern f-strings (f"{var}").

Reasoning: The legacy container environment installed Python 3.5. F-strings were introduced in Python 3.6, necessitating a syntax downgrade to ensure successful execution within the MapReduce streaming tasks.

🚀 CONCLUSION

Lab 1 was successfully executed. The pseudo-distributed Hadoop environment was stabilized by resolving internal Docker networking and dependency constraints. The Python-based MapReduce scripts accurately joined two distinct CSV files and calculated the expected aggregations, resulting in a fully automated, verifiable Big Data pipeline.
