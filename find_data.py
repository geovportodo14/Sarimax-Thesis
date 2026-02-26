import pymongo

uri = "mongodb+srv://Sarimax-Thesis:March142003!@sarimax-thesis.p6tv8ia.mongodb.net/?appName=Sarimax-Thesis"
client = pymongo.MongoClient(uri)

print("Databases:")
for db_name in client.list_database_names():
    db = client[db_name]
    collections = db.list_collection_names()
    print(f"\n--- {db_name} ---")
    for coll_name in collections:
        count = db[coll_name].estimated_document_count()
        if count > 0:
            print(f"  {coll_name}: {count} docs")

