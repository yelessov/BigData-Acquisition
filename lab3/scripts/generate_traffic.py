import csv
import random
from datetime import datetime, timedelta

highways = ["Route_66", "I-95", "Pacific_Coast", "Autobahn_1"]

# Generate 500 simulated vehicle speed logs
data = []
current_time = datetime.now()

for i in range(500):
    vehicle_id = f"CAR_{random.randint(1000, 9999)}"
    highway = random.choice(highways)
    # Simulate normal speeds (60-120) and occasional traffic jams (10-30)
    speed = random.randint(10, 30) if random.random() < 0.2 else random.randint(60, 120)
    
    # Space readings out by a few milliseconds/seconds
    current_time += timedelta(milliseconds=random.randint(100, 1500))
    timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
    
    data.append([vehicle_id, highway, speed, timestamp])

with open('../data/traffic_sensors.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Vehicle_ID', 'Highway_ID', 'Speed_KMH', 'Timestamp'])
    writer.writerows(data)

print("✅ Successfully generated 500 traffic sensor records in data/traffic_sensors.csv")