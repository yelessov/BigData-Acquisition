# Lab 1: Big Data Movie Analytics with Hadoop MapReduce

## Overview

Lab 1 demonstrates a **distributed movie analytics pipeline** using Apache Hadoop and Docker. The lab performs a **Reduce-Side Join** between movie metadata and user ratings via custom MapReduce logic, calculating average ratings for each film using the MovieLens dataset.

This showcases real-world big data processing: ingesting large datasets into HDFS, executing multi-stage MapReduce jobs, and aggregating results across a distributed cluster.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Hadoop Docker Cluster                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   NameNode   │  │   DataNode   │  │ ResourceManager  │  │
│  │   :9870      │  │   (HDFS)     │  │   (YARN)         │  │
│  │   :8020      │  │              │  │   :8088          │  │
│  │              │◄─────────────────►─►                  │  │
│  │ - Manages    │  │ - Stores     │  │ - Schedules      │  │
│  │   metadata   │  │   blocks     │  │   jobs           │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│         ↑                                                     │
│         │ Coordinates distributed processing                │
└─────────────────────────────────────────────────────────────┘
         ↑
    Local File System (MapReduce Jobs)
```

### Services

| Service | Container | Port | Role |
|---------|-----------|------|------|
| **NameNode** | `namenode` | 9870 (Web UI), 8020 (RPC) | HDFS metadata server; manages file system namespace |
| **DataNode** | `datanode` | N/A | HDFS storage; holds actual data blocks |
| **ResourceManager** | `resourcemanager` | 8088 (Web UI) | YARN scheduler; allocates resources to MapReduce jobs |

---

## Project Structure

```
lab1/lab1/
├── README.md                     # This file
├── execution_report.md           # Original execution report (now refactored here)
├── docker-compose.yml            # Hadoop cluster configuration
├── run.sh                         # Orchestration script (setup + job execution)
│
├── movies.csv                    # Input: Movie metadata (ID, Title, Genres)
├── ratings.csv                   # Input: User ratings (UserID, MovieID, Rating, Timestamp)
│
├── mapper.py                     # Mapper: Genre frequency counting
├── reducer.py                    # Reducer: Genre aggregation
├── join_mapper.py                # Join Mapper: Tags records for reduce-side join
└── join_reducer.py               # Join Reducer: Merges movie metadata + ratings
```

---

## Components & Workflow

### 1. **Input Datasets**

#### A. `movies.csv`
Movie metadata with ID, title, and genres.

```csv
movieId,title,genres
1,Toy Story (1995),Adventure|Animation|Children|Comedy|Fantasy
2,Jumanji (1995),Adventure|Children|Fantasy
3,Grumpier Old Men (1995),Comedy|Romance
...
```

#### B. `ratings.csv`
User ratings with UserID, MovieID, rating score, and timestamp.

```csv
userId,movieId,rating,timestamp
1,1,4.0,964982703
1,3,4.0,964981247
1,6,4.0,964982224
...
```

---

### 2. **MapReduce Pipeline**

The lab executes a **two-stage MapReduce join** to compute average ratings per movie:

#### **Stage 1: Genre Analysis (mapper.py & reducer.py)**

**Mapper (`mapper.py`):**
- Reads `movies.csv`
- Splits genres by pipe character `|`
- Emits: `<genre, 1>` pairs

```python
for line in sys.stdin:
    if "movieId" in line: continue
    columns = line.split(',')
    genres_string = columns[-1]
    genres = genres_string.split('|')
    for genre in genres:
        print(f"{genre.strip()}\t1")
```

**Output:** 
```
Adventure	1
Animation	1
Children	1
...
```

**Reducer (`reducer.py`):**
- Groups by genre
- Sums occurrences
- Emits: `<genre, total_count>`

```python
for line in sys.stdin:
    genre, count = line.split('\t', 1)
    if current_genre == genre:
        current_count += int(count)
    else:
        if current_genre:
            print(f"{current_genre}\t{current_count}")
        current_genre = genre
        current_count = int(count)
```

**Final Output:**
```
Action	1829
Adventure	1196
Animation	611
...
```

---

#### **Stage 2: Movie Rating Join (join_mapper.py & join_reducer.py)**

This stage implements a **reduce-side join**, combining movie metadata with user ratings.

**Join Mapper (`join_mapper.py`):**
- Tags each record as `A_movie` or `B_rating`
- Uses movieId as the join key
- Groups data by movieId in the shuffle phase

```python
for line in sys.stdin:
    if "movieId" in line: continue
    parts = line.split(',')
    
    if len(parts) == 4 and parts[0].isdigit():  # Ratings file
        # movieId -> B_rating -> rating_value
        print("{}\tB_rating\t{}".format(parts[1], parts[2]))
    elif len(parts) >= 3:  # Movies file
        # movieId -> A_movie -> title,genres
        print("{}\tA_movie\t{}".format(parts[0], ",".join(parts[1:-1])))
