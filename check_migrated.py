import pymongo
import json
from bson import json_util

uri = "mongodb+srv://Sarimax-Thesis:March142003!@sarimax-thesis.p6tv8ia.mongodb.net/?appName=Sarimax-Thesis"
client = pymongo.MongoClient(uri)
db = client["Sarimax-Thesis"]

doc = db.energybuckets.find_one({"date": "2026-02-12"})
print(json.dumps(doc, indent=2, default=json_util.default))
