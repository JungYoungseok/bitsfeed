from datetime import datetime, timedelta
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.operations import UpdateOne
from collections import Counter, defaultdict
import hashlib
import os
import re
from typing import List, Dict, Optional
from db.mongodb import client

# KoNLPy 한국어 분석 (선택적으로 사용)
try:
    from konlpy.tag import Okt
    okt = Okt()
    KONLPY_AVAILABLE = True
except ImportError:
    KONLPY_AVAILABLE = False
    print("⚠️ KoNLPy를 사용할 수 없습니다. 기본 키워드 추출을 사용합니다.")

# Collection 설정
news_collection = client["bitsfeed"]["news"]
keywords_collection = client["bitsfeed"]["keywords"]
keyword_trends_collection = client["bitsfeed"]["keyword_trends"]

def create_indexes():
    """키워드 관련 collection들에 인덱스 생성"""
    try:
        # keywords collection 인덱스
        keywords_collection.create_index([("keyword", ASCENDING)])
        keywords_collection.create_index([("frequency", DESCENDING)])
        keywords_collection.create_index([("last_updated", DESCENDING)])
        keywords_collection.create_index([("articles", ASCENDING)])
        
        # keyword_trends collection 인덱스
        keyword_trends_collection.create_index([("keyword", ASCENDING), ("date", ASCENDING)])
        keyword_trends_collection.create_index([("date", DESCENDING)])
        keyword_trends_collection.create_index([("keyword", ASCENDING)])
        
        print("✅ 키워드 collection 인덱스 생성 완료")
    except Exception as e:
        print(f"❌ 인덱스 생성 실패: {e}")

def extract_keywords_simple(text: str, min_length: int = 2) -> List[str]:
    """간단한 키워드 추출 (KoNLPy 없이)"""
    if not text:
        return []
    
    # 한글, 영어, 숫자만 추출
    text = re.sub(r'[^\w\s가-힣]', ' ', text)
    words = text.split()
    
    # 길이 필터링 및 불용어 제거
    stopwords = {
        '의', '이', '그', '저', '것', '수', '등', '및', '또는', '하지만', '그리고', 
        '이런', '저런', '이것', '저것', '들', '를', '을', '이', '가', '은', '는', 
        '에', '서', '로', '으로', '와', '과', '도', '만', '뿐', '까지', '부터', 
        '에서', '에게', '한테', '께', '더', '가장', '매우', '아주', '정말', '너무', 
        '조금', '약간', '또', '다시', '다른', '새로운', '오늘', '어제', '내일', 
        '이번', '지난', '다음', '있는', '없는', '있다', '없다', '되는', '되다',
        '하는', '하다', '있어', '없어', '된다', '한다', '같은', '다른', '있을',
        '위한', '위해', '통해', '대한', '대해', '관련', '기반', '중심', '주요',
        '전체', '일부', '대부분', '모든', '각각', '여러', '다양한', '특히'
    }
    
    filtered_words = []
    for word in words:
        if len(word) >= min_length and word not in stopwords and not word.isdigit():
            filtered_words.append(word)
    
    return filtered_words

