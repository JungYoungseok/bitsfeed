import os
import json
import time
import openai
import hashlib
from pymongo import MongoClient
from confluent_kafka import Consumer
from dateutil import parser
from datetime import datetime
import asyncio

from utils import build_prompt, call_openai, save_summary_to_mongo

def run_summary_consumer():
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

    async def poll_loop():
        print("poll_loop started")
        # while not consumer.assignment():
        #     consumer.poll(0.1)
        #     await asyncio.sleep(0.1)
        consumer.poll(0)
        consumer.list_topics(timeout=5.0)


        print("✅ Kafka partition assigned:", consumer.assignment())
        print(consumer.list_topics())

        try:
            while True:
                msg = consumer.poll(1.0)
                if msg is None:
                    await asyncio.sleep(0.1)
                    continue

                if msg.error():
                    print(f"❌ Kafka error: {msg.error()}")
                    continue

                try:                    
                    article = json.loads(msg.value().decode('utf-8'))
                    print("Message 확인: ", article)
                    article_id = article.get('_id') or hashlib.md5(article['link'].encode()).hexdigest()
                    prompt = build_prompt(article)
                    summary = call_openai(prompt)
                    save_summary_to_mongo(collection, article_id, summary)
                except Exception as e:
                    print(f"❗ 처리 중 오류 발생: {e}")

        except asyncio.CancelledError:
            print("🛑 Summary consumer shutdown requested.")
        finally:
            consumer.close()
            print("🛑 Kafka consumer closed.")

    asyncio.run(poll_loop())

if __name__ == "__main__":
    print("run_summary_consumer() executed")
    run_summary_consumer()
