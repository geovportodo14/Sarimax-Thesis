import os
import pymongo
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
# Ensure we use the correct destination database
DEST_DB_NAME = "Sarimax-Thesis"
SOURCE_DB_NAME = "sarimax_thesis"

client = pymongo.MongoClient(MONGODB_URI)
dest_db = client[DEST_DB_NAME]
source_db = client[SOURCE_DB_NAME]

def migrate_from_lowercase_db():
    print(f"Migrating from {SOURCE_DB_NAME}.energybuckets to {DEST_DB_NAME}.energybuckets...")
    source_coll = source_db["energybuckets"]
    dest_coll = dest_db["energybuckets"]
    
    docs = list(source_coll.find())
    print(f"Found {len(docs)} documents in {SOURCE_DB_NAME}")
    
    for doc in docs:
        query = {"date": doc["date"], "device_id": doc["device_id"]}
        # Using upsert logic to merge or insert
        # We try to push readings that don't exist
        dest_doc = dest_coll.find_one(query)
        if not dest_doc:
            print(f"  Inserting new doc for {doc['date']} - {doc['appliance_type']}")
            dest_coll.insert_one(doc)
        else:
            print(f"  Updating existing doc for {doc['date']} - {doc['appliance_type']}")
            # Merge readings array, avoiding duplicates by interval_index
            existing_indexes = [r["interval_index"] for r in dest_doc.get("readings", [])]
            new_readings = [r for r in doc.get("readings", []) if r["interval_index"] not in existing_indexes]
            
            if new_readings:
                dest_coll.update_one(
                    query,
                    {
                        "$push": {"readings": {"$each": new_readings}},
                        "$inc": {"reading_count": len(new_readings)},
                        "$set": {"last_updated": datetime.now()}
                    }
                )

def migrate_from_individual_collections():
    individual_colls = ["aircon", "refrigerator", "electric_fan", "electricfan"]
    dest_coll = dest_db["energybuckets"]
    
    print(f"Migrating individual collections from {DEST_DB_NAME} to energybuckets...")
    
    for coll_name in individual_colls:
        if coll_name not in dest_db.list_collection_names():
            continue
            
        print(f"  Processing collection: {coll_name}")
        source_coll = dest_db[coll_name]
        docs = list(source_coll.find())
        
        for doc in docs:
            # Check if this document looks like a bucket doc (has 'readings' array)
            if "readings" in doc and "date" in doc:
                query = {"date": doc["date"], "device_id": doc["device_id"]}
                dest_doc = dest_coll.find_one(query)
                if not dest_doc:
                    print(f"    Moving bucket doc for {doc['date']} from {coll_name} to energybuckets")
                    # Ensure appliance_type is set correctly
                    if "appliance_type" not in doc:
                        doc["appliance_type"] = coll_name.lower().replace("_", "")
                    dest_coll.insert_one(doc)
                else:
                    print(f"    Merging readings for {doc['date']} from {coll_name}")
                    existing_indexes = [r["interval_index"] for r in dest_doc.get("readings", [])]
                    new_readings = [r for r in doc.get("readings", []) if r["interval_index"] not in existing_indexes]
                    if new_readings:
                        dest_coll.update_one(
                            query,
                            {
                                "$push": {"readings": {"$each": new_readings}},
                                "$inc": {"reading_count": len(new_readings)},
                                "$set": {"last_updated": datetime.now()}
                            }
                        )
            else:
                # If it's a flat record (unlikely but checking structure I saw earlier)
                print(f"    Skipping flat record in {coll_name} (needs manual review if many)")

if __name__ == "__main__":
    migrate_from_lowercase_db()
    migrate_from_individual_collections()
    print("Migration complete!")
