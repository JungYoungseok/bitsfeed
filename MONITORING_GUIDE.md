# 🔍 Kafka 테스트 실시간 모니터링 가이드

## 📋 개요
로컬 환경에서 Kafka Data Streams Monitoring 테스트를 실시간으로 모니터링할 수 있는 도구들입니다.

## 🚀 빠른 시작

### 1. Kafka 테스트 실행
```bash
# 🎯 30초 테스트 + 결과 비교 (추천)
./kafka_test_with_diff.sh

# 웹 UI에서 실행
open http://localhost:3000  # "🚀 Kafka 테스트" 버튼 클릭

# 또는 기본 테스트만
./start_kafka_test.sh
```

### 2. 실시간 모니터링 시작
```bash
# 🎯 통합 대시보드 (추천)
./monitor_all.sh

# 📊 Consumer 통계만
./monitor_consumer.sh

# 🗄️ MySQL 데이터만
./monitor_mysql.sh
```

## 📊 모니터링 화면 설명

### 통합 대시보드 (monitor_all.sh)
- **Consumer 통계**: 처리된 메시지 수, 성공률, 가동시간
- **MySQL 데이터**: 저장된 테스트 메시지 개수, 최신 메시지
- **서비스 상태**: 모든 마이크로서비스 상태 확인
- **자동 새로고침**: 3초마다 업데이트

### Consumer 통계 (monitor_consumer.sh)
- 총 처리 메시지 수
- 오류 수 및 성공률
- 최신 처리된 메시지
- Kafka 연결 상태
- 2초마다 업데이트

### MySQL 데이터 (monitor_mysql.sh)
- 저장된 테스트 메시지 총 개수
- 최신 저장된 메시지 제목
- 최근 처리 시간
- 3초마다 업데이트

## 📋 실시간 로그 보기

### Producer 로그 (메시지 전송)
```bash
docker-compose logs -f backend
```
**확인 내용:**
- `🚀 Sent test message #N` - 메시지 전송
- `✅ Test message delivered` - 전송 성공

### Consumer 로그 (메시지 처리)
```bash
docker-compose logs -f news-consumer
```
**확인 내용:**
- `🧪 Test message detected` - 테스트 메시지 감지
- `✅ 테스트 메시지 저장됨` - MySQL 저장 성공
- `✅ 테스트 메시지 처리 완료` - 처리 완료

## 🌐 웹 UI 모니터링

### 브라우저에서 확인
- **메인 페이지**: http://localhost:3000
- **Consumer 상태**: http://localhost:3000/api/consumer/status
- **MySQL 테스트**: http://localhost:8002/mysql-test
- **Consumer 통계**: http://localhost:8002/stats
- **.NET Health**: http://localhost:3000/api/dotnet/health

## 🔧 트러블슈팅

### jq 명령어 설치 (JSON 파싱용)
```bash
# macOS
brew install jq

# Ubuntu/Debian
sudo apt-get install jq

# 설치하지 않아도 동작하지만, 보기 어려운 JSON으로 출력됩니다
```

### 서비스 상태 확인
```bash
docker-compose ps
```

### 서비스 재시작
```bash
docker-compose restart [service-name]
```

## 📈 테스트 플로우

1. **테스트 시작**: 웹 UI 또는 `start_kafka_test.sh`
2. **메시지 전송**: Backend Producer가 60초간 3초마다 전송
3. **실시간 처리**: Consumer가 즉시 감지하여 처리
4. **MySQL 저장**: 테스트 메시지만 별도 테이블에 저장
5. **통계 업데이트**: 실시간 통계 갱신

## ⚡ 성능 지표

- **처리 속도**: 평균 3초 간격으로 메시지 처리
- **성공률**: 97% 이상 목표
- **응답 시간**: 1초 이내 처리
- **저장률**: 100% MySQL 저장

## 🎯 모니터링 팁

1. **다중 터미널 사용**: 로그와 통계를 동시에 모니터링
2. **브라우저 개발자 도구**: 네트워크 탭에서 API 호출 확인
3. **Datadog**: 실제 Data Streams Monitoring에서 실시간 추적
4. **알림음**: 시스템 알림으로 테스트 완료 확인

---
🎉 **Happy Monitoring!** 문제가 있으면 docker-compose logs로 상세 로그를 확인하세요.