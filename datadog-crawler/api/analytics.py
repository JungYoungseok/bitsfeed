from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import json
from collections import Counter, defaultdict
import re
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from db.mongodb import get_all_news
from db.keyword_manager import (
    initialize_keyword_system, 
    update_keyword_data,
    get_keyword_frequency as get_mongo_keyword_frequency,
    get_keyword_trends as get_mongo_keyword_trends,
    get_keyword_network as get_mongo_keyword_network
)
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
import networkx as nx

# KoNLPy 한국어 분석 (선택적으로 사용)
try:
    from konlpy.tag import Okt
    okt = Okt()
    KONLPY_AVAILABLE = True
except ImportError:
    KONLPY_AVAILABLE = False
    print("⚠️ KoNLPy를 사용할 수 없습니다. 기본 키워드 추출을 사용합니다.")

router = APIRouter()

def extract_keywords_simple(text: str, min_length: int = 2) -> List[str]:
    """간단한 키워드 추출 (KoNLPy 없이)"""
    if not text:
        return []
    
    # 한글, 영어, 숫자만 추출
    text = re.sub(r'[^\w\s가-힣]', ' ', text)
    words = text.split()
    
    # 길이 필터링 및 불용어 제거
    stopwords = {'의', '이', '그', '저', '것', '수', '등', '및', '또는', '하지만', '그리고', '이런', '저런', '이것', '저것', '들', '를', '을', '이', '가', '은', '는', '에', '서', '로', '으로', '와', '과', '도', '만', '뿐', '까지', '부터', '에서', '에게', '한테', '께', '더', '가장', '매우', '아주', '정말', '너무', '조금', '약간', '또', '다시', '다른', '새로운', '오늘', '어제', '내일', '이번', '지난', '다음'}
    
    filtered_words = []
    for word in words:
        if len(word) >= min_length and word not in stopwords:
            filtered_words.append(word)
    
    return filtered_words

def extract_keywords_konlpy(text: str) -> List[str]:
    """KoNLPy를 사용한 키워드 추출"""
    if not text:
        return []
    
    try:
        # 명사와 고유명사만 추출
        nouns = okt.nouns(text)
        # 길이 2 이상인 단어만 필터링
        filtered_nouns = [noun for noun in nouns if len(noun) >= 2]
        return filtered_nouns
    except Exception as e:
        print(f"KoNLPy 분석 오류: {e}")
        return extract_keywords_simple(text)

def extract_keywords(text: str) -> List[str]:
    """키워드 추출 (KoNLPy 사용 가능하면 사용, 아니면 간단한 방법)"""
    if KONLPY_AVAILABLE:
        return extract_keywords_konlpy(text)
    else:
        return extract_keywords_simple(text)

# 키워드 데이터 관리 엔드포인트
@router.post("/keywords/initialize")
def initialize_keywords(background_tasks: BackgroundTasks):
    """키워드 시스템 초기화 (인덱스 생성 + 전체 데이터 분석)"""
    try:
        background_tasks.add_task(initialize_keyword_system)
        return {
            "message": "키워드 시스템 초기화를 백그라운드에서 시작했습니다.",
            "status": "processing"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"초기화 실패: {str(e)}")

@router.post("/keywords/update")
def update_keywords(background_tasks: BackgroundTasks):
    """키워드 데이터 업데이트"""
    try:
        background_tasks.add_task(update_keyword_data)
        return {
            "message": "키워드 데이터 업데이트를 백그라운드에서 시작했습니다.",
            "status": "processing"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"업데이트 실패: {str(e)}")

@router.get("/keywords/status")
def get_keyword_status():
    """키워드 데이터 상태 조회"""
    try:
        from db.keyword_manager import keywords_collection, keyword_trends_collection
        
        total_keywords = keywords_collection.count_documents({})
        total_trends = keyword_trends_collection.count_documents({})
        
        # 최신 업데이트 시간 조회
        latest_keyword = keywords_collection.find_one({}, sort=[('last_updated', -1)])
        latest_trend = keyword_trends_collection.find_one({}, sort=[('last_updated', -1)])
        
        return {
            "total_keywords": total_keywords,
            "total_trend_records": total_trends,
            "latest_keyword_update": latest_keyword.get('last_updated') if latest_keyword else None,
            "latest_trend_update": latest_trend.get('last_updated') if latest_trend else None,
            "status": "ready" if total_keywords > 0 else "empty"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상태 조회 실패: {str(e)}")

# MongoDB 기반 키워드 분석 엔드포인트
@router.get("/keywords/frequency")
def get_keyword_frequency(days: Optional[int] = 7, limit: Optional[int] = 50, use_mongodb: bool = True):
    """키워드 빈도 분석 (MongoDB 기반 또는 실시간)"""
    try:
        if use_mongodb:
            # MongoDB에서 미리 계산된 데이터 사용
            result = get_mongo_keyword_frequency(days=days, limit=limit)
            if 'error' in result:
                raise HTTPException(status_code=400, detail=result['error'])
            
            # 추가 메타데이터
            news_data = get_all_news()
            result['total_articles'] = len(news_data)
            
            return result
        else:
            # 기존 실시간 분석 (호환성을 위해 유지)
            return get_realtime_keyword_frequency(days=days, limit=limit)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"키워드 분석 오류: {str(e)}")

