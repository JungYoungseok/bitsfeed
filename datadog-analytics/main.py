from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.analytics import router as analytics_router
from api.visualization import router as visualization_router
import os

app = FastAPI(
    title="Datadog Analytics Service",
    description="키워드 분석 및 시각화 전용 서비스",
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

# API 라우터 등록
app.include_router(analytics_router, prefix="/analytics")
app.include_router(visualization_router, prefix="/viz")

@app.get("/")
def root():
    return {
        "service": "Datadog Analytics Service",
        "version": "1.0.0",
        "description": "키워드 분석 및 시각화 전용 마이크로서비스",
        "endpoints": {
            "analytics": "/analytics/*",
            "visualization": "/viz/*",
            "health": "/health"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "datadog-analytics",
        "port": 8001
    } 