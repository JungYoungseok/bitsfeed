# 🧪 Bitsfeed 실시간 통신 테스트 가이드

## 📋 **실행 중인 서비스 목록**

| 서비스 | 포트 | 용도 | 테스트 URL |
|--------|------|------|------------|
| **Frontend** | 3000 | 메인 웹 UI | http://localhost:3000 |
| **Backend** | 8000 | 뉴스 크롤러 API | http://localhost:8000 |
| **Analytics** | 8001 | 분석 서비스 | http://localhost:8001 |
| **Consumer** | 8002 | Kafka 컨슈머 | http://localhost:8002 |
| **🚀 .NET Sample** | 5000 | 실시간 통신 테스트 | http://localhost:5000 |
| **Datadog Agent** | 8126 | APM 수집 | http://localhost:8126 |

## 🎯 **1단계: 메인 서비스 테스트**

### 📱 **Frontend (Next.js)**
```bash
# 메인 대시보드 접속
open http://localhost:3000
```

**주요 기능:**
- 🔍 키워드 분석 → Datadog 뉴스 검색
- 📊 간단 차트 → 분석 시각화
- 🔧 Consumer 상태 → Kafka 처리 상태
- 🚀 .NET Health → dotnet-sample 상태
- 👥 .NET Users → 사용자 관리

### 🔧 **Backend Services API 테스트**
```bash
# 백엔드 서비스 상태 확인
curl http://localhost:8000

# 분석 서비스 상태 확인  
curl http://localhost:8001

# Consumer 서비스 상태 확인
curl http://localhost:8002
```

## 🔄 **2단계: 실시간 통신 패턴 테스트**

### 🧪 **실시간 테스트 UI 접속**
```bash
# 통합 테스트 페이지 오픈
open http://localhost:5000/realtime-test.html
```

**4가지 실시간 패턴 테스트:**

#### 📱 **1. SignalR Hub (/hub)**
- **목적**: GET /hub 패턴 재현
- **테스트**: 
  1. "Connect to Hub" 클릭
  2. "Send Heartbeat" 클릭
  3. 실시간 메시지 확인

#### ⏳ **2. Long Polling**
- **목적**: 5분+ 대기 시간 재현
- **테스트**:
  1. Timeout을 300초(5분)로 설정
  2. "Start Long Polling" 클릭
  3. 별도 탭에서 메시지 전송

#### 📡 **3. Server-Sent Events (SSE)**
- **목적**: 스트리밍 응답 패턴
- **테스트**:
  1. Duration을 60초로 설정
  2. "Start SSE Stream" 클릭
  3. 실시간 데이터 스트림 확인

#### 🔄 **4. Hub Simulation**
- **목적**: 정확히 5분 37초(337초) 재현
- **테스트**:
  1. Delay를 337초로 설정
  2. "Simulate /hub Delay" 클릭
  3. APM에서 동일한 패턴 확인

### 🌐 **API 직접 테스트**
```bash
# Quick API (기준점)
curl http://localhost:5000/api/realtime/quick

# Long Polling (30초 대기)
curl "http://localhost:5000/api/realtime/long-polling?timeoutSeconds=30"

# Hub Simulation (60초 지연)  
curl "http://localhost:5000/api/realtime/hub?delaySeconds=60"

# SSE Stream (30초)
curl "http://localhost:5000/api/realtime/sse?durationSeconds=30"
```

## 📊 **3단계: Datadog APM 모니터링**

### 🔍 **APM 트레이스 확인**
1. **Datadog APM 접속** (실제 환경에서)
2. **서비스별 트레이스 분석**:
   - `dotnet-sample` 서비스 선택
   - 실행 시간별 트레이스 정렬
   - `/hub`, `/api/realtime/*` 엔드포인트 비교

### 📈 **예상 APM 결과**

| 패턴 | 예상 실행시간 | 특징 |
|------|---------------|------|
| **Quick API** | < 100ms | 일반적인 HTTP 응답 |
| **SignalR Hub** | 연결 지속 | WebSocket 업그레이드 |
| **Long Polling** | 5분+ | 이벤트 대기 패턴 |
| **SSE** | 설정된 시간 | 스트리밍 응답 |
| **Hub Simulation** | 정확히 337초 | **GET /hub 패턴 재현** |

## 🎯 **4단계: 성능 비교 분석**

### 📋 **테스트 시나리오**
1. **동시에 4가지 패턴 실행**
2. **각 패턴의 CPU/메모리 사용률 확인**
3. **네트워크 연결 상태 모니터링**
4. **APM에서 트레이스 패턴 비교**

### 🔍 **주요 확인 포인트**
- ✅ SignalR Hub의 WebSocket 연결 협상
- ✅ Long Polling의 대기 시간 패턴
- ✅ SSE의 스트리밍 특성
- ✅ Hub Simulation의 정확한 지연 재현

## 🏆 **최종 검증 목표**

**GET /hub가 5분 37초 걸리는 이유**를 완전히 이해하기 위해:

1. **SignalR Hub 연결 패턴** 확인
2. **클라이언트 연결 유지 시간** 측정  
3. **WebSocket 프로토콜 전환** 모니터링
4. **실제 서버 처리 시간 vs 연결 유지 시간** 구분

## 🚀 **추가 테스트 옵션**

### 🔧 **개발자 도구 활용**
```bash
# WebSocket 연결 모니터링
# Chrome DevTools → Network → WS 탭

# SignalR 연결 상태 확인
# 콘솔에서 connection.state 확인
```

### 📊 **부하 테스트**
```bash
# 동시 접속 테스트 (별도 실행)
for i in {1..5}; do
  curl "http://localhost:5000/api/realtime/long-polling?timeoutSeconds=60" &
done
```

---

🎉 **이제 완벽한 실시간 통신 분석 환경이 준비되었습니다!**

각 패턴을 테스트하면서 GET /hub의 정체를 명확히 파악해보세요.