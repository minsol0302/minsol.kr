"""
Titanic API 스키마 모델
Pydantic 모델을 사용하여 요청/응답 스키마 정의
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any


class PassengerData(BaseModel):
    """승객 데이터 모델 (예측 요청용)"""
    Pclass: int = Field(..., description="승객 등급 (1, 2, 3)", example=1, ge=1, le=3)
    Sex: str = Field(..., description="성별 (male, female)", example="male")
    Age: Optional[float] = Field(None, description="나이", example=25.0, ge=0, le=120)
    SibSp: int = Field(..., description="형제/배우자 수", example=0, ge=0)
    Parch: int = Field(..., description="부모/자녀 수", example=0, ge=0)
    Fare: Optional[float] = Field(None, description="요금", example=7.25, ge=0)
    Embarked: Optional[str] = Field(None, description="탑승 항구 (S, C, Q)", example="S")
    Cabin: Optional[str] = Field(None, description="객실 번호", example="C85")
    Ticket: Optional[str] = Field(None, description="티켓 번호", example="A/5 21171")
    Name: Optional[str] = Field(None, description="이름", example="Braund, Mr. Owen Harris")
    PassengerId: Optional[int] = Field(None, description="승객 ID", example=1)

    class Config:
        json_schema_extra = {
            "example": {
                "Pclass": 3,
                "Sex": "male",
                "Age": 22.0,
                "SibSp": 1,
                "Parch": 0,
                "Fare": 7.25,
                "Embarked": "S"
            }
        }


class PredictionResponse(BaseModel):
    """예측 응답 모델"""
    status: str = Field(..., description="상태", example="success")
    prediction: int = Field(..., description="예측 결과 (0: 사망, 1: 생존)", example=0)
    prediction_label: str = Field(..., description="예측 결과 라벨", example="사망")
    probabilities: Dict[str, float] = Field(..., description="생존 확률", example={"사망": 0.85, "생존": 0.15})


class TrainRequest(BaseModel):
    """모델 학습 요청 모델"""
    test_size: float = Field(0.2, description="검증 데이터 비율", example=0.2, ge=0.1, le=0.5)
    random_state: int = Field(42, description="랜덤 시드", example=42)
    n_estimators: int = Field(100, description="랜덤 포레스트 트리 개수", example=100, ge=10, le=1000)


class TrainResponse(BaseModel):
    """모델 학습 응답 모델"""
    status: str = Field(..., description="상태", example="success")
    message: str = Field(..., description="메시지", example="모델 학습이 완료되었습니다.")
    result: Dict[str, Any] = Field(..., description="학습 결과")


class DataInfoResponse(BaseModel):
    """데이터 정보 응답 모델"""
    status: str = Field(..., description="상태", example="success")
    data: Dict[str, Any] = Field(..., description="데이터 정보")


class ModelStatusResponse(BaseModel):
    """모델 상태 응답 모델"""
    status: str = Field(..., description="상태", example="success")
    model_status: Dict[str, Any] = Field(..., description="모델 상태 정보")


class ServiceInfoResponse(BaseModel):
    """서비스 정보 응답 모델"""
    service: str = Field(..., description="서비스 이름", example="Titanic ML Service")
    endpoints: List[str] = Field(..., description="사용 가능한 엔드포인트 목록")


class RootResponse(BaseModel):
    """루트 엔드포인트 응답 모델"""
    service: str = Field(..., description="서비스 이름", example="Titanic Service")
    version: str = Field(..., description="서비스 버전", example="1.0.0")
    message: str = Field(..., description="메시지", example="Titanic Service API")


class PassengerInfo(BaseModel):
    """승객 정보 모델"""
    PassengerId: str = Field(..., description="승객 ID")
    Survived: str = Field(..., description="생존 여부 (0: 사망, 1: 생존)")
    Pclass: str = Field(..., description="승객 등급")
    Name: str = Field(..., description="이름")
    Sex: str = Field(..., description="성별")
    Age: str = Field(..., description="나이")
    SibSp: str = Field(..., description="형제/배우자 수")
    Parch: str = Field(..., description="부모/자녀 수")
    Ticket: str = Field(..., description="티켓 번호")
    Fare: str = Field(..., description="요금")
    Cabin: str = Field(..., description="객실 번호")
    Embarked: str = Field(..., description="탑승 항구")


class Top10PassengersResponse(BaseModel):
    """상위 10명 승객 정보 응답 모델"""
    count: int = Field(..., description="승객 수", example=10)
    passengers: List[PassengerInfo] = Field(..., description="승객 정보 목록")

