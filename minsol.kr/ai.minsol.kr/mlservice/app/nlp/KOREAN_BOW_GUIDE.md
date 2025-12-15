# 한국어 BoW (Bag of Words) 사용 가이드

## 1. 개요

이 가이드는 한국어 텍스트 분석을 위한 BoW 구축 및 지속적 사용 전략을 설명합니다.

## 2. 설치된 라이브러리

### Mecab (추천)
- **장점**: 가장 빠른 처리 속도, 높은 정확도
- **용도**: 대용량 텍스트 처리, 실시간 분석
- **설치 위치**: Docker 빌드 시 자동 설치

### Okt (Twitter) (대체)
- **장점**: 설치 간편, 신조어 처리 우수
- **용도**: 소셜 미디어 텍스트 분석
- **설치**: KoNLPy에 포함

## 3. 사용 방법

### 3.1 기본 사용

```python
from app.nlp.korean_bow_service import KoreanBowService

# 서비스 초기화
service = KoreanBowService(use_mecab=True)

# 텍스트에서 BoW 생성
text = "삼성전자가 새로운 스마트폰을 출시했습니다."
bow = service.create_bow(text, pos_filter=['Noun'])
print(bow)  # {'삼성전자': 1, '스마트폰': 1, '출시': 1}
```

### 3.2 파일에서 BoW 생성

```python
# 파일에서 직접 BoW 생성
bow = service.create_bow_from_file(
    'data/kr-Report_2018.txt',
    pos_filter=['Noun', 'Verb'],  # 명사와 동사만
    top_n=100,  # 상위 100개만
    encoding='utf-8'
)

# BoW 저장
service.save_bow(bow, 'save/korean_bow.json', format='json')
```

### 3.3 품사 필터링

```python
# 명사만 추출
nouns = service.extract_nouns(text)

# 명사 + 동사 + 형용사
bow = service.create_bow(
    text,
    pos_filter=['Noun', 'Verb', 'Adjective']
)
```

### 3.4 불용어 관리

```python
# 불용어 추가
service.add_stopwords(['것', '수', '등'])

# 사용자 사전 추가
service.add_user_dict({
    '갤럭시': 'Noun',
    '아이폰': 'Noun',
    '스마트워치': 'Noun'
})
```

## 4. Docker 환경 설정

### 4.1 Dockerfile 설정 (자동)

```dockerfile
# Mecab 자동 설치
RUN curl -s https://raw.githubusercontent.com/konlpy/konlpy/master/scripts/mecab.sh | bash -s

# KoNLPy 초기화
RUN python -c "from konlpy.tag import Okt; okt = Okt()" || true
```

### 4.2 사전 파일 영구 저장

Docker volume을 사용하여 사전과 캐시를 호스트에 저장:

```yaml
# docker-compose.yaml
volumes:
  - ./ai.minsol.kr/mlservice/app/nlp/data:/app/app/nlp/data
  - ./ai.minsol.kr/mlservice/app/nlp/cache:/app/app/nlp/cache
  - ./ai.minsol.kr/mlservice/app/nlp/save:/app/app/nlp/save
```

## 5. 지속적 사용 전략

### 5.1 사전 파일 구조

```
nlp/
├── data/
│   ├── stopwords.txt          # 한국어 불용어
│   ├── user_dict.txt          # 사용자 사전
│   └── kr-Report_2018.txt     # 소스 텍스트
├── cache/                     # 처리된 BoW 캐시
│   ├── korean_bow_nouns.json
│   └── korean_bow_full.pickle
└── save/                      # 결과 저장
    ├── wordcloud_*.png
    └── bow_analysis_*.json
```

### 5.2 캐싱 전략

```python
import hashlib
from pathlib import Path

def get_cache_key(text: str, options: dict) -> str:
    """텍스트와 옵션으로 캐시 키 생성"""
    content = f"{text}{str(options)}"
    return hashlib.md5(content.encode()).hexdigest()

def get_cached_bow(cache_key: str, cache_dir: Path):
    """캐시에서 BoW 로드"""
    cache_file = cache_dir / f"{cache_key}.json"
    if cache_file.exists():
        return service.load_bow(cache_file)
    return None

# 사용 예
cache_key = get_cache_key(text, {'pos_filter': ['Noun']})
cached = get_cached_bow(cache_key, Path('cache'))
if cached:
    bow = cached
else:
    bow = service.create_bow(text, pos_filter=['Noun'])
    service.save_bow(bow, f'cache/{cache_key}.json')
```

