"""
YOLO11 메인 실행 파일 - data/yolo 폴더의 이미지 처리
"""
from ultralytics import YOLO
import os
from pathlib import Path

if __name__ == "__main__":
    # YOLO11 모델 로드
    model = YOLO('yolo11n.pt')
    
    # 현재 스크립트의 디렉토리 기준으로 data/yolo 폴더 경로 설정
    current_dir = Path(__file__).resolve().parent
    data_yolo_dir = current_dir.parent / "data" / "yolo"
    
    # 디렉토리 존재 확인
    if not data_yolo_dir.exists():
        print(f"디렉토리를 찾을 수 없습니다: {data_yolo_dir}")
        print("디렉토리를 생성합니다...")
        data_yolo_dir.mkdir(parents=True, exist_ok=True)
        print("디렉토리가 생성되었습니다. 이미지를 업로드해주세요.")
        exit(0)
    
    # 지원하는 이미지 확장자
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
    
    # data/yolo 폴더의 모든 이미지 파일 찾기
    image_files = [
        f for f in data_yolo_dir.iterdir()
        if f.is_file() and f.suffix.lower() in image_extensions
    ]
    
    if not image_files:
        print(f"처리할 이미지 파일이 없습니다: {data_yolo_dir}")
        exit(0)
    
    print(f"총 {len(image_files)}개의 이미지 파일을 찾았습니다.")
    
    # 각 이미지 파일 처리
    for image_path in image_files:
        print(f"\n이미지 처리 중: {image_path.name}")
        
        try:
            # YOLO 모델로 이미지 처리
            results = model(str(image_path))
            
            # 결과 저장 (원본 파일명에 _result 추가)
            output_path = data_yolo_dir / f"{image_path.stem}_result{image_path.suffix}"
            results[0].save(str(output_path))
            print(f"결과가 저장되었습니다: {output_path.name}")
            
            # 결과 표시 (선택사항 - 주석 처리)
            # results[0].show()
            
        except Exception as e:
            print(f"오류 발생 ({image_path.name}): {e}")
            continue
    
    print(f"\n모든 이미지 처리 완료!")