def extract_english_keywords(text: str, min_length: int = 3) -> List[str]:
    """영어 키워드 추출"""
    if not text:
        return []
    
    # 영어 텍스트 전처리
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    words = text.split()
    
    # 영어 불용어
    english_stopwords = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above',
        'below', 'between', 'among', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have',
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
        'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we',
        'they', 'them', 'their', 'there', 'where', 'when', 'why', 'how', 'what', 'which', 'who',
        'whom', 'whose', 'if', 'unless', 'until', 'while', 'since', 'as', 'so', 'than', 'such',
        'both', 'either', 'neither', 'not', 'no', 'nor', 'only', 'own', 'same', 'few', 'more',
        'most', 'other', 'some', 'any', 'each', 'every', 'all', 'both', 'half', 'either',
        'neither', 'many', 'much', 'several', 'enough', 'too', 'very', 'quite', 'rather',
        'just', 'even', 'still', 'yet', 'already', 'also', 'again', 'once', 'twice', 'here',
        'there', 'everywhere', 'anywhere', 'somewhere', 'nowhere', 'today', 'yesterday',
        'tomorrow', 'now', 'then', 'soon', 'later', 'early', 'late', 'always', 'never',
        'often', 'sometimes', 'usually', 'seldom', 'rarely', 'hardly', 'nearly', 'almost',
        'quite', 'completely', 'entirely', 'totally', 'absolutely', 'perfectly', 'exactly',
        'probably', 'perhaps', 'maybe', 'certainly', 'definitely', 'surely', 'clearly',
        'obviously', 'apparently', 'generally', 'particularly', 'especially', 'specifically',
        'mainly', 'mostly', 'largely', 'partly', 'slightly', 'somewhat', 'rather', 'fairly',
        'pretty', 'really', 'actually', 'indeed', 'truly', 'seriously', 'honestly', 'frankly',
        'basically', 'essentially', 'fundamentally', 'originally', 'initially', 'finally',
        'eventually', 'ultimately', 'consequently', 'therefore', 'thus', 'hence', 'accordingly',
        'however', 'nevertheless', 'nonetheless', 'otherwise', 'meanwhile', 'furthermore',
        'moreover', 'additionally', 'besides', 'also', 'too', 'as', 'well', 'including',
        'such', 'like', 'unlike', 'similar', 'different', 'same', 'equal', 'equivalent',
        'comparable', 'related', 'relevant', 'important', 'significant', 'major', 'minor',
        'primary', 'secondary', 'main', 'key', 'central', 'basic', 'fundamental', 'essential',
        'necessary', 'required', 'optional', 'possible', 'impossible', 'likely', 'unlikely',
        'certain', 'uncertain', 'sure', 'unsure', 'clear', 'unclear', 'obvious', 'hidden',
        'known', 'unknown', 'public', 'private', 'open', 'closed', 'free', 'paid', 'cheap',
        'expensive', 'high', 'low', 'big', 'small', 'large', 'little', 'huge', 'tiny',
        'long', 'short', 'wide', 'narrow', 'thick', 'thin', 'heavy', 'light', 'strong',
        'weak', 'hard', 'soft', 'rough', 'smooth', 'hot', 'cold', 'warm', 'cool', 'dry',
        'wet', 'clean', 'dirty', 'new', 'old', 'young', 'fresh', 'stale', 'good', 'bad',
        'best', 'worst', 'better', 'worse', 'great', 'terrible', 'excellent', 'poor',
        'perfect', 'awful', 'wonderful', 'horrible', 'amazing', 'boring', 'interesting',
        'exciting', 'dull', 'fun', 'serious', 'funny', 'sad', 'happy', 'angry', 'calm',
        'quiet', 'loud', 'fast', 'slow', 'quick', 'gradual', 'sudden', 'immediate',
        'instant', 'delayed', 'early', 'late', 'recent', 'ancient', 'modern', 'traditional',
        'conventional', 'innovative', 'creative', 'original', 'unique', 'common', 'rare',
        'usual', 'unusual', 'normal', 'abnormal', 'regular', 'irregular', 'standard',
        'special', 'general', 'specific', 'particular', 'individual', 'personal', 'social',
        'political', 'economic', 'financial', 'commercial', 'industrial', 'agricultural',
        'educational', 'medical', 'legal', 'technical', 'scientific', 'artistic', 'cultural',
        'historical', 'geographical', 'physical', 'mental', 'emotional', 'spiritual',
        'natural', 'artificial', 'real', 'fake', 'true', 'false', 'right', 'wrong',
        'correct', 'incorrect', 'accurate', 'inaccurate', 'precise', 'vague', 'exact',
        'approximate', 'complete', 'incomplete', 'full', 'empty', 'total', 'partial',
        'whole', 'half', 'quarter', 'third', 'double', 'triple', 'single', 'multiple',
        'first', 'second', 'third', 'last', 'next', 'previous', 'following', 'preceding',
        'above', 'below', 'over', 'under', 'inside', 'outside', 'within', 'without',
        'near', 'far', 'close', 'distant', 'local', 'foreign', 'domestic', 'international',
        'global', 'worldwide', 'universal', 'regional', 'national', 'state', 'federal',
        'government', 'official', 'unofficial', 'formal', 'informal', 'legal', 'illegal',
        'valid', 'invalid', 'effective', 'ineffective', 'successful', 'unsuccessful',
        'positive', 'negative', 'active', 'passive', 'direct', 'indirect', 'forward',
        'backward', 'upward', 'downward', 'inward', 'outward', 'toward', 'away', 'across',
        'along', 'around', 'behind', 'beside', 'beyond', 'despite', 'except', 'including',
        'excluding', 'regarding', 'concerning', 'considering', 'given', 'provided',
        'assuming', 'suppose', 'imagine', 'believe', 'think', 'know', 'understand',
        'realize', 'recognize', 'remember', 'forget', 'learn', 'teach', 'study', 'research',
        'investigate', 'explore', 'discover', 'find', 'search', 'look', 'see', 'watch',
        'observe', 'notice', 'hear', 'listen', 'speak', 'talk', 'say', 'tell', 'ask',
        'answer', 'reply', 'respond', 'explain', 'describe', 'discuss', 'mention',
        'suggest', 'recommend', 'advise', 'warn', 'inform', 'notify', 'announce',
        'declare', 'state', 'claim', 'argue', 'prove', 'demonstrate', 'show', 'reveal',
        'hide', 'cover', 'protect', 'defend', 'attack', 'fight', 'win', 'lose', 'beat',
        'defeat', 'succeed', 'fail', 'try', 'attempt', 'effort', 'work', 'job', 'task',
        'duty', 'responsibility', 'role', 'function', 'purpose', 'goal', 'aim', 'target',
        'objective', 'plan', 'strategy', 'method', 'way', 'means', 'approach', 'technique',
        'process', 'procedure', 'system', 'structure', 'organization', 'institution',
        'company', 'business', 'industry', 'market', 'economy', 'finance', 'money',
        'cost', 'price', 'value', 'worth', 'benefit', 'advantage', 'disadvantage',
        'problem', 'issue', 'challenge', 'difficulty', 'trouble', 'risk', 'danger',
        'threat', 'opportunity', 'chance', 'possibility', 'option', 'choice', 'decision',
        'conclusion', 'result', 'outcome', 'consequence', 'effect', 'impact', 'influence',
        'change', 'development', 'improvement', 'progress', 'growth', 'increase', 'decrease',
        'reduction', 'decline', 'rise', 'fall', 'gain', 'loss', 'profit', 'revenue',
        'income', 'expense', 'investment', 'return', 'interest', 'rate', 'percentage',
        'ratio', 'proportion', 'amount', 'quantity', 'number', 'figure', 'data',
        'information', 'knowledge', 'fact', 'detail', 'feature', 'characteristic',
        'quality', 'property', 'attribute', 'aspect', 'element', 'component', 'part',
        'section', 'area', 'region', 'zone', 'location', 'place', 'position', 'site',
        'spot', 'point', 'line', 'curve', 'circle', 'square', 'triangle', 'shape',
        'form', 'size', 'dimension', 'length', 'width', 'height', 'depth', 'distance',
        'space', 'room', 'capacity', 'volume', 'weight', 'mass', 'density', 'pressure',
        'temperature', 'degree', 'level', 'grade', 'rank', 'status', 'condition',
        'situation', 'circumstance', 'context', 'environment', 'setting', 'background',
        'history', 'past', 'present', 'future', 'time', 'period', 'moment', 'instant',
        'second', 'minute', 'hour', 'day', 'week', 'month', 'year', 'decade', 'century',
        'age', 'generation', 'era', 'epoch', 'season', 'spring', 'summer', 'autumn',
        'winter', 'morning', 'afternoon', 'evening', 'night', 'midnight', 'noon',
        'dawn', 'dusk', 'sunrise', 'sunset', 'monday', 'tuesday', 'wednesday', 'thursday',
        'friday', 'saturday', 'sunday', 'january', 'february', 'march', 'april', 'may',
        'june', 'july', 'august', 'september', 'october', 'november', 'december'
    }
    
    # 기술/비즈니스 관련 중요 키워드는 보존
    important_keywords = {
        'ai', 'ml', 'api', 'cloud', 'data', 'tech', 'software', 'hardware', 'system',
        'platform', 'service', 'solution', 'product', 'company', 'business', 'market',
        'revenue', 'growth', 'investment', 'funding', 'startup', 'enterprise', 'digital',
        'innovation', 'technology', 'development', 'research', 'analysis', 'security',
        'privacy', 'performance', 'optimization', 'automation', 'integration', 'deployment',
        'infrastructure', 'architecture', 'framework', 'database', 'analytics', 'monitoring',
        'observability', 'devops', 'kubernetes', 'docker', 'microservices', 'serverless',
        'machine', 'learning', 'artificial', 'intelligence', 'neural', 'network', 'algorithm',
        'model', 'training', 'prediction', 'classification', 'regression', 'clustering',
        'visualization', 'dashboard', 'metrics', 'logs', 'traces', 'alerts', 'incidents'
    }
    
    filtered_words = []
    for word in words:
        if (len(word) >= min_length and 
            word not in english_stopwords and 
            not word.isdigit() and
            re.match(r'^[a-zA-Z]+$', word)):  # 영어 단어만
            # 중요 키워드이거나 대문자로 시작하는 단어(고유명사 가능성)는 포함
            if word in important_keywords or word[0].isupper() or len(word) >= 4:
                filtered_words.append(word.title())  # 첫 글자 대문자로 통일
    
    return filtered_words

