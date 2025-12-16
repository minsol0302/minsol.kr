"""
미국 실업률 데이터 시각화 라우터
"""
from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.responses import HTMLResponse
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys
import logging

# 공통 모듈 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.us_unemployment.service import USUnemploymentService

# common 모듈 import 시도
try:
    from common.utils import create_response, create_error_response, setup_logging
except ImportError:
    # common 모듈이 없을 경우 기본 함수 정의
    def setup_logging(name: str):
        return logging.getLogger(name)
    def create_response(data: Any, message: str = "Success", status: str = "success") -> Dict:
        from datetime import datetime
        return {
            "status": status,
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
    def create_error_response(message: str, error_code: str = "UNKNOWN_ERROR") -> Dict:
        from datetime import datetime
        return {
            "status": "error",
            "message": message,
            "error_code": error_code,
            "timestamp": datetime.utcnow().isoformat()
        }

# Logger 초기화
logger = logging.getLogger(__name__)

router = APIRouter(tags=["usa"])

# 서비스 인스턴스 생성 (싱글톤 패턴)
_service_instance: Optional[USUnemploymentService] = None


def get_service() -> USUnemploymentService:
    """USUnemploymentService 싱글톤 인스턴스 반환"""
    global _service_instance
    if _service_instance is None:
        logger.info("USUnemploymentService 인스턴스 생성 중...")
        _service_instance = USUnemploymentService()
        logger.info("USUnemploymentService 인스턴스 생성 완료")
    return _service_instance


@router.get("/")
async def usa_root():
    """
    미국 실업률 서비스 루트 및 지도 이미지 생성
    
    Returns:
        dict: 서비스 상태 및 지도 이미지 저장 정보
    """
    try:
        service = get_service()
        
        # 지도를 이미지로 저장
        image_path = service.save_map_as_image(
            output_filename="us_unemployment_map.png",
            fill_color="YlGn",
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name="Unemployment Rate (%)"
        )
        
        return create_response(
            data={
                "service": "mlservice",
                "module": "usa",
                "status": "running",
                "image_path": image_path,
                "image_saved": True
            },
            message="US Unemployment Service is running and map image saved"
        )
    except Exception as e:
        logger.error(f"지도 이미지 생성 오류: {str(e)}", exc_info=True)
        return create_response(
            data={
                "service": "mlservice",
                "module": "usa",
                "status": "running",
                "image_saved": False,
                "error": str(e)
            },
            message="US Unemployment Service is running but map image generation failed"
        )


@router.get("/map", response_class=HTMLResponse)
async def get_map(
    fill_color: str = Query(default="YlGn", description="채우기 색상"),
    fill_opacity: float = Query(default=0.7, ge=0.0, le=1.0, description="채우기 투명도"),
    line_opacity: float = Query(default=0.2, ge=0.0, le=1.0, description="선 투명도"),
    legend_name: str = Query(default="Unemployment Rate (%)", description="범례 이름")
):
    """
    미국 실업률 지도 생성 및 HTML 반환
    
    Returns:
        HTMLResponse: Folium 지도 HTML
    """
    try:
        service = get_service()
        map_obj = service.build_map(
            fill_color=fill_color,
            fill_opacity=fill_opacity,
            line_opacity=line_opacity,
            legend_name=legend_name
        )
        
        # Folium 지도를 HTML 문자열로 변환
        html_string = map_obj._repr_html_()
        
        return HTMLResponse(content=html_string)
    except Exception as e:
        logger.error(f"지도 생성 오류: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create map: {str(e)}"
        )


@router.post("/map/build")
async def build_map(
    fill_color: str = Body(default="YlGn", description="채우기 색상"),
    fill_opacity: float = Body(default=0.7, ge=0.0, le=1.0, description="채우기 투명도"),
    line_opacity: float = Body(default=0.2, ge=0.0, le=1.0, description="선 투명도"),
    legend_name: str = Body(default="Unemployment Rate (%)", description="범례 이름")
):
    """
    미국 실업률 지도 생성 (JSON 응답)
    
    Returns:
        dict: 지도 생성 결과
    """
    try:
        service = get_service()
        map_obj = service.build_map(
            fill_color=fill_color,
            fill_opacity=fill_opacity,
            line_opacity=line_opacity,
            legend_name=legend_name
        )
        
        return create_response(
            data={
                "map_created": map_obj is not None,
                "location": service.map_location,
                "zoom_start": service.zoom_start,
                "message": "지도가 생성되었습니다. /map 엔드포인트에서 HTML을 확인하세요."
            },
            message="Map created successfully"
        )
    except Exception as e:
        logger.error(f"지도 생성 오류: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create map: {str(e)}"
        )


@router.get("/data/geo")
async def get_geo_data():
    """지리 데이터 조회"""
    try:
        service = get_service()
        geo_data = service.load_geo_data()
        
        return create_response(
            data={
                "geo_data_loaded": geo_data is not None,
                "features_count": len(geo_data.get("features", [])) if geo_data else 0
            },
            message="Geo data loaded successfully"
        )
    except Exception as e:
        logger.error(f"지리 데이터 로드 오류: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load geo data: {str(e)}"
        )


@router.get("/data/unemployment")
async def get_unemployment_data():
    """실업률 데이터 조회"""
    try:
        service = get_service()
        unemployment_data = service.load_unemployment_data()
        
        # DataFrame을 딕셔너리로 변환 (일부만 반환)
        data_dict = unemployment_data.head(10).to_dict(orient="records")
        
        return create_response(
            data={
                "data_loaded": unemployment_data is not None,
                "total_states": len(unemployment_data) if unemployment_data is not None else 0,
                "sample_data": data_dict,
                "columns": unemployment_data.columns.tolist() if unemployment_data is not None else []
            },
            message="Unemployment data loaded successfully"
        )
    except Exception as e:
        logger.error(f"실업률 데이터 로드 오류: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load unemployment data: {str(e)}"
        )

