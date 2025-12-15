# ************
# NLTK 자연어 처리 패키지
# ************
"""
https://datascienceschool.net/view-notebook/118731eec74b4ad3bdd2f89bab077e1b/
NLTK(Natural Language Toolkit) 패키지는 
교육용으로 개발된 자연어 처리 및 문서 분석용 파이썬 패키지다. 
다양한 기능 및 예제를 가지고 있으며 실무 및 연구에서도 많이 사용된다.
NLTK 패키지가 제공하는 주요 기능은 다음과 같다.
말뭉치
토큰 생성
형태소 분석
품사 태깅
"""

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize, RegexpTokenizer
from nltk.stem import PorterStemmer, LancasterStemmer, WordNetLemmatizer
from nltk.tag import pos_tag, untag
from nltk import Text, FreqDist
from wordcloud import WordCloud
import matplotlib.pyplot as plt


class EmmaWordCloud:
    """
    제인 오스틴의 '엠마' 소설을 분석하고 워드클라우드를 생성하는 클래스
    
    NLTK를 사용하여 자연어 처리 작업을 수행하며,
    토큰 생성, 형태소 분석, 품사 태깅, 빈도 분석 등의 기능을 제공합니다.
    """
    
    def __init__(self, corpus_name: str = "austen-emma.txt", quiet: bool = True):
        """
        초기화 메서드
        
        Args:
            corpus_name: 분석할 말뭉치 파일명 (기본값: "austen-emma.txt")
            quiet: NLTK 다운로드 시 출력 여부 (기본값: True)
        """
        # NLTK 데이터 다운로드 (필요한 모든 리소스)
        try:
            nltk.download('book', quiet=quiet)
            nltk.download('punkt', quiet=quiet)
            nltk.download('averaged_perceptron_tagger', quiet=quiet)
            nltk.download('averaged_perceptron_tagger_eng', quiet=quiet)  # 품사 태깅용
            nltk.download('wordnet', quiet=quiet)
            nltk.download('omw-1.4', quiet=quiet)  # WordNet 다국어 지원
        except Exception as e:
            # 다운로드 실패 시 경고만 출력하고 계속 진행
            import warnings
            warnings.warn(f"NLTK 리소스 다운로드 중 오류 발생: {e}")
        
        # 말뭉치 설정
        self.corpus_name = corpus_name
        self.raw_text = None
        self.tokens = None
        self.tagged_tokens = None
        self.text_object = None
        self.freq_dist = None
        
        # 토크나이저 초기화
        self.regex_tokenizer = RegexpTokenizer("[\w]+")
        
        # 형태소 분석기 초기화
        self.porter_stemmer = PorterStemmer()
        self.lancaster_stemmer = LancasterStemmer()
        self.lemmatizer = WordNetLemmatizer()
        
        # 스톱워드 설정
        self.stopwords = ["Mr.", "Mrs.", "Miss", "Mr", "Mrs", "Dear"]
    
    def load_corpus(self) -> str:
        """
        말뭉치를 로드합니다.
        
        Returns:
            str: 원문 텍스트
        """
        self.raw_text = nltk.corpus.gutenberg.raw(self.corpus_name)
        return self.raw_text
    
    def get_corpus_fileids(self) -> list:
        """
        Gutenberg 말뭉치의 사용 가능한 파일 목록을 반환합니다.
        
        Returns:
            list: 파일 ID 목록
        """
        return nltk.corpus.gutenberg.fileids()
    
    def tokenize_sentences(self, text: str = None) -> list:
        """
        텍스트를 문장 단위로 토큰화합니다.
        
        Args:
            text: 토큰화할 텍스트 (None이면 raw_text 사용)
            
        Returns:
            list: 문장 토큰 리스트
        """
        if text is None:
            if self.raw_text is None:
                self.load_corpus()
            text = self.raw_text
        return sent_tokenize(text)
    
    def tokenize_words(self, text: str = None) -> list:
        """
        텍스트를 단어 단위로 토큰화합니다.
        
        Args:
            text: 토큰화할 텍스트 (None이면 raw_text 사용)
            
        Returns:
            list: 단어 토큰 리스트
        """
        if text is None:
            if self.raw_text is None:
                self.load_corpus()
            text = self.raw_text
        return word_tokenize(text)
    
    def tokenize_regex(self, text: str = None, pattern: str = "[\w]+") -> list:
        """
        정규표현식을 사용하여 텍스트를 토큰화합니다.
        
        Args:
            text: 토큰화할 텍스트 (None이면 raw_text 사용)
            pattern: 정규표현식 패턴 (기본값: "[\w]+")
            
        Returns:
            list: 토큰 리스트
        """
        if text is None:
            if self.raw_text is None:
                self.load_corpus()
            text = self.raw_text
        
        tokenizer = RegexpTokenizer(pattern)
        self.tokens = tokenizer.tokenize(text)
        return self.tokens
    
    def stem_porter(self, words: list) -> list:
        """
        Porter Stemmer를 사용하여 어간을 추출합니다.
        
        Args:
            words: 어간 추출할 단어 리스트
            
        Returns:
            list: 어간 추출된 단어 리스트
        """
        return [self.porter_stemmer.stem(w) for w in words]
    
    def stem_lancaster(self, words: list) -> list:
        """
        Lancaster Stemmer를 사용하여 어간을 추출합니다.
        
        Args:
            words: 어간 추출할 단어 리스트
            
        Returns:
            list: 어간 추출된 단어 리스트
        """
        return [self.lancaster_stemmer.stem(w) for w in words]
    
    def lemmatize(self, words: list, pos: str = None) -> list:
        """
        단어를 원형으로 복원합니다.
        
        Args:
            words: 원형 복원할 단어 리스트
            pos: 품사 태그 (None이면 자동 감지)
            
        Returns:
            list: 원형 복원된 단어 리스트
        """
        if pos:
            return [self.lemmatizer.lemmatize(w, pos=pos) for w in words]
        return [self.lemmatizer.lemmatize(w) for w in words]
    
    def pos_tag_text(self, tokens: list = None) -> list:
        """
        토큰에 품사를 부착합니다.
        
        Args:
            tokens: 품사 태깅할 토큰 리스트 (None이면 self.tokens 사용)
            
        Returns:
            list: (토큰, 품사) 튜플 리스트
        """
        if tokens is None:
            if self.tokens is None:
                self.tokenize_regex()
            tokens = self.tokens
        
        self.tagged_tokens = pos_tag(tokens)
        return self.tagged_tokens
    
    def get_pos_help(self, tag: str = None):
        """
        품사 태그에 대한 도움말을 출력합니다.
        
        Args:
            tag: 조회할 품사 태그 (None이면 전체 태그 설명)
        """
        if tag:
            nltk.help.upenn_tagset(tag)
        else:
            nltk.help.upenn_tagset()
    
    def filter_by_pos(self, pos_tag: str, tagged_list: list = None) -> list:
        """
        특정 품사만 필터링합니다.
        
        Args:
            pos_tag: 필터링할 품사 태그 (예: "NN", "NNP")
            tagged_list: 품사 태깅된 리스트 (None이면 self.tagged_tokens 사용)
            
        Returns:
            list: 필터링된 토큰 리스트
        """
        if tagged_list is None:
            if self.tagged_tokens is None:
                self.pos_tag_text()
            tagged_list = self.tagged_tokens
        
        return [t[0] for t in tagged_list if t[1] == pos_tag]
    
    def create_text_object(self, tokens: list = None, name: str = "Emma") -> Text:
        """
        NLTK Text 객체를 생성합니다.
        
        Args:
            tokens: 토큰 리스트 (None이면 self.tokens 사용)
            name: 텍스트 이름
            
        Returns:
            Text: NLTK Text 객체
        """
        if tokens is None:
            if self.tokens is None:
                self.tokenize_regex()
            tokens = self.tokens
        
        self.text_object = Text(tokens, name=name)
        return self.text_object
    
    def plot_word_frequency(self, num_words: int = 20, show: bool = True):
        """
        단어 빈도를 그래프로 표시합니다.
        
        Args:
            num_words: 표시할 단어 수
            show: 그래프 표시 여부
        """
        if self.text_object is None:
            self.create_text_object()
        
        self.text_object.plot(num_words)
        if show:
            plt.show()
    
    def plot_dispersion(self, words: list, show: bool = True):
        """
        단어의 분산도를 시각화합니다.
        
        Args:
            words: 시각화할 단어 리스트
            show: 그래프 표시 여부
        """
        if self.text_object is None:
            self.create_text_object()
        
        self.text_object.dispersion_plot(words)
        if show:
            plt.show()
 
    def get_concordance(self, word: str, lines: int = 5):
        """
        단어가 사용된 위치를 표시합니다.
        
        Args:
            word: 검색할 단어
            lines: 표시할 줄 수
        """
        if self.text_object is None:
            self.create_text_object()
        
        self.text_object.concordance(word, lines=lines)
    
    def get_similar_words(self, word: str, num: int = 10) -> list:
        """
        비슷한 문맥에서 사용된 단어들을 찾습니다.
        
        Args:
            word: 기준 단어
            num: 반환할 단어 수
            
        Returns:
            list: 유사 단어 리스트
        """
        if self.text_object is None:
            self.create_text_object()
        
        return self.text_object.similar(word, num)
    
    def get_collocations(self, num: int = 10):
        """
        연어(collocation)를 찾습니다.
        
        Args:
            num: 반환할 연어 수
        """
        if self.text_object is None:
            self.create_text_object()
        
        self.text_object.collocations(num)
    
    def create_freq_dist(self, tokens: list = None) -> FreqDist:
        """
        빈도 분포 객체를 생성합니다.
        
        Args:
            tokens: 빈도 분석할 토큰 리스트 (None이면 text_object.vocab() 사용)
            
        Returns:
            FreqDist: 빈도 분포 객체
        """
        if tokens is None:
            if self.text_object is None:
                self.create_text_object()
            self.freq_dist = self.text_object.vocab()
        else:
            self.freq_dist = FreqDist(tokens)
        
        return self.freq_dist
    
    def extract_names(self, pos_tag: str = "NNP", stopwords: list = None) -> FreqDist:
        """
        고유명사(이름)를 추출하여 빈도 분포를 생성합니다.
        
        Args:
            pos_tag: 추출할 품사 태그 (기본값: "NNP")
            stopwords: 제외할 단어 리스트 (None이면 self.stopwords 사용)
            
        Returns:
            FreqDist: 이름 빈도 분포 객체
        """
        if stopwords is None:
            stopwords = self.stopwords
        
        if self.tagged_tokens is None:
            self.pos_tag_text()
        
        names_list = [
            t[0] for t in self.tagged_tokens 
            if t[1] == pos_tag and t[0] not in stopwords
        ]
        
        self.freq_dist = FreqDist(names_list)
        return self.freq_dist
    
    def get_freq_stats(self, word: str = None) -> dict:
        """
        빈도 통계를 반환합니다.
        
        Args:
            word: 통계를 조회할 단어 (None이면 전체 통계)
            
        Returns:
            dict: 통계 정보 딕셔너리
        """
        if self.freq_dist is None:
            self.create_freq_dist()
        
        stats = {
            'total_words': self.freq_dist.N(),
        }
        
        if word:
            stats['word_count'] = self.freq_dist[word]
            stats['word_frequency'] = self.freq_dist.freq(word)
        
        return stats
    
    def get_most_common(self, num: int = 10) -> list:
        """
        가장 빈번한 단어를 반환합니다.
        
        Args:
            num: 반환할 단어 수
            
        Returns:
            list: (단어, 빈도) 튜플 리스트
        """
        if self.freq_dist is None:
            self.create_freq_dist()
        
        return self.freq_dist.most_common(num)
    
    def generate_wordcloud(
        self, 
        freq_dist: FreqDist = None,
        width: int = 1000,
        height: int = 600,
        background_color: str = "white",
        random_state: int = 0,
        show: bool = True
    ) -> WordCloud:
        """
        워드클라우드를 생성합니다.
        
        Args:
            freq_dist: 빈도 분포 객체 (None이면 self.freq_dist 사용)
            width: 이미지 너비
            height: 이미지 높이
            background_color: 배경색
            random_state: 랜덤 시드
            show: 그래프 표시 여부
            
        Returns:
            WordCloud: 워드클라우드 객체
        """
        if freq_dist is None:
            if self.freq_dist is None:
                self.extract_names()
            freq_dist = self.freq_dist
        
        wc = WordCloud(
            width=width,
            height=height,
            background_color=background_color,
            random_state=random_state
        )
        
        wc.generate_from_frequencies(freq_dist)
        
        if show:
            plt.imshow(wc)
            plt.axis("off")
            plt.show()
        
        return wc
    
    def save_wordcloud(
        self,
        output_path: str = None,
        freq_dist: FreqDist = None,
        width: int = 1000,
        height: int = 600,
        background_color: str = "white",
        random_state: int = 0,
        format: str = "png"
    ) -> str:
        """
        워드클라우드를 이미지 파일로 저장합니다.
        
        Args:
            output_path: 저장할 파일 경로 (None이면 기본 경로 사용)
            freq_dist: 빈도 분포 객체 (None이면 self.freq_dist 사용)
            width: 이미지 너비
            height: 이미지 높이
            background_color: 배경색
            random_state: 랜덤 시드
            format: 저장 형식 ("png", "jpg", "pdf" 등)
            
        Returns:
            str: 저장된 파일 경로
        """
        from pathlib import Path
        from datetime import datetime
        
        # 워드클라우드 생성
        wc = self.generate_wordcloud(
            freq_dist=freq_dist,
            width=width,
            height=height,
            background_color=background_color,
            random_state=random_state,
            show=False
        )
        
        # 저장 경로 설정
        if output_path is None:
            # 기본 저장 경로: nlp/save 디렉토리
            # __file__은 emma/emma_wordcloud.py이므로
            # parent.parent는 nlp 디렉토리
            base_dir = Path(__file__).parent.parent
            save_dir = base_dir / "save"
            save_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"emma_wordcloud_{timestamp}.{format}"
            output_path = save_dir / filename
        else:
            output_path = Path(output_path)
            # 절대 경로로 변환
            output_path = output_path.resolve()
            
            # emma/save 경로가 포함되어 있으면 nlp/save로 강제 변경
            output_str = str(output_path)
            if "/emma/save" in output_str or "\\emma\\save" in output_str:
                # emma/save 경로를 nlp/save로 변경
                base_dir = Path(__file__).parent.parent
                save_dir = base_dir / "save"
                save_dir.mkdir(parents=True, exist_ok=True)
                output_path = save_dir / output_path.name
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"경로가 emma/save로 설정되어 있어 nlp/save로 변경했습니다: {output_path}")
            
            # nlp/save 디렉토리만 사용하도록 확인
            if output_path.parent.name == "save" and "nlp" in str(output_path.parent.parent):
                output_path.parent.mkdir(parents=True, exist_ok=True)
            else:
                # nlp/save가 아니면 강제로 nlp/save로 변경
                base_dir = Path(__file__).parent.parent
                save_dir = base_dir / "save"
                save_dir.mkdir(parents=True, exist_ok=True)
                output_path = save_dir / output_path.name
        
        # 이미지 저장
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"워드클라우드 저장 시작: {output_path}")
        
        plt.figure(figsize=(width/100, height/100), dpi=100)
        plt.imshow(wc, interpolation='bilinear')
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
    
    def analyze_full_pipeline(self) -> dict:
        """
        전체 분석 파이프라인을 실행합니다.
        
        Returns:
            dict: 분석 결과 딕셔너리
        """
        # 1. 말뭉치 로드
        self.load_corpus()
        
        # 2. 토큰화
        self.tokenize_regex()
        
        # 3. 품사 태깅
        self.pos_tag_text()
        
        # 4. Text 객체 생성
        self.create_text_object()
        
        # 5. 이름 추출 및 빈도 분석
        self.extract_names()
        
        # 6. 통계 수집
        stats = self.get_freq_stats("Emma")
        most_common = self.get_most_common(10)
        
        return {
            'total_tokens': len(self.tokens),
            'total_tagged': len(self.tagged_tokens),
            'emma_stats': stats,
            'most_common_names': most_common
        }


