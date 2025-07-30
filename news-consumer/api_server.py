from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional
import json
import os
from pymongo import MongoClient

# 글로벌 상태 관리 클래스
class ConsumerStats:
    def __init__(self):
        self.start_time = datetime.now()
        self.total_processed = 0
        self.total_errors = 0
        self.last_processed_time = None
        self.last_message = None
        self.recent_summaries = []
        self.is_consumer_running = False
        self.kafka_connection_status = "disconnected"
        
    def update_processed(self, message_data: dict, summary: str):
        self.total_processed += 1
        self.last_processed_time = datetime.now()
        self.last_message = message_data.get('title', 'Unknown')
        
        # 최근 요약 목록 유지 (최대 10개)
        self.recent_summaries.append({
            'timestamp': self.last_processed_time.isoformat(),
            'title': message_data.get('title', 'Unknown'),
            'source': message_data.get('source', 'Unknown'),
            'summary': summary[:200] + '...' if len(summary) > 200 else summary,
            'link': message_data.get('link', '')
        })
        
        if len(self.recent_summaries) > 10:
            self.recent_summaries.pop(0)
    
    def update_error(self):
        self.total_errors += 1
    
    def set_consumer_status(self, status: bool):
        self.is_consumer_running = status
    
    def set_kafka_status(self, status: str):
        self.kafka_connection_status = status

# 글로벌 통계 객체
stats = ConsumerStats()

# FastAPI 앱 생성
app = FastAPI(
    title="News Consumer API",
    description="뉴스 소비자 서비스 모니터링 및 상태 확인 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    """서비스 헬스 체크"""
    return {
        "status": "healthy",
        "service": "news-consumer",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": int((datetime.now() - stats.start_time).total_seconds())
    }

@app.get("/stats")
def get_stats():
    """처리 통계 정보"""
    uptime = datetime.now() - stats.start_time
    
    return {
        "service": "news-consumer",
        "start_time": stats.start_time.isoformat(),
        "uptime_seconds": int(uptime.total_seconds()),
        "uptime_human": str(uptime).split('.')[0],
        "total_processed": stats.total_processed,
        "total_errors": stats.total_errors,
        "success_rate": round((stats.total_processed / (stats.total_processed + stats.total_errors)) * 100, 2) if (stats.total_processed + stats.total_errors) > 0 else 0,
        "last_processed_time": stats.last_processed_time.isoformat() if stats.last_processed_time else None,
        "last_message": stats.last_message,
        "consumer_running": stats.is_consumer_running,
        "kafka_status": stats.kafka_connection_status
    }

@app.get("/recent-summaries")
def get_recent_summaries():
    """최근 처리된 요약 목록"""
    return {
        "count": len(stats.recent_summaries),
        "summaries": stats.recent_summaries
    }

@app.get("/status")
def get_full_status():
    """전체 상태 정보"""
    return {
        "health": {
            "status": "healthy",
            "uptime_seconds": int((datetime.now() - stats.start_time).total_seconds())
        },
        "statistics": {
            "total_processed": stats.total_processed,
            "total_errors": stats.total_errors,
            "last_processed": stats.last_processed_time.isoformat() if stats.last_processed_time else None
        },
        "consumer": {
            "running": stats.is_consumer_running,
            "kafka_status": stats.kafka_connection_status
        },
        "recent_activity": {
            "count": len(stats.recent_summaries),
            "latest": stats.recent_summaries[-1] if stats.recent_summaries else None
        },
        "environment": {
            "mongo_uri_set": bool(os.getenv("MONGO_URI")),
            "kafka_servers_set": bool(os.getenv("KAFKA_BOOTSTRAP_SERVERS")),
            "openai_key_set": bool(os.getenv("OPENAI_API_KEY"))
        }
    }

@app.get("/mongo-test")
def test_mongo_connection():
    """MongoDB 연결 테스트"""
    try:
        mongo = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
        # 연결 테스트
        mongo.admin.command('ping')
        
        # 뉴스 데이터 개수 확인
        db = mongo["bitsfeed"]
        news_count = db["news"].count_documents({})
        
        return {
            "status": "connected",
            "database": "bitsfeed",
            "news_count": news_count,
            "collections": db.list_collection_names()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.get("/")
def root():
    """루트 엔드포인트"""
    return {
        "service": "News Consumer API",
        "version": "1.0.1",
        "description": "뉴스 소비자 서비스 모니터링 API",
        "build_info": "GitHub Actions Build Test 📰",
        "last_updated": "2024-01-30",
        "endpoints": {
            "health": "/health",
            "stats": "/stats", 
            "recent-summaries": "/recent-summaries",
            "status": "/status",
            "mongo-test": "/mongo-test"
        },
        "documentation": "/docs"
    }

# 서버 시작 함수
def start_api_server():
    """API 서버를 별도 스레드에서 시작"""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")

# 통계 객체를 외부에서 사용할 수 있도록 export
__all__ = ['stats', 'start_api_server', 'app'] 