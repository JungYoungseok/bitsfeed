# 📰 Datadog News Crawler

Google News에서 Datadog 관련 뉴스를 수집하고, FastAPI로 조회하는 서비스입니다.  
MongoDB Atlas를 사용해 데이터를 저장하며, AWS EKS에 배포할 수 있습니다.

## 📦 로컬 실행

```bash
cp .env.example .env
docker-compose up --build
