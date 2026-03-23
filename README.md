# Big Data Lab 1: Movie Analytics with Hadoop MapReduce

## Description
This project demonstrates a distributed Big Data pipeline using Apache Hadoop and Docker. It processes the MovieLens dataset to calculate the average rating for each movie by joining two separate datasets (`movies.csv` and `ratings.csv`) using the MapReduce paradigm.

## Technologies Used
* **Infrastructure:** Docker, Docker Compose
* **Big Data Framework:** Apache Hadoop (HDFS, YARN, MapReduce)
* **Programming Language:** Python 3 (via Hadoop Streaming)
* **Dataset:** MovieLens (Small)

## How I Made It
1. **Cluster Setup:** Configured a multi-node Hadoop cluster (NameNode, DataNode, ResourceManager) using `docker-compose.yml`. Fixed internal networking so nodes could communicate successfully.
2. **MapReduce Logic:** Wrote `join_mapper.py` and `join_reducer.py`. The mapper tags records as movies or ratings, and the reducer groups them by `movieId` to calculate the mathematical average.
3. **Environment Configuration:** Handled missing dependencies by accessing the Docker container as the root user, updating Debian archive repositories, and installing Python 3 directly onto the NameNode.
4. **Automation:** Created a `run.sh` bash script to automatically clear old directories, load local CSV files into HDFS, execute the Hadoop Streaming job, and output the final results.

## How to Run
1. Start the cluster: `docker-compose up -d`
2. Wait 45 seconds for DataNodes to register.
3. Make the script executable: `chmod +x run.sh mapper.py reducer.py`
4. Run the pipeline: `./run.sh`