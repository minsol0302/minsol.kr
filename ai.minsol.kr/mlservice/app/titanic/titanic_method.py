import pandas as pd
import numpy as np
from pandas import DataFrame
from pathlib import Path
from app.titanic.titanic_dataset import TitanicDataSet
from typing import Tuple
import logging

class TitanicMethod(object): 

    def __init__(self):
        self.dataset = TitanicDataSet()
        self.logger = logging.getLogger(__name__)

    def read_csv(self, fname: str) -> pd.DataFrame:
        return pd.read_csv(fname)

    def create_df(self, df: DataFrame, label: str) -> pd.DataFrame:
        return df.drop(columns=[label])

    def create_label(self, df: DataFrame, label: str) -> pd.DataFrame:
        return df[[label]]

    def drop_feature(self, this, *feature: str) -> object:
        [i.drop(j, axis=1, inplace=True) for j in feature for i in [this.train,this.test ] ]

        # for i in [this.train, this.test]:
        #     for j in feature:
        #         i.drop(j, axis=1, inplace=True)
 
        return this

    def check_null(self, this) -> int:
        [print(i.isnull().sum()) for i in [this.train, this.test]]
        for i in [this.train, this.test]:
            print(i.isnull().sum())

    # 척도 : nominal, ordinal, interval, ratio

    def pclass_ordinal(self, df: DataFrame) -> pd.DataFrame:
        """
        Pclass: 객실 등급 (1, 2, 3)
        - 서열형 척도(ordinal)로 처리합니다.
        - 1등석 > 2등석 > 3등석이므로, 생존률 관점에서 1이 가장 좋고 3이 가장 안 좋습니다.
        """
        # Pclass는 이미 ordinal이므로 그대로 사용하되, 명시적으로 정수형으로 변환
        df = df.copy()
        df["Pclass"] = df["Pclass"].astype(int)
        # 기존 Pclass는 유지 (필요시 drop_feature로 제거 가능)
        return df

    def fare_ordinal(self, df: DataFrame) -> pd.DataFrame:
        """
        Fare: 요금 (연속형 ratio 척도이지만, 여기서는 구간화하여 서열형으로 사용)
        - 결측치를 중앙값으로 채우고, 사분위수로 binning하여 ordinal 피처 생성
        """
        df = df.copy()
        
        # 결측치를 중앙값으로 채우기
        if df["Fare"].isnull().any():
            median_fare = df["Fare"].median()
            df["Fare"].fillna(median_fare, inplace=True)
            self.logger.info(f"Fare 결측치 {df['Fare'].isnull().sum()}개를 중앙값 {median_fare}로 채웠습니다")
        
        # 사분위수로 binning하여 ordinal 피처 생성
        try:
            df["Fare_ordinal"] = pd.qcut(
                df["Fare"], 
                q=4, 
                labels=[0, 1, 2, 3],
                duplicates="drop"
            ).astype(int)
        except (ValueError, TypeError):
            # 중복값이 많아 qcut이 실패할 경우, cut 사용
            fare_min = df["Fare"].min()
            fare_max = df["Fare"].max()
            df["Fare_ordinal"] = pd.cut(
                df["Fare"],
                bins=4,
                labels=[0, 1, 2, 3],
                include_lowest=True
            ).astype(int)
        
        # 원본 Fare 컬럼을 Fare_ordinal 값으로 대체
        df["Fare"] = df["Fare_ordinal"]
        df.drop(columns=["Fare_ordinal"], inplace=True)
        
        return df

    def embarked_ordinal(self, df: DataFrame) -> pd.DataFrame:
        """
        Embarked: 탑승 항구 (C, Q, S)
        - Label encoding 사용: S=1, C=2, Q=3
        """
        df = df.copy()
        
        # 결측치를 최빈값으로 채우기
        if df["Embarked"].isnull().any():
            mode_embarked = df["Embarked"].mode()[0] if not df["Embarked"].mode().empty else "S"
            df["Embarked"].fillna(mode_embarked, inplace=True)
            self.logger.info(f"Embarked 결측치를 최빈값 {mode_embarked}로 채웠습니다")
        
        # Label encoding: S=1, C=2, Q=3
        embarked_label_map = {
            'S': 1,
            'C': 2,
            'Q': 3
        }
        df["Embarked"] = df["Embarked"].map(embarked_label_map).astype(int)
        
        return df

    def gender_nominal(self, df: DataFrame) -> pd.DataFrame:
        """
        Sex: 성별 (male, female)
        - nominal 척도이므로 이진 인코딩 사용
        """
        df = df.copy()
        
        # 원본 Sex 컬럼을 "Gender" 로 변경하고 숫자로 변환 (male=0, female=1)
        df["Gender"] = (df["Sex"] == "female").astype(int)
        df.drop(columns=["Sex"], inplace=True)
         
        return df

    def age_ratio(self, df: DataFrame) -> pd.DataFrame:
        """
        Age: 나이
        - 원래는 ratio 척도지만, 나이를 구간으로 나눈 ordinal 피처를 생성
        - bins: [-1, 0, 5, 12, 18, 24, 35, 60, inf]
          구간 의미:
          0: 미상 (0세 미만)
          1: 유아 (0-5세)
          2: 어린이 (6-12세)
          3: 청소년 (13-18세)
          4: 청년 (19-24세)
          5: 성인 (25-35세)
          6: 중년 (36-60세)
          7: 노년 (60세 이상)
        """
        df = df.copy()
        # 7개 구간을 만들기 위해 bins 조정: [-1, 0, 5, 12, 18, 24, 35, 60, inf] -> 8개 경계값 = 7개 구간
        bins = [-1, 0, 5, 12, 18, 24, 35, 60, np.inf]
        
        # 결측치를 중앙값으로 채우기
        if df["Age"].isnull().any():
            median_age = df["Age"].median()
            df["Age"].fillna(median_age, inplace=True)
            self.logger.info(f"Age 결측치 {df['Age'].isnull().sum()}개를 중앙값 {median_age}로 채웠습니다")
        
        # 나이를 구간화하여 ordinal 피처 생성 (7개 구간: 0-6)
        df["Age"] = pd.cut(
            df["Age"],
            bins=bins,
            labels=[0, 1, 2, 3, 4, 5, 6, 7],
            include_lowest=True
        ).astype(int)
        
        # 원본 Age 컬럼은 유지
        return df
    
    def title_nominal(self, df: DataFrame) -> pd.DataFrame:
        """
        Title: 명칭 (Mr, Ms, Mrs, Master, Royal, Rare)
        - Name 컬럼에서 추출한 타이틀
        - nominal 척도이므로 Label Encoding 사용 (0~5)
        - 매핑: Mr=0, Ms=1, Mrs=2, Master=3, Royal=4, Rare=5
        """
        df = df.copy()
        
        # Name 컬럼에서 Title 추출 (정규표현식 사용)
        # 예: "Braund, Mr. Owen Harris" -> "Mr"
        df["Title"] = df["Name"].str.extract(r',\s*([^\.]+)\.', expand=False)
        
        # 타이틀 정리 및 그룹화
        # 일반적인 타이틀: Mr, Mrs, Miss, Master
        # Royal 타이틀: Lady, Countess, Sir, Don, Dona 등
        title_mapping = {
            'Mr': 'Mr',
            'Miss': 'Ms',
            'Mlle': 'Ms',  # Mademoiselle -> Ms
            'Ms': 'Ms',
            'Mrs': 'Mrs',
            'Mme': 'Mrs',  # Madame -> Mrs
            'Master': 'Master',
            'Lady': 'Royal',
            'Countess': 'Royal',
            'Sir': 'Royal',
            'Don': 'Royal',
            'Dona': 'Royal',
            'Jonkheer': 'Royal'
        }
        
        # 타이틀 매핑 적용
        df["Title"] = df["Title"].map(title_mapping).fillna('Rare')
        
        # 희소한 타이틀을 "Rare" 그룹으로 묶기
        common_titles = ["Mr", "Ms", "Mrs", "Master", "Royal"]
        df["Title"] = df["Title"].apply(
            lambda x: x if x in common_titles else "Rare"
        )
        
        # 결측치 처리 (혹시 모를 경우를 대비)
        if df["Title"].isnull().any():
            df["Title"].fillna("Mr", inplace=True)  # 가장 많은 타이틀로 채우기
        
        # Label Encoding: Mr=0, Ms=1, Mrs=2, Master=3, Royal=4, Rare=5
        title_label_map = {
            'Mr': 0,
            'Ms': 1,
            'Mrs': 2,
            'Master': 3,
            'Royal': 4,
            'Rare': 5
        }
        df["Title"] = df["Title"].map(title_label_map).astype(int)
        
        return df