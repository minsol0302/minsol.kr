# 로컬 모델 디렉터리

이 디렉터리는 로컬에서 사용할 AI 모델들을 저장하는 곳입니다.

## 현재 지원되는 모델

### Midm-2.0-Mini-Instruct
- **위치**: `app/model/midm/`
- **설명**: K-intelligence에서 개발한 한국어 특화 소형 Instruct 모델
- **사용법**:
  ```bash
  # .env 파일에서
  LLM_PROVIDER=midm
  ```

## 모델 추가 방법

1. 새 모델 디렉터리 생성 (예: `app/model/new_model/`)
2. 모델 파일들 배치:
   - `model.safetensors` (또는 `pytorch_model.bin`)
   - `config.json`
   - `tokenizer.json`
   - `tokenizer_config.json`
   - 기타 필요한 파일들

3. `app/core/llm/providers/` 에 새 provider 모듈 생성
4. `app/core/llm/factory.py` 에 새 provider 등록

## 주의사항

- 모델 파일들은 Git에 커밋되지 않습니다 (`.gitignore` 설정)
- 대용량 모델의 경우 충분한 메모리와 저장 공간이 필요합니다
- GPU 사용 시 CUDA 호환성을 확인하세요
