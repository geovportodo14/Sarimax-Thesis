import pymongo

uri = "mongodb+srv://Sarimax-Thesis:March142003!@sarimax-thesis.p6tv8ia.mongodb.net/?appName=Sarimax-Thesis"
client = pymongo.MongoClient(uri)
db = client["Sarimax-Thesis"]

docs = list(db.energybuckets.find())
print(f"Total in energybuckets: {len(docs)}")
for i, d in enumerate(docs[:10]):
    print(f"[{i}] {d.get('appliance_type')} | {d.get('date')} | {d.get('device_id')}")

if len(docs) > 10:
    print("...")
