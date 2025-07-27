import os
import json
import time
import openai
import hashlib
import threading
import sys
from pymongo import MongoClient
from confluent_kafka import Consumer
from dateutil import parser
from datetime import datetime
import asyncio

# API 서버 모듈 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api_server import stats, start_api_server

from utils import build_prompt, call_openai, save_summary_to_mongo

def run_summary_consumer():
    print("🚀 News Consumer Summary Service Starting... (GitHub Actions Test - v2024.1.20)")
    
    # 통계 상태 업데이트
    stats.set_consumer_status(True)
    
    openai.api_key = os.getenv("OPENAI_API_KEY")
    mongo = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
    collection = mongo["bitsfeed"]["news"]

    consumer = Consumer({
        'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
        'group.id': 'summary-consumer',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': True
    })
    print("news_raw topic subscribe")
    consumer.subscribe(['news_raw'])
    stats.set_kafka_status("connecting")

    async def poll_loop():
        print("poll_loop started")
        # while not consumer.assignment():
        #     consumer.poll(0.1)
        #     await asyncio.sleep(0.1)
        consumer.poll(0)
        consumer.list_topics(timeout=5.0)

        print("✅ Kafka partition assigned:", consumer.assignment())
        print(consumer.list_topics())
        stats.set_kafka_status("connected")

        try:
            while True:
                msg = consumer.poll(1.0)
                if msg is None:
                    await asyncio.sleep(0.1)
                    continue

                if msg.error():
                    print(f"❌ Kafka error: {msg.error()}")
                    stats.update_error()
                    stats.set_kafka_status("error")
                    continue

                try:                    
                    article = json.loads(msg.value().decode('utf-8'))
                    print("Message 확인: ", article)
                    article_id = article.get('_id') or hashlib.md5(article['link'].encode()).hexdigest()
                    prompt = build_prompt(article)
                    summary = call_openai(prompt)
                    save_summary_to_mongo(collection, article_id, summary)
                    
                    # 통계 업데이트
                    stats.update_processed(article, summary)
                    print(f"✅ 처리 완료 - 총 {stats.total_processed}개 처리됨")
                    
                except Exception as e:
                    print(f"❗ 처리 중 오류 발생: {e}")
                    stats.update_error()

        except asyncio.CancelledError:
            print("🛑 Summary consumer shutdown requested.")
        finally:
            stats.set_consumer_status(False)
            stats.set_kafka_status("disconnected")
            consumer.close()
            print("🛑 Kafka consumer closed.")

    asyncio.run(poll_loop())

def start_service():
    """API 서버와 Kafka Consumer를 동시 실행"""
    print("📊 Initializing News Consumer Summary Service...")
    
    # API 서버를 별도 스레드에서 시작
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()
    print("🌐 API Server starting on port 8002...")
    
    # 잠시 대기 (API 서버 시작 시간)
    time.sleep(2)
    
    # Kafka Consumer 시작
    print("🔧 Starting Kafka Consumer...")
    run_summary_consumer()

if __name__ == "__main__":
    start_service()
