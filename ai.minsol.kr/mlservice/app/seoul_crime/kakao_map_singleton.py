import os
import requests
from pathlib import Path
from dotenv import load_dotenv

class KakaoMapSingleton:
    _instance = None  # 싱글턴 인스턴스를 저장할 클래스 변수
    _base_url = "https://dapi.kakao.com/v2/local"
    _env_loaded = False  # .env 파일 로드 여부

    def __new__(cls):
        if cls._instance is None:  # 인스턴스가 없으면 생성
            cls._instance = super(KakaoMapSingleton, cls).__new__(cls)
            cls._instance._api_key = cls._instance._retrieve_api_key()  # API 키 가져오기
            cls._instance._headers = {
                "Authorization": f"KakaoAK {cls._instance._api_key}"
            }
        return cls._instance  # 기존 인스턴스 반환

    @classmethod
    def _load_env_file(cls):
        """프로젝트 루트의 .env 파일을 로드"""
        if cls._env_loaded:
            return
        
        # 현재 파일의 위치에서 프로젝트 루트까지 올라가면서 .env 파일 찾기
        current_file = Path(__file__).resolve()
        # ai.minsol.kr/mlservice/app/seoul_crime/kakao_map_singleton.py
        # -> ai.minsol.kr/mlservice/app/seoul_crime
        # -> ai.minsol.kr/mlservice/app
        # -> ai.minsol.kr/mlservice
        # -> ai.minsol.kr
        # -> minsol.kr (프로젝트 루트)
        
        # 프로젝트 루트까지 올라가기 (minsol.kr 디렉토리)
        root_path = current_file.parent.parent.parent.parent.parent
        
        # .env 파일 경로
        env_path = root_path / ".env"
        
        if env_path.exists():
            load_dotenv(env_path)
            cls._env_loaded = True
        else:
            # .env 파일이 없으면 현재 디렉토리에서도 시도
            load_dotenv()
            cls._env_loaded = True

    def _retrieve_api_key(self):
        """API 키를 .env 파일에서 가져오는 내부 메서드"""
        self._load_env_file()
        api_key = os.getenv("KAKAO_REST_API_KEY") or os.getenv("KAKAO_API_KEY")
        
        if not api_key:
            raise ValueError(
                "카카오 REST API 키가 설정되지 않았습니다. "
                ".env 파일에 KAKAO_REST_API_KEY 또는 KAKAO_API_KEY를 설정해주세요."
            )
        
        return api_key

    def get_api_key(self):
        """저장된 API 키 반환"""
        return self._api_key

    def geocode(self, address, language='ko'):
        """기관명/장소명 → 주소 + 위도 + 경도 3종 세트 반환"""
        
        url = f"{self._base_url}/search/keyword.json"
        params = {
            "query": address
        }

        try:
            response = requests.get(url, headers=self._headers, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get("documents") and len(data["documents"]) > 0:
                doc = data["documents"][0]

                # 주소
                formatted_address = doc.get("address_name", "")

                # 좌표
                x = float(doc.get("x", 0))  # 경도 (lng)
                y = float(doc.get("y", 0))  # 위도 (lat)

                # Google-style 형식으로 반환
                return [{
                    "formatted_address": formatted_address,
                    "geometry": {
                        "location": {
                            "lat": y,
                            "lng": x
                        }
                    },
                    "address_components": [
                        {
                            "long_name": formatted_address,
                            "short_name": formatted_address,
                            "types": ["locality", "political"]
                        }
                    ]
                }]
            else:
                return []

        except requests.exceptions.RequestException as e:
            raise Exception(f"카카오맵 API 요청 실패: {str(e)}")
