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
        "version": "1.0.0", 
        "description": "뉴스 크롤링 및 수집 전용 마이크로서비스",
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