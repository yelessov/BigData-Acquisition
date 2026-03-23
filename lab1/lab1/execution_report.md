# Lab 1 Execution Report: Hadoop MapReduce Movie Analytics

**Execution Date:** 2026-03-23  
**Execution Mode:** Hadoop Pseudo-Distributed (Docker Compose)  
**Application:** Dataset Join & Average Calculation (MapReduce Streaming)  

## 📥 INPUTS

### 1. Infrastructure
* **Docker Containers:**
  * `namenode` (Hadoop 3.2.1) - Ports: 9870 (Web UI), 8020 (HDFS)
  * `datanode` (Hadoop 3.2.1) - Port: 9864
  * `resourcemanager` (YARN) - Port: 8088
* **Hadoop Version:** 3.2.1 (bde2020 image)
* **Dependencies:** Python 3.5 (Manually provisioned via Debian Stretch archives)
* **OS:** Linux (Container host)

### 2. Dataset
* **Files:** `movies.csv` (496kB) and `ratings.csv` (2.49MB)
* **Source Dataset:** MovieLens (Small)
* **Local Source Location:** `lab1/` directory
* **HDFS Location:** `/input/`
* **Data Structure:** * `movies.csv`: `movieId,title,genres`
  * `ratings.csv`: `userId,movieId,rating,timestamp`

### 3. Application Code
* **Framework:** Hadoop Streaming
* **Scripts:**
  * `join_mapper.py` (Tags `movies.csv` records as `A_movie` and `ratings.csv` records as `B_rating`)
  * `join_reducer.py` (Calculates the mathematical average of ratings grouped by `movieId`)
* **Orchestration:** `run.sh` (Bash script for data ingestion and job execution)
* **Language:** Python 3

### 4. Job Configuration
* **Goal:** Perform a Reduce-Side Join to calculate the average user rating for every movie.
* **Input:** `hdfs://namenode:8020/input/*`
* **Output:** `hdfs://namenode:8020/output`
* **Streaming Tool:** `/opt/hadoop-3.2.1/share/hadoop/tools/lib/hadoop-streaming-3.2.1.jar`

---

## ⚙️ EXECUTION FLOW

**Phase 1: Environment Provisioning & Data Ingestion**
1. Booted cluster via `docker-compose up -d`.
2. Paused for 45 seconds to allow DataNode registration.
3. Cleaned previous HDFS directories (`hdfs dfs -rm -r -f /input /output`).
4. Copied local files and Python scripts to the `namenode` container via `docker cp`.
5. Ingested datasets into HDFS via `hdfs dfs -put`.

**Phase 2: Job Execution (MapReduce Join)**
```text
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

Processed output is successfully stored in the HDFS /output directory and can be viewed via docker exec namenode hdfs dfs -cat /output/part-00000.

🔍 KEY OBSERVATIONS & REASONING
1. Infrastructure Networking

Issue: The initial cluster boot resulted in 0 datanode(s) running, preventing file uploads to HDFS.

Reasoning & Fix: The bde2020 DataNode container requires explicit routing to the NameNode. We updated docker-compose.yml to inject the CORE_CONF_fs_defaultFS=hdfs://namenode:8020 environment variable, immediately restoring cluster health.

2. Container Dependency Limits

Issue: The MapReduce job crashed with Cannot run program "python3".

Reasoning & Fix: The Docker images do not include Python by default, and the underlying Debian "Stretch" OS had archived its package repositories. We bypassed this by rewriting /etc/apt/sources.list to point to http://archive.debian.org/debian, disabling validity checks, and manually running apt-get install -y python3 as root inside the running NameNode.

3. Code Compatibility

Issue: Syntax errors in the mapper and reducer.

Reasoning & Fix: The legacy container environment installed Python 3.5. F-strings (f"{var}") were introduced in Python 3.6. We refactored the Python scripts to use "{}\t{}".format() to ensure successful execution within the Hadoop Streaming tasks.

🚀 CONCLUSION
Lab 1 was successfully completed. The pseudo-distributed Hadoop environment was stabilized by resolving internal Docker networking and dependency constraints. The Python-based MapReduce scripts accurately joined two distinct CSV files and calculated the expected aggregations, resulting in a fully automated, verifiable Big Data pipeline.
