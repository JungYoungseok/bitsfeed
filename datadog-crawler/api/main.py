from fastapi import FastAPI
import asyncio
from crawler.google_news import fetch_google_news
from db.mongodb import insert_news, get_all_news
from fastapi.middleware.cors import CORSMiddleware
from crawler.scheduler import start_scheduler, crawl_all_news
from api.test_consume import router as test_consume_router
from api.analytics import router as analytics_router
from api.visualization import router as visualization_router
from crawler.rss import fetch_datadog_rss

try:
    from fastapi import FastAPI
    app = FastAPI()
except Exception as e:
    print("❌ FastAPI 로딩 실패:", e)
    raise e

# 글로벌 스케줄러 변수
scheduler = None

#app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(test_consume_router)
app.include_router(analytics_router, prefix="/analytics")
app.include_router(visualization_router, prefix="/viz")

# 앱 시작 시 스케줄러 자동 실행
@app.on_event("startup")
async def startup_event():
    """앱 시작 시 뉴스 크롤링 스케줄러 시작"""
    global scheduler
    print("[STARTUP] Starting news crawler scheduler...")
    scheduler = start_scheduler()

@app.get("/hello")
def hello():
    return {"message": "👋 Hello from Datadog News Crawler!!!!!!!"}

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

# 매일 오전 9시에 실행
# schedule.every().day.at("09:00").do(fetch_google_news)
# while True:
#     schedule.run_pending()
#     time.sleep(60)