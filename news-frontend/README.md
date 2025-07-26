# 🌐 News Frontend Service

Real-time 뉴스 피드를 위한 Next.js 기반 웹 애플리케이션

## 🎯 **주요 기능**

- **뉴스 피드**: 실시간 뉴스 목록 표시
- **키워드 분석**: Analytics 서비스 연동 대시보드
- **검색 기능**: 키워드 기반 뉴스 필터링
- **페이지네이션**: 효율적인 뉴스 브라우징
- **반응형 디자인**: 모바일/데스크톱 최적화

## 🏗️ **아키텍처**

```
User → Frontend (Next.js) → API Routes → Backend Services
  ↓         ↓                   ↓            ↓
브라우저   웹 애플리케이션      프록시 레이어   마이크로서비스
```

## 🚀 **실행 방법**

### **Docker Compose**
```bash
docker-compose up frontend
```

### **로컬 개발**
```bash
cd news-frontend
npm install
npm run dev
```

## 🔧 **환경 변수**

```bash
NEWS_API_URL=http://datadog-crawler:8000
ANALYTICS_API_URL=http://datadog-analytics:8001
```

## 📡 **API 프록시 라우팅**

### **뉴스 API**
- `GET /api/news` → `NEWS_API_URL/news`
- `POST /api/crawl` → `NEWS_API_URL/crawl`

### **Analytics API**
- `GET /api/analytics/keywords/*` → `ANALYTICS_API_URL/analytics/keywords/*`
- `GET /api/analytics/viz/*` → `ANALYTICS_API_URL/viz/*`

## 🎨 **UI 컴포넌트**

- **TailwindCSS**: 스타일링 프레임워크
- **TypeScript**: 타입 안전성
- **반응형 그리드**: 뉴스 카드 레이아웃
- **인터랙티브 버튼**: 키워드 분석, 간단 차트

## 📊 **페이지 구조**

```
/ (Home)
├── 뉴스 피드 목록
├── 검색 필터
├── 키워드 분석 버튼 → /api/analytics/viz/dashboard
├── 간단 차트 버튼 → /api/analytics/viz/simple
└── 페이지네이션
```

## 🧪 **테스트**

### **CI/CD Pipeline**
- GitHub Actions: `deploy-frontend.yml`
- ECR Image: `news-frontend:latest`
- EKS Deployment: `news-frontend.yaml`

### **접속 URL**
- **Local**: http://localhost:3000
- **Production**: https://bitsfeed.jacky.click

<!-- 🧪 Frontend workflow test: 2024-01-20 v1.0 -->
<!-- 🌐 Next.js deployment test trigger -->
<!-- ⚡ Frontend service optimization test -->

## 🔄 **마이크로서비스 연동**

### **Backend 연결**
- **Crawler Service**: 뉴스 데이터 조회
- **Analytics Service**: 키워드 분석 및 시각화
- **Consumer Service**: 백그라운드 처리

### **프록시 패턴**
- **Server-side API Routes**: 백엔드 서비스 프록시
- **Client-side Fetch**: 브라우저에서 API 호출
- **Error Handling**: 서비스 장애 시 Fallback

---
**Version**: 2024.1.20 | **Service**: news-frontend | **Status**: ✅ Active | **Framework**: Next.js 15
