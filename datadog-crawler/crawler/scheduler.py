from apscheduler.schedulers.background import BackgroundScheduler
from crawler.google_news import fetch_google_news
from crawler.rss import fetch_datadog_rss
from db.mongodb import insert_news
import atexit
from datetime import datetime

def crawl_all_news():
    """Google 뉴스와 RSS를 모두 크롤링하는 함수"""
    print(f"[INFO] Running scheduled news crawl at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_news = []
    
    try:
        # Google 뉴스 크롤링
        google_news = fetch_google_news()
        all_news.extend(google_news)
        print(f"[INFO] Fetched {len(google_news)} Google news items")
        
        # RSS 뉴스 크롤링
        rss_news = fetch_datadog_rss()
        all_news.extend(rss_news)
        print(f"[INFO] Fetched {len(rss_news)} RSS news items")
        
        # MongoDB에 저장
        if all_news:
            insert_news(all_news)
            print(f"[INFO] Successfully processed {len(all_news)} total news items")
        else:
            print("[INFO] No new news items to process")
            
    except Exception as e:
        print(f"[ERROR] Failed to crawl news: {e}")

def start_scheduler():
    """스케줄러 시작 - 2시간마다 뉴스 크롤링 실행"""
    scheduler = BackgroundScheduler()
    
    # 2시간마다 실행
    scheduler.add_job(
        crawl_all_news, 
        'interval', 
        hours=2,
        id='news_crawler',
        replace_existing=True
    )
    
    scheduler.start()
    print("[INIT] News crawler scheduler started - running every 2 hours")
    
    # 앱 시작 시 즉시 한 번 실행
    print("[INIT] Running initial news crawl...")
    crawl_all_news()
    
    # 앱 종료 시 스케줄러도 종료
    atexit.register(lambda: scheduler.shutdown())
    
    return scheduler