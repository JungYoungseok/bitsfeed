import feedparser
import schedule
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import urllib.parse


def fetch_google_news():
    query = "Datadog"
    rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"

    feed = feedparser.parse(rss_url)
    print(f"\n[Datadog 뉴스 업데이트 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
    
    results = []
    for entry in feed.entries[:5]:  # 최근 5개만 출력
        title = entry.title
        link = entry.link
        published = entry.published
        print(f"{published} | {title} | {link}")
        results.append({
            "published": published,
            "title": title,
            "link": link,
            "scraped_at": datetime.utcnow().isoformat()
        })

    print(results)
    return results

# 매일 오전 9시에 실행
#schedule.every().day.at("09:00").do(fetch_google_news)

# 수동 실행 시 아래 주석 해제
fetch_google_news()

# while True:
#     schedule.run_pending()
#     time.sleep(60)