def extract_keywords_konlpy(text: str) -> List[str]:
    """KoNLPy를 사용한 키워드 추출"""
    if not text:
        return []
    
    try:
        # 명사와 고유명사만 추출
        nouns = okt.nouns(text)
        # 길이 2 이상인 단어만 필터링
        filtered_nouns = [noun for noun in nouns if len(noun) >= 2 and not noun.isdigit()]
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

def is_korean_text(text: str) -> bool:
    """텍스트가 한국어인지 확인"""
    if not text:
        return False
    korean_chars = len(re.findall(r'[가-힣]', text))
    total_chars = len(re.findall(r'[가-힣a-zA-Z]', text))
    return korean_chars > total_chars * 0.3 if total_chars > 0 else False

def process_article_keywords(article: Dict) -> List[str]:
    """단일 기사에서 키워드 추출 (한국어/영어 구분)"""
    all_keywords = []
    
    # 제목에서 키워드 추출 (영어)
    title = article.get('title', '')
    if title:
        if is_korean_text(title):
            title_keywords = extract_keywords(title)  # 한국어 처리
        else:
            title_keywords = extract_english_keywords(title)  # 영어 처리
        all_keywords.extend(title_keywords)
    
    # 한국어 요약에서 키워드 추출
    summary_ko = article.get('summary_ko', '')
    if summary_ko:
        summary_keywords = extract_keywords(summary_ko)
        all_keywords.extend(summary_keywords)
    
    # 한국어 영향 분석에서 키워드 추출
    impact_ko = article.get('impact_ko', '')
    if impact_ko:
        impact_keywords = extract_keywords(impact_ko)
        all_keywords.extend(impact_keywords)
    
    # 원본 summary에서 영어 키워드 추출
    original_summary = article.get('summary', '')
    if original_summary and not is_korean_text(original_summary):
        original_summary_keywords = extract_english_keywords(original_summary)
        all_keywords.extend(original_summary_keywords)
    
    # 중복 제거 및 필터링
    unique_keywords = list(set([k for k in all_keywords if len(k) >= 2]))
    
    return unique_keywords

