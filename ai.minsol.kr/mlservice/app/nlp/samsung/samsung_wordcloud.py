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

class SamsungWordCloud:

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

    def text_process(self, save: bool = True):
        """
        전체 텍스트 처리 파이프라인을 실행합니다.
        
        Args:
            save: 워드클라우드 저장 여부 (기본값: True)
        
        Returns:
            dict: 처리 결과
        """
        freq_txt = self.find_freq()
        
        if save:
            # 워드클라우드 저장
            saved_path = self.save_wordcloud()
            return {
                '전처리 결과': '완료',
                'freq_txt': freq_txt,
                'wordcloud_saved': True,
                'file_path': saved_path
            }
        else:
            # 워드클라우드만 표시
            self.draw_wordcloud()
            return {
                '전처리 결과': '완료',
                'freq_txt': freq_txt
            }
    
    def read_file(self):
        self.okt.pos("삼성전자 글로벌센터 전자사업부", stem=True)
        # 상대 경로를 절대 경로로 변환
        base_dir = Path(__file__).parent.parent
        fname = base_dir / 'data' / 'kr-Report_2018.txt'
        with open(fname, 'r', encoding='utf-8') as f:
            self.text = f.read()
        return self.text

    def extract_hangeul(self, text: str):
        temp = text.replace('\n', ' ')
        tokenizer = re.compile('[^ ㄱ-ㅣ가-힣]+')
        return tokenizer.sub('',temp)

    def change_token(self, texts):
        return word_tokenize(texts)

    def extract_noun(self):
        # 삼성전자의 스마트폰은 -> 삼성전자 스마트폰
        noun_tokens = []
        tokens = self.change_token(self.extract_hangeul(self.read_file()))
        for i in tokens:
            pos = self.okt.pos(i)
            temp = [j[0] for j in pos if j[1] == 'Noun']
            if len(''.join(temp)) > 1 :
                noun_tokens.append(''.join(temp))
        texts = ' '.join(noun_tokens)
        logger.info(texts[:100])
        return texts

    def read_stopword(self):
        self.okt.pos("삼성전자 글로벌센터 전자사업부", stem=True)
        # 상대 경로를 절대 경로로 변환
        base_dir = Path(__file__).parent.parent
        fname = base_dir / 'data' / 'stopwords.txt'
        with open(fname, 'r', encoding='utf-8') as f:
            stopwords = f.read()
        return stopwords

    def remove_stopword(self):
        texts = self.extract_noun()
        tokens = self.change_token(texts)
        # print('------- 1 명사 -------')
        # print(texts[:30])
        stopwords = self.read_stopword()
        # print('------- 2 스톱 -------')
        # print(stopwords[:30])
        # print('------- 3 필터 -------')
        texts = [text for text in tokens
                 if text not in stopwords]
        # print(texts[:30])
        return texts

    def find_freq(self):
        texts = self.remove_stopword()
        freqtxt = pd.Series(dict(FreqDist(texts))).sort_values(ascending=False)
        logger.info(freqtxt[:30])
        return freqtxt

    def draw_wordcloud(self, show: bool = True):
        """
        워드클라우드를 생성하고 표시합니다.
        
        Args:
            show: 그래프 표시 여부 (기본값: True)
        """
        texts = self.remove_stopword()
        
        # 한글 폰트 경로 설정
        base_dir = Path(__file__).parent.parent
        font_path = base_dir / 'data' / 'D2Coding.ttf'
        
        # 폰트 파일이 없으면 기본 폰트 사용
        if not font_path.exists():
            logger.warning(f"한글 폰트 파일을 찾을 수 없습니다: {font_path}. 기본 폰트를 사용합니다.")
            font_path = None
        
        wcloud = WordCloud(
            font_path=str(font_path) if font_path else None,
            relative_scaling=0.2,
            background_color='white',
            width=1200,
            height=1200
        ).generate(" ".join(texts))
        
        plt.figure(figsize=(12, 12))
        plt.imshow(wcloud, interpolation='bilinear')
        plt.axis('off')
        
        if show:
            plt.show()
        
        return wcloud
    
    def save_wordcloud(
        self,
        output_path: str = None,
        width: int = 1200,
        height: int = 1200,
        background_color: str = "white",
        relative_scaling: float = 0.2,
        format: str = "png"
    ) -> str:
        """
        워드클라우드를 이미지 파일로 저장합니다.
        
        Args:
            output_path: 저장할 파일 경로 (None이면 기본 경로 사용)
            width: 이미지 너비
            height: 이미지 높이
            background_color: 배경색
            relative_scaling: 상대 크기 조정
            format: 저장 형식 ("png", "jpg", "pdf" 등)
            
        Returns:
            str: 저장된 파일 경로
        """
        texts = self.remove_stopword()
        
        # 한글 폰트 경로 설정
        base_dir = Path(__file__).parent.parent
        font_path = base_dir / 'data' / 'D2Coding.ttf'
        
        # 폰트 파일이 없으면 기본 폰트 사용
        if not font_path.exists():
            logger.warning(f"한글 폰트 파일을 찾을 수 없습니다: {font_path}. 기본 폰트를 사용합니다.")
            font_path = None
        
        # 워드클라우드 생성
        wcloud = WordCloud(
            font_path=str(font_path) if font_path else None,
            relative_scaling=relative_scaling,
            background_color=background_color,
            width=width,
            height=height
        ).generate(" ".join(texts))
        
        # 저장 경로 설정
        if output_path is None:
            # 기본 저장 경로: nlp/save 디렉토리
            # __file__은 samsung/samsung_wordcloud.py이므로
            # parent.parent는 nlp 디렉토리
            save_dir = base_dir / "save"
            save_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"samsung_wordcloud_{timestamp}.{format}"
            output_path = save_dir / filename
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 경로를 절대 경로로 변환
        output_path = output_path.resolve()
        
        # 이미지 저장
        logger.info(f"워드클라우드 저장 시작: {output_path}")
        
        plt.figure(figsize=(width/100, height/100), dpi=100)
        plt.imshow(wcloud, interpolation='bilinear')
        plt.axis("off")
        plt.tight_layout(pad=0)
        plt.savefig(str(output_path), format=format, bbox_inches='tight', dpi=100)
        plt.close()
        
        # 저장 확인
        if output_path.exists():
            file_size = output_path.stat().st_size
            logger.info(f"워드클라우드 저장 완료: {output_path} (크기: {file_size} bytes)")
        else:
            logger.error(f"워드클라우드 저장 실패: 파일이 생성되지 않았습니다. {output_path}")
            raise FileNotFoundError(f"워드클라우드 파일 저장 실패: {output_path}")
        
        return str(output_path)