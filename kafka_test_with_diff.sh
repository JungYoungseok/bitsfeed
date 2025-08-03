#!/bin/bash

echo "🚀 Kafka 테스트 실행 및 새로운 데이터 추적"
echo "=========================================="

# 1. 테스트 시작 전 MySQL 상태 확인
echo "📋 테스트 시작 전 상태 확인..."
before_response=$(curl -s http://localhost:8002/mysql-test 2>/dev/null)

if [ $? -eq 0 ] && command -v jq &> /dev/null; then
    before_count=$(echo "$before_response" | jq -r '.test_message_count // 0')
    echo "📊 현재 저장된 테스트 메시지: $before_count개"
else
    before_count=0
    echo "❌ MySQL 상태 확인 실패. 기본값 0으로 설정"
fi

echo ""

# 2. Kafka 테스트 실행
echo "🚀 30초 Kafka 테스트 시작..."
test_response=$(curl -s -X POST http://localhost:8000/kafka-test)

if [ $? -eq 0 ]; then
    echo "✅ 테스트 시작 성공!"
    if command -v jq &> /dev/null; then
        duration=$(echo "$test_response" | jq -r '.details.duration // "30초"')
        expected=$(echo "$test_response" | jq -r '.details.expected_messages // "약 10개"')
        echo "⏱️ 테스트 시간: $duration"
        echo "📨 예상 메시지: $expected"
    fi
else
    echo "❌ 테스트 시작 실패"
    exit 1
fi

echo ""
echo "⏳ 테스트 진행 중... (30초 대기)"
echo "   실시간 모니터링을 원하면 다른 터미널에서:"
echo "   ./monitor_consumer.sh"

# 3. 30초 + 5초 버퍼 대기 (메시지 처리 완료 시간 고려)
sleep 35

echo ""
echo "✅ 테스트 완료! 결과 분석 중..."

# 4. 테스트 후 MySQL 상태 확인
after_response=$(curl -s http://localhost:8002/mysql-test 2>/dev/null)

if [ $? -eq 0 ] && command -v jq &> /dev/null; then
    after_count=$(echo "$after_response" | jq -r '.test_message_count // 0')
    new_messages=$((after_count - before_count))
    
    echo ""
    echo "🎯 테스트 결과 요약"
    echo "==================="
    echo "📊 테스트 전: $before_count개"
    echo "📊 테스트 후: $after_count개"
    echo "🆕 새로 추가: $new_messages개"
    
    if [ $new_messages -gt 0 ]; then
        echo ""
        echo "🆕 새로 추가된 테스트 메시지들:"
        echo "================================"
        
        # 새로 추가된 메시지들만 표시 (최신 순으로)
        latest_messages=$(echo "$after_response" | jq -r ".latest_messages[:$new_messages][]")
        
        counter=1
        echo "$after_response" | jq -r ".latest_messages[:$new_messages][] | 
            \"📝 메시지 $counter: \" + .title + 
            \"\\n🕐 처리 시간: \" + .received_at + 
            \"\\n🆔 ID: \" + .message_id + 
            \"\\n\" + \"─────────────────────────────────────\"" 2>/dev/null || {
            
            # jq 파싱 실패 시 간단한 출력
            echo "$after_response" | head -20
        }
        
        echo ""
        echo "🎉 테스트 성공! $new_messages개의 새로운 메시지가 MySQL에 저장되었습니다."
        
    else
        echo ""
        echo "⚠️ 새로 추가된 메시지가 없습니다."
        echo "   Consumer 로그를 확인해보세요: docker-compose logs news-consumer"
    fi
    
else
    echo "❌ 테스트 후 상태 확인 실패"
fi

echo ""
echo "📊 실시간 통계 확인:"
echo "   curl http://localhost:8002/stats | jq '.'"
echo ""
echo "🔍 전체 모니터링:"
echo "   ./monitor_all.sh"