def update_keyword_data():
    """모든 뉴스 데이터에서 키워드를 추출하여 keywords collection 업데이트"""
    try:
        print("🔄 키워드 데이터 업데이트 시작...")
        
        # 모든 뉴스 데이터 가져오기
        news_data = list(news_collection.find({}))
        
        if not news_data:
            print("⚠️ 뉴스 데이터가 없습니다.")
            return
        
        # 키워드 빈도 계산
        keyword_frequency = Counter()
        keyword_articles = defaultdict(list)  # 키워드별 기사 ID 저장
        keyword_cooccurrence = defaultdict(int)  # 키워드 동시 출현
        daily_keywords = defaultdict(lambda: defaultdict(int))  # 날짜별 키워드 빈도
        
        for article in news_data:
            article_id = article.get('_id')
            article_keywords = process_article_keywords(article)
            
            if not article_keywords:
                continue
            
            # 기사 발행일 파싱
            try:
                if isinstance(article.get('published'), str):
                    pub_date = datetime.fromisoformat(article['published'].replace('Z', '+00:00')).date()
                else:
                    pub_date = article.get('published', datetime.utcnow()).date()
            except:
                pub_date = datetime.utcnow().date()
            
            # 키워드 빈도 및 기사 연결 정보 업데이트
            for keyword in article_keywords:
                keyword_frequency[keyword] += 1
                keyword_articles[keyword].append({
                    'article_id': article_id,
                    'title': article.get('title', ''),
                    'published': pub_date.isoformat(),
                    'source': article.get('source', '')
                })
                daily_keywords[pub_date][keyword] += 1
            
            # 키워드 동시 출현 계산
            for i, keyword1 in enumerate(article_keywords):
                for keyword2 in article_keywords[i+1:]:
                    pair = tuple(sorted([keyword1, keyword2]))
                    keyword_cooccurrence[pair] += 1
        
        # keywords collection 업데이트
        keywords_operations = []
        for keyword, frequency in keyword_frequency.items():
            keywords_operations.append(UpdateOne(
                {'keyword': keyword},
                {
                    '$set': {
                        'keyword': keyword,
                        'frequency': frequency,
                        'articles': keyword_articles[keyword],
                        'last_updated': datetime.utcnow()
                    }
                },
                upsert=True
            ))
        
        if keywords_operations:
            keywords_collection.bulk_write(keywords_operations)
            print(f"✅ {len(keywords_operations)}개 키워드 업데이트 완료")
        
        # keyword_trends collection 업데이트
        trends_operations = []
        for date, keywords in daily_keywords.items():
            for keyword, count in keywords.items():
                trends_operations.append(UpdateOne(
                    {'keyword': keyword, 'date': date.isoformat()},
                    {
                        '$set': {
                            'keyword': keyword,
                            'date': date.isoformat(),
                            'count': count,
                            'last_updated': datetime.utcnow()
                        }
                    },
                    upsert=True
                ))
        
        if trends_operations:
            keyword_trends_collection.bulk_write(trends_operations)
            print(f"✅ {len(trends_operations)}개 트렌드 데이터 업데이트 완료")
        
        # 키워드 동시 출현 데이터 저장
        cooccurrence_operations = []
        cooccurrence_collection = client["bitsfeed"]["keyword_cooccurrence"]
        
        for (keyword1, keyword2), count in keyword_cooccurrence.items():
            cooccurrence_operations.append(UpdateOne(
                {'keyword1': keyword1, 'keyword2': keyword2},
                {
                    '$set': {
                        'keyword1': keyword1,
                        'keyword2': keyword2,
                        'count': count,
                        'last_updated': datetime.utcnow()
                    }
                },
                upsert=True
            ))
        
        if cooccurrence_operations:
            cooccurrence_collection.bulk_write(cooccurrence_operations)
            print(f"✅ {len(cooccurrence_operations)}개 동시출현 데이터 업데이트 완료")
        
        print("🎉 키워드 데이터 업데이트 완료!")
        
        return {
            'total_articles': len(news_data),
            'total_keywords': len(keyword_frequency),
            'total_cooccurrences': len(keyword_cooccurrence)
        }
        
    except Exception as e:
        print(f"❌ 키워드 데이터 업데이트 실패: {e}")
        raise e

