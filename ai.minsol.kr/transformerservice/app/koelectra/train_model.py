"""
KoELECTRA 모델 훈련 스크립트
영화 리뷰 데이터를 사용한 감정분석 fine-tuning
"""
import json
import os
import logging
from pathlib import Path
from typing import List, Dict, Tuple
import torch
from torch.utils.data import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    ElectraForSequenceClassification,
    ElectraModel,
    ElectraConfig,
    TrainingArguments,
    Trainer,
    DataCollatorWithPadding
)
from sklearn.model_selection import train_test_split
import numpy as np
try:
    from datasets import load_metric
except ImportError:
    # datasets >= 2.0.0에서는 evaluate 사용
    try:
        import evaluate
        load_metric = evaluate.load
    except ImportError:
        # fallback: 직접 계산
        def load_metric(name):
            class Metric:
                def compute(self, predictions, references):
                    if name == "accuracy":
                        return {"accuracy": sum(p == r for p, r in zip(predictions, references)) / len(predictions)}
            return Metric()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SentimentDataset(Dataset):
    """감정분석 데이터셋"""
    
    def __init__(self, texts: List[str], labels: List[int], tokenizer, max_length: int = 512):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }


def load_review_data(data_dir: Path) -> Tuple[List[str], List[int]]:
    """
    JSON 파일들에서 리뷰 데이터 로드
    
    Returns:
        texts: 리뷰 텍스트 리스트
        labels: 감정 라벨 리스트 (0: negative, 1: positive)
    """
    texts = []
    labels = []
    
    json_files = list(data_dir.glob("*.json"))
    logger.info(f"총 {len(json_files)}개의 JSON 파일 발견")
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                for item in data:
                    review = item.get('review', '').strip()
                    rating = item.get('rating', '5')
                    
                    if not review:
                        continue
                    
                    # rating을 정수로 변환
                    try:
                        rating_int = int(rating)
                    except (ValueError, TypeError):
                        continue
                    
                    # 5 이상은 positive(1), 5 미만은 negative(0)
                    label = 1 if rating_int >= 5 else 0
                    
                    texts.append(review)
                    labels.append(label)
        
        except Exception as e:
            logger.warning(f"파일 {json_file} 로드 중 오류: {str(e)}")
            continue
    
    logger.info(f"총 {len(texts)}개의 리뷰 데이터 로드 완료")
    logger.info(f"Positive: {sum(labels)}, Negative: {len(labels) - sum(labels)}")
    
    return texts, labels


def load_model_and_tokenizer(model_path: Path, num_labels: int = 2):
    """모델과 토크나이저 로드"""
    logger.info(f"모델 로딩 시작: {model_path}")
    
    # 토크나이저 로드
    tokenizer = AutoTokenizer.from_pretrained(
        str(model_path),
        do_lower_case=False
    )
    logger.info("토크나이저 로드 완료")
    
    # 모델 로드 시도
    try:
        # 먼저 SequenceClassification으로 시도
        model = AutoModelForSequenceClassification.from_pretrained(
            str(model_path),
            num_labels=num_labels
        )
        logger.info("AutoModelForSequenceClassification으로 모델 로드 성공")
    except Exception as e1:
        logger.warning(f"AutoModelForSequenceClassification 로드 실패: {e1}")
        try:
            # ElectraForSequenceClassification으로 시도
            model = ElectraForSequenceClassification.from_pretrained(
                str(model_path),
                num_labels=num_labels
            )
            logger.info("ElectraForSequenceClassification으로 모델 로드 성공")
        except Exception as e2:
            logger.warning(f"ElectraForSequenceClassification 로드 실패: {e2}")
            # Base 모델로 로드 후 분류 헤드 추가
            logger.info("Base Electra 모델로 로드 시도 중...")
            base_model = ElectraModel.from_pretrained(str(model_path))
            config = base_model.config
            config.num_labels = num_labels
            model = ElectraForSequenceClassification(config)
            model.electra = base_model
            logger.info("Base 모델 + 분류 헤드로 모델 구성 완료")
    
    return model, tokenizer


def compute_metrics(eval_pred):
    """평가 메트릭 계산"""
    metric = load_metric("accuracy")
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    return metric.compute(predictions=predictions, references=labels)


def train_model(
    model_path: Path,
    data_dir: Path,
    output_dir: Path,
    epochs: int = 5,
    batch_size: int = 16,
    learning_rate: float = 2e-5,
    train_split: float = 0.8
):
    """
    모델 훈련
    
    Args:
        model_path: 사전 훈련된 모델 경로
        data_dir: 훈련 데이터 디렉토리
        output_dir: 훈련된 모델 저장 경로
        epochs: 에포크 수
        batch_size: 배치 크기
        learning_rate: 학습률
        train_split: 훈련 데이터 비율
    """
    # 디바이스 설정
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"사용 디바이스: {device}")
    
    # 데이터 로드
    logger.info("데이터 로드 시작...")
    texts, labels = load_review_data(data_dir)
    
    if len(texts) == 0:
        raise ValueError("훈련 데이터가 없습니다.")
    
    # 훈련/검증 데이터 분할
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        texts, labels, test_size=1-train_split, random_state=42, stratify=labels
    )
    
    logger.info(f"훈련 데이터: {len(train_texts)}개")
    logger.info(f"검증 데이터: {len(val_texts)}개")
    
    # 모델 및 토크나이저 로드
    model, tokenizer = load_model_and_tokenizer(model_path, num_labels=2)
    model.to(device)
    
    # 데이터셋 생성
    train_dataset = SentimentDataset(train_texts, train_labels, tokenizer)
    val_dataset = SentimentDataset(val_texts, val_labels, tokenizer)
    
    # 데이터 콜레이터
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
    
    # 출력 디렉토리 생성
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 훈련 인자 설정
    training_args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=learning_rate,
        weight_decay=0.01,
        logging_dir=str(output_dir / "logs"),
        logging_steps=100,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
        greater_is_better=True,
        save_total_limit=3,
        warmup_steps=500,
        fp16=torch.cuda.is_available(),  # GPU가 있으면 fp16 사용
    )
    
    # Trainer 생성
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
    )
    
    # 훈련 시작
    logger.info("훈련 시작...")
    trainer.train()
    
    # 최종 평가
    logger.info("최종 평가 중...")
    eval_results = trainer.evaluate()
    logger.info(f"최종 평가 결과: {eval_results}")
    
    # 모델 저장
    logger.info(f"모델 저장 중: {output_dir}")
    trainer.save_model()
    tokenizer.save_pretrained(str(output_dir))
    
    logger.info("훈련 완료!")


if __name__ == "__main__":
    # 경로 설정
    base_dir = Path(__file__).parent
    model_path = base_dir / "koelectra_model"
    data_dir = base_dir.parent / "data"
    output_dir = base_dir / "trained_model"
    
    # 훈련 실행
    train_model(
        model_path=model_path,
        data_dir=data_dir,
        output_dir=output_dir,
        epochs=5,
        batch_size=16,
        learning_rate=2e-5
    )