@router.get("/keywords/treemap")
def get_keyword_treemap(days: Optional[int] = 7, limit: Optional[int] = 30, use_mongodb: bool = True):
    """키워드 빈도를 트리맵으로 시각화"""
    try:
        # 키워드 빈도 데이터 가져오기
        freq_data = get_keyword_frequency(days=days, limit=limit, use_mongodb=use_mongodb)
        
        if "error" in freq_data:
            return freq_data
        
        keywords = list(freq_data["top_keywords"].keys())
        values = list(freq_data["top_keywords"].values())
        
        if not keywords:
            return {"error": "키워드가 없습니다."}
        
        # 트리맵 생성
        fig = go.Figure(go.Treemap(
            labels=keywords,
            values=values,
            parents=[""] * len(keywords),
            textinfo="label+value",
            hovertemplate="<b>%{label}</b><br>빈도: %{value}<br><extra></extra>",
            maxdepth=1,
            textfont_size=12
        ))
        
        fig.update_layout(
            title=f"키워드 빈도 트리맵 (최근 {days}일) - {'MongoDB' if use_mongodb else '실시간'}",
            font_size=12,
            width=800,
            height=600
        )
        
        # JSON으로 변환
        graphJSON = json.dumps(fig, cls=PlotlyJSONEncoder)
        
        return {
            "chart_data": json.loads(graphJSON),
            "metadata": {
                "total_articles": freq_data.get("total_articles", 0),
                "total_keywords": freq_data.get("total_keywords", 0),
                "unique_keywords": len(keywords),
                "data_source": "mongodb" if use_mongodb else "realtime"
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"트리맵 생성 오류: {str(e)}")

@router.get("/keywords/network")
def get_keyword_network(days: Optional[int] = 7, min_cooccurrence: Optional[int] = 2, use_mongodb: bool = True):
    """키워드 간 연관관계를 네트워크 그래프로 시각화"""
    try:
        if use_mongodb:
            # MongoDB에서 미리 계산된 네트워크 데이터 사용
            network_data = get_mongo_keyword_network(days=days, min_cooccurrence=min_cooccurrence)
            if 'error' in network_data:
                return network_data
            
            # NetworkX를 사용한 레이아웃 계산
            G = nx.Graph()
            for edge in network_data['edges']:
                G.add_edge(edge['source'], edge['target'], weight=edge['weight'])
            
            if len(G.nodes()) == 0:
                return {"error": "네트워크에 노드가 없습니다."}
            
            # 레이아웃 계산
            pos = nx.spring_layout(G, k=1, iterations=50)
            
            # 노드 정보
            node_x = []
            node_y = []
            node_text = []
            node_size = []
            
            for node_data in network_data['nodes']:
                node = node_data['id']
                if node in pos:
                    x, y = pos[node]
                    node_x.append(x)
                    node_y.append(y)
                    node_text.append(node)
                    node_size.append(node_data['strength'])
            
            # 엣지 정보
            edge_x = []
            edge_y = []
            
            for edge in network_data['edges']:
                if edge['source'] in pos and edge['target'] in pos:
                    x0, y0 = pos[edge['source']]
                    x1, y1 = pos[edge['target']]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])
            
        else:
            # 기존 실시간 분석 로직 (호환성을 위해 유지)
            return get_realtime_keyword_network(days=days, min_cooccurrence=min_cooccurrence)
        
        # Plotly 그래프 생성
        fig = go.Figure()
        
        # 엣지 추가
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='#888'),
            hoverinfo='none',
            mode='lines'
        ))
        
        # 노드 추가
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            textposition="middle center",
            hovertext=[f"{text}<br>연결강도: {size}" for text, size in zip(node_text, node_size)],
            marker=dict(
                size=[max(10, min(50, size * 3)) for size in node_size],
                color=node_size,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="연결 강도")
            )
        ))
        
        fig.update_layout(
            title=dict(
                text=f"키워드 연관관계 네트워크 (최근 {days}일) - {'MongoDB' if use_mongodb else '실시간'}",
                font=dict(size=16)
            ),
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[ dict(
                text="노드 크기: 다른 키워드와의 연결 강도<br>색상: 연결 강도",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002,
                xanchor='left', yanchor='bottom',
                font=dict(size=12)
            )],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            width=900,
            height=700
        )
        
        # JSON으로 변환
        graphJSON = json.dumps(fig, cls=PlotlyJSONEncoder)
        
        return {
            "chart_data": json.loads(graphJSON),
            "metadata": {
                "total_nodes": network_data.get('total_nodes', len(node_text)),
                "total_edges": network_data.get('total_edges', len(network_data.get('edges', []))),
                "min_cooccurrence": min_cooccurrence,
                "data_source": "mongodb" if use_mongodb else "realtime"
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"네트워크 그래프 생성 오류: {str(e)}")

@router.get("/keywords/trends")
def get_keyword_trends(days: Optional[int] = 30, top_n: Optional[int] = 10, use_mongodb: bool = True):
    """키워드 트렌드 시계열 분석"""
    try:
        if use_mongodb:
            # MongoDB에서 미리 계산된 트렌드 데이터 사용
            trend_result = get_mongo_keyword_trends(days=days, top_n=top_n)
            if 'error' in trend_result:
                return trend_result
            
            # Plotly 시계열 그래프 생성
            fig = go.Figure()
            
            for keyword in trend_result['top_keywords']:
                fig.add_trace(go.Scatter(
                    x=trend_result['dates'],
                    y=trend_result['trend_data'][keyword],
                    mode='lines+markers',
                    name=keyword,
                    hovertemplate=f"<b>{keyword}</b><br>날짜: %{{x}}<br>빈도: %{{y}}<extra></extra>"
                ))
            
            fig.update_layout(
                title=f"키워드 트렌드 ({days}일간 상위 {top_n}개) - MongoDB",
                xaxis_title="날짜",
                yaxis_title="빈도",
                width=1000,
                height=600,
                hovermode='x unified'
            )
            
            # JSON으로 변환
            graphJSON = json.dumps(fig, cls=PlotlyJSONEncoder)
            
            return {
                "chart_data": json.loads(graphJSON),
                "metadata": {
                    "analysis_days": trend_result['analysis_days'],
                    "top_keywords": trend_result['top_keywords'],
                    "data_source": "mongodb"
                }
            }
        else:
            # 기존 실시간 분석 로직 (호환성을 위해 유지)
            return get_realtime_keyword_trends(days=days, top_n=top_n)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"트렌드 분석 오류: {str(e)}")

