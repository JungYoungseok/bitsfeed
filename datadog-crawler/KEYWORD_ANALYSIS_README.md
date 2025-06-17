# 📊 뉴스 키워드 분석 기능

유입된 기사와 요약(summary) 내용을 바탕으로 키워드 빈도를 시각화하고 단어간 연관관계를 분석할 수 있는 기능입니다.

## 🚀 설치 및 실행

### 1. 의존성 설치

```bash
cd datadog-crawler
pip install -r requirements.txt
```

**주의**: KoNLPy 사용을 위해서는 Java가 설치되어 있어야 합니다. Java가 없어도 기본적인 키워드 추출은 가능합니다.

### 2. API 서버 실행

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 웹 브라우저에서 확인

- **전체 대시보드**: http://localhost:8000/viz/dashboard
- **간단한 시각화**: http://localhost:8000/viz/simple

## 📈 제공되는 시각화

### 1. 키워드 빈도 트리맵 🌳
- 키워드의 출현 빈도를 사각형 크기로 표현
- 자주 나오는 키워드일수록 큰 사각형으로 표시
- API: `GET /analytics/keywords/treemap`

### 2. 키워드 연관관계 네트워크 🕸️
- 함께 나타나는 키워드들을 노드와 링크로 연결
- 노드 크기는 다른 키워드와의 연결 강도를 나타냄
- API: `GET /analytics/keywords/network`

### 3. 키워드 트렌드 시계열 📈
- 시간에 따른 키워드 출현 빈도 변화
- 상위 키워드들의 트렌드를 한눈에 파악
- API: `GET /analytics/keywords/trends`

## 🔧 API 엔드포인트

### 키워드 빈도 분석
```http
GET /analytics/keywords/frequency?days=7&limit=50
```

**파라미터:**
- `days`: 분석할 기간 (기본값: 7일)
- `limit`: 상위 키워드 개수 (기본값: 50개)

### 트리맵 시각화
```http
GET /analytics/keywords/treemap?days=7&limit=30
```

### 네트워크 그래프
```http
GET /analytics/keywords/network?days=7&min_cooccurrence=2
```

**파라미터:**
- `min_cooccurrence`: 최소 동시 출현 횟수 (기본값: 2회)

### 키워드 트렌드
```http
GET /analytics/keywords/trends?days=30&top_n=10
```

**파라미터:**
- `top_n`: 상위 키워드 개수 (기본값: 10개)

## 💡 사용 예제

### Python으로 API 호출
```python
import requests
import json

# 키워드 빈도 데이터 가져오기
response = requests.get("http://localhost:8000/analytics/keywords/frequency?days=7")
data = response.json()

print(f"총 {data['total_articles']}개 기사에서 {data['unique_keywords']}개 고유 키워드 발견")
print("상위 10개 키워드:")
for keyword, count in list(data['top_keywords'].items())[:10]:
    print(f"  {keyword}: {count}회")
```

### 트리맵 데이터 가져오기
```python
response = requests.get("http://localhost:8000/analytics/keywords/treemap?days=7&limit=20")
treemap_data = response.json()

# 차트 데이터는 treemap_data['chart_data']에 들어있음
# Plotly.js로 직접 렌더링 가능
```

## 🎯 주요 특징

1. **한국어 지원**: KoNLPy를 사용한 한국어 형태소 분석 (선택사항)
2. **실시간 분석**: 매일 수집되는 뉴스 데이터 실시간 분석
3. **다양한 시각화**: 트리맵, 네트워크, 시계열 차트 지원
4. **인터랙티브**: 웹 대시보드에서 파라미터 조정 가능
5. **데이터 내보내기**: JSON 형태로 분석 결과 다운로드 가능

## 🔍 분석 대상 텍스트

- 뉴스 제목 (`title`)
- 한국어 요약 (`summary_ko`)  
- 시장 영향 분석 (`impact_ko`)

## 📝 키워드 추출 방식

1. **KoNLPy 사용 (권장)**: 한국어 명사 및 고유명사 추출
2. **기본 방식**: 정규표현식 기반 단어 분리 및 불용어 제거

## 🚀 성능 최적화

- 대용량 데이터 처리를 위한 메모리 효율적인 알고리즘 사용
- 캐싱 및 백그라운드 처리 지원 (향후 추가 예정)
- 분석 결과 MongoDB 저장 (향후 추가 예정)

## 🎨 시각화 커스터마이징

대시보드에서 다음 요소들을 조정할 수 있습니다:

- 분석 기간 (1일 ~ 365일)
- 표시할 키워드 개수
- 네트워크 그래프의 최소 연결 강도
- 트렌드 분석 기간 및 상위 키워드 수

## 📊 사용 사례

1. **콘텐츠 전략 수립**: 인기 키워드 트렌드 파악
2. **시장 동향 분석**: 특정 키워드의 언급 빈도 변화 모니터링  
3. **토픽 모델링**: 연관 키워드 클러스터 발견
4. **SEO 최적화**: 자주 언급되는 키워드 조합 분석

---

문의사항이나 개선 제안이 있으시면 언제든지 알려주세요! 🚀 