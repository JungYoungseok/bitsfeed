# 📊 News Consumer Summary Service

실시간 뉴스 요약 처리를 위한 Kafka Consumer 서비스

## 🎯 **주요 기능**

- **Kafka Message Consumption**: 뉴스 데이터 실시간 수신
- **OpenAI Integration**: GPT를 활용한 자동 뉴스 요약
- **MongoDB Storage**: 요약된 뉴스 데이터 저장
- **Error Handling**: 안정적인 메시지 처리 및 재시도

## 🏗️ **아키텍처**

```
Kafka Topic → News Consumer → OpenAI API → MongoDB
    ↓              ↓             ↓           ↓
뉴스 원본 데이터   메시지 수신    AI 요약    요약 저장
```

## 🚀 **실행 방법**

### **Docker Compose**
```bash
docker-compose up news-consumer
```

### **로컬 개발**
```bash
cd news-consumer
pip install -r requirements.txt
python ./kafka/consumer_summary.py
```

## 🔧 **환경 변수**

```bash
OPENAI_API_KEY=your_openai_api_key
MONGO_URI=mongodb://mongo:27017
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
```

## 📈 **모니터링**

- **로그**: Consumer 시작 시 "🚀 News Consumer Summary Service Starting..." 메시지 출력
- **Kafka Lag**: Consumer group 지연 모니터링
- **MongoDB**: 요약 데이터 저장 상태 확인

## 🧪 **테스트**

### **CI/CD Pipeline**
- GitHub Actions: `deploy-consumer.yml`
- ECR Image: `news-consumer:latest`
- EKS Deployment: `consumer-summary.yaml`

<!-- 🧪 GitHub Actions Test: 2024-01-20 v1.0 -->
<!-- 🚀 Consumer workflow test trigger -->
<!-- 📊 Summary service deployment test -->

---
**Version**: 2024.1.20 | **Service**: news-consumer | **Status**: ✅ Active 