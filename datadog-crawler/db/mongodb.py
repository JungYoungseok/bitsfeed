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

def update_keywords_for_article(article_id: str):
    """단일 기사에 대한 키워드 데이터 업데이트"""
    try:
        from db.keyword_manager import (
            process_article_keywords, 
            keywords_collection, 
            keyword_trends_collection
        )
        
        # 기사 데이터 조회
        article = collection.find_one({"_id": article_id})
        if not article:
            return
        
        # 키워드 추출
        article_keywords = process_article_keywords(article)
        if not article_keywords:
            return
        
        # 발행일 파싱
        try:
            if isinstance(article.get('published'), str):
                pub_date = datetime.fromisoformat(article['published'].replace('Z', '+00:00')).date()
            else:
                pub_date = article.get('published', datetime.utcnow()).date()
        except:
            pub_date = datetime.utcnow().date()
        
        # 키워드별 빈도 및 기사 정보 업데이트
        for keyword in article_keywords:
            # keywords collection 업데이트
            keywords_collection.update_one(
                {"keyword": keyword},
                {
                    "$inc": {"frequency": 1},
                    "$push": {
                        "articles": {
                            "article_id": article_id,
                            "title": article.get('title', ''),
                            "published": pub_date.isoformat(),
                            "source": article.get('source', '')
                        }
                    },
                    "$set": {"last_updated": datetime.utcnow()}
                },
                upsert=True
            )
            
            # keyword_trends collection 업데이트
            keyword_trends_collection.update_one(
                {"keyword": keyword, "date": pub_date.isoformat()},
                {
                    "$inc": {"count": 1},
                    "$set": {
                        "keyword": keyword,
                        "date": pub_date.isoformat(),
                        "last_updated": datetime.utcnow()
                    }
                },
                upsert=True
            )
        
        # 키워드 동시 출현 업데이트
        cooccurrence_collection = client["bitsfeed"]["keyword_cooccurrence"]
        
        for i, keyword1 in enumerate(article_keywords):
            for keyword2 in article_keywords[i+1:]:
                pair_key1, pair_key2 = sorted([keyword1, keyword2])
                cooccurrence_collection.update_one(
                    {"keyword1": pair_key1, "keyword2": pair_key2},
                    {
                        "$inc": {"count": 1},
                        "$set": {
                            "keyword1": pair_key1,
                            "keyword2": pair_key2,
                            "last_updated": datetime.utcnow()
                        }
                    },
                    upsert=True
                )
        
        print(f"✅ 기사 {article_id}의 키워드 데이터 업데이트 완료")
        
    except Exception as e:
        print(f"❌ 기사 {article_id} 키워드 업데이트 실패: {e}")

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
            
            # 🔄 새로 추가된 기사의 키워드 데이터 업데이트
            update_keywords_for_article(upserted_id)

def get_all_news():
    return list(
        collection.find({}, {"_id": 0}).sort("published", -1)
    )