# 사용 예제
if __name__ == "__main__":
    # 클래스 인스턴스 생성
    emma = EmmaWordCloud()
    
    # 전체 파이프라인 실행
    results = emma.analyze_full_pipeline()
    print("분석 결과:", results)
    
    # 워드클라우드 생성
    emma.generate_wordcloud()
    
    # 추가 분석 예제
    print("\n=== 문장 토큰화 예제 ===")
    sentences = emma.tokenize_sentences(emma.raw_text[:1000])
    print(f"문장 수: {len(sentences)}")
    if sentences:
        print(f"첫 번째 문장: {sentences[0]}")
    
    print("\n=== 형태소 분석 예제 ===")
    words = ['lives', 'crying', 'flies', 'dying']
    print(f"원본: {words}")
    print(f"Porter Stemming: {emma.stem_porter(words)}")
    print(f"Lancaster Stemming: {emma.stem_lancaster(words)}")
    print(f"Lemmatization: {emma.lemmatize(words)}")
    
    print("\n=== 품사 태깅 예제 ===")
    sentence = "Emma refused to permit us to obtain the refuse permit"
    tokens = word_tokenize(sentence)
    tagged = pos_tag(tokens)
    print(f"태깅 결과: {tagged}")
    
    print("\n=== 빈도 통계 ===")
    stats = emma.get_freq_stats("Emma")
    print(f"Emma 통계: {stats}")
    
    print("\n=== 가장 빈번한 이름 Top 5 ===")
    top_names = emma.get_most_common(5)
    for name, count in top_names:
        print(f"{name}: {count}회")