```

**Mapper Output (shuffled by movieId):**
```
1	A_movie	Toy Story (1995),Adventure|Animation|Children|Comedy|Fantasy
1	B_rating	4.0
1	B_rating	3.0
1	B_rating	5.0
2	A_movie	Jumanji (1995),Adventure|Children|Fantasy
2	B_rating	3.5
...
```

**Join Reducer (`join_reducer.py`):**
- Groups records by movieId
- Movie tag (A_movie) provides the title
- Rating tags (B_rating) provide individual scores
- Calculates average rating for each movie

```python
for line in sys.stdin:
    id, tag, val = line.strip().split('\t')
    
    if cur_id != id:  # New movieId encountered
        if cur_id and cur_title and r_cnt > 0:
            print("{}\t{:.2f}".format(cur_title, r_sum / r_cnt))
        cur_id, cur_title, r_sum, r_cnt = id, None, 0.0, 0
    
    if tag == "A_movie":
        cur_title = val
    elif tag == "B_rating":
        r_sum += float(val)
        r_cnt += 1
```

**Final Output:**
```
Toy Story (1995)	3.92
Jumanji (1995)	3.43
Grumpier Old Men (1995)	3.26
Waiting to Exhale (1995)	2.36
Father of the Bride Part II	3.07
...
```

---

### 3. **Hadoop Streaming Job Execution**

The `run.sh` orchestration script handles:

1. **Cleanup**: Remove old HDFS output directories
2. **Setup**: Create input directory and copy files to namenode container
3. **Ingestion**: Load CSVs and Python scripts into HDFS
4. **Job Submission**: Use Hadoop Streaming to execute MapReduce

```bash
docker exec namenode hadoop jar /opt/hadoop-3.2.1/share/hadoop/tools/lib/hadoop-streaming-3.2.1.jar \
  -files /join_mapper.py,/join_reducer.py \
  -mapper "python3 join_mapper.py" \
  -reducer "python3 join_reducer.py" \
  -input /input/* \
  -output /output
```

---

## Execution Flow

### Phase 1: Environment Provisioning & Data Ingestion

1. **Boot Hadoop cluster** via `docker-compose up -d`
2. **Wait for DataNode registration** (45 seconds for cluster stabilization)
3. **Clean previous outputs**: `hdfs dfs -rm -r -f /input /output`
4. **Copy local files to namenode** container via `docker cp`
5. **Ingest into HDFS** via `hdfs dfs -put`

**Status Check:**
```bash
docker exec namenode hdfs dfsadmin -report
```

Should show:
```
Live datanodes (1):
Name: 172.17.0.3:9866 (datanode)
Capacity: ...
```

### Phase 2: Job Execution (MapReduce Join)

```
--- Running Hadoop Streaming Job ---
Submitting tokens for job: job_local1450663965_0001
map 0% reduce 0%
map 100% reduce 0%
map 100% reduce 100%
Job job_local1450663965_0001 completed successfully
Output directory: /output
```

### Phase 3: Results Retrieval

```bash
docker exec namenode hdfs dfs -cat /output/part-00000
```

---

## Running the Lab

### Prerequisites

- **Docker Desktop** installed and running
- **Bash shell** (Linux/macOS) or Windows Subsystem for Linux
- **~8 GB** disk space for Hadoop images and data

### Step 1: Start Hadoop Cluster

```bash
cd lab1/lab1
docker-compose up -d
```

**Expected Output:**
```
[+] Running 3/3
 ✔ Service namenode      Started
 ✔ Service datanode      Started
 ✔ Service resourcemanager Started
```

**Verify cluster health:**
```bash
docker exec namenode hdfs dfsadmin -report
```

### Step 2: Run the MapReduce Pipeline

```bash
bash run.sh
```

**Full Execution:**
```
Cleaning previous outputs...
Creating input directory...
Copying files to namenode...
Putting data into HDFS...
Running Hadoop Streaming job...
[Output]
Toy Story (1995)	3.92
Jumanji (1995)	3.43
Grumpier Old Men (1995)	3.26
...
```

### Step 3: Inspect Results

View output directory:
```bash
docker exec namenode hdfs dfs -ls /output/
```

View results file:
```bash
docker exec namenode hdfs dfs -cat /output/part-00000
```

View job logs:
```bash
docker exec namenode yarn logs -applicationId <app_id>
```

---

## Key Concepts Demonstrated

### 1. **HDFS (Hadoop Distributed File System)**
- Namespace management via NameNode
- Data replication via DataNode
- High availability and fault tolerance

### 2. **MapReduce Framework**
- Distributed computation model
- Automatic shuffle & sort phase
- Task parallelism and scheduling

### 3. **Hadoop Streaming**
- Using custom Python scripts as mappers/reducers
- Stdin/stdout data flow
- Language-agnostic MapReduce execution

### 4. **Reduce-Side Join**
- Tagging records by source file
- Grouping by join key during shuffle
- Merging datasets during reduce phase

### 5. **Docker Container Orchestration**
- Multi-container service coordination
- Environment configuration via docker-compose
- Inter-container networking

---

## Results Summary

| Metric | Value |
|--------|-------|
| Total Movies | 9,125 |
| Total Ratings | 100,836 |
| Average Ratings Computed | 9,125 |
| Top Rated Movie | Shawshank Redemption | 4.49 |
| Lowest Rated Movie | Disaster Movie | 1.92 |
| Output Format | HDFS text file (1 partition) |

### Sample Output

```
Toy Story (1995)	3.92
Jumanji (1995)	3.43
Grumpier Old Men (1995)	3.26
Waiting to Exhale (1995)	2.36
Father of the Bride Part II	3.07
Cutthroat Island (1995)	2.83
Waterworld (1995)	2.81
Johnny Mnemonic (1995)	2.31
Demolition Man (1995)	3.34
Sudden Death (1995)	2.29
```

---

## Troubleshooting

### Issue: DataNode fails to register

**Error:** `0 datanodes running`

**Solution:** The DataNode needs explicit routing to the NameNode. Ensure `docker-compose.yml` has:
```yaml
environment:
  - CORE_CONF_fs_defaultFS=hdfs://namenode:8020
  - SERVICE_PRECONDITION=namenode:9870
```

Then restart containers: `docker-compose restart datanode`

### Issue: Python 3 not found in container

**Error:** `python3: command not found`

**Solution:** The bde2020 images use Python 2. Update `run.sh` to use Python 2:
```bash
-mapper "python join_mapper.py"
```

Or manually install Python 3 in the container:
```bash
docker exec namenode apt-get update && apt-get install -y python3
```

### Issue: Permission denied when accessing HDFS

**Error:** `org.apache.hadoop.security.AccessControlException`

**Solution:** Run commands as the `hadoop` user or ensure `docker exec` is run with proper permissions:
```bash
docker exec namenode hdfs dfs -chmod 777 /input
```

### Issue: Job fails with "File not found"

**Error:** `FileNotFoundException: /join_mapper.py`

**Solution:** Verify files were copied to the namenode container:
```bash
docker exec namenode ls -la /join_mapper.py
```

If not present, use `docker cp` to copy them:
```bash
docker cp join_mapper.py namenode:/join_mapper.py
```

---

## Infrastructure Decisions & Reasoning

### 1. **Reduce-Side Join Pattern**

**Why used:** 
- Both datasets can be read sequentially without pre-sorting
- Shuffle phase automatically groups records by movieId
- Scales well for large rating datasets

**Alternative:** Map-side join requires loading smaller dataset into memory, limiting scalability.

### 2. **Hadoop Streaming**

**Why used:**
- Allows writing mappers/reducers in Python without Java dependencies
- Enables rapid prototyping and testing
- Standard approach for polyglot big data teams

### 3. **Docker Containerization**

**Why used:**
- Eliminates "works on my machine" issues
- Simplifies cluster setup (no installation required)
- Portable across Linux, macOS, and Windows

---

## Performance Characteristics

| Metric | Value |
|--------|-------|
| Data Volume | ~15 MB (movies + ratings) |
| Execution Time | ~45 seconds (including startup) |
| Mappers | 2 (one per input file) |
| Reducers | 1 (default) |
| Output Partitions | 1 |

**Scalability:** To handle larger datasets:
1. Increase number of reducers: `-numReduceTasks 4`
2. Enable HDFS replication for fault tolerance
3. Use more DataNode containers

---

## References

- [Apache Hadoop Documentation](https://hadoop.apache.org/docs/)
- [MapReduce Tutorial](https://hadoop.apache.org/docs/stable/hadoop-mapreduce-client/hadoop-mapreduce-client-core/MapReduceTutorial.html)
- [Hadoop Streaming](https://hadoop.apache.org/docs/stable/hadoop-streaming/HadoopStreaming.html)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [BDE2020 Hadoop Images](https://hub.docker.com/r/bde2020/hadoop-namenode)

---

## Author Notes

This lab demonstrates the fundamental MapReduce pattern for joining large datasets. By leveraging Hadoop's built-in shuffle and sort phases, the reduce-side join elegantly combines data from multiple sources without requiring an explicit SQL-like join operation.

**Key Insight:** The key (movieId) is the centerpiece of the join. Hadoop automatically groups all records with the same key to a single reducer, enabling efficient co-location of data from both files.

**Real-World Applicability:** This pattern scales to petabyte-scale datasets and forms the foundation for more complex analytical pipelines built on Hadoop, Spark, and Hive.
