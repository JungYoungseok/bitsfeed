FROM python:3.10-slim

# 시스템 패키지 및 Java 설치 (KoNLPy용)
RUN apt-get update && apt-get install -y \
    default-jdk \
    curl \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Java 환경변수 설정
ENV JAVA_HOME=/usr/lib/jvm/default-java

WORKDIR /app

# Analytics 전용 requirements 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 8001 노출 (크롤러와 구분)
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"] 