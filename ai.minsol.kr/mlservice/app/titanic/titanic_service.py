"""
타이타닉 데이터 서비스
판다스, 넘파이, 사이킷런을 사용한 데이터 처리 및 머신러닝 서비스
"""
import sys
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any, ParamSpecArgs
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
from app.titanic.titanic_method import TitanicMethod
from app.titanic.titanic_dataset import TitanicDataSet

class TitanicService:
    """타이타닉 데이터 처리 및 머신러닝 서비스"""
    
    def __init__(self):
        # CSV 파일 경로 설정 (resources/titanic 디렉토리 기준)
        self.titanic_dir = Path(__file__).parent.parent / 'resources' / 'titanic'
        self.titanic_dir = self.titanic_dir.resolve()  # 절대 경로로 변환
        self.train_csv_path = self.titanic_dir / 'train.csv'
        self.test_csv_path = self.titanic_dir / 'test.csv'
        # Logger 설정
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"CSV 파일 경로 확인 완료 - Train: {self.train_csv_path}, Test: {self.test_csv_path}")
        # 전처리된 데이터 저장
        self.dataset = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        # 모델 저장
        self.models = {}

    def preprocess(self):
        self.logger.info("❤️❤️ Train 전처리 시작") 
        self.logger.info(f"Train CSV 경로: {self.train_csv_path}")
        self.logger.info(f"Test CSV 경로: {self.test_csv_path}")
        
        try:
            the_method = TitanicMethod()
            df_train = the_method.read_csv(str(self.train_csv_path))
            df_test = the_method.read_csv(str(self.test_csv_path))
        except FileNotFoundError as e:
            self.logger.error(f"CSV 파일을 찾을 수 없습니다: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"CSV 파일 읽기 오류: {str(e)}")
            raise
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
        
        # 전처리된 데이터 저장
        self.dataset = this
        # 원본 train 데이터에서 label 추출
        df_train_original = the_method.read_csv(str(self.train_csv_path))
        y_train = df_train_original['Survived']
        # 전처리된 train 데이터를 feature로 사용
        self.X_train = this_train
        self.X_test = this_test
        self.y_train = y_train

    def modeling(self):
        self.logger.info("🍀🍀 모델링 시작")

        # 모델 초기화
        self.models = {
            'logistic_regression': LogisticRegression(random_state=42, max_iter=1000),
            'naive_bayes': GaussianNB(),
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'svm': SVC(random_state=42, probability=True)
        }
        
        # LightGBM이 사용 가능한 경우 추가 (지연 import)
        try:
            import lightgbm as lgb
            self.models['lightgbm'] = lgb.LGBMClassifier(random_state=42, verbose=-1)
            self.logger.info("LightGBM 모델 추가됨")
        except (ImportError, OSError) as e:
            # ImportError: 패키지가 설치되지 않은 경우
            # OSError: 시스템 라이브러리가 없는 경우 (libgomp.so.1 등)
            self.logger.warning(f"LightGBM이 사용 불가능하여 제외됩니다: {str(e)}")

        self.logger.info("🍀🍀 모델링 완료")

    def learning(self):
        self.logger.info("🍀🍀 학습 시작")

        if self.X_train is None or self.y_train is None:
            self.logger.error("전처리된 데이터가 없습니다. 먼저 preprocess()를 실행해주세요.")
            return

        # 모델이 초기화되지 않은 경우 초기화
        if not self.models:
            self.modeling()

        # 각 모델 학습
        for model_name, model in self.models.items():
            self.logger.info(f"{model_name} 학습 시작...")
            model.fit(self.X_train, self.y_train)
            self.logger.info(f"{model_name} 학습 완료")

        self.logger.info("🍀🍀 학습 완료")

    def evaluate(self):
        self.logger.info("🍀🍀 평가 시작")
        
        if not self.models:
            self.logger.error("학습된 모델이 없습니다. 먼저 learning()을 실행해주세요.")
            return {}
        
        if self.X_train is None or self.y_train is None:
            self.logger.error("전처리된 데이터가 없습니다. 먼저 preprocess()를 실행해주세요.")
            return {}

        # train 데이터를 train/validation으로 분할
        X_train_split, X_val_split, y_train_split, y_val_split = train_test_split(
            self.X_train, self.y_train, test_size=0.2, random_state=42, stratify=self.y_train
        )

        results = {}
        
        # 각 모델 평가
        for model_name, model in self.models.items():
            # 학습 (validation set으로 평가하기 위해)
            model.fit(X_train_split, y_train_split)
            # 예측
            y_pred = model.predict(X_val_split)
            # 정확도 계산
            accuracy = accuracy_score(y_val_split, y_pred)
            results[model_name] = accuracy
            
            # 한글 이름 매핑
            model_name_kr = {
                'logistic_regression': '로지스틱 회귀',
                'naive_bayes': '나이브베이즈',
                'random_forest': '랜덤포레스트',
                'lightgbm': 'LightGBM',
                'svm': 'SVM'
            }.get(model_name, model_name)
            
            self.logger.info(f'{model_name_kr} 활용한 검증 정확도: {accuracy:.4f}')

        self.logger.info("🍀🍀 평가 완료")
        return results

    def submit(self):
        self.logger.info("🍀🍀 제출 시작")
        
        if self.X_train is None or self.y_train is None or self.X_test is None:
            self.logger.error("전처리된 데이터가 없습니다. 먼저 preprocess()를 실행해주세요.")
            return None
        
        if not self.models:
            self.logger.error("학습된 모델이 없습니다. 먼저 learning()을 실행해주세요.")
            return None
        
        # 평가를 통해 최고 성능 모델 선택
        self.logger.info("모델 평가를 통해 최고 성능 모델 선택 중...")
        results = self.evaluate()
        
        if not results:
            self.logger.error("평가 결과가 없습니다.")
            return None
        
        # 최고 정확도 모델 선택
        best_model_name = max(results, key=results.get)
        best_accuracy = results[best_model_name]
        
        self.logger.info(f"최고 성능 모델: {best_model_name} (정확도: {best_accuracy:.4f})")
        
        # 최고 모델로 전체 train 데이터 재학습
        best_model = self.models[best_model_name]
        self.logger.info(f"{best_model_name}로 전체 train 데이터 재학습 중...")
        best_model.fit(self.X_train, self.y_train)
        
        # test 데이터 예측
        self.logger.info("test 데이터 예측 중...")
        predictions = best_model.predict(self.X_test)
        
        # PassengerId 추출 (test 데이터에서)
        passenger_ids = self.X_test['PassengerId'].values
        
        # 제출용 DataFrame 생성
        submission_df = pd.DataFrame({
            'PassengerId': passenger_ids,
            'Survived': predictions.astype(int)
        })
        
        # download 폴더에 저장 (절대 경로 사용)
        download_dir = Path(__file__).parent.parent / 'download'
        download_dir = download_dir.resolve()  # 절대 경로로 변환
        download_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"파일 저장 경로: {download_dir}")
        self.logger.info(f"경로 존재 여부: {download_dir.exists()}")
        
        # CSV 파일 저장
        submission_path = download_dir / 'submission.csv'
        try:
            submission_df.to_csv(submission_path, index=False)
            self.logger.info(f"제출 파일 저장 완료: {submission_path}")
            self.logger.info(f"파일 존재 여부: {submission_path.exists()}")
            self.logger.info(f"파일 크기: {submission_path.stat().st_size if submission_path.exists() else 0} bytes")
        except Exception as e:
            self.logger.error(f"CSV 파일 저장 실패: {str(e)}", exc_info=True)
            raise
        
        # 모델 파일 저장
        model_path = download_dir / f'{best_model_name}_model.pkl'
        try:
            joblib.dump(best_model, model_path)
            self.logger.info(f"모델 파일 저장 완료: {model_path}")
            self.logger.info(f"파일 존재 여부: {model_path.exists()}")
            self.logger.info(f"파일 크기: {model_path.stat().st_size if model_path.exists() else 0} bytes")
        except Exception as e:
            self.logger.error(f"모델 파일 저장 실패: {str(e)}", exc_info=True)
            raise
        
        # 결과 요약 저장
        summary_path = download_dir / 'model_summary.txt'
        try:
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write("=== 모델 평가 결과 ===\n\n")
                for model_name, accuracy in sorted(results.items(), key=lambda x: x[1], reverse=True):
                    model_name_kr = {
                        'logistic_regression': '로지스틱 회귀',
                        'naive_bayes': '나이브베이즈',
                        'random_forest': '랜덤포레스트',
                        'lightgbm': 'LightGBM',
                        'svm': 'SVM'
                    }.get(model_name, model_name)
                    f.write(f"{model_name_kr}: {accuracy:.4f}\n")
                f.write(f"\n선택된 모델: {best_model_name} (정확도: {best_accuracy:.4f})\n")
            self.logger.info(f"결과 요약 저장 완료: {summary_path}")
            self.logger.info(f"파일 존재 여부: {summary_path.exists()}")
            self.logger.info(f"파일 크기: {summary_path.stat().st_size if summary_path.exists() else 0} bytes")
        except Exception as e:
            self.logger.error(f"요약 파일 저장 실패: {str(e)}", exc_info=True)
            raise
        
        self.logger.info("🍀🍀 제출 완료")
        return {
            'submission_file': str(submission_path),
            'model_file': str(model_path),
            'summary_file': str(summary_path),
            'best_model': best_model_name,
            'best_accuracy': best_accuracy
        }

 