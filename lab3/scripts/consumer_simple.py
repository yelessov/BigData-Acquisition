#!/usr/bin/env python3
"""Simple Kafka consumer that reads traffic data and calculates rolling averages."""

import json
import sys
import time
from collections import defaultdict
from datetime import datetime, timedelta
from confluent_kafka import Consumer, OFFSET_BEGINNING

# Kafka consumer configuration
conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': f'traffic-consumer-{int(time.time())}',
    'auto.offset.reset': 'latest',
    'enable.auto.commit': True
}

# Try to connect to Kafka
try:
    consumer = Consumer(conf)
    consumer.subscribe(['highway-telemetry'])
    print("✅ Connected to Kafka 'highway-telemetry' topic")
except Exception as e:
    print(f"❌ Failed to connect: {e}")
    sys.exit(1)

# Store speeds for each highway
highway_speeds = defaultdict(list)
message_count = 0

print("\n📊 Real-time Traffic Monitoring\n")
print(f"{'Time':<20} {'Highway':<15} {'Avg Speed (KMH)':<20} {'Messages':<10}")
print("-" * 65)

try:
    while True:
        msg = consumer.poll(timeout=1.0)
        
        if msg is None:
            continue
            
        if msg.error():
            print(f"❌ Consumer error: {msg.error()}")
            continue
        
        # Parse the message
        try:
            data = json.loads(msg.value().decode('utf-8'))
            highway_id = data['Highway_ID']
            speed = data['Speed_KMH']
            
            # Store the speed
            highway_speeds[highway_id].append(speed)
            message_count += 1
            
            # Keep only the last 50 records per highway
            if len(highway_speeds[highway_id]) > 50:
                highway_speeds[highway_id].pop(0)
            
            # Display stats every 10 messages
            if message_count % 10 == 0:
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                for highway in sorted(highway_speeds.keys()):
                    avg_speed = sum(highway_speeds[highway]) / len(highway_speeds[highway])
                    print(f"{current_time:<20} {highway:<15} {avg_speed:>18.2f} {message_count:>10}")
                print("-" * 65)
                
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing message: {e}")
            continue
            
except KeyboardInterrupt:
    print("\n\n✅ Shutting down consumer...")
finally:
    consumer.close()
