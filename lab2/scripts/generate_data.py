import pandas as pd
import numpy as np

# Total records required
n = 200000

data = {
    'id': range(n),
    'duration': np.random.randint(0, 1000, n),
    'protocol_type': np.random.choice(['TCP', 'UDP', 'ICMP'], n),
    'src_bytes': np.random.randint(100, 50000, n),
    'dst_bytes': np.random.randint(100, 50000, n),
    'is_attack': np.random.choice([0, 1], n, p=[0.8, 0.2]) # 20% are attacks
}

df = pd.DataFrame(data)
df.to_csv('data/network_traffic.csv', index=False)
print("Successfully generated 200,000 records in data/network_traffic.csv")