def get_keyword_frequency(days: Optional[int] = 7, limit: Optional[int] = 50) -> Dict:
    """키워드 빈도 데이터 조회 (MongoDB에서)"""
    try:
        # 날짜 필터링을 위한 pipeline
        pipeline = []
        
        if days:
            cutoff_date = (datetime.now() - timedelta(days=days)).date().isoformat()
            pipeline.append({
                '$match': {
                    'articles.published': {'$gte': cutoff_date}
                }
            })
        
        pipeline.extend([
            {'$sort': {'frequency': -1}},
            {'$limit': limit}
        ])
        
        results = list(keywords_collection.aggregate(pipeline))
        
        top_keywords = {item['keyword']: item['frequency'] for item in results}
        
        return {
            'total_keywords': keywords_collection.count_documents({}),
            'top_keywords': top_keywords,
            'analysis_period_days': days
        }
        
    except Exception as e:
        print(f"❌ 키워드 빈도 조회 실패: {e}")
        return {'error': str(e)}

def get_keyword_trends(days: Optional[int] = 30, top_n: Optional[int] = 10) -> Dict:
    """키워드 트렌드 데이터 조회 (MongoDB에서)"""
    try:
        cutoff_date = (datetime.now() - timedelta(days=days)).date()
        
        # 상위 키워드 선택
        top_keywords = list(keywords_collection.find({}, {'keyword': 1, 'frequency': 1})
                           .sort('frequency', -1).limit(top_n))
        top_keyword_list = [item['keyword'] for item in top_keywords]
        
        # 날짜별 트렌드 데이터 조회
        pipeline = [
            {
                '$match': {
                    'keyword': {'$in': top_keyword_list},
                    'date': {'$gte': cutoff_date.isoformat()}
                }
            },
            {
                '$group': {
                    '_id': {'keyword': '$keyword', 'date': '$date'},
                    'count': {'$sum': '$count'}
                }
            },
            {
                '$sort': {'_id.date': 1}
            }
        ]
        
        results = list(keyword_trends_collection.aggregate(pipeline))
        
        # 데이터 구조화
        trend_data = defaultdict(dict)
        dates = set()
        
        for item in results:
            keyword = item['_id']['keyword']
            date = item['_id']['date']
            count = item['count']
            trend_data[keyword][date] = count
            dates.add(date)
        
        dates = sorted(dates)
        
        # 누락된 날짜는 0으로 채움
        final_trend_data = {}
        for keyword in top_keyword_list:
            daily_counts = []
            for date in dates:
                count = trend_data[keyword].get(date, 0)
                daily_counts.append(count)
            final_trend_data[keyword] = daily_counts
        
        return {
            'trend_data': final_trend_data,
            'dates': dates,
            'top_keywords': top_keyword_list,
            'analysis_days': len(dates)
        }
        
    except Exception as e:
        print(f"❌ 키워드 트렌드 조회 실패: {e}")
        return {'error': str(e)}

