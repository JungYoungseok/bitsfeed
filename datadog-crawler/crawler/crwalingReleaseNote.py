import requests
import os
import re
from bs4 import BeautifulSoup

API_URL = "https://api.github.com/repos/DataDog/datadog-agent/releases/latest"
VERSION_FILE = "last_api_release.txt"

def extract_bug_fixes(body_text):
    """
    '## Bug Fixes' 섹션부터 다음 제목(# 또는 ## 등)까지 추출 (HTML 제거 포함)
    """
    # Bug Fixes 섹션 추출
    match = re.search(r"## Bug Fixes\s*(.*?)(\n#+\s|$)", body_text, re.DOTALL)
    if not match:
        return "No 'Bug Fixes' section found."

    raw_section = match.group(1).strip()

    # HTML 제거
    soup = BeautifulSoup(raw_section, "html.parser")
    text_only = soup.get_text().strip()
    return text_only

def fetch_latest_release():
    headers = {"Accept": "application/vnd.github+json"}
    response = requests.get(API_URL, headers=headers,timeout=5)
    data = response.json()

    latest_tag = data.get("tag_name")
    release_name = data.get("name", "(no title)")
    html_url = data.get("html_url")
    published_at = data.get("published_at")
    body = data.get("body", "")

    if not latest_tag:
        print("릴리스 정보를 가져올 수 없습니다.")
        return

    # 이전 버전 비교
    last_seen = None
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, 'r') as f:
            last_seen = f.read().strip()

    if latest_tag == last_seen:
        print(f"\n[새 릴리스] {release_name} ({latest_tag}) - {published_at}")
        print(f"🔗 {html_url}\n")
        bug_fixes = extract_bug_fixes(body)
        print("🐛 Bug Fixes:")
        print(bug_fixes)
        with open(VERSION_FILE, 'w') as f:
            f.write(latest_tag)
    else:
        print(f"[변경 없음] 최신 릴리스: {latest_tag}")

# 이 스크립트는 현재 사용하지 않습니다 (APScheduler 사용)
# 매일 오전 9시 실행
# schedule.every().day.at("09:00").do(fetch_latest_release)
# schedule.every().day.at("15:00").do(fetch_latest_release)

# 테스트용 수동 실행
# fetch_latest_release()

# while True:
#     schedule.run_pending()
#     time.sleep(60)
