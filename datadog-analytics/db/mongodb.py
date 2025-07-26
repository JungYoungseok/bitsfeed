from pymongo import MongoClient
import os
import hashlib
from datetime import datetime
from pymongo.operations import UpdateOne
from dateutil import parser

# MongoDB 연결 설정
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)

# 데이터베이스 및 컬렉션 설정
db = client["bitsfeed"]
collection = db["news"]
keywords_collection = db["keywords"]
keyword_trends_collection = db["keyword_trends"]
cooccurrence_collection = db["keyword_cooccurrence"]

def get_all_news():
    """모든 뉴스 조회 (분석용)"""
    try:
        cursor = collection.find().sort("published", -1).limit(100)
        news_list = []
        for item in cursor:
            item["_id"] = str(item["_id"])
            if isinstance(item.get("published"), str):
                item["published"] = parser.parse(item["published"])
            
            if item.get("published"):
                item["published"] = item["published"].isoformat()
            
            news_list.append(item)
        
        return news_list
    except Exception as e:
        print(f"[ERROR] Failed to fetch news: {e}")
        return []

def get_recent_news(days=7):
    """최근 N일간의 뉴스 조회 (분석용)"""
    try:
        from datetime import datetime, timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        cursor = collection.find({
            "published": {"$gte": cutoff_date}
        }).sort("published", -1)
        
        news_list = []
        for item in cursor:
            item["_id"] = str(item["_id"])
            if isinstance(item.get("published"), str):
                item["published"] = parser.parse(item["published"])
            
            if item.get("published"):
                item["published"] = item["published"].isoformat()
            
            news_list.append(item)
        
        return news_list
    except Exception as e:
        print(f"[ERROR] Failed to fetch recent news: {e}")
        return []

def test_connection():
    """MongoDB 연결 테스트"""
    try:
        client.admin.command('ping')
        return {"status": "connected", "database": "bitsfeed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
