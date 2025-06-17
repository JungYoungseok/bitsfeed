#!/usr/bin/env python3
"""
키워드 데이터 업데이트 스크립트
"""

import sys
import os

# 현재 디렉토리를 Python path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def main():
    try:
        from db.keyword_manager import update_keyword_data
        
        print('🔄 키워드 데이터 업데이트 시작...')
        result = update_keyword_data()
        print(f'✅ 업데이트 완료: {result}')
        
    except Exception as e:
        print(f'❌ 업데이트 실패: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 