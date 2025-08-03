#!/bin/bash

echo "📊 Consumer 통계 실시간 모니터링"
echo "==============================="
echo "Ctrl+C로 종료하세요"
echo ""

while true; do
    echo "⏰ $(date '+%H:%M:%S') - Consumer 처리 현황"
    
    # Consumer 통계 조회
    response=$(curl -s http://localhost:8002/stats 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        if command -v jq &> /dev/null; then
            processed=$(echo "$response" | jq -r '.total_processed // "N/A"')
            errors=$(echo "$response" | jq -r '.total_errors // "N/A"')
            success_rate=$(echo "$response" | jq -r '.success_rate // "N/A"')
            last_message=$(echo "$response" | jq -r '.last_message // "N/A"')
            last_time=$(echo "$response" | jq -r '.last_processed_time // "N/A"')
            uptime=$(echo "$response" | jq -r '.uptime_human // "N/A"')
            kafka_status=$(echo "$response" | jq -r '.kafka_status // "N/A"')
            
            echo "✅ 총 처리: $processed개 | ❌ 오류: $errors개 | 📈 성공률: $success_rate%"
            echo "🕐 가동시간: $uptime | 🔗 Kafka 상태: $kafka_status"
            echo "📝 최신 메시지: $last_message"
            echo "🕐 최근 처리: $last_time"
        else
            echo "📊 Consumer 응답 (jq 설치 권장):"
            echo "$response" | head -5
        fi
    else
        echo "❌ Consumer 서비스 연결 실패"
    fi
    
    echo "--------------------------------"
    sleep 2
done