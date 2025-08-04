# bitsfeed
Datadog news service with comprehensive monitoring

## 🚀 Features
- **Real-time News Aggregation**: Google News & RSS feeds
- **AI-Powered Summarization**: OpenAI integration for news analysis  
- **Kafka Data Streams**: Producer/Consumer architecture with full tracing
- **Datadog APM Integration**: Complete observability with spans and metrics
- **Multi-Service Architecture**: Frontend, Backend, Analytics, Consumer services
- **Production Ready**: EKS deployment with autoscaling and monitoring

## 📊 Architecture
- **Producer**: `datadog-news-crawler` (FastAPI)
- **Consumer**: `news-consumer` (Kafka + MySQL + MongoDB)
- **Frontend**: `news-frontend` (Next.js)
- **Analytics**: `datadog-analytics` (Data visualization)

## 🔍 Monitoring
- Datadog APM with full request tracing
- Data Streams Monitoring for Kafka flows
- Custom metrics and alerts
- Performance analytics and autoscaling

---
*Last updated: 2025-08-03 - Full Datadog tracing implementation*
