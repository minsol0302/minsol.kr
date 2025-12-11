"""
Titanic Service - FastAPI 애플리케이션
"""
import sys
import csv
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# 공통 모듈 경로 추가 (최우선)
current_file = Path(__file__).resolve()
base_dir = current_file.parent.parent  # /app (Docker) 또는 mlservice (로컬)

# 경로 추가
base_path_str = str(base_dir)
if base_path_str not in sys.path:
    sys.path.insert(0, base_path_str)

# Docker 환경 확인 및 /app 경로 추가
if os.path.exists("/app"):
    if "/app" not in sys.path:
        sys.path.insert(0, "/app")

# 설정 로드 (경로 설정 후)
try:
    from app.config import TitanicServiceConfig
    config = TitanicServiceConfig()
except Exception as e:
    # config.py를 찾을 수 없는 경우 기본값 사용
    class Config:
        service_name = "mlservice"
        service_version = "1.0.0"
        port = 9010
    config = Config()

# 라우터 및 공통 모듈 import
LoggingMiddleware = None
seoul_router = None
try:
    from app.titanic.titanic_router import router as titanic_router
    from app.seoul_crime.seoul_router import router as seoul_router
    from common.middleware import LoggingMiddleware
    from common.utils import setup_logging
except ImportError as e:
    # 모듈을 찾을 수 없는 경우 기본값 사용
    from fastapi import APIRouter
    titanic_router = APIRouter()
    seoul_router = APIRouter()
    def setup_logging(name):
        import logging
        return logging.getLogger(name)

# 로깅 설정
import logging
logging.basicConfig(level=logging.INFO)
logger = setup_logging(config.service_name)

# FastAPI 앱 생성
app = FastAPI(
    title="Titanic Service API",
    description="""
    ## 타이타닉 데이터 서비스 API
    
    머신러닝을 활용한 타이타닉 승객 데이터 분석 및 생존 예측 서비스입니다.
    
    ### 주요 기능
    - 승객 데이터 조회 및 통계 분석
    - 머신러닝 모델 훈련 (Random Forest)
    - 승객 생존 예측
    - 배치 예측 지원
    
    ### 기술 스택
    - **Framework**: FastAPI
    - **ML Library**: scikit-learn, pandas, numpy
    - **Model**: Random Forest Classifier
    
    ### API 문서
    - Swagger UI: `/docs`
    - ReDoc: `/redoc`
    - OpenAPI Schema: `/openapi.json`
    """,
    version=config.service_version,
    contact={
        "name": "ML Service Team",
        "email": "support@labzang.com",
    },
    license_info={
        "name": "MIT",
    },
    tags_metadata=[
        {
            "name": "titanic",
            "description": "타이타닉 승객 데이터 관련 API",
        },
    ],
    openapi_tags=[
        {
            "name": "titanic",
            "description": "타이타닉 승객 데이터 및 머신러닝 예측 기능",
        },
    ],
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 미들웨어 추가
if LoggingMiddleware is not None:
    app.add_middleware(LoggingMiddleware)

# 라우터 등록
# Gateway에서 이미 /ml로 rewrite하므로 prefix 없이 등록
app.include_router(titanic_router, prefix="/titanic")
if seoul_router is not None:
    app.include_router(seoul_router, prefix="/seoul")

# CSV 파일 경로
CSV_FILE_PATH = Path(__file__).parent / "resources" / "titanic" / "train.csv"


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "service": config.service_name,
        "version": config.service_version,
        "message": "Titanic Service API"
    }


@app.on_event("startup")
async def startup_event():
    """서비스 시작 시 실행"""
    logger.info(f"{config.service_name} v{config.service_version} started")


@app.on_event("shutdown")
async def shutdown_event():
    """서비스 종료 시 실행"""
    logger.info(f"{config.service_name} shutting down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.port)
