import sys
import pandas as pd
import numpy as np
from pathlib import Path
from app.seoul_crime.seoul_method import SeoulMethod
from app.seoul_crime.seoul_data import SeoulData
import logging
from app.seoul_crime.kakao_map_singleton import KakaoMapSingleton

logger = logging.getLogger(__name__)

class SeoulService:

    
    def __init__(self):
        self.data = SeoulData()
        self.method = SeoulMethod()
        self.crime_rate_columns = ['살인검거율', '강도검거율', '강간검거율', '절도검거율', '폭력검거율']
        self.crime_columns = ['살인', '강도', '강간', '절도', '폭력']
    
    def preprocess(self):
        data_dir = Path(self.data.dname)
        cctv_path = data_dir / "cctv.csv"
        crime_path = data_dir / "crime.csv"
        pop_path = data_dir / "pop.xls"
        
        # 데이터 로드
        cctv = self.method.csv_to_df(str(cctv_path))
        cctv = cctv.drop(['2013년도 이전', '2014년', '2015년', '2016년'], axis=1)
        crime = self.method.csv_to_df(str(crime_path))
        pop = self.method.xlsx_to_df(str(pop_path))

        # pop 컬럼 편집
        # axis = 1 방향으로 자치구와 좌로부터 4번째 컬럼만 남기고 모두 삭제
        # axis = 0 방향으로 위로부터 2, 3, 4번째 행을 제거 
        
        # 먼저 원본 데이터 구조 확인
        logger.info(f"pop 원본 shape: {pop.shape}")
        logger.info(f"pop 원본 columns: {pop.columns.tolist()}")
        
        # axis=0: 위로부터 2, 3, 4번째 행(인덱스 1, 2, 3) 제거 (먼저 행 제거)
        pop = pop.drop([1, 2, 3], axis=0)
        pop = pop.reset_index(drop=True)
        
        # 첫 번째 행이 '기간', '합계' 같은 헤더 정보인 경우 제거
        if len(pop) > 0 and (str(pop.iloc[0, 0]) == '기간' or str(pop.iloc[0, 0]) == '합계'):
            pop = pop.drop([0], axis=0)
            pop = pop.reset_index(drop=True)
        
        # axis=1: 자치구(인덱스 1)와 좌로부터 4번째 컬럼(인덱스 3)만 남기고 나머지 삭제
        # 이미지 설명에 따르면 Column 1이 자치구, Column 3이 인구(합계, 계)
        if len(pop.columns) > 3:
            columns_to_keep = [pop.columns[1], pop.columns[3]]  # 1번째: 자치구, 3번째: 인구
            pop = pop[columns_to_keep]
        elif len(pop.columns) == 2:
            # 이미 2개 컬럼만 있는 경우, 컬럼명만 변경
            pass
        
        # 컬럼명을 명시적으로 지정
        pop.columns = ['자치구', '인구']
        
        # 인덱스 리셋
        pop = pop.reset_index(drop=True)
        
        logger.info(f"  cctv 탑 5 : {cctv.head(5).to_string()}")
        logger.info(f"  crime 탑 5 : {crime.head(5).to_string()}")
        logger.info(f"  pop 탑 5 : {pop.head(5).to_string()}")
        
        # cctv와 pop 머지 전략
        # - cctv의 "기관명"과 pop의 "자치구"를 키로 사용
        # - 중복된 feature가 없도록 처리
        # - "기관명"과 "자치구"는 같은 값이지만 컬럼명이 다르므로 left_on, right_on 사용
        
        # 머지 전에 컬럼명 확인 및 중복 컬럼 체크
        logger.info(f"cctv 컬럼: {cctv.columns.tolist()}")
        logger.info(f"pop 컬럼: {pop.columns.tolist()}")
        
        # 중복되는 컬럼 확인 (키 컬럼 제외)
        cctv_cols = set(cctv.columns) - {'기관명'}
        pop_cols = set(pop.columns) - {'자치구'}
        duplicate_cols = cctv_cols & pop_cols
        
        if duplicate_cols:
            logger.warning(f"중복되는 컬럼이 발견되었습니다: {duplicate_cols}")
            logger.info("머지 시 suffixes를 사용하여 중복 컬럼을 구분합니다.")
        
        # cctv의 "기관명"과 pop의 "자치구"를 키로 머지
        cctv_pop = self.method.df_merge(
            left=cctv,
            right=pop,
            left_on='기관명',
            right_on='자치구',
            how='inner'
        )
        
        # 머지 후 "자치구" 컬럼 제거 (기관명과 동일한 값이므로)
        if '자치구' in cctv_pop.columns and '기관명' in cctv_pop.columns:
            # 두 컬럼의 값이 동일한지 확인
            if cctv_pop['기관명'].equals(cctv_pop['자치구']):
                cctv_pop = cctv_pop.drop(columns=['자치구'])
                logger.info("'자치구' 컬럼을 제거했습니다 (기관명과 동일한 값).")
            else:
                logger.warning("'기관명'과 '자치구'의 값이 다릅니다. 두 컬럼 모두 유지합니다.")
        
        logger.info(f"머지 완료: cctv_pop shape = {cctv_pop.shape}")
        logger.info(f"cctv_pop 컬럼: {cctv_pop.columns.tolist()}")
        logger.info(f"cctv_pop 탑 5:\n{cctv_pop.head(5).to_string()}")

        # 관서명에 따른 경찰서 주소 찾기
        station_names = [] # 경찰서 관서명 리스트
        for name in crime['관서명']:
            station_names.append(('서울' + str(name[:-1]) + '경찰서').replace(" ", ""))
        print(f"🔥💧경찰서 관서명 리스트: {station_names}")
        station_addrs = []
        station_lats = []
        station_lngs = []
        gmaps1 =  KakaoMapSingleton()
        gmaps2 =  KakaoMapSingleton()
        if gmaps1 is gmaps2:
            print("동일한 객체 입니다.")
        else:
            print("다른 객체 입니다.")
        gmaps = KakaoMapSingleton() # 카카오맵 객체 생성
        for name in station_names:
            try:
                tmp = gmaps.geocode(name, language = 'ko')
                if not tmp or len(tmp) == 0:
                    logger.warning(f"{name}의 geocode 결과가 비어있습니다.")
                    station_addrs.append("")
                    station_lats.append(0.0)
                    station_lngs.append(0.0)
                    continue
                
                formatted_addr = tmp[0].get("formatted_address", "")
                tmp_loc = tmp[0].get("geometry", {})
                location = tmp_loc.get('location', {})
                lat = location.get('lat', 0.0)
                lng = location.get('lng', 0.0)
                print(f"""{name}의 검색 결과: {formatted_addr} (위도: {lat}, 경도: {lng})""")
                station_addrs.append(formatted_addr)
                station_lats.append(lat)
                station_lngs.append(lng)
            except Exception as e:
                logger.error(f"{name}의 geocode 처리 중 오류 발생: {str(e)}")
                station_addrs.append("")
                station_lats.append(0.0)
                station_lngs.append(0.0)
        
        print(f"🔥💧자치구 리스트: {station_addrs}")

        gu_names = []
        for addr in station_addrs:
            if not addr:
                gu_names.append("")
                continue
            try:
                tmp = addr.split()
                tmp_gu_list = [gu for gu in tmp if gu[-1] == '구']
                if tmp_gu_list:
                    tmp_gu = tmp_gu_list[0]
                    gu_names.append(tmp_gu)
                else:
                    logger.warning(f"주소에서 '구'를 찾을 수 없습니다: {addr}")
                    gu_names.append("")
            except Exception as e:
                logger.error(f"주소 파싱 중 오류 발생: {addr}, {str(e)}")
                gu_names.append("")
        [print(f"🔥💧자치구 리스트 2: {gu_names}")]
        
        # crime 데이터프레임에 주소와 자치구 컬럼 추가, 관서명 컬럼 내용 변경
        crime['자치구'] = gu_names
        crime['관서명'] = station_names  # 기존 관서명을 '서울중부경찰서' 형식으로 변경
        crime['주소'] = station_addrs
        
        # 컬럼 순서 재배치: 자치구, 관서명, 주소, 그리고 나머지 기존 컬럼들
        original_columns = [col for col in crime.columns if col not in ['자치구', '관서명', '주소']]
        new_column_order = ['자치구', '관서명', '주소'] + original_columns
        crime = crime[new_column_order]
        
        # 데이터 확인
        logger.info(f"crime 데이터프레임 shape: {crime.shape}")
        logger.info(f"crime 컬럼 순서: {crime.columns.tolist()}")
        logger.info(f"자치구 샘플: {crime['자치구'].head(3).tolist()}")
        logger.info(f"관서명 샘플: {crime['관서명'].head(3).tolist()}")
        logger.info(f"주소 샘플: {crime['주소'].head(3).tolist()}")
        
        # save 폴더에 새로운 CSV 파일 생성
        save_dir = Path(self.data.sname)
        save_dir.mkdir(parents=True, exist_ok=True)  # save 폴더가 없으면 생성
        crime_output_path = save_dir / "crime_with_address.csv"
        
        try:
            crime.to_csv(str(crime_output_path), index=False, encoding='utf-8-sig')
            logger.info(f"새로운 CSV 파일이 생성되었습니다: {crime_output_path}")
            logger.info(f"컬럼 순서: 자치구, 관서명, 주소, 그리고 나머지 기존 컬럼들")
            logger.info(f"파일 shape: {crime.shape}, 컬럼: {crime.columns.tolist()}")
            
            # 저장 확인
            if crime_output_path.exists():
                logger.info(f"파일 저장 확인: {crime_output_path} 파일이 존재합니다.")
                # 저장된 파일 읽어서 확인
                saved_crime = pd.read_csv(str(crime_output_path), encoding='utf-8-sig')
                logger.info(f"저장된 파일 컬럼 순서: {saved_crime.columns.tolist()}")
                logger.info(f"저장된 파일 shape: {saved_crime.shape}")
                logger.info(f"저장된 파일 첫 3행:\n{saved_crime.head(3).to_string()}")
            else:
                logger.error(f"파일 저장 실패: {crime_output_path} 파일이 생성되지 않았습니다.")
        except Exception as e:
            logger.error(f"CSV 파일 저장 중 오류 발생: {str(e)}")
            logger.exception(e)
            raise


        # crime 편집


        return {
            "status": "success",
            "cctv_rows": len(cctv),
            "cctv_columns": cctv.columns.tolist(),
            "crime_rows": len(crime),
            "crime_columns": crime.columns.tolist(),
            "pop_rows": len(pop),
            "pop_columns": pop.columns.tolist(),
            "cctv_pop_rows": len(cctv_pop),
            "cctv_pop_columns": cctv_pop.columns.tolist(),
            "cctv_preview": cctv.head(3).to_dict(orient='records'),
            "crime_preview": crime.head(3).to_dict(orient='records'),
            "pop_preview": pop.head(3).to_dict(orient='records'),
            "cctv_pop_preview": cctv_pop.head(3).to_dict(orient='records'),
            "message": "데이터 전처리 및 머지가 완료되었습니다"
        }
