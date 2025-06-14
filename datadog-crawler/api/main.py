from fastapi import FastAPI
import asyncio
from crawler.google_news import fetch_google_news
from db.mongodb import insert_news, get_all_news
from fastapi.middleware.cors import CORSMiddleware
from crawler.scheduler import start_scheduler
from api.test_consume import router as test_consume_router
#from kafka.consumer_summary import run_summary_consumer


try:
    from fastapi import FastAPI
    app = FastAPI()
except Exception as e:
    print("❌ FastAPI 로딩 실패:", e)
    raise e

#app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(test_consume_router)


# @app.on_event("startup")
# async def startup_event():
#     start_scheduler()  # ✅ 매시간 자동 실행 등록
#     asyncio.create_task(run_summary_consumer())  # ✅ Kafka consumer 실행

@app.get("/hello")
def hello():
    return {"message": "👋 Hello from Datadog News Crawler!!!!!!"}

@app.get("/news")
def list_news():
    return get_all_news()

@app.post("/crawl")
def crawl_news():
    news_items = fetch_google_news()
    insert_news(news_items)
    return {"inserted": len(news_items)}

# 매일 오전 9시에 실행
# schedule.every().day.at("09:00").do(fetch_google_news)
# while True:
#     schedule.run_pending()
#     time.sleep(60)