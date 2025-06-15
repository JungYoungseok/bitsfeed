import feedparser
from hashlib import md5
from datetime import datetime

def fetch_datadog_rss(limit=5):
    rss_url = "https://www.datadoghq.com/blog/index.xml"
    feed = feedparser.parse(rss_url)

    news_items = []
    for entry in feed.entries[:limit]:
        item = {
            "_id": md5(entry.link.encode('utf-8')).hexdigest(),
            "title": entry.title,
            "summary": entry.summary,
            "link": entry.link,
            "published": datetime(*entry.published_parsed[:6]),
            "source": "datadog-blog"
        }
        news_items.append(item)

    return news_items
