import feedparser
import schedule
import time
from bs4 import BeautifulSoup
from datetime import datetime
import urllib.parse
from dateutil import parser
import requests
   
def resolve_redirect_url(google_link: str) -> str:
    try:
        res = requests.get(google_link, timeout=5, allow_redirects=True)
        return res.url
    except Exception as e:
        print(f"⚠️ 링크 추적 실패: {e}")
        return google_link  # 실패 시 원본 링크 fallback

def fetch_google_news():
    query = "Datadog"
    rss_url = f"https://news.google.com/rss/search?q={query}+when:1d&hl=en-NG&gl=US&ceid=NG:en"

    feed = feedparser.parse(rss_url)
    print(f"\n[Datadog 뉴스 업데이트 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
    
    results = []
    for entry in feed.entries[:5]:  # 최근 5개만 출력
        title = entry.title
        original_link = entry.link
        resolved_link = resolve_redirect_url(original_link)  # ✅ 여기서 실제 기사 링크로 변환
        published = parser.parse(entry.published)
        source = source = entry.source.title

        print(f"{published} | {title} | {source} | {resolved_link}")
        results.append({
            "published": published,
            "title": title,
            "source": source,
            "link": resolved_link,
            "scraped_at": datetime.utcnow().isoformat()        
        })
        # article_content = extract_article_text(resolved_link)
        # print("extract_article_text: " + article_content)

    print(results)
    return results

fetch_google_news()