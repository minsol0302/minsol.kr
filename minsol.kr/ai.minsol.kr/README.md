# AI Services - FastAPI MSA 구조

이 디렉토리는 FastAPI 기반 마이크로서비스 아키텍처로 구성된 AI 서비스들을 포함합니다.

## 구조

```
ai.labzang.com/
├── common/                    # 공통 라이브러리
│   ├── __init__.py
│   ├── config.py              # 공통 설정 관리
│   ├── exceptions.py          # 공통 예외 클래스
│   ├── utils.py               # 유틸리티 함수
│   └── middleware.py          # 공통 미들웨어
│
├── authservice/               # 인증 서비스 (포트: 9002)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI 앱 진입점
│   │   ├── config.py          # 서비스별 설정
│   │   └── routers/           # API 라우터
│   │       ├── __init__.py
│   │       └── auth.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── crawlerservice/            # 크롤링 서비스 (포트: 9001)
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── routers/
│   │   │   └── crawler.py
│   │   └── bs_demo/           # 크롤링 로직
│   ├── Dockerfile
│   └── requirements.txt
│
└── chatbotservice/            # 챗봇 서비스 (포트: 9003)
    ├── app/
    │   ├── main.py
    │   ├── config.py
    │   └── routers/
    │       └── chatbot.py
    ├── Dockerfile
    └── requirements.txt
```

## 공통 라이브러리 (common/)

모든 서비스에서 공유하는 코드:

- **config.py**: 공통 설정 관리 (BaseServiceConfig, DatabaseConfig, RedisConfig)
- **exceptions.py**: 공통 예외 클래스 (ServiceException, NotFoundException, ValidationException)
- **utils.py**: 유틸리티 함수 (로깅, 응답 형식 생성)
- **middleware.py**: 공통 미들웨어 (로깅, CORS)

## 서비스 구조

각 서비스는 다음 구조를 따릅니다:

```
service/
├── app/
│   ├── main.py              # FastAPI 앱 진입점
│   ├── config.py            # 서비스별 설정
│   ├── routers/             # API 라우터
│   ├── services/            # 비즈니스 로직 (선택)
│   └── models/              # 데이터 모델 (선택)
├── Dockerfile
└── requirements.txt
```

## 실행 방법

### 로컬 개발

```bash
# 각 서비스 디렉토리에서
cd authservice
pip install -r requirements.txt
python -m app.main

# 또는 uvicorn 직접 실행
uvicorn app.main:app --host 0.0.0.0 --port 9002 --reload
```

### Docker 빌드 및 실행

```bash
# 개별 서비스 빌드
docker build -t authservice:latest ./ai.labzang.com/authservice
docker build -t crawlerservice:latest ./ai.labzang.com/crawlerservice
docker build -t chatbotservice:latest ./ai.labzang.com/chatbotservice

# Docker Compose로 전체 실행
docker compose --profile ai up
```

## 서비스 포트

- **authservice**: 9002
- **crawlerservice**: 9001
- **chatbotservice**: 9003

## 공통 기능

### 표준 응답 형식

모든 API는 다음 형식으로 응답합니다:

```json
{
  "status": "success",
  "message": "Success",
  "data": {...},
  "timestamp": "2025-12-02T16:00:00"
}
```

### 에러 응답 형식

```json
{
  "status": "error",
  "message": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2025-12-02T16:00:00"
}
```

### 로깅

모든 서비스는 표준화된 로깅을 사용합니다:
- 요청/응답 로깅
- 처리 시간 측정
- 에러 로깅

## 환경 변수

각 서비스는 `.env` 파일을 통해 설정을 관리할 수 있습니다:

```env
# 서비스 기본 설정
SERVICE_NAME=service_name
SERVICE_VERSION=1.0.0
DEBUG=false

# 데이터베이스 (필요시)
DATABASE_URL=postgresql://user:pass@host:port/db

# Redis (필요시)
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=
```

## 개발 가이드

### 새 서비스 추가

1. `ai.labzang.com/` 하위에 새 서비스 디렉토리 생성
2. `app/` 디렉토리 구조 생성
3. `common/` 모듈 import하여 사용
4. `Dockerfile` 및 `requirements.txt` 작성
5. `docker-compose.yaml`에 서비스 추가

### 공통 기능 사용

```python
from common.config import BaseServiceConfig
from common.exceptions import NotFoundException
from common.utils import create_response, setup_logging
from common.middleware import LoggingMiddleware
```

## API 문서

각 서비스는 FastAPI 자동 문서를 제공합니다:
- Swagger UI: `http://localhost:{port}/docs`
- ReDoc: `http://localhost:{port}/redoc`

