FROM python:3.10-slim

# curl 설치 (헬스체크용)
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# requirements.txt 먼저 복사하여 layer caching 최적화
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사 (requirements가 변경되지 않으면 이 단계만 재실행)
COPY . .

# API 서버 포트 노출
EXPOSE 8002

# Health check 추가
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

CMD ["python", "./kafka/consumer_summary.py"]
