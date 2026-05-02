#!/usr/bin/env python3
import sys
from confluent_kafka import Producer

print("Testing Kafka producer connection...")
print(f"Python version: {sys.version}")

conf = {'bootstrap.servers': 'localhost:9092',  'debug': 'all'}
print(f"Producer config: {conf}")

try:
    producer = Producer(conf)
    print("Producer created successfully!")
    
    # Try to send a test message
    producer.produce('highway-telemetry', value=b'test message', callback=lambda err, msg: print(f"Callback: err={err}, msg={msg}"))
    producer.flush(timeout=5)
    print("Message sent successfully!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
