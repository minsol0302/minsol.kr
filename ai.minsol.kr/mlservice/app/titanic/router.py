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
from app.titanic.titanic_model import TitanicModels
from common.utils import create_response, create_error_response

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
        service.load_train_data()
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
        service = get_service()
        passengers = service.get_passenger_list(limit=limit)
        return create_response(
            data={"passengers": passengers, "count": len(passengers)},
            message=f"Successfully retrieved {len(passengers)} passengers"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get passengers: {str(e)}")


@router.get("/statistics")
async def get_statistics():
    """데이터 통계 정보 조회"""
    try:
        service = get_service()
        stats = service.get_statistics()
        return create_response(
            data=stats,
            message="Successfully retrieved statistics"
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
        results = service.train_model(
            test_size=test_size,
            random_state=random_state,
            n_estimators=n_estimators
        )
        return create_response(
            data=results,
            message=f"Model trained successfully with accuracy: {results['accuracy']:.4f}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to train model: {str(e)}")


@router.post("/predict")
async def predict_survival(passenger_data: Dict[str, Any] = Body(..., description="승객 정보")):
    """승객 생존 예측"""
    try:
        service = get_service()
        
        # 모델이 훈련되지 않은 경우
        if service.model is None:
            raise HTTPException(
                status_code=400,
                detail="Model not trained. Please train the model first by calling /titanic/train"
            )
        
        prediction = service.predict(passenger_data)
        return create_response(
            data=prediction,
            message=f"Prediction completed. Survived: {prediction['survived']}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to predict: {str(e)}")


@router.post("/predict-batch")
async def predict_batch(passengers_data: List[Dict[str, Any]] = Body(..., description="승객 정보 리스트")):
    """여러 승객 생존 예측 (배치)"""
    try:
        service = get_service()
        
        # 모델이 훈련되지 않은 경우
        if service.model is None:
            raise HTTPException(
                status_code=400,
                detail="Model not trained. Please train the model first by calling /titanic/train"
            )
        
        predictions = []
        for passenger_data in passengers_data:
            try:
                prediction = service.predict(passenger_data)
                predictions.append({
                    "passenger_data": passenger_data,
                    "prediction": prediction
                })
            except Exception as e:
                predictions.append({
                    "passenger_data": passenger_data,
                    "error": str(e)
                })
        
        return create_response(
            data={"predictions": predictions, "count": len(predictions)},
            message=f"Batch prediction completed for {len(predictions)} passengers"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to predict batch: {str(e)}")


@router.get("/model/status")
async def get_model_status():
    """모델 훈련 상태 확인"""
    try:
        service = get_service()
        is_trained = service.model is not None
        return create_response(
            data={
                "is_trained": is_trained,
                "has_scaler": service.scaler is not None,
                "has_label_encoders": len(service.label_encoders) > 0
            },
            message="Model status retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get model status: {str(e)}")