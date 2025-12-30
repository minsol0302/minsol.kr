"""
FastAPI 서버 - 파일 업로드 API
"""
import os
import sys
import uuid
from pathlib import Path
from typing import List

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

# 현재 스크립트의 디렉토리 기준으로 경로 설정
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "app" / "data"
YOLO_DATA_DIR = DATA_DIR / "yolo"

# 디렉토리 생성
YOLO_DATA_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="CV Service API", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙 (업로드된 파일 접근용)
app.mount("/data", StaticFiles(directory=str(DATA_DIR)), name="data")


@app.get("/health")
def health():
    """헬스 체크"""
    return {"ok": True, "status": "healthy"}


@app.post("/api/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """
    파일 업로드 API
    - multipart/form-data로 파일 수신
    - 저장 위치: app/data/yolo/
    - 파일명: uuid_원본파일명 형식으로 저장
    """
    if not files:
        raise HTTPException(status_code=400, detail="파일이 없습니다.")

    # 허용된 파일 형식
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.pdf', '.txt'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    saved_files = []
    errors = []

    for file in files:
        try:
            # 파일 확장자 확인
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                errors.append(f"{file.filename}: 지원하지 않는 파일 형식입니다.")
                continue

            # 파일 크기 확인
            contents = await file.read()
            file_size = len(contents)
            
            if file_size > MAX_FILE_SIZE:
                errors.append(f"{file.filename}: 파일 크기가 너무 큽니다 (최대 10MB).")
                continue

            if file_size == 0:
                errors.append(f"{file.filename}: 빈 파일입니다.")
                continue

            # 파일명 생성 (UUID + 원본 파일명)
            file_uuid = uuid.uuid4().hex[:8]
            original_name = Path(file.filename).stem
            extension = Path(file.filename).suffix
            new_filename = f"{file_uuid}_{original_name}{extension}"

            # 파일 저장
            file_path = YOLO_DATA_DIR / new_filename
            with open(file_path, "wb") as f:
                f.write(contents)

            saved_files.append({
                "original_name": file.filename,
                "saved_name": new_filename,
                "size": file_size,
                "url": f"/data/yolo/{new_filename}",
            })

        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")

    if errors and not saved_files:
        raise HTTPException(
            status_code=500,
            detail={"message": "모든 파일 저장 실패", "errors": errors}
        )

    return JSONResponse({
        "success": True,
        "message": f"{len(saved_files)}개의 파일이 저장되었습니다.",
        "files": saved_files,
        "errors": errors if errors else None,
    })


@app.get("/api/files")
async def list_files():
    """
    업로드된 파일 목록 조회
    """
    files = []
    for file_path in YOLO_DATA_DIR.iterdir():
        if file_path.is_file():
            stat = file_path.stat()
            files.append({
                "name": file_path.name,
                "size": stat.st_size,
                "url": f"/data/yolo/{file_path.name}",
            })
    
    return {"files": files, "count": len(files)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

