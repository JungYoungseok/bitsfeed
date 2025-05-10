from fastapi import FastAPI
from crawler.google_news import fetch_google_news
from db.mongodb import insert_news, get_all_news

app = FastAPI()

@app.get("/")
def root():
    return {"message": "👋 Hello from Datadog News Crawler!!!!!!!"}

@app.get("/news")
def list_news():
    return get_all_news()

@app.post("/crawl")
def crawl_news():
    news_items = fetch_google_news()
    insert_news(news_items)
    return {"inserted": len(news_items)}
