"""
Transformer Service - FastAPI 애플리케이션
KoELECTRA 기반 감정분석 서비스
"""
import sys
import os
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 공통 모듈 경로 추가
current_file = Path(__file__).resolve()
base_dir = current_file.parent.parent  # transformer 디렉토리

# 경로 추가
base_path_str = str(base_dir)
if base_path_str not in sys.path:
    sys.path.insert(0, base_path_str)

# Docker 환경 확인 및 /app 경로 추가
if os.path.exists("/app"):
    if "/app" not in sys.path:
        sys.path.insert(0, "/app")

# 설정 로드
try:
    from app.config import TransformerServiceConfig
    config = TransformerServiceConfig()
except Exception as e:
    # config.py를 찾을 수 없는 경우 기본값 사용
    class Config:
        service_name = "transformer"
        service_version = "1.0.0"
        port = 9004
    config = Config()

# 로깅 기본 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 라우터 import
try:
    from app.koelectra.koelectra_router import router as koelectra_router
    logger.info("koelectra_router import 성공")
except ImportError as e:
    logger.error(f"koelectra_router import 실패: {e}", exc_info=True)
    from fastapi import APIRouter
    koelectra_router = APIRouter()

# 공통 모듈 import
try:
    from common.middleware import LoggingMiddleware
    from common.utils import setup_logging
except ImportError as e:
    logger.warning(f"common 모듈 import 실패: {e}")
    LoggingMiddleware = None
    def setup_logging(name):
        return logging.getLogger(name)

# 로깅 설정
logger = setup_logging(config.service_name)

# FastAPI 앱 생성
app = FastAPI(
    title="Transformer Service API",
    description="""
    ## KoELECTRA 기반 감정분석 서비스 API
    
    허깅페이스 transformers를 사용한 영화 리뷰 감정분석 서비스입니다.
    
    ### 주요 기능
    - 단일 텍스트 감정 분석
    - 배치 텍스트 감정 분석
    - 모델 상태 확인
    
    ### 기술 스택
    - **Framework**: FastAPI
    - **Model**: KoELECTRA
    - **Library**: transformers, PyTorch
    
    ### API 문서
    - Swagger UI: `/docs`
    - ReDoc: `/redoc`
    - OpenAPI Schema: `/openapi.json`
    """,
    version=config.service_version,
    contact={
        "name": "Transformer Service Team",
        "email": "support@minsol.kr",
    },
    license_info={
        "name": "MIT",
    },
    tags_metadata=[
        {
            "name": "koelectra",
            "description": "KoELECTRA 기반 감정분석 API",
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
app.include_router(koelectra_router)


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "service": config.service_name,
        "version": config.service_version,
        "message": "Transformer Service API - KoELECTRA Sentiment Analysis",
        "endpoints": {
            "analyze": "/koelectra/analyze",
            "analyze_batch": "/koelectra/analyze-batch",
            "health": "/koelectra/health",
            "model_info": "/koelectra/model-info"
        }
    }


@app.on_event("startup")
async def startup_event():
    """서비스 시작 시 실행"""
    logger.info(f"{config.service_name} v{config.service_version} started")
    logger.info("KoELECTRA 감정분석 서비스가 시작되었습니다.")


@app.on_event("shutdown")
async def shutdown_event():
    """서비스 종료 시 실행"""
    logger.info(f"{config.service_name} shutting down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.port)