def get_keyword_network(days: Optional[int] = 7, min_cooccurrence: Optional[int] = 2) -> Dict:
    """키워드 네트워크 데이터 조회 (MongoDB에서)"""
    try:
        cooccurrence_collection = client["bitsfeed"]["keyword_cooccurrence"]
        
        # 동시 출현 데이터 조회
        query = {'count': {'$gte': min_cooccurrence}}
        cooccurrences = list(cooccurrence_collection.find(query))
        
        if not cooccurrences:
            return {'error': f'최소 {min_cooccurrence}회 이상 함께 나타나는 키워드 쌍이 없습니다.'}
        
        # 네트워크 데이터 구성
        nodes = set()
        edges = []
        
        for item in cooccurrences:
            keyword1 = item['keyword1']
            keyword2 = item['keyword2']
            count = item['count']
            
            nodes.add(keyword1)
            nodes.add(keyword2)
            edges.append({
                'source': keyword1,
                'target': keyword2,
                'weight': count
            })
        
        # 노드별 연결 강도 계산
        node_strength = defaultdict(int)
        for edge in edges:
            node_strength[edge['source']] += edge['weight']
            node_strength[edge['target']] += edge['weight']
        
        nodes_data = [
            {'id': node, 'strength': node_strength[node]}
            for node in nodes
        ]
        
        return {
            'nodes': nodes_data,
            'edges': edges,
            'total_nodes': len(nodes),
            'total_edges': len(edges),
            'min_cooccurrence': min_cooccurrence
        }
        
    except Exception as e:
        print(f"❌ 키워드 네트워크 조회 실패: {e}")
        return {'error': str(e)}

def initialize_keyword_system():
    """키워드 시스템 초기화 (인덱스 생성 + 데이터 업데이트)"""
    print("🚀 키워드 시스템 초기화 시작...")
    create_indexes()
    return update_keyword_data()

if __name__ == "__main__":
    # 테스트 실행
    initialize_keyword_system() 