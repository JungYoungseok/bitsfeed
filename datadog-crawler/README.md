# 📰 Datadog News Crawler

<!-- 🧪 Deploy.yml 테스트: 2024-01-20 -->

Google News에서 Datadog 관련 뉴스를 수집하고, FastAPI로 조회하는 서비스입니다.  
MongoDB Atlas를 사용해 데이터를 저장하며, AWS EKS에 배포할 수 있습니다.

## 📦 로컬 실행

```bash
cp .env.example .env
docker-compose up --build

```

# Bitsfeed - Datadog News Crawler 🚀

뉴스 수집, 분석 및 키워드 시각화 통합 플랫폼

## 🚀 Docker Compose로 실행하기

### 1. 환경 설정

`.env` 파일을 생성하고 다음 환경변수들을 설정하세요:

```bash
# MongoDB 설정
MONGO_URI=mongodb://mongo:27017

# Kafka 설정  
KAFKA_BOOTSTRAP_SERVERS=kafka:29092

# OpenAI API 설정 (뉴스 요약 생성용)
OPENAI_API_KEY=your_openai_api_key_here

# Datadog APM 설정 (선택사항)
DD_ENV=development
DD_VERSION=1.0.0
DD_SERVICE=bitsfeed-api
```

### 2. 서비스 시작

```bash
cd datadog-crawler
docker-compose up -d
```

### 3. 서비스 확인

- **API 서버**: http://localhost:8000
- **키워드 분석 대시보드**: http://localhost:8000/viz/dashboard
- **간단한 시각화**: http://localhost:8000/viz/simple
- **MongoDB**: localhost:27017
- **Kafka**: localhost:9092

### 4. 뉴스 수집 시작

```bash
# 뉴스 크롤링 실행
curl -X POST http://localhost:8000/crawl

# 수집된 뉴스 확인
curl http://localhost:8000/news
```

## 📊 키워드 분석 기능

### 주요 기능
- 🌳 **키워드 빈도 트리맵**: 키워드 출현 빈도를 시각화
- 🕸️ **연관관계 네트워크**: 키워드 간 연결 관계 분석
- 📈 **트렌드 분석**: 시간별 키워드 변화 추적

### API 엔드포인트
- `GET /analytics/keywords/frequency` - 키워드 빈도 분석
- `GET /analytics/keywords/treemap` - 트리맵 데이터
- `GET /analytics/keywords/network` - 네트워크 그래프 데이터
- `GET /analytics/keywords/trends` - 트렌드 데이터

## 🛠️ 개발 모드

```bash
# 로그 확인 (실시간)
docker-compose logs -f api

# 컨테이너 재시작
docker-compose restart api

# 전체 환경 재구축
docker-compose down
docker-compose up --build -d
```

## 🧹 정리

```bash
# 컨테이너 정지 및 제거
docker-compose down

# 볼륨까지 모두 제거
docker-compose down -v
```
