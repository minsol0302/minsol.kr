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
try:
    from app.titanic.titanic_router import router as titanic_router
    from common.middleware import LoggingMiddleware
    from common.utils import setup_logging
except ImportError as e:
    # 모듈을 찾을 수 없는 경우 기본값 사용
    from fastapi import APIRouter
    titanic_router = APIRouter()
    class LoggingMiddleware:
        pass
    def setup_logging(name):
        import logging
        return logging.getLogger(name)

# 로깅 설정
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
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
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
app.add_middleware(LoggingMiddleware)

# 라우터 등록
app.include_router(titanic_router)

# CSV 파일 경로
CSV_FILE_PATH = Path(__file__).parent / "titanic" / "train.csv"


def load_top_10_passengers():
    """train.csv에서 상위 10명의 승객 정보를 로드"""
    passengers = []
    
    try:
        with open(CSV_FILE_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i >= 10:  # 상위 10명만
                    break
                passengers.append({
                    "PassengerId": row.get("PassengerId", ""),
                    "Survived": row.get("Survived", ""),
                    "Pclass": row.get("Pclass", ""),
                    "Name": row.get("Name", ""),
                    "Sex": row.get("Sex", ""),
                    "Age": row.get("Age", ""),
                    "SibSp": row.get("SibSp", ""),
                    "Parch": row.get("Parch", ""),
                    "Ticket": row.get("Ticket", ""),
                    "Fare": row.get("Fare", ""),
                    "Cabin": row.get("Cabin", ""),
                    "Embarked": row.get("Embarked", "")
                })
    except FileNotFoundError:
        logger.error(f"CSV 파일을 찾을 수 없습니다: {CSV_FILE_PATH}")
        return []
    except Exception as e:
        logger.error(f"CSV 파일 읽기 오류: {e}")
        return []
    
    return passengers


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "service": config.service_name,
        "version": config.service_version,
        "message": "Titanic Service API"
    }


@app.get("/passengers/top10")
async def get_top_10_passengers():
    """상위 10명의 승객 정보를 반환"""
    passengers = load_top_10_passengers()
    
    if not passengers:
        return JSONResponse(
            status_code=404,
            content={"error": "승객 데이터를 찾을 수 없습니다."}
        )
    
    return {
        "count": len(passengers),
        "passengers": passengers
    }


@app.get("/passengers/top10/print")
async def print_top_10_passengers():
    """상위 10명의 승객 정보를 터미널에 출력"""
    passengers = load_top_10_passengers()
    
    if not passengers:
        logger.warning("출력할 승객 데이터가 없습니다.")
        return {"message": "출력할 승객 데이터가 없습니다."}
    
    # 터미널에 출력
    print("\n" + "="*80)
    print("타이타닉 승객 상위 10명")
    print("="*80)
    
    for i, passenger in enumerate(passengers, 1):
        print(f"\n[{i}] {passenger['Name']}")
        print(f"    PassengerId: {passenger['PassengerId']}")
        print(f"    Survived: {passenger['Survived']} ({'생존' if passenger['Survived'] == '1' else '사망'})")
        print(f"    Pclass: {passenger['Pclass']}")
        print(f"    Sex: {passenger['Sex']}")
        print(f"    Age: {passenger['Age']}")
        print(f"    Fare: {passenger['Fare']}")
        print(f"    Embarked: {passenger['Embarked']}")
    
    print("\n" + "="*80)
    logger.info(f"상위 10명의 승객 정보를 터미널에 출력했습니다.")
    
    return {
        "message": "상위 10명의 승객 정보를 터미널에 출력했습니다.",
        "count": len(passengers)
    }


