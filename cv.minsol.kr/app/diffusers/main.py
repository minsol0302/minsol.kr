# FastAPI 엔트리 + 정적 파일 서빙(/outputs/...) 
# + 라우팅 등록입니다.
import sys
from pathlib import Path

# 현재 디렉토리를 sys.path에 추가하여 상대 import 문제 해결
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api.v1.routes.generate import router as generate_router
from core.config import OUTPUTS_DIR, IMAGES_DIR, META_DIR

app = FastAPI(title="Diffusers API", version="1.0.0")

# outputs 디렉토리 생성 (존재하지 않을 경우)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
META_DIR.mkdir(parents=True, exist_ok=True)

# outputs 정적 서빙 (로컬 개발/단독 서버에서 편리)
app.mount("/outputs", StaticFiles(directory=str(OUTPUTS_DIR)), name="outputs")

app.include_router(generate_router, prefix="/api/v1")

@app.get("/health")
def health():
    return {"ok": True}