# 호환성을 위한 기존 실시간 분석 함수들 (간소화 버전)
def get_realtime_keyword_frequency(days: int = 7, limit: int = 50):
    """실시간 키워드 빈도 분석 (기존 로직)"""
    # 기존 실시간 분석 코드 (간소화)
    news_data = get_all_news()
    
    if not news_data:
        return {"error": "뉴스 데이터가 없습니다."}
    
    # 날짜 필터링
    if days:
        cutoff_date = datetime.now() - timedelta(days=days)
        news_data = [
            item for item in news_data 
            if isinstance(item.get('published'), str) and 
            datetime.fromisoformat(item['published'].replace('Z', '+00:00')) >= cutoff_date
        ]
    
    # 간단한 키워드 추출 및 빈도 계산
    all_keywords = []
    for item in news_data:
        title_keywords = extract_keywords_simple(item.get('title', ''))
        all_keywords.extend(title_keywords)
        
        summary_keywords = extract_keywords_simple(item.get('summary_ko', ''))
        all_keywords.extend(summary_keywords)
    
    keyword_freq = Counter(all_keywords)
    top_keywords = dict(keyword_freq.most_common(limit))
    
    return {
        "total_articles": len(news_data),
        "total_keywords": len(all_keywords),
        "unique_keywords": len(keyword_freq),
        "top_keywords": top_keywords,
        "analysis_period_days": days
    }

def get_realtime_keyword_network(days: int = 7, min_cooccurrence: int = 2):
    """실시간 키워드 네트워크 분석 (기존 로직 간소화)"""
    # 실시간 분석 구현 (간소화된 버전)
    return {"error": "실시간 네트워크 분석은 MongoDB 모드를 사용해주세요."}

def get_realtime_keyword_trends(days: int = 30, top_n: int = 10):
    """실시간 키워드 트렌드 분석 (기존 로직 간소화)"""
    # 실시간 분석 구현 (간소화된 버전)
    return {"error": "실시간 트렌드 분석은 MongoDB 모드를 사용해주세요."} 