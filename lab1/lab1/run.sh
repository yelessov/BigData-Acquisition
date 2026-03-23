#!/bin/bash

# 1. Clean up any old output from previous failed runs just in case
docker exec namenode hdfs dfs -rm -r -f /input /output

# 2. Create a fresh input folder inside HDFS
docker exec namenode hdfs dfs -mkdir -p /input

# 3. Copy BOTH CSV files AND the Python scripts into the container
docker cp movies.csv namenode:/movies.csv
docker cp ratings.csv namenode:/ratings.csv
docker cp join_mapper.py namenode:/join_mapper.py
docker cp join_reducer.py namenode:/join_reducer.py

docker exec namenode hdfs dfs -put /movies.csv /input/
docker exec namenode hdfs dfs -put /ratings.csv /input/

# 4. Run the Hadoop Streaming job (notice the added '/' in the -files line)
docker exec namenode hadoop jar /opt/hadoop-3.2.1/share/hadoop/tools/lib/hadoop-streaming-3.2.1.jar \
  -files /join_mapper.py,/join_reducer.py \
  -mapper "python3 join_mapper.py" \
  -reducer "python3 join_reducer.py" \
  -input /input/* \
  -output /output
  
# 5. View the final results
echo "Job complete! Here are your movie ratings:"
docker exec namenode hdfs dfs -cat /output/part-00000