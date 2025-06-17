#!/usr/bin/env python3
"""
영어 키워드 추출 테스트 스크립트
"""

import sys
import os

# 현재 디렉토리를 Python path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def test_english_keyword_extraction():
    """영어 키워드 추출 테스트"""
    try:
        from db.keyword_manager import extract_english_keywords, process_article_keywords
        
        # 테스트 영어 텍스트들
        test_texts = [
            "Datadog Inc. (NASDAQ:DDOG) Upgraded at Wolfe Research - MarketBeat",
            "US tech firm Datadog sets up Bengaluru office to drive Asia-Pacific expansion",
            "Datadog director Amit Agarwal sells $2.99 million in stock",
            "Datadog DASH 2025: Autonomous Agents Transform IT Observability Operations",
            "Learn how Datadog developed an integration between OpenAI's Codex CLI and our new MCP server"
        ]
        
        print("🧪 영어 키워드 추출 테스트:")
        for i, text in enumerate(test_texts, 1):
            keywords = extract_english_keywords(text)
            print(f"  {i}. '{text[:50]}...'")
            print(f"     키워드: {keywords}")
            print()
        
        # 실제 기사 데이터로 테스트
        test_articles = [
            {
                "title": "Datadog (NASDAQ:DDOG) Given New $140.00 Price Target at Needham & Company LLC",
                "summary_ko": "Needham & Company LLC는 Datadog에 대한 목표 주가를 $140로 제시했다.",
                "impact_ko": "이 소식은 Datadog의 주가에 긍정적인 영향을 미칠 것으로 예상된다.",
                "summary": "Needham & Company LLC has set a new price target of $140 for Datadog stock."
            },
            {
                "title": "US tech firm Datadog sets up Bengaluru office to drive Asia-Pacific expansion",
                "summary_ko": "미국 기반의 클라우드 모니터링 솔루션 기업인 Datadog가 아시아-태평양 지역 확장을 위해 인도의 벵갈루루에 사무실을 설립했다.",
                "impact_ko": "Datadog의 아시아-태평양 지역 진출로 인한 영향을 보여준다.",
                "summary": "Datadog establishes new office in Bengaluru to accelerate growth in Asia-Pacific markets."
            }
        ]
        
        print("📰 실제 기사 키워드 추출 테스트:")
        for i, article in enumerate(test_articles, 1):
            keywords = process_article_keywords(article)
            print(f"  {i}. 제목: {article['title'][:50]}...")
            print(f"     추출된 키워드: {keywords}")
            print()
        
        return True
    except Exception as e:
        print(f"❌ 영어 키워드 추출 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔍 영어 키워드 추출 테스트 시작\n")
    
    success = test_english_keyword_extraction()
    
    if success:
        print("✅ 영어 키워드 추출 테스트 성공!")
    else:
        print("❌ 영어 키워드 추출 테스트 실패!")

if __name__ == "__main__":
    main() 