import pymongo
from datetime import datetime

uri = "mongodb+srv://Sarimax-Thesis:March142003!@sarimax-thesis.p6tv8ia.mongodb.net/?appName=Sarimax-Thesis"
client = pymongo.MongoClient(uri)
db = client["Sarimax-Thesis"]
target = db["energybuckets"]

appliances = ["aircon", "refrigerator", "electric_fan"]
total_migrated = 0

for app in appliances:
    print(f"Migrating {app}...")
    docs = db[app].find()
    app_enum = app.replace("_", "")
    for doc in docs:
        # Check if already exists in energybuckets using date and device_id
        if target.find_one({"device_id": doc.get("device_id"), "date": doc.get("date")}):
            continue
        
        doc["appliance_type"] = app_enum
        
        # We must remove the original _id before inserting into a new collection 
        # to ensure MongoDB generates a fresh one or allows insertion without _id conflict
        if "_id" in doc:
            del doc["_id"]
            
        try:
            target.insert_one(doc)
            total_migrated += 1
        except Exception as e:
            print(f"Error migrating doc {doc.get('date')} for {app}: {e}")

print(f"Successfully migrated {total_migrated} historical documents to energybuckets.")
