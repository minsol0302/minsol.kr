"""
KoELECTRA 감정분석 서비스
허깅페이스 transformers를 사용한 영화 리뷰 감정분석
"""
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    ElectraForSequenceClassification,
    ElectraModel
)
import numpy as np

logger = logging.getLogger(__name__)


class KoElectraService:
    """KoELECTRA 모델을 사용한 감정분석 서비스 (싱글톤 패턴)"""
    
    _instance: Optional['KoElectraService'] = None
    _initialized: bool = False
    
    def __new__(cls):
        """싱글톤 패턴 구현"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """서비스 초기화 (한 번만 실행)"""
        if self._initialized:
            return
        
        self.model = None
        self.tokenizer = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_path = Path(__file__).parent / "koelectra_model"
        
        logger.info(f"KoElectraService 초기화 시작 (Device: {self.device})")
        logger.info(f"모델 경로: {self.model_path}")
        
        try:
            self._load_model()
            self._initialized = True
            logger.info("KoElectraService 초기화 완료")
        except Exception as e:
            logger.error(f"모델 로딩 실패: {str(e)}", exc_info=True)
            raise
    
    def _load_model(self):
        """모델 및 토크나이저 로드"""
        try:
            # 모델 경로 확인
            if not self.model_path.exists():
                raise FileNotFoundError(f"모델 경로를 찾을 수 없습니다: {self.model_path}")
            
            config_path = self.model_path / "config.json"
            if not config_path.exists():
                raise FileNotFoundError(f"config.json을 찾을 수 없습니다: {config_path}")
            
            logger.info("토크나이저 로딩 중...")
            # 토크나이저 로드
            self.tokenizer = AutoTokenizer.from_pretrained(
                str(self.model_path),
                do_lower_case=False
            )
            logger.info("토크나이저 로딩 완료")
            
            logger.info("모델 로딩 중...")
            # 모델 로드 시도
            # 먼저 SequenceClassification으로 시도
            try:
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    str(self.model_path)
                )
                logger.info("AutoModelForSequenceClassification으로 모델 로딩 성공")
            except Exception as e1:
                logger.warning(f"AutoModelForSequenceClassification 로딩 실패: {e1}")
                # ElectraForSequenceClassification으로 시도
                try:
                    self.model = ElectraForSequenceClassification.from_pretrained(
                        str(self.model_path)
                    )
                    logger.info("ElectraForSequenceClassification으로 모델 로딩 성공")
                except Exception as e2:
                    logger.warning(f"ElectraForSequenceClassification 로딩 실패: {e2}")
                    # Base 모델로 로드 후 분류 헤드 추가
                    logger.info("Base Electra 모델로 로드 시도 중...")
                    from transformers import ElectraConfig
                    base_model = ElectraModel.from_pretrained(str(self.model_path))
                    # config를 수정하여 분류 헤드 추가
                    config = base_model.config
                    config.num_labels = 2
                    self.model = ElectraForSequenceClassification(config)
                    self.model.electra = base_model
                    logger.info("Base 모델 + 분류 헤드로 모델 구성 완료")
            
            # 모델을 디바이스로 이동
            self.model.to(self.device)
            self.model.eval()  # 평가 모드로 설정
            
            logger.info(f"모델이 {self.device}로 로드되었습니다")
            
        except Exception as e:
            logger.error(f"모델 로딩 중 오류 발생: {str(e)}", exc_info=True)
            raise
    
    def predict(self, text: str) -> Dict[str, any]:
        """
        단일 텍스트에 대한 감정 분석
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            감정 분석 결과 딕셔너리
        """
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("모델이 로드되지 않았습니다. 서비스를 먼저 초기화해주세요.")
        
        try:
            # 텍스트 전처리
            text = text.strip()
            if not text:
                raise ValueError("입력 텍스트가 비어있습니다.")
            
            # 토크나이징
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            )
            
            # 디바이스로 이동
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # 추론
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
            
            # 확률 계산
            probabilities = torch.softmax(logits, dim=-1)
            probabilities = probabilities.cpu().numpy()[0]
            
            # 결과 해석
            # 일반적으로 0: negative, 1: positive
            negative_score = float(probabilities[0])
            positive_score = float(probabilities[1])
            
            # 감정 결정
            sentiment = "positive" if positive_score > negative_score else "negative"
            confidence = max(positive_score, negative_score)
            
            return {
                "text": text,
                "sentiment": sentiment,
                "confidence": round(confidence, 4),
                "scores": {
                    "positive": round(positive_score, 4),
                    "negative": round(negative_score, 4)
                }
            }
            
        except Exception as e:
            logger.error(f"예측 중 오류 발생: {str(e)}", exc_info=True)
            raise
    
    def predict_batch(self, texts: List[str]) -> List[Dict[str, any]]:
        """
        여러 텍스트에 대한 배치 감정 분석
        
        Args:
            texts: 분석할 텍스트 리스트
            
        Returns:
            감정 분석 결과 리스트
        """
        if not texts:
            return []
        
        results = []
        for text in texts:
            try:
                result = self.predict(text)
                results.append(result)
            except Exception as e:
                logger.error(f"텍스트 '{text[:50]}...' 분석 중 오류: {str(e)}")
                results.append({
                    "text": text,
                    "sentiment": "error",
                    "confidence": 0.0,
                    "scores": {
                        "positive": 0.0,
                        "negative": 0.0
                    },
                    "error": str(e)
                })
        
        return results
    
    def get_model_info(self) -> Dict[str, any]:
        """모델 정보 반환"""
        return {
            "model_type": type(self.model).__name__ if self.model else None,
            "device": str(self.device),
            "model_path": str(self.model_path),
            "is_loaded": self.model is not None and self.tokenizer is not None,
            "vocab_size": len(self.tokenizer) if self.tokenizer else None
        }

