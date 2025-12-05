"""
Titanic 서비스 모듈
데이터 로드, 전처리, 모델 학습, 예측 기능 제공
"""

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from icecream import ic
import joblib
from typing import Dict, List, Optional, Tuple


class TitanicService:
    """Titanic 데이터 처리 및 머신러닝 서비스"""

    def __init__(self, data_dir: Optional[str] = None):
        """
        초기화
        
        Args:
            data_dir: 데이터 파일이 있는 디렉토리 경로 (None이면 자동으로 titanic 디렉토리 사용)
        """
        if data_dir is None:
            # 현재 파일의 위치를 기준으로 titanic 디렉토리 경로 설정
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.data_dir = current_dir
        else:
            self.data_dir = data_dir
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = None

    def load_data(self, filename: str = "train.csv") -> pd.DataFrame:
        """
        CSV 파일에서 데이터 로드
        
        Args:
            filename: 로드할 파일명
            
        Returns:
            DataFrame: 로드된 데이터
        """
        filepath = os.path.join(self.data_dir, filename)
        ic(f"데이터 로드: {filepath}")
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {filepath}")
        
        df = pd.read_csv(filepath)
        ic(f"데이터 로드 완료: {len(df)} 행, {len(df.columns)} 열")
        return df

    def preprocess_data(self, df: pd.DataFrame, is_training: bool = True) -> pd.DataFrame:
        """
        데이터 전처리
        
        Args:
            df: 전처리할 DataFrame
            is_training: 학습 데이터인지 여부
            
        Returns:
            DataFrame: 전처리된 데이터
        """
        ic("데이터 전처리 시작")
        df = df.copy()
        
        # 1. 결측치 처리
        # Age 결측치를 중앙값으로 채우기
        if 'Age' in df.columns:
            df['Age'].fillna(df['Age'].median(), inplace=True)
        
        # Embarked 결측치를 최빈값으로 채우기
        if 'Embarked' in df.columns:
            df['Embarked'].fillna(df['Embarked'].mode()[0], inplace=True)
        
        # Fare 결측치를 중앙값으로 채우기
        if 'Fare' in df.columns:
            df['Fare'].fillna(df['Fare'].median(), inplace=True)
        
        # Cabin은 너무 많은 결측치가 있어서 제거하거나 새로운 특징으로 변환
        if 'Cabin' in df.columns:
            df['HasCabin'] = df['Cabin'].notna().astype(int)
            df.drop('Cabin', axis=1, inplace=True)
        
        # 2. 범주형 변수 인코딩
        if 'Sex' in df.columns:
            if is_training:
                le_sex = LabelEncoder()
                df['Sex'] = le_sex.fit_transform(df['Sex'])
                self.label_encoders['Sex'] = le_sex
            else:
                if 'Sex' in self.label_encoders:
                    df['Sex'] = self.label_encoders['Sex'].transform(df['Sex'])
        
        if 'Embarked' in df.columns:
            if is_training:
                le_embarked = LabelEncoder()
                df['Embarked'] = le_embarked.fit_transform(df['Embarked'].astype(str))
                self.label_encoders['Embarked'] = le_embarked
            else:
                if 'Embarked' in self.label_encoders:
                    df['Embarked'] = self.label_encoders['Embarked'].transform(df['Embarked'].astype(str))
        
        # 3. 불필요한 컬럼 제거
        columns_to_drop = ['PassengerId', 'Name', 'Ticket']
        for col in columns_to_drop:
            if col in df.columns:
                df.drop(col, axis=1, inplace=True)
        
        # 4. 특징 선택 (Survived는 타겟 변수이므로 제외)
        if 'Survived' in df.columns:
            feature_columns = [col for col in df.columns if col != 'Survived']
        else:
            feature_columns = df.columns.tolist()
        
        if is_training:
            self.feature_columns = feature_columns
        
        # 5. 특징 순서 정렬 (학습 시와 동일하게)
        if self.feature_columns:
            df = df[self.feature_columns]
        
        ic(f"전처리 완료: {df.shape}")
        return df

    def train_model(
        self,
        train_df: pd.DataFrame,
        test_size: float = 0.2,
        random_state: int = 42,
        n_estimators: int = 100
    ) -> Dict:
        """
        모델 학습
        
        Args:
            train_df: 학습 데이터
            test_size: 검증 데이터 비율
            random_state: 랜덤 시드
            n_estimators: 랜덤 포레스트 트리 개수
            
        Returns:
            Dict: 학습 결과 (정확도, 리포트 등)
        """
        ic("모델 학습 시작")
        
        # 데이터 전처리
        X = self.preprocess_data(train_df, is_training=True)
        y = train_df['Survived']
        
        # 학습/검증 데이터 분할
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        # 스케일링
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        
        # 모델 학습
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            random_state=random_state,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # 예측 및 평가
        y_pred = self.model.predict(X_val_scaled)
        accuracy = accuracy_score(y_val, y_pred)
        
        ic(f"모델 학습 완료 - 정확도: {accuracy:.4f}")
        
        return {
            'accuracy': accuracy,
            'classification_report': classification_report(y_val, y_pred),
            'confusion_matrix': confusion_matrix(y_val, y_pred).tolist(),
            'feature_importance': dict(zip(
                self.feature_columns,
                self.model.feature_importances_.tolist()
            ))
        }

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """
        생존 예측
        
        Args:
            df: 예측할 데이터
            
        Returns:
            np.ndarray: 예측 결과 (0: 사망, 1: 생존)
        """
        if self.model is None:
            raise ValueError("모델이 학습되지 않았습니다. train_model()을 먼저 호출하세요.")
        
        ic("예측 시작")
        
        # 데이터 전처리
        X = self.preprocess_data(df, is_training=False)
        
        # 스케일링
        X_scaled = self.scaler.transform(X)
        
        # 예측
        predictions = self.model.predict(X_scaled)
        
        ic(f"예측 완료: {len(predictions)}개")
        return predictions

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        """
        생존 확률 예측
        
        Args:
            df: 예측할 데이터
            
        Returns:
            np.ndarray: 생존 확률 (각 클래스에 대한 확률)
        """
        if self.model is None:
            raise ValueError("모델이 학습되지 않았습니다. train_model()을 먼저 호출하세요.")
        
        ic("확률 예측 시작")
        
        # 데이터 전처리
        X = self.preprocess_data(df, is_training=False)
        
        # 스케일링
        X_scaled = self.scaler.transform(X)
        
        # 확률 예측
        probabilities = self.model.predict_proba(X_scaled)
        
        ic(f"확률 예측 완료: {len(probabilities)}개")
        return probabilities

    def save_model(self, filepath: str = "titanic_model.joblib"):
        """
        모델 저장
        
        Args:
            filepath: 저장할 파일 경로
        """
        if self.model is None:
            raise ValueError("저장할 모델이 없습니다.")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'feature_columns': self.feature_columns
        }
        
        joblib.dump(model_data, filepath)
        ic(f"모델 저장 완료: {filepath}")

    def load_model(self, filepath: str = "titanic_model.joblib"):
        """
        모델 로드
        
        Args:
            filepath: 로드할 파일 경로
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"모델 파일을 찾을 수 없습니다: {filepath}")
        
        model_data = joblib.load(filepath)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.label_encoders = model_data['label_encoders']
        self.feature_columns = model_data['feature_columns']
        
        ic(f"모델 로드 완료: {filepath}")

    def get_data_info(self, df: pd.DataFrame) -> Dict:
        """
        데이터 정보 조회
        
        Args:
            df: 조회할 DataFrame
            
        Returns:
            Dict: 데이터 정보
        """
        info = {
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'dtypes': df.dtypes.astype(str).to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'statistics': df.describe().to_dict() if len(df.select_dtypes(include=[np.number]).columns) > 0 else {}
        }
        
        if 'Survived' in df.columns:
            info['survived_distribution'] = df['Survived'].value_counts().to_dict()
        
        return info


# 싱글톤 인스턴스 (선택사항)
_titanic_service: Optional[TitanicService] = None


def get_titanic_service() -> TitanicService:
    """TitanicService 싱글톤 인스턴스 반환"""
    global _titanic_service
    if _titanic_service is None:
        _titanic_service = TitanicService()
    return _titanic_service
