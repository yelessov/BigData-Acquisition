# Lab 3: Real-Time Traffic Monitoring with Kafka & Spark Streaming

## Overview

Lab 3 demonstrates a **real-time data streaming pipeline** using Apache Kafka and Spark Structured Streaming. The lab simulates smart city traffic sensors that continuously stream vehicle speed data, which is then aggregated and analyzed in real-time to monitor average speeds across different highways. This showcases the fundamentals of modern data streaming architectures for IoT applications.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    Docker Compose Stack                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────┐         ┌────────────────────────┐            │
│  │  Zookeeper   │         │   Apache Kafka         │            │
│  │   :2181      │◄────────┤   Broker :9092         │            │
│  │              │         │                        │            │
│  │ - Manages    │         │ - Message Queue        │            │
│  │   Kafka      │         │ - Topic: highway-      │            │
│  │   cluster    │         │   telemetry            │            │
│  └──────────────┘         └────────────────────────┘            │
│                                    ▲                              │
│         ┌──────────────────────────┼──────────────────────────┐  │
│         │                          │                          │  │
│    ┌─────────────┐        ┌──────────────┐       ┌──────────────┐
│    │  Producer   │        │  Consumer    │       │Spark Streaming│
│    │             │        │              │       │(Optional)    │
│    │ - Reads     │        │ - Reads from │       │              │
│    │   traffic   │        │   Kafka topic│       │ - Aggregates │
│    │   sensors   │        │ - Calculates │       │   by window  │
│    │   CSV       │        │   moving avg │       │ - Displays   │
│    │ - Publishes │        │ - Displays   │       │   stats      │
│    │   to Kafka  │        │   stats      │       │              │
│    └─────────────┘        └──────────────┘       └──────────────┘
│         │                          ▲                     ▲         │
│         └──────────────────────────┼─────────────────────┘         │
│              highway-telemetry     │                              │
│              (Kafka Topic)         │ Messages streamed            │
│                                    │ in real-time                │
└──────────────────────────────────────────────────────────────────┘
```

### Services

| Service | Container | Port | Role |
|---------|-----------|------|------|
| **Zookeeper** | `zookeeper` | 2181 | Coordinates Kafka brokers, manages cluster state |
| **Kafka Broker** | `kafka` | 9092 | Message broker; stores and distributes real-time traffic data |
| **Producer** | Local Python | N/A | Reads traffic sensor CSV and publishes to Kafka |
| **Consumer** | Local Python | N/A | Subscribes to Kafka topic and displays real-time statistics |

---

## Project Structure

```
lab3/
├── README.md                              # This file
├── docker-compose.yml                     # Kafka + Zookeeper configuration
├── run_lab3.sh                            # Execution orchestration script
├── test_kafka.py                          # Kafka connectivity test script
│
├── data/
│   └── traffic_sensors.csv                # Generated traffic sensor data
│
└── scripts/
    ├── generate_traffic.py                # Data generator: Creates traffic_sensors.csv
    ├── producer.py                        # Producer: Publishes messages to Kafka
    ├── consumer_simple.py                 # Consumer: Displays real-time traffic stats
    └── spark_consumer.py                  # Spark Structured Streaming consumer (optional)
