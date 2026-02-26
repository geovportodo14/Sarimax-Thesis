import pymongo

uri = "mongodb+srv://Sarimax-Thesis:March142003!@sarimax-thesis.p6tv8ia.mongodb.net/?appName=Sarimax-Thesis"
client = pymongo.MongoClient(uri)
db = client["Sarimax-Thesis"]

doc = db.aircon.find_one()
if doc:
    print("AIRCON DOC DATE:", doc.get("date"))
    print("AIRCON READINGS COUNT:", len(doc.get("readings", [])))
    docs = list(db.aircon.find())
    dates = set([d.get("date") for d in docs])
    print("ALL AIRCON DATES:", dates)
else:
    print("No documents found in aircon.")