### 5.3 배치 처리

```python
from pathlib import Path
import logging

def process_multiple_files(file_pattern: str):
    """여러 파일을 배치로 처리"""
    service = KoreanBowService()
    results = {}
    
    for file_path in Path('data').glob(file_pattern):
        logger.info(f"처리 중: {file_path}")
        bow = service.create_bow_from_file(
            str(file_path),
            pos_filter=['Noun'],
            top_n=100
        )
        results[file_path.name] = bow
        
        # 개별 저장
        service.save_bow(
            bow,
            f'save/{file_path.stem}_bow.json'
        )
    
    return results
```

## 6. 성능 최적화

### 6.1 Mecab 사용 (최대 10배 빠름)

```python
# Mecab 사용 (권장)
service = KoreanBowService(use_mecab=True)

# Okt 사용 (Mecab 없을 때)
service = KoreanBowService(use_mecab=False)
```

### 6.2 대용량 파일 처리

```python
def process_large_file(file_path: str, chunk_size: int = 10000):
    """대용량 파일을 청크로 나눠 처리"""
    service = KoreanBowService()
    total_bow = Counter()
    
    with open(file_path, 'r', encoding='utf-8') as f:
        chunk = []
        for line in f:
            chunk.append(line)
            if len(chunk) >= chunk_size:
                text = ''.join(chunk)
                bow = service.create_bow(text, pos_filter=['Noun'])
                total_bow.update(bow)
                chunk = []
        
        # 마지막 청크 처리
        if chunk:
            text = ''.join(chunk)
            bow = service.create_bow(text, pos_filter=['Noun'])
            total_bow.update(bow)
    
    return dict(total_bow)
```

## 7. API 통합 예제

```python
# nlp_router.py에 추가
from app.nlp.korean_bow_service import KoreanBowService

@router.post("/korean/bow")
async def create_korean_bow(
    text: str = Body(...),
    pos_filter: Optional[List[str]] = Body(default=['Noun']),
    top_n: Optional[int] = Body(default=50)
):
    """한국어 BoW 생성 API"""
    service = KoreanBowService()
    bow = service.create_bow(text, pos_filter, top_n)
    stats = service.analyze_text_statistics(text, pos_filter)
    
    return {
        "bow": bow,
        "statistics": stats
    }
```

## 8. 사전 관리

### 8.1 불용어 파일 (data/stopwords.txt)

```text
것
수
등
때
곳
```

### 8.2 사용자 사전 추가

```python
# 프로그래밍 방식
service.add_user_dict({
    '갤럭시노트': 'Noun',
    '인공지능': 'Noun',
    '머신러닝': 'Noun'
})

# 또는 Mecab 사용자 사전 파일 생성
# /usr/local/lib/mecab/dic/mecab-ko-dic/user-dic/
```

## 9. 트러블슈팅

### 9.1 Mecab 설치 실패

```bash
# Docker 컨테이너 내부에서
apt-get update
apt-get install -y curl git
bash <(curl -s https://raw.githubusercontent.com/konlpy/konlpy/master/scripts/mecab.sh)
```

### 9.2 Java 오류

```bash
# Java 확인
java -version

# Java 설치
apt-get install -y default-jdk
export JAVA_HOME=/usr/lib/jvm/default-java
```

### 9.3 메모리 부족

```python
# 청크 크기 줄이기
bow = service.create_bow_from_file(
    'large_file.txt',
    top_n=1000  # 상위 1000개만 유지
)
```

## 10. 참고 자료

- [KoNLPy 공식 문서](https://konlpy.org/)
- [Mecab 설치 가이드](https://bitbucket.org/eunjeon/mecab-ko-dic)
- [한국어 NLP 리소스](https://github.com/konlpy/konlpy)

