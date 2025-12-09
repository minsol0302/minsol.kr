"""
타이타닉 관련 라우터
"""
from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys

# 공통 모듈 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.titanic.titanic_service import TitanicService
from common.utils import create_response, create_error_response, setup_logging

router = APIRouter(prefix="/titanic", tags=["titanic"])

# 서비스 인스턴스 생성 (싱글톤 패턴)
_service_instance: Optional[TitanicService] = None


def get_service() -> TitanicService:
    """TitanicService 싱글톤 인스턴스 반환"""
    global _service_instance
    if _service_instance is None:
        _service_instance = TitanicService()
    return _service_instance


@router.get("/")
async def titanic_root():
    """타이타닉 서비스 루트"""
    return create_response(
        data={"service": "mlservice", "module": "titanic", "status": "running"},
        message="Titanic Service is running"
    )


@router.get("/health")
async def health_check():
    """헬스 체크"""
    try:
        service = get_service()
        return create_response(
            data={"status": "healthy", "service": "titanic"},
            message="Titanic service is healthy"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Service unhealthy: {str(e)}")


@router.get("/passengers")
async def get_passengers(limit: int = Query(default=10, ge=1, le=100, description="조회할 승객 수")):
    """승객 목록 조회"""
    try:
        return create_response(
            data={"message": "이 기능은 아직 구현되지 않았습니다."},
            message="Passenger list endpoint is not yet implemented"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get passengers: {str(e)}")


@router.get("/statistics")
async def get_statistics():
    """데이터 통계 정보 조회"""
    try:
        return create_response(
            data={"message": "이 기능은 아직 구현되지 않았습니다."},
            message="Statistics endpoint is not yet implemented"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@router.post("/train")
async def train_model(
    test_size: float = Body(default=0.2, ge=0.1, le=0.5, description="테스트 데이터 비율"),
    random_state: int = Body(default=42, description="랜덤 시드"),
    n_estimators: int = Body(default=100, ge=10, le=1000, description="랜덤 포레스트 트리 개수")
):
    """머신러닝 모델 훈련"""
    try:
        service = get_service()
        service.learning()
        return create_response(
            data={"message": "학습이 완료되었습니다. (터미널 로그 확인)"},
            message="Model training completed"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to train model: {str(e)}")


@router.post("/predict")
async def predict_survival(passenger_data: Dict[str, Any] = Body(..., description="승객 정보")):
    """승객 생존 예측"""
    try:
        return create_response(
            data={"message": "이 기능은 아직 구현되지 않았습니다."},
            message="Prediction endpoint is not yet implemented"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to predict: {str(e)}")


@router.post("/predict-batch")
async def predict_batch(passengers_data: List[Dict[str, Any]] = Body(..., description="승객 정보 리스트")):
    """여러 승객 생존 예측 (배치)"""
    try:
        return create_response(
            data={"message": "이 기능은 아직 구현되지 않았습니다."},
            message="Batch prediction endpoint is not yet implemented"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to predict batch: {str(e)}")


@router.get("/preprocess")
async def preprocess_data():
    """데이터 전처리"""
    try:
        service = get_service()
        service.preprocess()
        return create_response(
            data={"message": "전처리가 완료되었습니다. (터미널 로그 확인)"},
            message="Data preprocessing completed"
        )
    except Exception as e:
        logger = setup_logging("mlservice")
        logger.error(f"전처리 오류: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to preprocess data: {str(e)}")


@router.get("/model/status")
async def get_model_status():
    """모델 훈련 상태 확인"""
    try:
        return create_response(
            data={
                "is_trained": False,
                "message": "이 기능은 아직 구현되지 않았습니다."
            },
            message="Model status endpoint is not yet implemented"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get model status: {str(e)}")