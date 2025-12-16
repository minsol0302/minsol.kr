"""
NLP 자연어 처리 라우터
"""
from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional, Dict, Any
from pathlib import Path
import sys
import logging
from datetime import datetime
import pandas as pd

# 공통 모듈 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.nlp.emma.emma_wordcloud import EmmaWordCloud
from app.nlp.samsung.samsung_wordcloud import SamsungWordCloud

# common 모듈 import 시도
try:
    from common.utils import create_response, create_error_response, setup_logging
except ImportError:
    # common 모듈이 없을 경우 기본 함수 정의
    def setup_logging(name: str):
        return logging.getLogger(name)
    
    def create_response(data: Any, message: str = "Success", status: str = "success") -> Dict:
        return {
            "status": status,
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def create_error_response(message: str, error_code: str = "UNKNOWN_ERROR") -> Dict:
        return {
            "status": "error",
            "message": message,
            "error_code": error_code,
            "timestamp": datetime.utcnow().isoformat()
        }

# Logger 초기화
logger = logging.getLogger(__name__)

router = APIRouter(tags=["nlp"])

# 서비스 인스턴스 생성 (싱글톤 패턴)
_emma_service_instance: Optional[EmmaWordCloud] = None
_samsung_service_instance: Optional[SamsungWordCloud] = None


def get_emma_service() -> EmmaWordCloud:
    """EmmaWordCloud 싱글톤 인스턴스 반환"""
    global _emma_service_instance
    if _emma_service_instance is None:
        logger.info("EmmaWordCloud 인스턴스 생성 중...")
        _emma_service_instance = EmmaWordCloud()
        logger.info("EmmaWordCloud 인스턴스 생성 완료")
    return _emma_service_instance


def get_samsung_service() -> SamsungWordCloud:
    """SamsungWordCloud 싱글톤 인스턴스 반환"""
    global _samsung_service_instance
    if _samsung_service_instance is None:
        logger.info("SamsungWordCloud 인스턴스 생성 중...")
        _samsung_service_instance = SamsungWordCloud()
        logger.info("SamsungWordCloud 인스턴스 생성 완료")
    return _samsung_service_instance


@router.get("/emma")
async def generate_emma_wordcloud(
    width: int = Query(default=1000, ge=100, le=5000, description="이미지 너비"),
    height: int = Query(default=600, ge=100, le=5000, description="이미지 높이"),
    background_color: str = Query(default="white", description="배경색"),
    random_state: int = Query(default=0, description="랜덤 시드"),
    format: str = Query(default="png", regex="^(png|jpg|jpeg|pdf)$", description="저장 형식")
):
    """
    엠마 소설 워드클라우드 생성 및 저장
    
    제인 오스틴의 '엠마' 소설을 분석하여 워드클라우드를 생성하고 저장합니다.
    
    Returns:
        dict: 워드클라우드 생성 결과 및 파일 경로
    """
    try:
        service = get_emma_service()
        
        # 전체 분석 파이프라인 실행
        logger.info("엠마 소설 분석 시작...")
        analysis_results = service.analyze_full_pipeline()
        logger.info(f"분석 완료: {analysis_results}")
        
        # 워드클라우드 생성 및 저장
        logger.info("워드클라우드 생성 및 저장 중...")
        output_path = service.save_wordcloud(
            output_path=None,  # 기본 경로 사용 (nlp/save)
            width=width,
            height=height,
            background_color=background_color,
            random_state=random_state,
            format=format
        )
        logger.info(f"워드클라우드 저장 완료: {output_path}")
        
        return create_response(
            data={
                "service": "mlservice",
                "module": "nlp",
                "endpoint": "emma",
                "wordcloud_saved": True,
                "file_path": output_path,
                "file_name": Path(output_path).name,
                "analysis_results": analysis_results,
                "image_settings": {
                    "width": width,
                    "height": height,
                    "background_color": background_color,
                    "format": format
                }
            },
            message="Emma wordcloud generated and saved successfully"
        )
    except Exception as e:
        logger.error(f"워드클라우드 생성 오류: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate wordcloud: {str(e)}"
        )


@router.post("/emma")
async def generate_emma_wordcloud_post(
    width: int = Body(default=1000, ge=100, le=5000, description="이미지 너비"),
    height: int = Body(default=600, ge=100, le=5000, description="이미지 높이"),
    background_color: str = Body(default="white", description="배경색"),
    random_state: int = Body(default=0, description="랜덤 시드"),
    format: str = Body(default="png", description="저장 형식 (png, jpg, jpeg, pdf)"),
    output_filename: Optional[str] = Body(default=None, description="출력 파일명 (선택사항)")
):
    """
    엠마 소설 워드클라우드 생성 및 저장 (POST)
    
    제인 오스틴의 '엠마' 소설을 분석하여 워드클라우드를 생성하고 저장합니다.
    
    Returns:
        dict: 워드클라우드 생성 결과 및 파일 경로
    """
    try:
        service = get_emma_service()
        
        # 전체 분석 파이프라인 실행
        logger.info("엠마 소설 분석 시작...")
        analysis_results = service.analyze_full_pipeline()
        logger.info(f"분석 완료: {analysis_results}")
        
        # 출력 경로 설정
        output_path = None
        if output_filename:
            base_dir = Path(__file__).parent / "save"
            base_dir.mkdir(parents=True, exist_ok=True)
            output_path = str(base_dir / output_filename)
        
        # 워드클라우드 생성 및 저장
        logger.info("워드클라우드 생성 및 저장 중...")
        saved_path = service.save_wordcloud(
            output_path=output_path,
            width=width,
            height=height,
            background_color=background_color,
            random_state=random_state,
            format=format
        )
        logger.info(f"워드클라우드 저장 완료: {saved_path}")
        
        return create_response(
            data={
                "service": "mlservice",
                "module": "nlp",
                "endpoint": "emma",
                "wordcloud_saved": True,
                "file_path": saved_path,
                "file_name": Path(saved_path).name,
                "analysis_results": analysis_results,
                "image_settings": {
                    "width": width,
                    "height": height,
                    "background_color": background_color,
                    "format": format
                }
            },
            message="Emma wordcloud generated and saved successfully"
        )
    except Exception as e:
        logger.error(f"워드클라우드 생성 오류: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate wordcloud: {str(e)}"
        )


@router.get("/emma/analysis")
async def get_emma_analysis():
    """
    엠마 소설 분석 결과 조회
    
    Returns:
        dict: 분석 결과 통계
    """
    try:
        service = get_emma_service()
        
        # 분석 파이프라인 실행
        analysis_results = service.analyze_full_pipeline()
        
        # 추가 통계 정보
        stats = service.get_freq_stats("Emma")
        most_common = service.get_most_common(10)
        
        return create_response(
            data={
                "analysis_results": analysis_results,
                "emma_stats": stats,
                "most_common_names": most_common,
                "total_tokens": len(service.tokens) if service.tokens else 0,
                "total_tagged": len(service.tagged_tokens) if service.tagged_tokens else 0
            },
            message="Emma analysis completed successfully"
        )
    except Exception as e:
        logger.error(f"분석 오류: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze: {str(e)}"
        )


@router.get("/emma/file/{filename}")
async def get_wordcloud_file(filename: str):
    """
    저장된 워드클라우드 파일 다운로드
    
    Args:
        filename: 다운로드할 파일명
        
    Returns:
        FileResponse: 파일 응답
    """
    try:
        base_dir = Path(__file__).parent / "save"
        file_path = base_dir / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"File not found: {filename}"
            )
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type="image/png" if filename.endswith(".png") else "application/octet-stream"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"파일 다운로드 오류: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download file: {str(e)}"
        )


