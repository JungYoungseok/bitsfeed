from datetime import datetime
from pymongo import MongoClient, UpdateOne
import hashlib
import os
from dateutil import parser
from kafka.kafka_producer import send_news_to_kafka

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
client = MongoClient(MONGO_URI)
collection = client["bitsfeed"]["news"]

def serialize_news_item(item):
    """Kafka 전송을 위한 JSON 직렬화 안전 복사본 생성"""
    def encode_value(value):
        if isinstance(value, datetime):
            return value.isoformat()
        return value

    return {k: encode_value(v) for k, v in item.items()}

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

        # ✅ Kafka로 새로 insert된 데이터만 전송
        for upserted_id in result.upserted_ids.values():
            new_item = collection.find_one({"_id": upserted_id})
            send_news_to_kafka(serialize_news_item(new_item))

def get_all_news():
    return list(
        collection.find({}, {"_id": 0}).sort("published", -1)
    )
