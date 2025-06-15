from fastapi import FastAPI
import asyncio
from crawler.google_news import fetch_google_news
from db.mongodb import insert_news, get_all_news
from fastapi.middleware.cors import CORSMiddleware
from crawler.scheduler import start_scheduler
from api.test_consume import router as test_consume_router
from crawler.rss import fetch_datadog_rss

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

@app.get("/hello")
def hello():
    return {"message": "👋 Hello from Datadog News Crawler!!!!!!"}

@app.get("/news")
def list_news():
    return get_all_news()

@app.post("/crawl")
def crawl_news():
    all_news = []

    google_news = fetch_google_news()
    rss_news = fetch_datadog_rss()

    all_news.extend(google_news)
    all_news.extend(rss_news)

    insert_news(all_news)

    return {"message": f"Inserted {len(all_news)} news items"}

# 매일 오전 9시에 실행
# schedule.every().day.at("09:00").do(fetch_google_news)
# while True:
#     schedule.run_pending()
#     time.sleep(60)