```

---

## Components & Workflow

### 1. **Data Generation** (`scripts/generate_traffic.py`)

Generates synthetic traffic sensor data simulating real-time vehicle telemetry from multiple highways.

**Features Generated:**
- `Vehicle_ID`: Unique vehicle identifier (CAR_0000 to CAR_9999)
- `Highway_ID`: Highway name (I-95, Route_66, Pacific_Coast, Autobahn_1)
- `Speed_KMH`: Vehicle speed in kilometers per hour (10–120 KMH)
- `Timestamp`: ISO 8601 timestamp when measurement was taken

**Output:** `data/traffic_sensors.csv` (5,000+ records)

```csv
Vehicle_ID,Highway_ID,Speed_KMH,Timestamp
CAR_5939,Route_66,28,2026-03-30 20:09:44
CAR_6636,I-95,71,2026-03-30 20:09:45
CAR_3154,Route_66,16,2026-03-30 20:09:46
CAR_8354,Pacific_Coast,94,2026-03-30 20:09:47
```

**Run command:**
```bash
cd /Users/yelessov/Desktop/movie-hadoop-project/lab3/scripts
python3.11 generate_traffic.py
```

---

### 2. **Kafka Producer** (`scripts/producer.py`)

Continuously publishes traffic sensor data to the Kafka topic `highway-telemetry`.

**Workflow:**
1. Reads traffic sensor records from `traffic_sensors.csv`
2. Converts each row to JSON format
3. Publishes to Kafka topic with 0.5-second delays (simulates real-time streaming)
4. Displays confirmation for each message sent

**Output Format:**
```json
{
  "Vehicle_ID": "CAR_5939",
  "Highway_ID": "Route_66",
  "Speed_KMH": 28,
  "Timestamp": "2026-03-30 20:09:44"
}
```

**Run command:**
```bash
cd /Users/yelessov/Desktop/movie-hadoop-project/lab3/scripts
/opt/homebrew/bin/python3.11 producer.py
```

**Expected Output:**
```
🚦 Starting Smart City Traffic Sensors...
🚗 Sensor Data Sent -> {"Vehicle_ID": "CAR_5939", "Highway_ID": "Route_66", "Speed_KMH": 28, "Timestamp": "2026-03-30 20:09:44"}
🚗 Sensor Data Sent -> {"Vehicle_ID": "CAR_6636", "Highway_ID": "I-95", "Speed_KMH": 71, "Timestamp": "2026-03-30 20:09:45"}
...
```

---

### 3. **Kafka Consumer** (`scripts/consumer_simple.py`)

Subscribes to the Kafka topic and displays real-time traffic statistics.

**Workflow:**
1. Connects to Kafka broker at `localhost:9092`
2. Subscribes to `highway-telemetry` topic with a unique consumer group
3. Maintains a rolling window of 50 speed measurements per highway
4. Calculates and displays average speeds every 10 messages
5. Updates display with timestamp, highway, and calculated average

**Key Configuration:**
- `auto.offset.reset`: `'latest'` — Only shows new messages (not historical data)
- `group.id`: Unique timestamp-based ID — Prevents offset caching issues
- Display interval: Every 10 messages received

**Run command:**
```bash
cd /Users/yelessov/Desktop/movie-hadoop-project/lab3/scripts
/opt/homebrew/bin/python3.11 consumer_simple.py
```

**Expected Output:**
```
✅ Connected to Kafka 'highway-telemetry' topic

📊 Real-time Traffic Monitoring

Time                 Highway         Avg Speed (KMH)      Messages  
-----------------------------------------------------------------
2026-03-30 21:08:08  Autobahn_1                   82.00         10
2026-03-30 21:08:08  I-95                         73.50         10
2026-03-30 21:08:08  Pacific_Coast                86.25         10
-----------------------------------------------------------------
2026-03-30 21:08:13  Autobahn_1                   73.71         20
2026-03-30 21:08:13  I-95                         49.40         20
2026-03-30 21:08:13  Pacific_Coast                65.00         20
2026-03-30 21:08:13  Route_66                     16.00         20
-----------------------------------------------------------------
```

---

### 4. **Spark Structured Streaming Consumer** (`scripts/spark_consumer.py`)

Optional advanced consumer using Apache Spark for complex stream processing.

**Features:**
- 10-second tumbling window aggregation
- Calculates average speed per highway within each window
- Console output of windowed statistics
- Scalable to handle high-volume streams

**Prerequisites:**
```bash
# Install confluent-kafka for local consumer
/opt/homebrew/bin/python3.11 -m pip install confluent-kafka

# For Spark streaming (requires Spark 3.3.1+)
export PYSPARK_PYTHON=/opt/homebrew/bin/python3.11
export PYSPARK_DRIVER_PYTHON=/opt/homebrew/bin/python3.11
```

**Run command:**
```bash
cd /Users/yelessov/Desktop/movie-hadoop-project/lab3
export PYSPARK_PYTHON=/opt/homebrew/bin/python3.11
export PYSPARK_DRIVER_PYTHON=/opt/homebrew/bin/python3.11

spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.1 \
    scripts/spark_consumer.py
```

---

## Quick Start

### Step 1: Start Kafka & Zookeeper
```bash
cd /Users/yelessov/Desktop/movie-hadoop-project/lab3
docker-compose up -d

