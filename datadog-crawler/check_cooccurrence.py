#!/usr/bin/env python3
"""
키워드 동시출현 데이터 확인 스크립트
"""

import sys
import os
from pymongo import MongoClient

# 현재 디렉토리를 Python path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def main():
    try:
        MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
        client = MongoClient(MONGO_URI)
        cooccurrence_collection = client['bitsfeed']['keyword_cooccurrence']

        print('🔍 동시출현 데이터 샘플:')
        samples = list(cooccurrence_collection.find({}).sort('count', -1).limit(10))
        for i, item in enumerate(samples, 1):
            print(f'{i}. {item["keyword1"]} + {item["keyword2"]}: {item["count"]}회')

        total_count = cooccurrence_collection.count_documents({})
        min2_count = cooccurrence_collection.count_documents({"count": {"$gte": 2}})
        min1_count = cooccurrence_collection.count_documents({"count": {"$gte": 1}})
        
        print(f'\n📊 통계:')
        print(f'총 동시출현 쌍: {total_count}개')
        print(f'최소 2회 이상: {min2_count}개')
        print(f'최소 1회 이상: {min1_count}개')
        
        # 네트워크 생성 테스트
        print(f'\n🌐 네트워크 생성 테스트:')
        from db.keyword_manager import get_keyword_network
        
        # 최소 1회로 테스트
        network_result = get_keyword_network(days=7, min_cooccurrence=1)
        if 'error' in network_result:
            print(f'❌ 네트워크 생성 실패 (min=1): {network_result["error"]}')
        else:
            print(f'✅ 네트워크 생성 성공 (min=1): 노드 {len(network_result.get("nodes", []))}개, 엣지 {len(network_result.get("edges", []))}개')
        
        # 최소 2회로 테스트
        network_result = get_keyword_network(days=7, min_cooccurrence=2)
        if 'error' in network_result:
            print(f'❌ 네트워크 생성 실패 (min=2): {network_result["error"]}')
        else:
            print(f'✅ 네트워크 생성 성공 (min=2): 노드 {len(network_result.get("nodes", []))}개, 엣지 {len(network_result.get("edges", []))}개')
        
    except Exception as e:
        print(f'❌ 오류: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 