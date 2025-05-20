from apscheduler.schedulers.background import BackgroundScheduler
from crawler.google_news import fetch_google_news
from db.mongodb import insert_news

def crawl_and_store():
    print("[INFO] Running scheduled news fetch...")
    news_items = fetch_google_news()
    insert_news(news_items)

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(crawl_and_store, 'interval', hours=1)
    scheduler.start()

    print("[INIT] App started — running initial crawl...")
    crawl_and_store()