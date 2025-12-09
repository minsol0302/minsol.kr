"""
타이타닉 데이터 서비스
판다스, 넘파이, 사이킷런을 사용한 데이터 처리 및 머신러닝 서비스
"""
import sys
from pathlib import Path
from typing import List, Dict, Optional, Any, ParamSpecArgs
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from app.titanic.titanic_method import TitanicMethod
from app.titanic.titanic_dataset import TitanicDataSet

# 공통 모듈 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    from common.utils import setup_logging
except ImportError:
    import logging
    def setup_logging(name: str):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

class TitanicService:
    """타이타닉 데이터 처리 및 머신러닝 서비스"""
    
    def __init__(self):
        # CSV 파일 경로 설정 (titanic 디렉토리 기준)
        self.titanic_dir = Path(__file__).parent
        self.train_csv_path = self.titanic_dir / 'train.csv'
        self.test_csv_path = self.titanic_dir / 'test.csv'
        # Logger 설정
        self.logger = setup_logging("mlservice")

    def preprocess(self):
        self.logger.info("❤️❤️ Train 전처리 시작") 
        the_method = TitanicMethod()
        df_train = the_method.read_csv(str(self.train_csv_path))
        df_test = the_method.read_csv(str(self.test_csv_path))
        this_train = the_method.create_df(df_train, 'Survived')
        # test 데이터에는 Survived 컬럼이 없으므로 그대로 사용
        this_test = df_test.copy()
        self.logger.info(f'1. Train 의 type \n {type(this_train)} ')
        self.logger.info(f'2. Train 의 column \n {this_train.columns} ')
        self.logger.info(f'3. Train 의 상위 5개 행\n {this_train.head(5)} ')
        self.logger.info(f'4. Train 의 null 의 갯수\n {int(this_train.isnull().sum().sum())}개')
        self.logger.info("💙💙 Test 전처리 시작")
        # test 데이터에는 Survived 컬럼이 없으므로 그대로 사용
        self.logger.info(f'1. Test 의 type \n {type(this_test)}')
        self.logger.info(f'2. Test 의 column \n {this_test.columns}')
        self.logger.info(f'3. Test 의 상위 5개 행\n {this_test.head(5)}')
        self.logger.info(f'4. Test 의 null 의 갯수\n {int(this_test.isnull().sum().sum())}개')

        this = TitanicDataSet()
        this.train = this_train
        this.test = this_test

        drop_features = ['SibSp', 'Parch', 'Cabin', 'Ticket']
        this = the_method.drop_feature(this, *drop_features)
        this.train = the_method.pclass_ordinal(this.train)
        this.test = the_method.pclass_ordinal(this.test)
        this.train = the_method.gender_nominal(this.train)
        this.test = the_method.gender_nominal(this.test)
        this.train = the_method.age_ratio(this.train)
        this.test = the_method.age_ratio(this.test)
        this.train = the_method.fare_ordinal(this.train)
        this.test = the_method.fare_ordinal(this.test)
        this.train = the_method.embarked_ordinal(this.train)
        this.test = the_method.embarked_ordinal(this.test)
        this.train = the_method.title_nominal(this.train)
        this.test = the_method.title_nominal(this.test)
        drop_name = ['Name']
        this = the_method.drop_feature(this, *drop_name)
        
        # this 객체에서 다시 변수로 할당
        this_train = this.train
        this_test = this.test

        self.logger.info("❤️❤️ Train 전처리 완료")
        self.logger.info(f'1. Train 의 type \n {type(this_train)} ')
        self.logger.info(f'2. Train 의 column \n {this_train.columns} ')
        self.logger.info(f'3. Train 의 상위 5개 행\n {this_train.head(5)} ')
        self.logger.info(f'4. Train 의 null 의 갯수\n {int(this_train.isnull().sum().sum())}개')
        self.logger.info("💙💙 Test 전처리 완료")
        self.logger.info(f'1. Test 의 type \n {type(this_test)} ')
        self.logger.info(f'2. Test 의 column \n {this_test.columns} ')
        self.logger.info(f'3. Test 의 상위 5개 행\n {this_test.head(5)} ')
        self.logger.info(f'4. Test 의 null 의 갯수\n {int(this_test.isnull().sum().sum())}개')

    def modeling(self):
        self.logger.info("🍀🍀 모델링 시작")
        self.logger.info("🍀🍀 모델링 완료")

    def learning(self):
        self.logger.info("🍀🍀 학습 시작")
        self.logger.info("🍀🍀 학습 완료")

    def evaluate(self):
        self.logger.info("🍀🍀 평가 시작")
        self.logger.info("🍀🍀 평가 완료")

    def submit(self):
        self.logger.info("🍀🍀 제출 시작")
        self.logger.info("🍀🍀 제출 완료")

 