#!/usr/bin/env python3
"""
키워드 추출 기능 테스트 스크립트
"""

import sys
import os

# 현재 디렉토리를 Python path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def test_basic_extraction():
    """기본 키워드 추출 테스트"""
    try:
        from db.keyword_manager import extract_keywords
        
        test_text = "Datadog는 클라우드 모니터링 솔루션을 제공하는 회사입니다. AI와 머신러닝 기술을 활용한 새로운 서비스가 출시되었습니다."
        
        print(f"테스트 텍스트: {test_text}")
        keywords = extract_keywords(test_text)
        print(f"추출된 키워드: {keywords}")
        
        return True
    except Exception as e:
        print(f"키워드 추출 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mongodb_connection():
    """MongoDB 연결 테스트"""
    try:
        from pymongo import MongoClient
        import os
        
        MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        client = MongoClient(MONGO_URI)
        
        # 연결 테스트
        client.admin.command('ping')
        print("✅ MongoDB 연결 성공")
        
        # 뉴스 데이터 확인
        collection = client["bitsfeed"]["news"]
        count = collection.count_documents({})
        print(f"📰 뉴스 데이터: {count}개")
        
        return client, count
    except Exception as e:
        print(f"❌ MongoDB 연결 실패: {e}")
        return None, 0

def test_keyword_initialization():
    """키워드 초기화 테스트"""
    try:
        from db.keyword_manager import initialize_keyword_system
        
        print("🚀 키워드 시스템 초기화 시작...")
        result = initialize_keyword_system()
        print(f"✅ 초기화 결과: {result}")
        
        return True
    except Exception as e:
        print(f"❌ 키워드 초기화 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔍 키워드 추출 테스트 시작\n")
    
    # 1. 기본 키워드 추출 테스트
    print("1. 기본 키워드 추출 테스트")
    extraction_ok = test_basic_extraction()
    print()
    
    # 2. MongoDB 연결 테스트
    print("2. MongoDB 연결 테스트")
    client, news_count = test_mongodb_connection()
    print()
    
    # 3. 키워드 시스템 초기화 테스트
    if client and news_count > 0 and extraction_ok:
        print("3. 키워드 시스템 초기화 테스트")
        init_ok = test_keyword_initialization()
        print()
        
        if init_ok:
            # 4. 결과 확인
            print("4. 키워드 데이터 확인")
            try:
                keywords_collection = client["bitsfeed"]["keywords"]
                keyword_count = keywords_collection.count_documents({})
                print(f"✅ 키워드 데이터: {keyword_count}개")
                
                if keyword_count > 0:
                    # 상위 키워드 5개 출력
                    top_keywords = list(keywords_collection.find({}).sort("frequency", -1).limit(5))
                    print("🔝 상위 키워드 5개:")
                    for i, kw in enumerate(top_keywords, 1):
                        print(f"  {i}. {kw.get('keyword')}: {kw.get('frequency')}회")
                
            except Exception as e:
                print(f"❌ 키워드 데이터 확인 실패: {e}")
    else:
        print("⚠️ 전제 조건이 충족되지 않아 키워드 초기화를 건너뜁니다.")
        if not client:
            print("  - MongoDB 연결 실패")
        if news_count == 0:
            print("  - 뉴스 데이터 없음")
        if not extraction_ok:
            print("  - 키워드 추출 기능 오류")

if __name__ == "__main__":
    main() 