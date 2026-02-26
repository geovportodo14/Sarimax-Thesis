import pymongo

uri = "mongodb+srv://Sarimax-Thesis:March142003!@sarimax-thesis.p6tv8ia.mongodb.net/?appName=Sarimax-Thesis"
client = pymongo.MongoClient(uri)
db = client["Sarimax-Thesis"]

doc = db.energybuckets.find_one({"date": "2026-02-12", "appliance_type": "aircon"})
print("Has daily_summary?:", "daily_summary" in doc)

if "readings" in doc and len(doc["readings"]) > 0:
    first_reading = doc["readings"][0]
    print("First reading keys:", list(first_reading.keys()))
    if "processed_data" in first_reading:
        print("Processed data:", first_reading["processed_data"])
    else:
        print("NO processed_data found in reading!")
