import csv
import json
import time
from confluent_kafka import Producer

# Configure the Kafka Producer to connect to our local Docker container
conf = {'bootstrap.servers': 'localhost:9092'}
producer = Producer(conf)
topic = 'highway-telemetry'

def delivery_report(err, msg):
    if err is not None:
        print(f"❌ Message delivery failed: {err}")
    else:
        print(f"🚗 Sensor Data Sent -> {msg.value().decode('utf-8')}")

print("🚦 Starting Smart City Traffic Sensors...")

# Read the CSV and stream it to Kafka
with open('../data/traffic_sensors.csv', mode='r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        # Convert the CSV row into a JSON payload
        payload = json.dumps({
            "Vehicle_ID": row["Vehicle_ID"],
            "Highway_ID": row["Highway_ID"],
            "Speed_KMH": int(row["Speed_KMH"]),
            "Timestamp": row["Timestamp"]
        })
        
        # Publish to Kafka
        producer.produce(topic, value=payload.encode('utf-8'), callback=delivery_report)
        producer.poll(0)
        
        # Pause slightly to simulate real-time data streaming
        time.sleep(0.5)

producer.flush()
print("🛑 All traffic data successfully transmitted.")