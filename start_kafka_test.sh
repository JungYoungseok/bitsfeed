#!/bin/bash

echo "🚀 Kafka Data Streams Monitoring 테스트 시작"
echo "==========================================="

# Kafka 테스트 실행
echo "📤 테스트 메시지 전송 시작..."
response=$(curl -s -X POST http://localhost:8000/kafka-test)

if [ $? -eq 0 ]; then
    echo "✅ 테스트 시작됨!"
    if command -v jq &> /dev/null; then
        echo "$response" | jq '.'
    else
        echo "$response"
    fi
    
    echo ""
    echo "🔍 실시간 모니터링을 시작하려면:"
    echo "   ./monitor_all.sh         # 통합 대시보드"
    echo "   ./monitor_consumer.sh    # Consumer 통계만"
    echo "   ./monitor_mysql.sh       # MySQL 데이터만"
    echo ""
    echo "🆕 테스트 완료 후 새로운 데이터 확인:"
    echo "   ./kafka_test_with_diff.sh # 30초 테스트 + 결과 비교"
    echo ""
    echo "📋 로그 확인:"
    echo "   docker-compose logs -f backend       # Producer 로그"
    echo "   docker-compose logs -f news-consumer # Consumer 로그"
    
else
    echo "❌ 테스트 시작 실패"
    echo "서비스가 실행 중인지 확인하세요: docker-compose ps"
fi