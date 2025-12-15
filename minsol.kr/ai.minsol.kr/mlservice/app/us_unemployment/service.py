import requests
import pandas as pd
import folium
import logging
from typing import Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class USUnemploymentService:
    """미국 실업률 데이터 시각화 서비스"""
    
    def __init__(
        self,
        geo_data_path: Optional[str] = None,
        data_path: Optional[str] = None,
        map_location: list = [48, -102],
        zoom_start: int = 3
    ):
        """
        초기화
        
        Args:
            geo_data_path: 지리 데이터 JSON 파일 경로 (로컬)
            data_path: 실업률 데이터 CSV 파일 경로 (로컬)
            map_location: 지도 중심 좌표 [위도, 경도]
            zoom_start: 초기 줌 레벨
        """
        # 파일 경로 설정
        base_dir = Path(__file__).parent
        if geo_data_path is None:
            geo_data_path = str(base_dir / "data" / "us-states.json")
        if data_path is None:
            data_path = str(base_dir / "data" / "us_unemployment.csv")
        
        self.geo_data_path = Path(geo_data_path)
        self.data_path = Path(data_path)
        self.map_location = map_location
        self.zoom_start = zoom_start
        
        # save 폴더 경로
        self.save_dir = base_dir / "save"
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        self.state_geo = None
        self.state_data = None
        self.map = None
        
        logger.info("UnemploymentService 초기화 완료")
    
    def load_geo_data(self) -> dict:
        """
        지리 데이터 로드 (로컬 파일)
        
        Returns:
            dict: 지리 데이터 JSON
        """
        try:
            with open(self.geo_data_path, 'r', encoding='utf-8') as f:
                self.state_geo = json.load(f)
            logger.info(f"지리 데이터 로드 완료: {self.geo_data_path}")
            return self.state_geo
        except Exception as e:
            logger.error(f"지리 데이터 로드 실패: {str(e)}")
            raise
    
    def load_unemployment_data(self) -> pd.DataFrame:
        """
        실업률 데이터 로드 (로컬 파일)
        
        Returns:
            pd.DataFrame: 실업률 데이터
        """
        try:
            self.state_data = pd.read_csv(self.data_path)
            logger.info(f"실업률 데이터 로드 완료: {self.data_path}")
            return self.state_data
        except Exception as e:
            logger.error(f"실업률 데이터 로드 실패: {str(e)}")
            raise
    
    def create_map(self) -> folium.Map:
        """
        Folium 지도 생성
        
        Returns:
            folium.Map: 생성된 지도 객체
        """
        self.map = folium.Map(
            location=self.map_location,
            zoom_start=self.zoom_start
        )
        logger.info("지도 생성 완료")
        return self.map
    
    def add_choropleth(
        self,
        fill_color: str = "YlGn",
        fill_opacity: float = 0.7,
        line_opacity: float = 0.2,
        legend_name: str = "Unemployment Rate (%)"
    ) -> None:
        """
        Choropleth 레이어 추가
        
        Args:
            fill_color: 채우기 색상
            fill_opacity: 채우기 투명도
            line_opacity: 선 투명도
            legend_name: 범례 이름
        """
        if self.map is None:
            self.create_map()
        
        if self.state_geo is None:
            self.load_geo_data()
        
        if self.state_data is None:
            self.load_unemployment_data()
        
        folium.Choropleth(
            geo_data=self.state_geo,
            name="choropleth",
            data=self.state_data,
            columns=["State", "Unemployment"],
            key_on="feature.id",
            fill_color=fill_color,
            fill_opacity=fill_opacity,
            line_opacity=line_opacity,
            legend_name=legend_name,
        ).add_to(self.map)
        
        logger.info("Choropleth 레이어 추가 완료")
    
    def add_layer_control(self) -> None:
        """레이어 컨트롤 추가"""
        if self.map is None:
            raise ValueError("지도가 생성되지 않았습니다. create_map()을 먼저 호출하세요.")
        
        folium.LayerControl().add_to(self.map)
        logger.info("레이어 컨트롤 추가 완료")
    
    def build_map(
        self,
        fill_color: str = "YlGn",
        fill_opacity: float = 0.7,
        line_opacity: float = 0.2,
        legend_name: str = "Unemployment Rate (%)"
    ) -> folium.Map:
        """
        전체 지도 생성 및 설정 (편의 메서드)
        
        Args:
            fill_color: 채우기 색상
            fill_opacity: 채우기 투명도
            line_opacity: 선 투명도
            legend_name: 범례 이름
            
        Returns:
            folium.Map: 완성된 지도 객체
        """
        self.load_geo_data()
        self.load_unemployment_data()
        self.create_map()
        self.add_choropleth(fill_color, fill_opacity, line_opacity, legend_name)
        self.add_layer_control()
        
        logger.info("지도 빌드 완료")
        return self.map
    
    def get_map(self) -> Optional[folium.Map]:
        """
        현재 지도 객체 반환
        
        Returns:
            Optional[folium.Map]: 지도 객체 (없으면 None)
        """
        return self.map
    
    def save_map_as_image(
        self,
        output_filename: str = "us_unemployment_map.png",
        fill_color: str = "YlGn",
        fill_opacity: float = 0.7,
        line_opacity: float = 0.2,
        legend_name: str = "Unemployment Rate (%)"
    ) -> str:
        """
        지도를 이미지로 저장
        
        Folium 지도는 HTML/JavaScript 기반이므로 이미지로 변환하려면 브라우저 렌더링이 필요합니다.
        Playwright를 우선 사용하고, 없으면 HTML 파일로 저장합니다.
        
        Args:
            output_filename: 출력 파일명
            fill_color: 채우기 색상
            fill_opacity: 채우기 투명도
            line_opacity: 선 투명도
            legend_name: 범례 이름
            
        Returns:
            str: 저장된 이미지 파일 경로
        """
        try:
            # 지도 생성
            self.build_map(fill_color, fill_opacity, line_opacity, legend_name)
            
            if self.map is None:
                raise ValueError("지도가 생성되지 않았습니다.")
            
            # 임시 HTML 파일 저장
            temp_html = self.save_dir / "temp_map.html"
            self.map.save(str(temp_html))
            
            output_path = self.save_dir / output_filename
            
            # Playwright를 사용하여 이미지로 변환 (selenium보다 간단하고 빠름)
            try:
                from playwright.sync_api import sync_playwright
                import time
                import os
                
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    page = browser.new_page(viewport={'width': 1920, 'height': 1080})
                    
                    # HTML 파일 로드
                    file_url = f"file://{temp_html.resolve()}"
                    page.goto(file_url, wait_until='networkidle')
                    
                    # 지도 렌더링 대기
                    time.sleep(2)
                    
                    # 스크린샷 저장
                    page.screenshot(path=str(output_path), full_page=True)
                    browser.close()
                    
                    logger.info(f"지도 이미지 저장 완료 (Playwright): {output_path}")
                    
                    # 임시 HTML 파일 삭제
                    if temp_html.exists():
                        temp_html.unlink()
                    
                    return str(output_path)
                    
            except ImportError:
                # Playwright가 없으면 HTML 파일로 저장
                logger.warning("Playwright가 설치되지 않아 HTML 파일로 저장합니다.")
                html_path = self.save_dir / output_filename.replace('.png', '.html')
                self.map.save(str(html_path))
                logger.info(f"지도 HTML 저장 완료: {html_path}")
                logger.warning("이미지로 변환하려면 Playwright를 설치하세요: pip install playwright && playwright install chromium")
                # HTML 파일 경로 반환 (이미지가 아니지만 경로는 반환)
                return str(html_path)
            except Exception as e:
                logger.error(f"Playwright로 이미지 저장 실패: {str(e)}", exc_info=True)
                # 실패해도 HTML은 저장
                html_path = self.save_dir / output_filename.replace('.png', '.html')
                self.map.save(str(html_path))
                logger.info(f"지도 HTML 저장 완료 (이미지 변환 실패): {html_path}")
                return str(html_path)
                
        except Exception as e:
            logger.error(f"지도 저장 중 오류 발생: {str(e)}")
            logger.exception(e)
            raise
