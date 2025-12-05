"""
Titanic 라우터 모듈
Titanic 관련 API 엔드포인트 정의
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Optional
import pandas as pd
from pathlib import Path

from app.titanic.service import get_titanic_service
from app.titanic.schemas import (
    PassengerData,
    PredictionResponse,
    TrainRequest,
    TrainResponse,
    DataInfoResponse,
    ModelStatusResponse,
    ServiceInfoResponse
)

# APIRouter 생성
router = APIRouter(
    prefix="/titanic",
    tags=["titanic"]
)

# 데이터 디렉토리 경로
DATA_DIR = Path(__file__).parent


@router.get(
    "/",
    response_model=ServiceInfoResponse,
    summary="Titanic 서비스 정보",
    description="Titanic ML 서비스의 기본 정보와 사용 가능한 엔드포인트 목록을 반환합니다."
)
async def titanic_root():
    """
    Titanic 서비스 루트 엔드포인트
    
    사용 가능한 모든 엔드포인트 목록을 반환합니다.
    """
    return {
        "service": "Titanic ML Service",
        "endpoints": [
            "/titanic/data/info",
            "/titanic/train",
            "/titanic/predict",
            "/titanic/model/status"
        ]
    }


@router.get(
    "/data/info",
    response_model=DataInfoResponse,
    summary="학습 데이터 정보 조회",
    description="train.csv 파일의 데이터 정보를 조회합니다. (행/열 수, 컬럼 정보, 결측치, 통계 등)"
)
async def get_data_info():
    """
    학습 데이터 정보 조회
    
    다음 정보를 포함합니다:
    - 데이터 형태 (행, 열 수)
    - 컬럼 목록 및 데이터 타입
    - 결측치 정보
    - 통계 정보
    - 생존 분포 (Survived 컬럼이 있는 경우)
    """
    try:
        service = get_titanic_service()
        df = service.load_data("train.csv")
        info = service.get_data_info(df)
        return {
            "status": "success",
            "data": info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 정보 조회 실패: {str(e)}")


@router.get(
    "/train",
    response_model=TrainResponse,
    summary="모델 학습",
    description="Random Forest 분류 모델을 학습합니다. (GET 요청, 쿼리 파라미터 사용)"
)
async def train_model(
    test_size: float = Query(0.2, description="검증 데이터 비율", ge=0.1, le=0.5),
    random_state: int = Query(42, description="랜덤 시드"),
    n_estimators: int = Query(100, description="랜덤 포레스트 트리 개수", ge=10, le=1000)
):
    """
    모델 학습
    
    Random Forest 분류기를 사용하여 생존 예측 모델을 학습합니다.
    
    **학습 파라미터 (쿼리 파라미터):**
    - **test_size**: 검증 데이터 비율 (0.1 ~ 0.5) - 기본값: 0.2
    - **random_state**: 랜덤 시드 - 기본값: 42
    - **n_estimators**: 랜덤 포레스트 트리 개수 (10 ~ 1000) - 기본값: 100
    
    **반환 정보:**
    - 정확도 (accuracy)
    - 분류 리포트 (classification_report)
    - 혼동 행렬 (confusion_matrix)
    - 특징 중요도 (feature_importance)
    
    **사용 예시:**
    - 기본값 사용: `GET /titanic/train`
    - 파라미터 지정: `GET /titanic/train?test_size=0.3&n_estimators=200`
    """
    try:
        service = get_titanic_service()
        df = service.load_data("train.csv")
        result = service.train_model(
            df,
            test_size=test_size,
            random_state=random_state,
            n_estimators=n_estimators
        )
        return {
            "status": "success",
            "message": "모델 학습이 완료되었습니다.",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"모델 학습 실패: {str(e)}")


@router.get(
    "/predict",
    response_model=PredictionResponse,
    summary="생존 예측",
    description="학습된 모델을 사용하여 승객의 생존 여부를 예측합니다. (GET 요청, 쿼리 파라미터 사용)"
)
async def predict_survival(
    Pclass: int = Query(..., description="승객 등급 (1, 2, 3)", ge=1, le=3),
    Sex: str = Query(..., description="성별 (male, female)"),
    SibSp: int = Query(..., description="형제/배우자 수", ge=0),
    Parch: int = Query(..., description="부모/자녀 수", ge=0),
    Age: Optional[float] = Query(None, description="나이", ge=0, le=120),
    Fare: Optional[float] = Query(None, description="요금", ge=0),
    Embarked: Optional[str] = Query(None, description="탑승 항구 (S, C, Q)"),
    Cabin: Optional[str] = Query(None, description="객실 번호"),
    Ticket: Optional[str] = Query(None, description="티켓 번호"),
    Name: Optional[str] = Query(None, description="이름"),
    PassengerId: Optional[int] = Query(None, description="승객 ID")
):
    """
    생존 예측
    
    학습된 모델을 사용하여 주어진 승객 정보로 생존 여부를 예측합니다.
    
    **필수 쿼리 파라미터:**
    - **Pclass**: 승객 등급 (1, 2, 3)
    - **Sex**: 성별 (male, female)
    - **SibSp**: 형제/배우자 수
    - **Parch**: 부모/자녀 수
    
    **선택 쿼리 파라미터:**
    - **Age**: 나이
    - **Fare**: 요금
    - **Embarked**: 탑승 항구 (S, C, Q)
    - **Cabin**: 객실 번호
    - **Ticket**: 티켓 번호
    - **Name**: 이름
    - **PassengerId**: 승객 ID
    
    **반환 정보:**
    - 예측 결과 (0: 사망, 1: 생존)
    - 예측 라벨
    - 생존 확률 (사망/생존 각각의 확률)
    
    **주의:** 모델이 학습되지 않은 경우 400 에러가 반환됩니다.
    
    **사용 예시:**
    - 최소 필수 파라미터: `GET /titanic/predict?Pclass=3&Sex=male&SibSp=1&Parch=0`
    - 전체 파라미터: `GET /titanic/predict?Pclass=3&Sex=male&Age=22.0&SibSp=1&Parch=0&Fare=7.25&Embarked=S`
    """
    try:
        service = get_titanic_service()
        
        # 쿼리 파라미터를 딕셔너리로 변환
        passenger_dict = {
            "Pclass": Pclass,
            "Sex": Sex,
            "SibSp": SibSp,
            "Parch": Parch
        }
        
        # 선택적 파라미터 추가
        if Age is not None:
            passenger_dict["Age"] = Age
        if Fare is not None:
            passenger_dict["Fare"] = Fare
        if Embarked is not None:
            passenger_dict["Embarked"] = Embarked
        if Cabin is not None:
            passenger_dict["Cabin"] = Cabin
        if Ticket is not None:
            passenger_dict["Ticket"] = Ticket
        if Name is not None:
            passenger_dict["Name"] = Name
        if PassengerId is not None:
            passenger_dict["PassengerId"] = PassengerId
        
        # 딕셔너리를 DataFrame으로 변환
        df = pd.DataFrame([passenger_dict])
        
        # 예측 수행
        predictions = service.predict(df)
        probabilities = service.predict_proba(df)
        
        return {
            "status": "success",
            "prediction": int(predictions[0]),
            "prediction_label": "생존" if predictions[0] == 1 else "사망",
            "probabilities": {
                "사망": float(probabilities[0][0]),
                "생존": float(probabilities[0][1])
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"모델이 학습되지 않았습니다: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"예측 실패: {str(e)}")


@router.get(
    "/model/status",
    response_model=ModelStatusResponse,
    summary="모델 상태 조회",
    description="현재 모델의 학습 상태 및 구성 요소 정보를 조회합니다."
)
async def get_model_status():
    """
    모델 상태 조회
    
    다음 정보를 반환합니다:
    - **is_trained**: 모델 학습 여부
    - **has_scaler**: 스케일러 존재 여부
    - **has_encoders**: 라벨 인코더 존재 여부
    - **feature_columns**: 사용된 특징 컬럼 목록
    """
    try:
        service = get_titanic_service()
        is_trained = service.model is not None
        
        status = {
            "is_trained": is_trained,
            "has_scaler": service.scaler is not None,
            "has_encoders": len(service.label_encoders) > 0,
            "feature_columns": service.feature_columns if service.feature_columns else []
        }
        
        return {
            "status": "success",
            "model_status": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"모델 상태 조회 실패: {str(e)}")
