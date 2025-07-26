FROM python:3.10-slim

WORKDIR /app

# requirements.txt 먼저 복사하여 layer caching 최적화
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사 (requirements가 변경되지 않으면 이 단계만 재실행)
COPY . .

CMD ["python", "./kafka/consumer_summary.py"]
