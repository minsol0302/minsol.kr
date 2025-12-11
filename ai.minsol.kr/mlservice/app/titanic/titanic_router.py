"""
타이타닉 관련 라우터
"""
from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys
import logging

# 공통 모듈 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.titanic.titanic_service import TitanicService

# common 모듈 import 시도
try:
    from common.utils import create_response, create_error_response, setup_logging
except ImportError:
    # common 모듈이 없을 경우 기본 함수 정의
    import logging
    def setup_logging(name: str):
        return logging.getLogger(name)
    def create_response(data: Any, message: str = "Success", status: str = "success") -> Dict:
        from datetime import datetime
        return {
            "status": status,
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
    def create_error_response(message: str, error_code: str = "UNKNOWN_ERROR") -> Dict:
        from datetime import datetime
        return {
            "status": "error",
            "message": message,
            "error_code": error_code,
            "timestamp": datetime.utcnow().isoformat()
        }

# Logger 초기화
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/titanic", tags=["titanic"])

# 서비스 인스턴스 생성 (싱글톤 패턴)
_service_instance: Optional[TitanicService] = None


def get_service() -> TitanicService:
    """TitanicService 싱글톤 인스턴스 반환"""
    global _service_instance
    if _service_instance is None:
        logger.info("TitanicService 인스턴스 생성 중...")
        _service_instance = TitanicService()
        logger.info("TitanicService 인스턴스 생성 완료")
    return _service_instance


@router.get("/")
async def titanic_root():
    """타이타닉 서비스 루트"""
    return create_response(
        data={"service": "mlservice", "module": "titanic", "status": "running"},
        message="Titanic Service is running"
    )





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
        logger.info("=" * 50)
        logger.info("전처리 요청 수신")
        logger.info("=" * 50)
        service = get_service()
        logger.info("서비스 인스턴스 획득 완료, preprocess() 호출 시작")
        service.preprocess()
        logger.info("전처리 완료")
        return create_response(
            data={"message": "전처리가 완료되었습니다. (터미널 로그 확인)"},
            message="Data preprocessing completed"
        )
    except FileNotFoundError as e:
        logger.error(f"파일을 찾을 수 없습니다: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=404, 
            detail=f"파일을 찾을 수 없습니다: {str(e)}"
        )
    except Exception as e:
        logger.error(f"전처리 오류: {str(e)}", exc_info=True)
        import traceback
        error_detail = f"Failed to preprocess data: {str(e)}\n{traceback.format_exc()}"
        logger.error(f"상세 에러: {error_detail}")
        raise HTTPException(status_code=500, detail=error_detail)


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

@router.get("/evaluate")
async def evaluate_model():
    """
    모델 평가 실행
    - 실행 후 모델 평가 결과 반환
    """
    try:
        service = get_service()
        
        # 전처리 확인
        if service.X_train is None:
            return create_response(
                data={"message": "전처리가 필요합니다. 먼저 /preprocess를 실행해주세요."},
                message="Preprocessing required"
            )
        
        # 모델링 및 학습
        service.modeling()
        service.learning()
        
        # 평가 실행
        results = service.evaluate()
        
        # 결과 반환
        return create_response(
            data={
                "results": results,
                "message": "모델 평가가 완료되었습니다."
            },
            message="Model evaluation completed"
        )
    except Exception as e:
        logger = setup_logging("mlservice")
        logger.error(f"평가 오류: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to evaluate models: {str(e)}")


@router.get("/submit")
async def submit_model():
    """
    캐글 제출용 파일 생성
    - 모델 평가를 통해 최고 성능 모델 선택
    - 전체 train 데이터로 재학습
    - test 데이터 예측 및 submission.csv 생성
    - 모델 파일 및 결과 요약 저장
    """
    try:
        service = get_service()
        
        # 전처리 확인
        if service.X_train is None:
            return create_response(
                data={"message": "전처리가 필요합니다. 먼저 /preprocess를 실행해주세요."},
                message="Preprocessing required"
            )
        
        # 모델이 없으면 모델링 및 학습
        if not service.models:
            service.modeling()
            service.learning()
        
        # 제출 실행
        result = service.submit()
        
        if result is None:
            return create_response(
                data={"message": "제출 파일 생성에 실패했습니다."},
                message="Failed to create submission files"
            )
        
        # 결과 반환
        return create_response(
            data={
                "submission_file": result["submission_file"],
                "model_file": result["model_file"],
                "summary_file": result["summary_file"],
                "best_model": result["best_model"],
                "best_accuracy": result["best_accuracy"],
                "message": "캐글 제출 파일이 생성되었습니다. (app/download 폴더 확인)"
            },
            message="Submission files created successfully"
        )
    except Exception as e:
        logger = setup_logging("mlservice")
        logger.error(f"제출 오류: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create submission files: {str(e)}")