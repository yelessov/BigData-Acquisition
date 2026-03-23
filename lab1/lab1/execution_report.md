# Lab 1: Big Data Movie Analytics with Hadoop MapReduce

## 📖 1. Project Overview
This project demonstrates a distributed Big Data pipeline built using **Apache Hadoop** and **Docker**. The primary objective was to calculate average user ratings from the MovieLens dataset by performing a **Reduce-Side Join** between movie metadata and user ratings via custom MapReduce logic.

---

## 🛠️ 2. Infrastructure & Source Code

### A. Mapper Logic (`join_mapper.py`)
This script tags records as `A_movie` or `B_rating` to facilitate the distributed join.

```python
#!/usr/bin/env python3
import sys

for line in sys.stdin:
    line = line.strip()
    if not line or "movieId" in line: continue
    parts = line.split(',')
    
    if len(parts) == 4 and parts[0].isdigit(): # Ratings
        print("{}\tB_rating\t{}".format(parts[1], parts[2]))
    elif len(parts) >= 3: # Movies
        print("{}\tA_movie\t{}".format(parts[0], ",".join(parts[1:-1])))

B. Reducer Logic (join_reducer.py)

This script aggregates ratings and calculates the average for each title.

Python
#!/usr/bin/env python3
import sys

cur_id, cur_title, r_sum, r_cnt = None, None, 0.0, 0

for line in sys.stdin:
    id, tag, val = line.strip().split('\t')
    if cur_id != id:
        if cur_id and cur_title and r_cnt > 0:
            print("{}\t{:.2f}".format(cur_title, r_sum / r_cnt))
        cur_id, cur_title, r_sum, r_cnt = id, None, 0.0, 0
    
    if tag == "A_movie": cur_title = val
    elif tag == "B_rating":
        r_sum += float(val)
        r_cnt += 1

if cur_id and cur_title and r_cnt > 0:
    print("{}\t{:.2f}".format(cur_title, r_sum / r_cnt))
⚙️ 3. Execution Flow
Phase 1: Environment Provisioning & Data Ingestion

Booted cluster via docker-compose up -d.

Paused for 45 seconds to allow DataNode registration.

Cleaned previous HDFS directories (hdfs dfs -rm -r -f /input /output).

Copied local files and Python scripts to the namenode container via docker cp.

Ingested datasets into HDFS via hdfs dfs -put.

Phase 2: Job Execution (MapReduce Join)

Plaintext
--- Running Hadoop Streaming Job ---
Submitting tokens for job: job_local1450663965_0001
map 0% reduce 0%
map 100% reduce 0%
map 100% reduce 100%
Job job_local1450663965_0001 completed successfully
Output directory: /output
📊 4. Outputs & Metrics
1. Sample Results (/output/part-00000)

Movie Title	Average Rating
Toy Story (1995)	3.92
Jumanji (1995)	3.43
Grumpier Old Men (1995)	3.26
Waiting to Exhale (1995)	2.36
Father of the Bride Part II	3.07
2. Artifacts

Processed output is successfully stored in the HDFS /output directory and can be viewed via:
docker exec namenode hdfs dfs -cat /output/part-00000

🔍 5. Key Observations & Reasoning
Infrastructure Networking

Issue: The initial cluster boot resulted in 0 datanode(s) running, preventing file uploads to HDFS.

Reasoning & Fix: The bde2020 DataNode container requires explicit routing to the NameNode. We updated docker-compose.yml to inject the CORE_CONF_fs_defaultFS=hdfs://namenode:8020 environment variable, immediately restoring cluster health.

Container Dependency & Syntax

Issue: Lightweight Docker images lack Python 3 by default.

Reasoning & Fix: We manually updated the container's Debian archives to install python3. Additionally, we refactored code to use .format() strings to maintain compatibility with the container's Python 3.5 interpreter.

🚀 Conclusion
Lab 1 successfully demonstrated an automated, distributed data join using Hadoop. By resolving networking and dependency gaps, we created a stable pipeline capable of handling large-scale movie analytics.
