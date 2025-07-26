# 📊 Datadog Analytics Service

키워드 분석 및 시각화 전용 마이크로서비스

## 🎯 **서비스 목적**

뉴스 기사로부터 키워드를 추출하고 다양한 시각화를 제공하는 분석 전용 서비스입니다.

### **주요 기능**
- 🔍 **키워드 분석**: KoNLPy를 활용한 한국어/영어 키워드 추출
- 📊 **트리맵 시각화**: 키워드 빈도 기반 계층적 시각화
- 🕸️ **네트워크 그래프**: 키워드 간 연관관계 시각화  
- 📈 **트렌드 분석**: 시간대별 키워드 변화 추이
- 🖥️ **대시보드**: 통합 시각화 대시보드

## 🏗️ **아키텍처**

```
Datadog Analytics Service (Port 8001)
├── FastAPI Framework
├── MongoDB Integration (읽기 전용)
├── Analytics Engine
│   ├── KoNLPy (한국어 분석)
│   ├── scikit-learn (머신러닝)
│   └── Custom keyword extraction
└── Visualization Engine
    ├── Plotly (인터랙티브 차트)
    ├── NetworkX (그래프 분석)
    └── Matplotlib/Seaborn (통계 차트)
```

## 📦 **의존성**

### **Core Libraries**
- FastAPI, Uvicorn
- PyMongo (MongoDB 연결)

### **Analytics & ML**
- KoNLPy (한국어 자연어 처리)
- scikit-learn (머신러닝)
- pandas, numpy (데이터 처리)

### **Visualization**
- Plotly (인터랙티브 시각화)
- NetworkX (네트워크 분석)
- Matplotlib, Seaborn (통계 차트)
- Wordcloud (워드클라우드)

## 🚀 **실행 방법**

### **Docker Compose 실행**
```bash
# 전체 시스템 실행
docker-compose up --build

# Analytics 서비스만 실행
docker-compose up analytics --build
```

### **개발 환경 실행**
```bash
cd datadog-analytics
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

## 📡 **API 엔드포인트**

### **Health Check**
- `GET /health` - 서비스 상태 확인

### **Analytics API**
- `GET /analytics/keywords/frequency` - 키워드 빈도 분석
- `GET /analytics/keywords/treemap` - 트리맵 데이터
- `GET /analytics/keywords/network` - 네트워크 그래프 데이터
- `GET /analytics/keywords/trends` - 키워드 트렌드 분석
- `POST /analytics/keywords/initialize` - 키워드 시스템 초기화
- `POST /analytics/keywords/update` - 키워드 데이터 업데이트

### **Visualization API**
- `GET /viz/dashboard` - 통합 대시보드
- `GET /viz/simple` - 간단 시각화

## 🔧 **환경 변수**

```bash
MONGO_URI=mongodb://mongo:27017
PORT=8001
DD_SERVICE=datadog-analytics
DD_ENV=prod
```

## 🔄 **다른 서비스와의 연동**

### **데이터 소스**
- **MongoDB**: `datadog-crawler`가 수집한 뉴스 데이터 읽기

### **Frontend 연동**
- **news-frontend**: `/api/analytics/*` 경로로 프록시 연결
- **ANALYTICS_API_URL**: `http://datadog-analytics:8001`

### **독립적 운영**
- 크롤링 서비스와 완전 분리
- 분석 요청 시에만 MongoDB 조회
- 무거운 ML/시각화 패키지로 인한 크롤링 성능 영향 없음

## 🎯 **성능 최적화**

### **분리 효과**
- ⚡ **크롤링 서비스 경량화**: 3-5분 빌드 (기존 12-15분)
- 🔄 **독립적 배포**: 분석 기능 변경 시 크롤링 영향 없음
- 📈 **확장성**: 분석 요청 증가 시 독립적 스케일링 