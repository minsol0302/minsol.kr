FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 시스템 패키지 설치 (LightGBM을 위한 OpenMP 및 기타 라이브러리)
# 한글 폰트 설치 (matplotlib 한글 표시를 위해)
RUN apt-get update && apt-get install -y \
    libgomp1 \
    gcc \
    g++ \
    fonts-nanum \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

# 공통 모듈 복사 (빌드 컨텍스트가 ai.labzang.com인 경우)
COPY common ./common

# requirements.txt 복사 및 설치
COPY mlservice/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Playwright 브라우저 설치
RUN playwright install chromium
RUN playwright install-deps chromium

# 앱 복사
COPY mlservice/app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9010"]