from datetime import datetime
from pymongo import MongoClient, UpdateOne
import hashlib
import os
from dateutil import parser

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
client = MongoClient(MONGO_URI)
collection = client["bitsfeed"]["news"]

def insert_news(news_items):
    operations = []
    for item in news_items:
        unique_id = hashlib.md5(item["link"].encode()).hexdigest()
        item["_id"] = unique_id

        if isinstance(item["published"], str):
            item["published"] = parser.parse(item["published"])

        item["scraped_at"] = datetime.utcnow()


        operations.append(
            UpdateOne(
                {"_id": unique_id},
                {"$setOnInsert": item},
                upsert=True
            )
        )

    if operations:
        result = collection.bulk_write(operations, ordered=False)
        print(f"[MongoDB] Upserted {result.upserted_count} new items.")

def get_all_news():
    return list(
        collection.find({}, {"_id": 0}).sort("published", -1)
    )