@router.get("/samsung")
async def generate_samsung_wordcloud(
    width: int = Query(default=1200, ge=100, le=5000, description="이미지 너비"),
    height: int = Query(default=1200, ge=100, le=5000, description="이미지 높이"),
    background_color: str = Query(default="white", description="배경색"),
    relative_scaling: float = Query(default=0.2, ge=0.0, le=1.0, description="상대 크기 조정"),
    format: str = Query(default="png", regex="^(png|jpg|jpeg|pdf)$", description="저장 형식")
):
    """
    삼성 리포트 한국어 워드클라우드 생성 및 저장
    
    삼성 리포트 텍스트를 분석하여 한국어 워드클라우드를 생성하고 저장합니다.
    
    Returns:
        dict: 워드클라우드 생성 결과 및 파일 경로
    """
    try:
        service = get_samsung_service()
        
        # 텍스트 처리 및 워드클라우드 생성
        logger.info("삼성 리포트 분석 시작...")
        result = service.text_process(save=False)  # 일단 저장하지 않고 분석만
        logger.info(f"분석 완료")
        
        # 워드클라우드 생성 및 저장
        logger.info("워드클라우드 생성 및 저장 중...")
        output_path = service.save_wordcloud(
            output_path=None,  # 기본 경로 사용 (nlp/save)
            width=width,
            height=height,
            background_color=background_color,
            relative_scaling=relative_scaling,
            format=format
        )
        logger.info(f"워드클라우드 저장 완료: {output_path}")
        
        return create_response(
            data={
                "service": "mlservice",
                "module": "nlp",
                "endpoint": "samsung",
                "wordcloud_saved": True,
                "file_path": output_path,
                "file_name": Path(output_path).name,
                "analysis_results": {
                    "전처리 결과": result.get("전처리 결과"),
                    "freq_txt_top_30": result.get("freq_txt", pd.Series()).head(30).to_dict() if hasattr(result.get("freq_txt"), "to_dict") else str(result.get("freq_txt", ""))[:500]
                },
                "image_settings": {
                    "width": width,
                    "height": height,
                    "background_color": background_color,
                    "relative_scaling": relative_scaling,
                    "format": format
                }
            },
            message="Samsung wordcloud generated and saved successfully"
        )
    except Exception as e:
        logger.error(f"워드클라우드 생성 오류: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate wordcloud: {str(e)}"
        )


