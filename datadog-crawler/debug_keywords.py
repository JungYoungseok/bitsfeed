#!/usr/bin/env python3
"""
키워드 시스템 디버깅 스크립트
"""

import os
import sys
from pymongo import MongoClient
from datetime import datetime

# MongoDB 연결
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

def check_mongo_connection():
    """MongoDB 연결 확인"""
    try:
        client = MongoClient(MONGO_URI)
        # 연결 테스트
        client.admin.command('ping')
        print("✅ MongoDB 연결 성공")
        return client
    except Exception as e:
        print(f"❌ MongoDB 연결 실패: {e}")
        return None

def check_news_data(client):
    """뉴스 데이터 확인"""
    try:
        collection = client["bitsfeed"]["news"]
        count = collection.count_documents({})
        print(f"📰 뉴스 데이터: {count}개")
        
        if count > 0:
            # 최신 뉴스 3개 확인
            latest_news = list(collection.find({}).sort("published", -1).limit(3))
            print("\n📋 최신 뉴스 3개:")
            for i, news in enumerate(latest_news, 1):
                print(f"  {i}. {news.get('title', 'No title')[:50]}...")
                print(f"     발행일: {news.get('published', 'Unknown')}")
                print(f"     요약(ko): {news.get('summary_ko', 'None')[:30]}...")
                print(f"     영향(ko): {news.get('impact_ko', 'None')[:30]}...")
                print()
        return count
    except Exception as e:
        print(f"❌ 뉴스 데이터 확인 실패: {e}")
        return 0

def check_keyword_data(client):
    """키워드 데이터 확인"""
    try:
        keywords_collection = client["bitsfeed"]["keywords"]
        trends_collection = client["bitsfeed"]["keyword_trends"]
        cooccurrence_collection = client["bitsfeed"]["keyword_cooccurrence"]
        
        keyword_count = keywords_collection.count_documents({})
        trend_count = trends_collection.count_documents({})
        cooccurrence_count = cooccurrence_collection.count_documents({})
        
        print(f"🔍 키워드 데이터:")
        print(f"  - keywords: {keyword_count}개")
        print(f"  - trends: {trend_count}개")
        print(f"  - cooccurrence: {cooccurrence_count}개")
        
        if keyword_count > 0:
            top_keywords = list(keywords_collection.find({}).sort("frequency", -1).limit(5))
            print("\n🔝 상위 키워드 5개:")
            for i, kw in enumerate(top_keywords, 1):
                print(f"  {i}. {kw.get('keyword')}: {kw.get('frequency')}회")
        
        return keyword_count, trend_count, cooccurrence_count
    except Exception as e:
        print(f"❌ 키워드 데이터 확인 실패: {e}")
        return 0, 0, 0

def test_keyword_extraction():
    """키워드 추출 테스트"""
    try:
        # 현재 디렉토리를 Python path에 추가
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        from db.keyword_manager import extract_keywords, process_article_keywords
        
        # 테스트 텍스트
        test_texts = [
            "Datadog는 클라우드 모니터링 솔루션을 제공하는 회사입니다.",
            "AI와 머신러닝 기술을 활용한 새로운 서비스가 출시되었습니다.",
            "Docker와 Kubernetes를 이용한 컨테이너 오케스트레이션"
        ]
        
        print("\n🧪 키워드 추출 테스트:")
        for i, text in enumerate(test_texts, 1):
            keywords = extract_keywords(text)
            print(f"  {i}. '{text[:30]}...'")
            print(f"     키워드: {keywords}")
        
        # 테스트 기사 데이터
        test_article = {
            "title": "Datadog 새로운 AI 모니터링 기능 발표",
            "summary_ko": "Datadog이 인공지능을 활용한 새로운 모니터링 기능을 발표했습니다. 이 기능은 클라우드 환경에서 더 정확한 성능 분석을 제공합니다.",
            "impact_ko": "클라우드 모니터링 시장에서 Datadog의 경쟁력이 강화될 것으로 예상됩니다."
        }
        
        article_keywords = process_article_keywords(test_article)
        print(f"\n📰 테스트 기사 키워드: {article_keywords}")
        
        return True
    except Exception as e:
        print(f"❌ 키워드 추출 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def manual_keyword_initialization():
    """수동 키워드 초기화"""
    try:
        print("\n🚀 수동 키워드 초기화 시작...")
        
        # 현재 디렉토리를 Python path에 추가
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        from db.keyword_manager import initialize_keyword_system
        
        result = initialize_keyword_system()
        print(f"✅ 키워드 초기화 완료: {result}")
        return True
    except Exception as e:
        print(f"❌ 수동 키워드 초기화 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔍 키워드 시스템 디버깅 시작\n")
    
    # 1. MongoDB 연결 확인
    client = check_mongo_connection()
    if not client:
        return
    
    # 2. 뉴스 데이터 확인
    news_count = check_news_data(client)
    
    # 3. 키워드 데이터 확인
    keyword_count, trend_count, cooccurrence_count = check_keyword_data(client)
    
    # 4. 키워드 추출 테스트
    extraction_ok = test_keyword_extraction()
    
    print("\n" + "="*50)
    print("📊 진단 결과:")
    print(f"  - MongoDB 연결: {'✅' if client else '❌'}")
    print(f"  - 뉴스 데이터: {news_count}개")
    print(f"  - 키워드 데이터: {keyword_count}개")
    print(f"  - 키워드 추출: {'✅' if extraction_ok else '❌'}")
    
    # 5. 권장 사항
    print("\n💡 권장 사항:")
    if news_count == 0:
        print("  1. 먼저 뉴스 데이터를 수집하세요: curl -X POST http://localhost:8000/crawl")
    if keyword_count == 0 and news_count > 0:
        print("  2. 키워드 시스템을 초기화하세요.")
        
        # 자동 초기화 제안
        choice = input("\n❓ 지금 키워드 시스템을 초기화하시겠습니까? (y/N): ")
        if choice.lower() in ['y', 'yes']:
            manual_keyword_initialization()
            # 재확인
            check_keyword_data(client)

if __name__ == "__main__":
    main() 