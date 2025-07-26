from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from api.analytics import get_keyword_treemap, get_keyword_network, get_keyword_trends, get_keyword_frequency
import json

router = APIRouter()

@router.get("/dashboard", response_class=HTMLResponse)
def keyword_dashboard():
    """키워드 분석 대시보드 HTML 페이지"""
    
    html_content = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>뉴스 키워드 분석 대시보드 (MongoDB)</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 30px;
            }
            .section {
                margin-bottom: 40px;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: #fafafa;
            }
            .section h2 {
                color: #555;
                margin-top: 0;
            }
            .controls {
                margin-bottom: 20px;
                padding: 15px;
                background-color: #e9ecef;
                border-radius: 5px;
            }
            .controls label {
                margin-right: 10px;
                font-weight: bold;
            }
            .controls input, .controls button {
                margin: 5px;
                padding: 8px 12px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            .controls button {
                background-color: #007bff;
                color: white;
                cursor: pointer;
                border: none;
            }
            .controls button:hover {
                background-color: #0056b3;
            }
            .controls button.success {
                background-color: #28a745;
            }
            .controls button.warning {
                background-color: #ffc107;
                color: #212529;
            }
            .chart-container {
                width: 100%;
                height: 600px;
                margin: 20px 0;
            }
            .loading {
                text-align: center;
                padding: 50px;
                color: #666;
            }
            .error {
                color: #dc3545;
                background-color: #f8d7da;
                border: 1px solid #f5c6cb;
                padding: 10px;
                border-radius: 4px;
                margin: 10px 0;
            }
            .info {
                background-color: #d1ecf1;
                border: 1px solid #bee5eb;
                color: #0c5460;
                padding: 10px;
                border-radius: 4px;
                margin: 10px 0;
            }
            .status {
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                color: #856404;
                padding: 10px;
                border-radius: 4px;
                margin: 10px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔍 뉴스 키워드 분석 대시보드 (MongoDB 기반)</h1>
            
            <!-- 시스템 상태 및 초기화 -->
            <div class="section">
                <h2>⚙️ 시스템 관리</h2>
                <div class="controls">
                    <button onclick="checkStatus()">📊 상태 확인</button>
                    <button onclick="initializeSystem()" class="warning">🚀 시스템 초기화</button>
                    <button onclick="updateKeywords()" class="success">🔄 키워드 업데이트</button>
                </div>
                <div id="status-info" class="status" style="display:none;"></div>
            </div>
            
            <div class="controls">
                <label for="days">분석 기간:</label>
                <input type="number" id="days" value="7" min="1" max="365">
                <label>일</label>
                
                <label for="limit">키워드 개수:</label>
                <input type="number" id="limit" value="30" min="5" max="100">
                
                <label for="use-mongodb">
                    <input type="checkbox" id="use-mongodb" checked> MongoDB 사용
                </label>
                
                <button onclick="updateAllCharts()">📊 차트 업데이트</button>
                <button onclick="downloadData()">💾 데이터 다운로드</button>
            </div>
            
            <div id="info" class="info" style="display:none;"></div>
            <div id="error" class="error" style="display:none;"></div>
            
            <!-- 키워드 빈도 트리맵 -->
            <div class="section">
                <h2>🌳 키워드 빈도 트리맵</h2>
                <div id="treemap-loading" class="loading">트리맵 로딩 중...</div>
                <div id="treemap" class="chart-container"></div>
            </div>
            
            <!-- 키워드 연관관계 네트워크 -->
            <div class="section">
                <h2>🕸️ 키워드 연관관계 네트워크</h2>
                <div class="controls">
                    <label for="min-cooccurrence">최소 동시출현:</label>
                    <input type="number" id="min-cooccurrence" value="2" min="1" max="10">
                    <button onclick="updateNetwork()">네트워크 업데이트</button>
                </div>
                <div id="network-loading" class="loading">네트워크 로딩 중...</div>
                <div id="network" class="chart-container"></div>
            </div>
            
            <!-- 키워드 트렌드 -->
            <div class="section">
                <h2>📈 키워드 트렌드</h2>
                <div class="controls">
                    <label for="trend-days">트렌드 기간:</label>
                    <input type="number" id="trend-days" value="30" min="7" max="365">
                    <label for="top-n">상위 키워드 수:</label>
                    <input type="number" id="top-n" value="10" min="5" max="30">
                    <button onclick="updateTrends()">트렌드 업데이트</button>
                </div>
                <div id="trends-loading" class="loading">트렌드 로딩 중...</div>
                <div id="trends" class="chart-container"></div>
            </div>
        </div>
        
        <script>
            let currentData = {};
            
            // 페이지 로드 시 상태 확인 후 차트 초기화
            window.onload = function() {
                checkStatus();
            };
            
            function showError(message) {
                const errorDiv = document.getElementById('error');
                errorDiv.textContent = message;
                errorDiv.style.display = 'block';
                setTimeout(() => {
                    errorDiv.style.display = 'none';
                }, 5000);
            }
            
            function showInfo(message) {
                const infoDiv = document.getElementById('info');
                infoDiv.textContent = message;
                infoDiv.style.display = 'block';
                setTimeout(() => {
                    infoDiv.style.display = 'none';
                }, 3000);
            }
            
            function showStatus(message) {
                const statusDiv = document.getElementById('status-info');
                statusDiv.innerHTML = message;
                statusDiv.style.display = 'block';
            }
            
            async function fetchData(endpoint, params = {}) {
                const url = new URL(endpoint, window.location.origin);
                Object.keys(params).forEach(key => {
                    if (params[key] !== null && params[key] !== undefined) {
                        url.searchParams.append(key, params[key]);
                    }
                });
                
                try {
                    const response = await fetch(url);
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return await response.json();
                } catch (error) {
                    showError(`데이터 가져오기 실패: ${error.message}`);
                    throw error;
                }
            }
            
            async function checkStatus() {
                try {
                    const status = await fetchData('/api/analytics/keywords/status');
                    
                    let statusMessage = `
                        <strong>📊 키워드 시스템 상태:</strong><br>
                        • 총 키워드: ${status.total_keywords}개<br>
                        • 트렌드 레코드: ${status.total_trend_records}개<br>
                        • 상태: ${status.status === 'ready' ? '✅ 준비됨' : '⚠️ 빈 상태'}<br>
                    `;
                    
                    if (status.latest_keyword_update) {
                        statusMessage += `• 최근 키워드 업데이트: ${new Date(status.latest_keyword_update).toLocaleString()}<br>`;
                    }
                    if (status.latest_trend_update) {
                        statusMessage += `• 최근 트렌드 업데이트: ${new Date(status.latest_trend_update).toLocaleString()}`;
                    }
                    
                    showStatus(statusMessage);
                    
                    if (status.status === 'ready') {
                        updateAllCharts();
                    } else {
                        showInfo('키워드 데이터가 없습니다. 시스템을 초기화해주세요.');
                    }
                    
                } catch (error) {
                    showError('상태 확인 실패');
                }
            }
            
            async function initializeSystem() {
                if (!confirm('키워드 시스템을 초기화하시겠습니까? 시간이 다소 걸릴 수 있습니다.')) {
                    return;
                }
                
                try {
                    const response = await fetch('/api/analytics/keywords/initialize', {method: 'POST'});
                    const result = await response.json();
                    
                    showInfo(result.message);
                    
                    // 30초 후 상태 재확인
                    setTimeout(() => {
                        checkStatus();
                    }, 30000);
                    
                } catch (error) {
                    showError('시스템 초기화 실패');
                }
            }
            
            async function updateKeywords() {
                try {
                    const response = await fetch('/api/analytics/keywords/update', {method: 'POST'});
                    const result = await response.json();
                    
                    showInfo(result.message);
                    
                    // 10초 후 상태 재확인
                    setTimeout(() => {
                        checkStatus();
                    }, 10000);
                    
                } catch (error) {
                    showError('키워드 업데이트 실패');
                }
            }
            
            async function updateTreemap() {
                const days = document.getElementById('days').value;
                const limit = document.getElementById('limit').value;
                const useMongodb = document.getElementById('use-mongodb').checked;
                
                document.getElementById('treemap-loading').style.display = 'block';
                document.getElementById('treemap').innerHTML = '';
                
                try {
                    const data = await fetchData('/api/analytics/keywords/treemap', { 
                        days, 
                        limit, 
                        use_mongodb: useMongodb 
                    });
                    
                    if (data.error) {
                        showError(data.error);
                        return;
                    }
                    
                    Plotly.newPlot('treemap', data.chart_data.data, data.chart_data.layout);
                    currentData.treemap = data;
                    
                    const source = data.metadata.data_source || 'unknown';
                    showInfo(`트리맵 업데이트 완료 (${data.metadata.total_articles}개 기사, ${data.metadata.unique_keywords}개 키워드) - ${source}`);
                } catch (error) {
                    showError('트리맵 생성 실패');
                } finally {
                    document.getElementById('treemap-loading').style.display = 'none';
                }
            }
            
            async function updateNetwork() {
                const days = document.getElementById('days').value;
                const minCooccurrence = document.getElementById('min-cooccurrence').value;
                const useMongodb = document.getElementById('use-mongodb').checked;
                
                document.getElementById('network-loading').style.display = 'block';
                document.getElementById('network').innerHTML = '';
                
                try {
                    const data = await fetchData('/api/analytics/keywords/network', { 
                        days, 
                        min_cooccurrence: minCooccurrence,
                        use_mongodb: useMongodb
                    });
                    
                    if (data.error) {
                        showError(data.error);
                        return;
                    }
                    
                    Plotly.newPlot('network', data.chart_data.data, data.chart_data.layout);
                    currentData.network = data;
                    
                    const source = data.metadata.data_source || 'unknown';
                    showInfo(`네트워크 업데이트 완료 (${data.metadata.total_nodes}개 노드, ${data.metadata.total_edges}개 연결) - ${source}`);
                } catch (error) {
                    showError('네트워크 생성 실패');
                } finally {
                    document.getElementById('network-loading').style.display = 'none';
                }
            }
            
            async function updateTrends() {
                const trendDays = document.getElementById('trend-days').value;
                const topN = document.getElementById('top-n').value;
                const useMongodb = document.getElementById('use-mongodb').checked;
                
                document.getElementById('trends-loading').style.display = 'block';
                document.getElementById('trends').innerHTML = '';
                
                try {
                    const data = await fetchData('/api/analytics/keywords/trends', { 
                        days: trendDays, 
                        top_n: topN,
                        use_mongodb: useMongodb
                    });
                    
                    if (data.error) {
                        showError(data.error);
                        return;
                    }
                    
                    Plotly.newPlot('trends', data.chart_data.data, data.chart_data.layout);
                    currentData.trends = data;
                    
                    const source = data.metadata.data_source || 'unknown';
                    showInfo(`트렌드 업데이트 완료 (${data.metadata.analysis_days}일간 분석) - ${source}`);
                } catch (error) {
                    showError('트렌드 생성 실패');
                } finally {
                    document.getElementById('trends-loading').style.display = 'none';
                }
            }
            
            async function updateAllCharts() {
                showInfo('모든 차트를 업데이트하고 있습니다...');
                
                await Promise.all([
                    updateTreemap(),
                    updateNetwork(),
                    updateTrends()
                ]);
            }
            
            function downloadData() {
                if (Object.keys(currentData).length === 0) {
                    showError('다운로드할 데이터가 없습니다. 먼저 차트를 생성해주세요.');
                    return;
                }
                
                const dataStr = JSON.stringify(currentData, null, 2);
                const dataBlob = new Blob([dataStr], {type: 'application/json'});
                const url = URL.createObjectURL(dataBlob);
                
                const link = document.createElement('a');
                link.href = url;
                link.download = `keyword_analysis_${new Date().toISOString().split('T')[0]}.json`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                URL.revokeObjectURL(url);
                
                showInfo('데이터 다운로드가 시작되었습니다.');
            }
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@router.get("/simple", response_class=HTMLResponse)
def simple_visualization():
    """간단한 키워드 분석 시각화 (MongoDB 기반)"""
    
    html_content = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>간단한 키워드 분석 (MongoDB)</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .chart { margin: 20px 0; height: 500px; }
            button { padding: 10px 20px; margin: 10px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .init-btn { background: #ffc107; color: #212529; }
            .status { background: #f8f9fa; border: 1px solid #dee2e6; padding: 10px; border-radius: 5px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <h1>🔍 뉴스 키워드 분석 (MongoDB 기반)</h1>
        
        <div class="status" id="status">상태 확인 중...</div>
        
        <button onclick="checkStatus()">상태 확인</button>
        <button onclick="initializeSystem()" class="init-btn">시스템 초기화</button>
        <button onclick="loadTreemap()">트리맵 보기</button>
        <button onclick="loadNetwork()">네트워크 보기</button>
        
        <div id="chart" class="chart"></div>
        
        <script>
            window.onload = checkStatus;
            
            async function checkStatus() {
                try {
                    const response = await fetch('/api/analytics/keywords/status');
                    const status = await response.json();
                    
                    document.getElementById('status').innerHTML = `
                        <strong>시스템 상태:</strong> ${status.status === 'ready' ? '✅ 준비됨' : '⚠️ 초기화 필요'}<br>
                        키워드: ${status.total_keywords}개 | 트렌드: ${status.total_trend_records}개
                    `;
                    
                    if (status.status === 'ready') {
                        loadTreemap();
                    }
                } catch (error) {
                    document.getElementById('status').innerHTML = '❌ 상태 확인 실패';
                }
            }
            
            async function initializeSystem() {
                if (!confirm('시스템을 초기화하시겠습니까?')) return;
                
                try {
                    const response = await fetch('/api/analytics/keywords/initialize', {method: 'POST'});
                    const result = await response.json();
                    
                    alert(result.message);
                    setTimeout(checkStatus, 30000); // 30초 후 상태 재확인
                } catch (error) {
                    alert('초기화 실패: ' + error.message);
                }
            }
            
            async function loadTreemap() {
                try {
                    const response = await fetch('/api/analytics/keywords/treemap?days=7&limit=20&use_mongodb=true');
                    const data = await response.json();
                    
                    if (data.error) {
                        alert(data.error);
                        return;
                    }
                    
                    Plotly.newPlot('chart', data.chart_data.data, data.chart_data.layout);
                } catch (error) {
                    alert('트리맵 로딩 실패: ' + error.message);
                }
            }
            
            async function loadNetwork() {
                try {
                    const response = await fetch('/api/analytics/keywords/network?days=7&min_cooccurrence=2&use_mongodb=true');
                    const data = await response.json();
                    
                    if (data.error) {
                        alert(data.error);
                        return;
                    }
                    
                    Plotly.newPlot('chart', data.chart_data.data, data.chart_data.layout);
                } catch (error) {
                    alert('네트워크 로딩 실패: ' + error.message);
                }
            }
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content) 