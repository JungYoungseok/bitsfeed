#!/bin/bash

echo "🎯 Bitsfeed Kafka 테스트 통합 모니터링 대시보드"
echo "=============================================="
echo "Ctrl+C로 종료하세요"
echo ""

while true; do
    # 화면 클리어
    clear
    
    echo "🎯 Bitsfeed Kafka 테스트 통합 모니터링 대시보드"
    echo "=============================================="
    echo "📅 $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    
    # Consumer 통계
    echo "📊 CONSUMER 통계"
    echo "=================="
    consumer_response=$(curl -s http://localhost:8002/stats 2>/dev/null)
    if [ $? -eq 0 ] && command -v jq &> /dev/null; then
        processed=$(echo "$consumer_response" | jq -r '.total_processed // "N/A"')
        errors=$(echo "$consumer_response" | jq -r '.total_errors // "N/A"')
        success_rate=$(echo "$consumer_response" | jq -r '.success_rate // "N/A"')
        last_message=$(echo "$consumer_response" | jq -r '.last_message // "N/A"')
        uptime=$(echo "$consumer_response" | jq -r '.uptime_human // "N/A"')
        kafka_status=$(echo "$consumer_response" | jq -r '.kafka_status // "N/A"')
        
        echo "✅ 총 처리: $processed개"
        echo "❌ 오류: $errors개" 
        echo "📈 성공률: $success_rate%"
        echo "🕐 가동시간: $uptime"
        echo "🔗 Kafka 상태: $kafka_status"
        echo "📝 최신 메시지: $last_message"
    else
        echo "❌ Consumer 서비스 연결 실패"
    fi
    
    echo ""
    echo "🗄️ MYSQL 데이터"
    echo "================"
    mysql_response=$(curl -s http://localhost:8002/mysql-test 2>/dev/null)
    if [ $? -eq 0 ] && command -v jq &> /dev/null; then
        count=$(echo "$mysql_response" | jq -r '.test_message_count // "N/A"')
        latest_title=$(echo "$mysql_response" | jq -r '.latest_messages[0].title // "N/A"')
        latest_time=$(echo "$mysql_response" | jq -r '.latest_messages[0].received_at // "N/A"')
        
        echo "📊 저장된 테스트 메시지: $count개"
        echo "📝 최신 저장: $latest_title"
        echo "🕐 최신 시간: $latest_time"
    else
        echo "❌ MySQL 서비스 연결 실패"
    fi
    
    echo ""
    echo "🚀 서비스 상태"
    echo "=============="
    
    # 각 서비스 상태 확인
    services=(
        "http://localhost:8000:Backend Crawler"
        "http://localhost:8001:Analytics"
        "http://localhost:8002:News Consumer"  
        "http://localhost:5000/api/health:.NET API"
        "http://localhost:3000:Frontend"
    )
    
    for service in "${services[@]}"; do
        url=$(echo $service | cut -d: -f1-2)
        name=$(echo $service | cut -d: -f3)
        
        if curl -s -f "$url" > /dev/null 2>&1; then
            echo "✅ $name: 정상"
        else
            echo "❌ $name: 오류"
        fi
    done
    
    echo ""
    echo "🔄 자동 새로고침 중... (3초마다)"
    echo "=============================================="
    
    sleep 3
done