@router.post("/samsung")
async def generate_samsung_wordcloud_post(
    width: int = Body(default=1200, ge=100, le=5000, description="이미지 너비"),
    height: int = Body(default=1200, ge=100, le=5000, description="이미지 높이"),
    background_color: str = Body(default="white", description="배경색"),
    relative_scaling: float = Body(default=0.2, ge=0.0, le=1.0, description="상대 크기 조정"),
    format: str = Body(default="png", description="저장 형식 (png, jpg, jpeg, pdf)"),
    output_filename: Optional[str] = Body(default=None, description="출력 파일명 (선택사항)")
):
    """
    삼성 리포트 한국어 워드클라우드 생성 및 저장 (POST)
    
    삼성 리포트 텍스트를 분석하여 한국어 워드클라우드를 생성하고 저장합니다.
    
    Returns:
        dict: 워드클라우드 생성 결과 및 파일 경로
    """
    try:
        service = get_samsung_service()
        
        # 텍스트 처리 및 워드클라우드 생성
        logger.info("삼성 리포트 분석 시작...")
        result = service.text_process(save=False)
        logger.info(f"분석 완료")
        
        # 출력 경로 설정
        output_path = None
        if output_filename:
            base_dir = Path(__file__).parent / "save"
            base_dir.mkdir(parents=True, exist_ok=True)
            output_path = str(base_dir / output_filename)
        
        # 워드클라우드 생성 및 저장
        logger.info("워드클라우드 생성 및 저장 중...")
        saved_path = service.save_wordcloud(
            output_path=output_path,
            width=width,
            height=height,
            background_color=background_color,
            relative_scaling=relative_scaling,
            format=format
        )
        logger.info(f"워드클라우드 저장 완료: {saved_path}")
        
        return create_response(
            data={
                "service": "mlservice",
                "module": "nlp",
                "endpoint": "samsung",
                "wordcloud_saved": True,
                "file_path": saved_path,
                "file_name": Path(saved_path).name,
                "analysis_results": {
                    "전처리 결과": result.get("전처리 결과"),
                    "freq_txt_top_30": result.get("freq_txt", pd.Series()).head(30).to_dict() if hasattr(result.get("freq_txt"), "to_dict") else str(result.get("freq_txt", ""))[:500]
                },
                "image_settings": {
                    "width": width,
                    "height": height,
                    "background_color": background_color,
                    "relative_scaling": relative_scaling,
                    "format": format
                }
            },
            message="Samsung wordcloud generated and saved successfully"
        )
    except Exception as e:
        logger.error(f"워드클라우드 생성 오류: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate wordcloud: {str(e)}"
        )


@router.get("/samsung/analysis")
async def get_samsung_analysis():
    """
    삼성 리포트 분석 결과 조회
    
    Returns:
        dict: 분석 결과 통계
    """
    try:
        service = get_samsung_service()
        
        # 텍스트 처리 파이프라인 실행
        result = service.text_process(save=False)
        freq_txt = result.get("freq_txt", pd.Series())
        
        return create_response(
            data={
                "analysis_results": {
                    "전처리 결과": result.get("전처리 결과"),
                    "freq_txt_top_50": freq_txt.head(50).to_dict() if hasattr(freq_txt, "to_dict") else str(freq_txt)[:1000],
                    "total_unique_words": len(freq_txt) if hasattr(freq_txt, "__len__") else 0
                }
            },
            message="Samsung analysis completed successfully"
        )
    except Exception as e:
        logger.error(f"분석 오류: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze: {str(e)}"
        )


@router.get("/samsung/file/{filename}")
async def get_samsung_wordcloud_file(filename: str):
    """
    저장된 삼성 워드클라우드 파일 다운로드
    
    Args:
        filename: 다운로드할 파일명
        
    Returns:
        FileResponse: 파일 응답
    """
    try:
        base_dir = Path(__file__).parent / "save"
        file_path = base_dir / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"File not found: {filename}"
            )
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type="image/png" if filename.endswith(".png") else "application/octet-stream"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"파일 다운로드 오류: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download file: {str(e)}"
        )


@router.get("/")
async def nlp_root():
    """
    NLP 서비스 루트 엔드포인트
    
    Returns:
        dict: 서비스 정보
    """
    return create_response(
        data={
            "service": "mlservice",
            "module": "nlp",
            "status": "running",
            "endpoints": {
                "emma_wordcloud": "/emma",
                "emma_analysis": "/emma/analysis",
                "emma_download": "/emma/file/{filename}",
                "samsung_wordcloud": "/samsung",
                "samsung_analysis": "/samsung/analysis",
                "samsung_download": "/samsung/file/{filename}"
            }
        },
        message="NLP Service is running"
    )

