from pymongo import MongoClient
import pandas as pd

client = MongoClient('mongodb://localhost:27017/')
db = client['Sarimax-Thesis']

data = list(db['energybuckets'].find({}, {'date': 1, 'appliance_type': 1, 'readings.timestamp': 1, 'readings.processed_data.power_w': 1}))

records = []
for doc in data:
    if 'readings' not in doc: continue
    for r in doc['readings']:
        if 'timestamp' in r and 'processed_data' in r and 'power_w' in r['processed_data']:
            records.append({
                'appliance': doc['appliance_type'],
                'timestamp': r['timestamp'],
                'power_w': r['processed_data']['power_w']
            })

df = pd.DataFrame(records)
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['hour'] = df['timestamp'].dt.tz_convert('Asia/Manila').dt.hour if df['timestamp'].dt.tz is not None else df['timestamp'].dt.hour

for app in df['appliance'].unique():
    print(f"\n--- {app} ---")
    app_df = df[df['appliance'] == app]
    profile = app_df.groupby('hour')['power_w'].mean()
    print(profile.apply(lambda x: f"{x:.2f} W").to_string())
