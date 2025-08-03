from fastapi import FastAPI
import asyncio
from crawler.google_news import fetch_google_news
from db.mongodb import insert_news, get_all_news
from fastapi.middleware.cors import CORSMiddleware
from crawler.scheduler import start_scheduler, crawl_all_news
from api.test_consume import router as test_consume_router
from crawler.rss import fetch_datadog_rss

try:
    from fastapi import FastAPI
    app = FastAPI(
        title="Datadog News Crawler",
        description="뉴스 크롤링 및 수집 전용 서비스",
        version="1.0.0"
    )
except Exception as e:
    print("❌ FastAPI 로딩 실패:", e)
    raise e

# 글로벌 스케줄러 변수
scheduler = None

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 크롤링 관련 라우터만 등록
app.include_router(test_consume_router)

# 앱 시작 시 스케줄러 자동 실행
@app.on_event("startup")
async def startup_event():
    """앱 시작 시 뉴스 크롤링 스케줄러 시작"""
    global scheduler
    print("[STARTUP] Starting news crawler scheduler...")
    scheduler = start_scheduler()

@app.get("/")
def root():
    return {
        "service": "Datadog News Crawler",
        "version": "1.0.1", 
        "description": "뉴스 크롤링 및 수집 전용 마이크로서비스",
        "build_info": "GitHub Actions Build Test 🚀",
        "last_updated": "2024-01-30",
        "endpoints": {
            "crawl": "/crawl",
            "news": "/news",
            "scheduler": "/scheduler/*",
            "hello": "/hello"
        },
        "analytics_service": "http://datadog-analytics:8001"
    }

@app.get("/hello")
def hello():
    return {"message": "👋 Hello from Datadog News Crawler! (Lightweight & Fast)"}

@app.get("/news")
def list_news():
    return get_all_news()

@app.post("/crawl")
def crawl_news():
    """수동으로 뉴스 크롤링을 실행하는 엔드포인트"""
    all_news = []

    google_news = fetch_google_news()
    rss_news = fetch_datadog_rss()

    all_news.extend(google_news)
    all_news.extend(rss_news)

    insert_news(all_news)

    return {"message": f"Inserted {len(all_news)} news items"}

@app.post("/crawl/immediate")
def crawl_immediate():
    """즉시 스케줄된 크롤링 함수를 실행"""
    try:
        crawl_all_news()
        return {"message": "Immediate news crawling completed successfully"}
    except Exception as e:
        return {"error": f"Failed to run immediate crawl: {str(e)}"}

@app.get("/scheduler/status")
def get_scheduler_status():
    """스케줄러 상태 확인"""
    global scheduler
    if scheduler is None:
        return {"status": "not_started", "message": "Scheduler not initialized"}
    
    if scheduler.running:
        jobs = []
        for job in scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "func": job.func.__name__,
                "trigger": str(job.trigger),
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None
            })
        return {
            "status": "running",
            "message": "Scheduler is active",
            "jobs": jobs
        }
    else:
        return {"status": "stopped", "message": "Scheduler is not running"}

@app.post("/kafka-test")
def start_kafka_test():
    """Datadog Data Streams Monitoring 테스트를 위한 Kafka Producer"""
    import threading
    import time
    import uuid
    from datetime import datetime
    from confluent_kafka import Producer
    import os
    import json
    
    def kafka_test_producer():
        """1분 동안 2-3초마다 테스트 메시지를 전송하는 producer"""
        producer = Producer({
            'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
            'client.id': 'datadog-test-producer'
        })
        
        def delivery_report(err, msg):
            if err is not None:
                print(f'❌ Message delivery failed: {err}')
            else:
                print(f'✅ Test message delivered to {msg.topic()} [{msg.partition()}]')
        
        # 30초 동안 3초 간격으로 10개 메시지 전송
        start_time = datetime.now()
        message_count = 0
        
        try:
            while (datetime.now() - start_time).seconds < 30:
                message_count += 1
                test_message = {
                    "_id": f"test_{uuid.uuid4().hex[:8]}",
                    "title": f"📊 Data Streams Monitoring Test Message #{message_count}",
                    "link": f"https://test.datadog.com/test-{message_count}",
                    "source": "Datadog Test Producer",
                    "published": datetime.now().isoformat(),
                    "content": f"This is a test message for Datadog Data Streams Monitoring. Message #{message_count} sent at {datetime.now().strftime('%H:%M:%S')}",
                    "test_metadata": {
                        "test_type": "data_streams_monitoring",
                        "message_id": message_count,
                        "producer": "datadog-crawler",
                        "consumer": "news-consumer",
                        "target_table": "kafka_test_logs"
                    }
                }
                
                producer.produce(
                    'news_raw',
                    key=f"test-{message_count}",
                    value=json.dumps(test_message),
                    callback=delivery_report
                )
                
                producer.poll(0)  # Trigger any available delivery report callbacks
                print(f"🚀 Sent test message #{message_count} at {datetime.now().strftime('%H:%M:%S')}")
                
                time.sleep(3)  # 3초 대기
                
        except Exception as e:
            print(f"❌ Kafka test producer error: {e}")
        finally:
            producer.flush()  # Wait for all messages to be delivered
            print(f"✅ Kafka test completed. Sent {message_count} messages.")
    
    # 백그라운드에서 producer 실행
    producer_thread = threading.Thread(target=kafka_test_producer, daemon=True)
    producer_thread.start()
    
    return {
        "message": "🚀 Kafka Data Streams Monitoring 테스트가 시작되었습니다.",
        "details": {
            "duration": "30초",
            "interval": "3초마다",
            "topic": "news_raw",
            "expected_messages": "약 10개",
            "producer": "datadog-crawler",
            "consumer": "news-consumer"
        },
        "monitoring": "Datadog Data Streams Monitoring에서 실시간 데이터 플로우를 확인하세요."
    }