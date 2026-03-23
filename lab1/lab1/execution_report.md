# Lab 1 Execution Report: Distributed Movie Analytics

## 1. Objective
To deploy a local Hadoop cluster using Docker and execute a MapReduce job to join two datasets (`movies.csv` and `ratings.csv`) and calculate average movie ratings.

## 2. Architecture & Tools
* **Environment:** Docker, Docker Compose
* **Cluster Nodes:** 1 NameNode, 1 DataNode, 1 ResourceManager
* **Processing Framework:** Hadoop Streaming with Python 3

## 3. Execution Steps
1. Initialized the multi-node Hadoop cluster using `docker-compose.yml`.
2. Configured internal networking variables to ensure the DataNode could communicate with the NameNode.
3. Accessed the NameNode container as root to update Debian archives and install Python 3.
4. Uploaded datasets and Python scripts to the container, then moved datasets into HDFS.
5. Executed the MapReduce Hadoop Streaming job via an automated `run.sh` bash script.

## 4. Challenges & Troubleshooting
* **Issue 1: "0 datanode(s) running"** * *Diagnosis:* The DataNode container was running, but it wasn't registering with the NameNode.
  * *Fix:* Added `CORE_CONF_fs_defaultFS=hdfs://namenode:8020` to the Docker Compose file so the worker could locate the manager.
* **Issue 2: "JAR does not exist"**
  * *Diagnosis:* The Hadoop Streaming tool was in a different directory than expected.
  * *Fix:* Used the Linux `find` command inside the container to locate the correct path (`/opt/hadoop-3.2.1/share/hadoop/tools/lib/hadoop-streaming-3.2.1.jar`).
* **Issue 3: "Cannot run program 'python3'"**
  * *Diagnosis:* The lightweight Docker image lacked a Python interpreter.
  * *Fix:* Updated the Debian archive repository links and ran `apt-get install python3` directly inside the running container.

## 5. Results & Conclusion
The MapReduce job successfully mapped the datasets by `movieId`, reduced them by calculating the mathematical average of the ratings, and outputted the final processed list. The underlying Docker infrastructure is now stable and fully operational.