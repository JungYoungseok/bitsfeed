#!/bin/bash

echo "🗄️ MySQL 테스트 데이터 실시간 모니터링"
echo "=================================="
echo "Ctrl+C로 종료하세요"
echo ""

while true; do
    echo "⏰ $(date '+%H:%M:%S') - MySQL 테스트 메시지 현황"
    
    # MySQL 테스트 데이터 개수 및 최신 메시지 조회
    response=$(curl -s http://localhost:8002/mysql-test 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        # jq가 있는 경우 JSON 파싱, 없으면 raw 출력
        if command -v jq &> /dev/null; then
            count=$(echo "$response" | jq -r '.test_message_count // "N/A"')
            latest_title=$(echo "$response" | jq -r '.latest_messages[0].title // "N/A"')
            latest_time=$(echo "$response" | jq -r '.latest_messages[0].received_at // "N/A"')
            
            echo "📊 총 저장된 테스트 메시지: $count개"
            echo "📝 최신 메시지: $latest_title"
            echo "🕐 최신 처리 시간: $latest_time"
        else
            echo "📊 MySQL 응답 (jq 설치 권장):"
            echo "$response" | head -3
        fi
    else
        echo "❌ MySQL 서비스 연결 실패"
    fi
    
    echo "--------------------------------"
    sleep 3
done