@app.get("/titanic/preprocess")
async def preprocess_data():
    """타이타닉 데이터 전처리 실행"""
    try:
        import os
        import sys
        import pandas as pd
        import numpy as np
        from io import StringIO
        from app.titanic.titanic_service import TitanicService
        from app.titanic.titanic_method import TitanicMethod
        
        # 작업 디렉토리를 titanic 폴더로 변경
        titanic_dir = Path(__file__).parent / "titanic"
        original_cwd = os.getcwd()
        
        try:
            os.chdir(str(titanic_dir))
            service = TitanicService()
            
            # preprocess 실행
            service.preprocess()
            
            # 결과 수집을 위해 직접 메서드 호출
            the_method = TitanicMethod()
            df_train = the_method.new_model('train.csv')
            df_test = the_method.new_model('test.csv')
            this_train = the_method.create_df(df_train, 'Survived')
            this_test = the_method.create_df(df_test, 'Survived')
            
            # 결과 데이터 구성 (안전하게 처리)
            def safe_head_to_dict(df):
                """DataFrame의 head를 안전하게 딕셔너리로 변환"""
                try:
                    if len(df) > 0:
                        head_data = df.head(1)
                        # NaN 값을 None으로 변환하고, 숫자 타입을 Python 기본 타입으로 변환
                        head_dict = head_data.iloc[0].to_dict()
                        # 값들을 JSON 직렬화 가능한 형태로 변환
                        for key, value in head_dict.items():
                            if pd.isna(value):
                                head_dict[key] = None
                            elif isinstance(value, (pd.Timestamp,)):
                                head_dict[key] = str(value)
                            elif isinstance(value, (np.integer,)):
                                head_dict[key] = int(value)
                            elif isinstance(value, (np.floating,)):
                                head_dict[key] = float(value)
                        return head_dict
                    else:
                        return {}
                except Exception as e:
                    logger.warning(f"head 변환 오류: {e}")
                    return {}
            
            result = {
                "status": "success",
                "message": "데이터 전처리가 완료되었습니다.",
                "train": {
                    "type": str(type(this_train)),
                    "columns": this_train.columns.tolist(),
                    "shape": [int(this_train.shape[0]), int(this_train.shape[1])],
                    "null_count": int(the_method.check_null(this_train)),
                    "head": safe_head_to_dict(this_train)
                },
                "test": {
                    "type": str(type(this_test)),
                    "columns": this_test.columns.tolist(),
                    "shape": [int(this_test.shape[0]), int(this_test.shape[1])],
                    "null_count": int(the_method.check_null(this_test)),
                    "head": safe_head_to_dict(this_test)
                }
            }
            
            # 터미널에도 출력
            print("\n" + "="*80)
            print("🍀🍀 전처리 시작")
            print(f"1. Train 의 type: {type(this_train)}")
            print(f"2. Train 의 column: {this_train.columns.tolist()}")
            print(f"3. Train 의 상위 1개 행:\n{this_train.head(1)}")
            print(f"4. Train 의 null 의 갯수: {the_method.check_null(this_train)}개")
            print(f"5. Test 의 type: {type(this_test)}")
            print(f"6. Test 의 column: {this_test.columns.tolist()}")
            print(f"7. Test 의 상위 1개 행:\n{this_test.head(1)}")
            print(f"8. Test 의 null 의 갯수: {the_method.check_null(this_test)}개")
            print("🍀🍀 전처리 완료")
            print("="*80 + "\n")
            
            return result
        finally:
            os.chdir(original_cwd)
    except FileNotFoundError as e:
        logger.error(f"파일을 찾을 수 없습니다: {e}")
        return JSONResponse(
            status_code=404,
            content={"error": f"파일을 찾을 수 없습니다: {str(e)}"}
        )
    except Exception as e:
        logger.error(f"전처리 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"전처리 중 오류가 발생했습니다: {str(e)}"}
        )


@app.on_event("startup")
async def startup_event():
    """서비스 시작 시 실행"""
    logger.info(f"{config.service_name} v{config.service_version} started")
    # 시작 시 상위 10명 출력
    await print_top_10_passengers()


@app.on_event("shutdown")
async def shutdown_event():
    """서비스 종료 시 실행"""
    logger.info(f"{config.service_name} shutting down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.port)
