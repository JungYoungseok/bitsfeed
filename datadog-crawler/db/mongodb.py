from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
client = MongoClient(MONGO_URI)
db = client["datadog"]
collection = db["news"]

def insert_news(news_list):
    if news_list:
        collection.insert_many(news_list)

def get_all_news():
    return list(collection.find({}, {"_id": 0}))