# Verify services are running
docker ps | grep -E "kafka|zookeeper"
```

### Step 2: Generate Traffic Data
```bash
cd /Users/yelessov/Desktop/movie-hadoop-project/lab3/scripts
/opt/homebrew/bin/python3.11 generate_traffic.py
```

### Step 3: Start Producer (Terminal 1)
```bash
cd /Users/yelessov/Desktop/movie-hadoop-project/lab3/scripts
/opt/homebrew/bin/python3.11 producer.py
```

### Step 4: Start Consumer (Terminal 2)
```bash
cd /Users/yelessov/Desktop/movie-hadoop-project/lab3/scripts
/opt/homebrew/bin/python3.11 consumer_simple.py
```

---

## System Requirements

### Software
- **Python**: 3.11.15+ (required for Spark 4.1.1 compatibility)
- **Docker**: Latest version
- **confluent-kafka**: Python library for Kafka client
- **Apache Spark**: 3.3.1+ (optional, for spark_consumer.py)

### Installation
```bash
# Install Python 3.11
brew install python@3.11

# Install confluent-kafka
/opt/homebrew/bin/python3.11 -m pip install confluent-kafka

# Verify installations
/opt/homebrew/bin/python3.11 --version
docker --version
```

### Hardware
- **Minimum**: 2 CPU cores, 4GB RAM
- **Recommended**: 4+ CPU cores, 8GB+ RAM

---

## Troubleshooting

### Issue: Consumer shows no data

**Cause**: Consumer group has committed offset; using `'earliest'` offset reset causes it to start from committed position, not the beginning.

**Solution**: Use unique `group.id` with timestamp and set `auto.offset.reset` to `'latest'`:
```python
conf = {
    'group.id': f'traffic-consumer-{int(time.time())}',
    'auto.offset.reset': 'latest'
}
```

### Issue: Kafka connection refused

**Cause**: Kafka broker not running or hostname mismatch.

**Solution**: 
```bash
# Verify containers are running
docker ps

# Check Kafka is accessible
/opt/homebrew/bin/python3.11 -c "from confluent_kafka import Producer; p = Producer({'bootstrap.servers': 'localhost:9092'}); print('✅ Kafka connected')"
```

### Issue: "No module named 'confluent_kafka'"

**Cause**: Python 3.11 doesn't have the library installed.

**Solution**:
```bash
/opt/homebrew/bin/python3.11 -m pip install confluent-kafka
```

### Issue: Spark consumer exits with type error

**Cause**: Spark 4.1.1 incompatibility. Local Spark 4.1.1 doesn't work with Kafka connector 3.3.1.

**Solution**: Use the simple consumer instead, or use Docker Spark container.

---

## Key Learnings

1. **Real-Time Streaming**: Kafka enables low-latency, high-throughput message distribution
2. **Consumer Groups**: Multiple consumers can process the same stream independently with different group IDs
3. **Offset Management**: Proper offset reset strategy determines whether to process historical or new messages
4. **Windowed Aggregations**: Time-based windows allow calculating statistics over moving time periods
5. **Producer-Consumer Pattern**: Decouples data sources (sensors) from consumers (dashboards, analytics)

---

## Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs kafka
docker-compose logs zookeeper

# Check running containers
docker ps

# Access Kafka inside container
docker exec -it kafka bash
```

---

## Performance Metrics

| Metric | Value |
|--------|-------|
| **Messages/sec** | ~2 (0.5s delay per message for simulation) |
| **Data per message** | ~150 bytes |
| **Average throughput** | ~300 bytes/sec |
| **Consumer latency** | <100ms |
| **Window size** | 10 seconds (default) |

---

## Future Enhancements

1. **Alert System**: Trigger alerts when average speed exceeds highway limits
2. **Machine Learning**: Predict traffic congestion using historical patterns
3. **Dashboard**: Build a web-based visualization (Grafana, Kibana)
4. **Persistence**: Store results in time-series database (InfluxDB, TimescaleDB)
5. **Multiple Producers**: Simulate multiple highway segments with independent producers
6. **Load Testing**: Increase message volume to test scalability

---

## References

- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Confluent Python Client](https://docs.confluent.io/kafka-clients/python/current/overview.html)
- [Spark Structured Streaming](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html)
- [Docker Compose](https://docs.docker.com/compose/)

---

## Author Notes

This lab demonstrates the core concepts of real-time data streaming and event-driven architectures. The producer-consumer pattern is fundamental to modern cloud platforms, microservices, and IoT systems. Understanding Kafka's offset management and consumer group dynamics is critical for building reliable streaming applications.

**Status**: ✅ Fully functional and tested on macOS with Python 3.11 and Apache Kafka 7.5.0
