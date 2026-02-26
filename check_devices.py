import pymongo

uri = "mongodb+srv://Sarimax-Thesis:March142003!@sarimax-thesis.p6tv8ia.mongodb.net/?appName=Sarimax-Thesis"
client = pymongo.MongoClient(uri)
db = client["Sarimax-Thesis"]

appliances = ["aircon", "refrigerator", "electric_fan"]
for app in appliances:
    docs = db[app].find()
    print(f"--- {app} ---")
    devices = set([d.get("device_id") for d in docs])
    print("Devices:", devices)

# Let's see the unique indexes on energybuckets
print("Indexes on energybuckets:", db.energybuckets.index_information())
