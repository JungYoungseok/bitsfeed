from fastapi import FastAPI
from crawler.google_news import fetch_google_news
from db.mongodb import insert_news, get_all_news
from fastapi.middleware.cors import CORSMiddleware
from crawler.scheduler import start_scheduler
# import schedule
# import time

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    start_scheduler()  # ✅ 매시간 자동 실행 등록

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