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

# Datadog tracing
from ddtrace import tracer

# API 서버 모듈 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api_server import stats, start_api_server

from utils import build_prompt, call_openai, save_summary_to_mongo
from mysql_utils import create_kafka_test_table, save_test_message_to_mysql

def run_summary_consumer():
    print("🚀 News Consumer Summary Service Starting... (GitHub Actions Test - v2024.1.20)")
    
    # 통계 상태 업데이트
    stats.set_consumer_status(True)
    
    # MySQL 테스트 테이블 초기화
    print("📊 Initializing MySQL test table...")
    create_kafka_test_table()
    
    openai.api_key = os.getenv("OPENAI_API_KEY")
    mongo = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
    collection = mongo["bitsfeed"]["news"]

    consumer = Consumer({
        'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
        'group.id': 'summary-consumer',
        'client.id': 'news-consumer-client',  # Data Streams Monitoring을 위한 클라이언트 식별
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': True,
        'session.timeout.ms': 10000,          # Consumer Group 세션 타임아웃
        'heartbeat.interval.ms': 3000,        # Consumer Group heartbeat
        'max.poll.interval.ms': 300000,       # 최대 poll 간격
        'statistics.interval.ms': 10000,      # 통계 정보 수집 (Data Streams 관련)
    })
    print("news_raw topic subscribe")
    consumer.subscribe(['news_raw'])
    stats.set_kafka_status("connecting")

    async def poll_loop():
        print("poll_loop started")
        
        # Consumer Group coordinator와 partition 할당 대기
        print("🔄 Waiting for partition assignment...")
        assignment_retries = 0
        max_retries = 30  # 최대 30초 대기
        
        while not consumer.assignment() and assignment_retries < max_retries:
            consumer.poll(0.1)
            await asyncio.sleep(0.1)
            assignment_retries += 1
            if assignment_retries % 10 == 0:  # 1초마다 로그 출력
                print(f"🔄 Still waiting for partition assignment... ({assignment_retries}/30)")
        
        final_assignment = consumer.assignment()
        if final_assignment:
            print("✅ Kafka partition assigned:", final_assignment)
            # Data Streams Monitoring을 위한 추가 정보 로그
            for tp in final_assignment:
                print(f"📊 DSM: Topic={tp.topic}, Partition={tp.partition}, Consumer Group=summary-consumer")
        else:
            print("❌ Failed to get partition assignment after 30 seconds")
            
        consumer.list_topics(timeout=5.0)
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
                    
                    # Datadog span으로 message 처리 추적
                    with tracer.trace("kafka.message.process", service="news-consumer") as span:
                        span.set_tag("kafka.topic", "news_raw")
                        span.set_tag("kafka.partition", msg.partition())
                        span.set_tag("kafka.offset", msg.offset())
                        span.set_tag("message.id", article.get('_id', 'unknown'))
                        
                        # 테스트 메시지 감지 및 MySQL 저장
                        if 'test_metadata' in article and article.get('test_metadata', {}).get('test_type') == 'data_streams_monitoring':
                            span.set_tag("message.type", "test")
                            span.set_tag("test.type", "data_streams_monitoring")
                            print("🧪 Test message detected for Data Streams Monitoring")
                            
                            with tracer.trace("mysql.test_message.save", service="news-consumer") as mysql_span:
                                mysql_span.set_tag("message.title", article.get('title', 'unknown'))
                                if save_test_message_to_mysql(article):
                                    print("✅ Test message saved to MySQL successfully")
                                    mysql_span.set_tag("save.status", "success")
                                else:
                                    print("❌ Failed to save test message to MySQL")
                                    mysql_span.set_tag("save.status", "failed")
                            
                            # 통계 업데이트 (테스트 메시지도 처리 카운트에 포함)
                            stats.update_processed(article, {"summary_ko": "Test message processed", "impact_ko": "Monitoring test"})
                            print(f"✅ 테스트 메시지 처리 완료 - 총 {stats.total_processed}개 처리됨")
                        else:
                            # 일반 뉴스 메시지 처리
                            span.set_tag("message.type", "news")
                            article_id = article.get('_id') or hashlib.md5(article['link'].encode()).hexdigest()
                            
                            with tracer.trace("openai.summary.generate", service="news-consumer") as ai_span:
                                ai_span.set_tag("article.id", article_id)
                                ai_span.set_tag("article.title", article.get('title', 'unknown'))
                                prompt = build_prompt(article)
                                summary = call_openai(prompt)
                            
                            with tracer.trace("mongo.summary.save", service="news-consumer") as mongo_span:
                                mongo_span.set_tag("article.id", article_id)
                                save_summary_to_mongo(collection, article_id, summary)
                            
                            # 통계 업데이트
                            stats.update_processed(article, summary)
                            print(f"✅ 일반 뉴스 처리 완료 - 총 {stats.total_processed}개 처리됨")
                    
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
