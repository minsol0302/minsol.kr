# ************
# NLTK 자연어 처리 패키지
# ************

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize, RegexpTokenizer
from nltk.stem import PorterStemmer, LancasterStemmer, WordNetLemmatizer
from nltk.tag import pos_tag, untag
from nltk import Text, FreqDist
from wordcloud import WordCloud
from konlpy.tag import Okt
import logging
import re
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class EmotionInference:

    def __init__(self, quiet: bool = True):
        """
        초기화 메서드
        
        Args:
            quiet: NLTK 다운로드 시 출력 여부 (기본값: True)
        """
        # NLTK 데이터 다운로드 (word_tokenize 사용을 위해 필요)
        try:
            nltk.download('punkt', quiet=quiet)
            nltk.download('punkt_tab', quiet=quiet)  # 최신 NLTK 버전에서 필요
            nltk.download('stopwords', quiet=quiet)
        except Exception as e:
            # 다운로드 실패 시 경고만 출력하고 계속 진행
            import warnings
            warnings.warn(f"NLTK 리소스 다운로드 중 오류 발생: {e}")
        
        self.okt = Okt()