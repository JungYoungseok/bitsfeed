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
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 포트 8000 노출
EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
