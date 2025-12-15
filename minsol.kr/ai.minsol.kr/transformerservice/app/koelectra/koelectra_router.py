"""
KoELECTRA 감정분석 라우터
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys
import logging
from datetime import datetime
from pydantic import BaseModel, Field

# 공통 모듈 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.koelectra.koelectra_service import KoElectraService


# Pydantic 모델 정의
class SentimentAnalysisRequest(BaseModel):
    """감정 분석 요청 모델"""
    text: str = Field(..., description="감정 분석할 텍스트", min_length=1, example="이 영화 정말 재미있어요!")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "이 영화 정말 재미있어요!"
            }
        }


class BatchSentimentAnalysisRequest(BaseModel):
    """배치 감정 분석 요청 모델"""
    texts: List[str] = Field(..., description="감정 분석할 텍스트 리스트", min_items=1, max_items=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "texts": [
                    "이 영화 정말 재미있어요!",
                    "별로 재미없었어요."
                ]
            }
        }

# common 모듈 import 시도
try:
    from common.utils import create_response, create_error_response
except ImportError:
    # common 모듈이 없을 경우 기본 함수 정의
    def create_response(data: Any, message: str = "Success", status: str = "success") -> Dict:
        return {
            "status": status,
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def create_error_response(message: str, error_code: str = "UNKNOWN_ERROR") -> Dict:
        return {
            "status": "error",
            "message": message,
            "error_code": error_code,
            "timestamp": datetime.utcnow().isoformat()
        }

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/koelectra", tags=["koelectra"])

# 서비스 인스턴스 생성 (싱글톤 패턴)
_service_instance: Optional[KoElectraService] = None


def get_service() -> KoElectraService:
    """KoElectraService 싱글톤 인스턴스 반환"""
    global _service_instance
    if _service_instance is None:
        logger.info("KoElectraService 인스턴스 생성 중...")
        try:
            _service_instance = KoElectraService()
            logger.info("KoElectraService 인스턴스 생성 완료")
        except Exception as e:
            logger.error(f"KoElectraService 인스턴스 생성 실패: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"모델 로딩 실패: {str(e)}"
            )
    return _service_instance


@router.get("/")
async def koelectra_root():
    """KoELECTRA 서비스 루트"""
    return create_response(
        data={
            "service": "transformer",
            "module": "koelectra",
            "status": "running",
            "description": "KoELECTRA 기반 영화 리뷰 감정분석 서비스"
        },
        message="KoELECTRA Sentiment Analysis Service is running"
    )


@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_sentiment(request: SentimentAnalysisRequest):
    """
    단일 텍스트에 대한 감정 분석
    
    영화 리뷰나 감정이 포함된 텍스트를 입력하면 긍정/부정 감정을 분석합니다.
    
    **요청 예시:**
    ```json
    {
        "text": "이 영화 정말 재미있어요!"
    }
    ```
    
    **응답 예시:**
    ```json
    {
        "status": "success",
        "message": "감정 분석이 완료되었습니다.",
        "data": {
            "text": "이 영화 정말 재미있어요!",
            "sentiment": "positive",
            "confidence": 0.9823,
            "scores": {
                "positive": 0.9823,
                "negative": 0.0177
            }
        },
        "timestamp": "2025-01-12T10:00:00"
    }
    ```
    """
    try:
        if not request.text or not request.text.strip():
            raise HTTPException(
                status_code=400,
                detail="텍스트가 비어있습니다."
            )
        
        service = get_service()
        result = service.predict(request.text)
        
        return create_response(
            data=result,
            message="감정 분석이 완료되었습니다."
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"입력 검증 오류: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"감정 분석 오류: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"감정 분석 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/analyze-batch", response_model=Dict[str, Any])
async def analyze_sentiment_batch(request: BatchSentimentAnalysisRequest):
    """
    여러 텍스트에 대한 배치 감정 분석
    
    최대 100개의 텍스트를 한 번에 분석할 수 있습니다.
    
    **요청 예시:**
    ```json
    {
        "texts": [
            "이 영화 정말 재미있어요!",
            "별로 재미없었어요."
        ]
    }
    ```
    
    **응답 예시:**
    ```json
    {
        "status": "success",
        "message": "2개의 텍스트 분석이 완료되었습니다.",
        "data": {
            "results": [
                {
                    "text": "이 영화 정말 재미있어요!",
                    "sentiment": "positive",
                    "confidence": 0.9823,
                    "scores": {
                        "positive": 0.9823,
                        "negative": 0.0177
                    }
                },
                {
                    "text": "별로 재미없었어요.",
                    "sentiment": "negative",
                    "confidence": 0.8765,
                    "scores": {
                        "positive": 0.1235,
                        "negative": 0.8765
                    }
                }
            ],
            "total": 2,
            "success_count": 2
        },
        "timestamp": "2025-01-12T10:00:00"
    }
    ```
    """
    try:
        if not request.texts:
            raise HTTPException(
                status_code=400,
                detail="텍스트 리스트가 비어있습니다."
            )
        
        if len(request.texts) > 100:
            raise HTTPException(
                status_code=400,
                detail="한 번에 최대 100개의 텍스트만 처리할 수 있습니다."
            )
        
        service = get_service()
        results = service.predict_batch(request.texts)
        
        return create_response(
            data={
                "results": results,
                "total": len(results),
                "success_count": sum(1 for r in results if r.get("sentiment") != "error")
            },
            message=f"{len(results)}개의 텍스트 분석이 완료되었습니다."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"배치 감정 분석 오류: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"배치 감정 분석 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """
    모델 로드 상태 확인
    
    KoELECTRA 모델이 정상적으로 로드되었는지 확인합니다.
    """
    try:
        service = get_service()
        model_info = service.get_model_info()
        
        if model_info["is_loaded"]:
            return create_response(
                data=model_info,
                message="모델이 정상적으로 로드되었습니다."
            )
        else:
            return create_error_response(
                message="모델이 로드되지 않았습니다.",
                error_code="MODEL_NOT_LOADED"
            )
    except Exception as e:
        logger.error(f"헬스 체크 오류: {str(e)}", exc_info=True)
        return create_error_response(
            message=f"헬스 체크 중 오류가 발생했습니다: {str(e)}",
            error_code="HEALTH_CHECK_ERROR"
        )


@router.get("/model-info", response_model=Dict[str, Any])
async def get_model_info():
    """
    모델 정보 조회
    
    현재 로드된 KoELECTRA 모델의 상세 정보를 조회합니다.
    """
    try:
        service = get_service()
        model_info = service.get_model_info()
        
        return create_response(
            data=model_info,
            message="모델 정보를 조회했습니다."
        )
    except Exception as e:
        logger.error(f"모델 정보 조회 오류: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"모델 정보 조회 중 오류가 발생했습니다: {str(e)}"
        )

