"""
YOLO11 얼굴 감지 - family.jpg 이미지에서 얼굴만 디텍팅
파일 감시 기능 포함: data/yolo 폴더에 새 이미지가 추가되면 자동으로 얼굴 감지
"""
from ultralytics import YOLO
import cv2
import numpy as np
from pathlib import Path
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def detect_faces_yolo(image_path: str, output_path: str = None):
    """
    YOLO11을 사용하여 이미지에서 얼굴을 감지합니다.
    
    Args:
        image_path: 입력 이미지 경로
        output_path: 출력 이미지 경로 (None이면 자동 생성)
    """
    # 현재 스크립트의 디렉토리 기준으로 경로 설정
    current_dir = Path(__file__).resolve().parent
    image_path_obj = Path(image_path)
    
    # 상대 경로인 경우 절대 경로로 변환
    if not image_path_obj.is_absolute():
        image_path_obj = current_dir.parent / "data" / "yolo" / image_path
    
    image_path = str(image_path_obj)
    
    # 파일 존재 확인
    if not Path(image_path).exists():
        print(f"이미지 파일을 찾을 수 없습니다: {image_path}")
        return None
    
    # YOLO11 모델 로드
    # 참고: YOLO11 기본 모델은 얼굴 클래스가 없으므로 person 클래스를 감지합니다
    # 더 정확한 얼굴 감지를 원하면 얼굴 전용 모델을 사용하세요
    model = YOLO('yolo11n.pt')
    
    print(f"이미지 처리 중: {image_path}")
    
    # 이미지 로드
    image = cv2.imread(image_path)
    if image is None:
        print(f"이미지를 로드할 수 없습니다: {image_path}")
        return None
    
    # YOLO로 객체 감지
    results = model(image_path)
    
    # 결과에서 person 클래스만 필터링 (얼굴은 보통 person의 일부)
    # COCO 데이터셋에서 person 클래스 ID는 0
    person_class_id = 0
    
    # 이미지 복사본 생성 (원본 보존)
    annotated_image = image.copy()
    face_count = 0
    
    # 감지된 객체 중 person 클래스만 처리
    for result in results:
        boxes = result.boxes
        
        for box in boxes:
            # 클래스 ID 확인
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            
            # person 클래스이고 신뢰도가 0.5 이상인 경우
            if class_id == person_class_id and confidence > 0.5:
                # 바운딩 박스 좌표 추출
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                
                # person 영역에서 얼굴 영역 추정 (상단 1/3 부분)
                face_height = int((y2 - y1) * 0.4)  # 상단 40%를 얼굴로 간주
                face_y1 = y1
                face_y2 = y1 + face_height
                face_x1 = x1
                face_x2 = x2
                
                # 얼굴 영역 그리기
                cv2.rectangle(annotated_image, (face_x1, face_y1), (face_x2, face_y2), (0, 255, 0), 2)
                
                # 신뢰도 표시
                label = f"Face {confidence:.2f}"
                cv2.putText(annotated_image, label, (face_x1, face_y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                face_count += 1
                print(f"얼굴 감지됨: ({face_x1}, {face_y1}) - ({face_x2}, {face_y2}), 신뢰도: {confidence:.2f}")
    
    print(f"총 {face_count}개의 얼굴이 감지되었습니다.")
    
    # 출력 경로 설정 (-detected 접미사 사용)
    if output_path is None:
        image_path_obj = Path(image_path)
        output_path = str(image_path_obj.parent / f"{image_path_obj.stem}-detected{image_path_obj.suffix}")
    
    # 결과 이미지 저장
    cv2.imwrite(output_path, annotated_image)
    print(f"결과가 저장되었습니다: {output_path}")
    
    # 결과 이미지 표시 (선택사항)
    # cv2.imshow('Face Detection', annotated_image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    
    return annotated_image, face_count


def detect_faces_opencv_haar(image_path: str, output_path: str = None):
    """
    OpenCV Haar Cascade를 사용한 얼굴 감지 (더 정확한 방법)
    """
    # 현재 스크립트의 디렉토리 기준으로 경로 설정
    current_dir = Path(__file__).resolve().parent
    image_path_obj = Path(image_path)
    
    if not image_path_obj.is_absolute():
        image_path_obj = current_dir.parent / "data" / "yolo" / image_path
    
    image_path = str(image_path_obj)
    
    if not Path(image_path).exists():
        print(f"이미지 파일을 찾을 수 없습니다: {image_path}")
        return None
    
    # 이미지 로드
    image = cv2.imread(image_path)
    if image is None:
        print(f"이미지를 로드할 수 없습니다: {image_path}")
        return None
    
    # 그레이스케일로 변환 (얼굴 감지에 필요)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Haar Cascade 얼굴 감지기 로드
    # OpenCV에 포함된 기본 얼굴 감지 모델 사용
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # 얼굴 감지
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )
    
    # 이미지 복사본 생성
    annotated_image = image.copy()
    face_count = len(faces)
    
    print(f"총 {face_count}개의 얼굴이 감지되었습니다.")
    
    # 감지된 얼굴에 박스 그리기
    for (x, y, w, h) in faces:
        cv2.rectangle(annotated_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        label = "Face"
        cv2.putText(annotated_image, label, (x, y - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        print(f"얼굴 감지됨: ({x}, {y}) - ({x + w}, {y + h})")
    
    # 출력 경로 설정 (-detected 접미사 사용)
    if output_path is None:
        image_path_obj = Path(image_path)
        output_path = str(image_path_obj.parent / f"{image_path_obj.stem}-detected{image_path_obj.suffix}")
    
    # 결과 이미지 저장
    cv2.imwrite(output_path, annotated_image)
    print(f"결과가 저장되었습니다: {output_path}")
    
    return annotated_image, face_count


class ImageFileHandler(FileSystemEventHandler):
    """파일 시스템 이벤트 핸들러 - 새 이미지 파일 감지"""
    
    def __init__(self, watch_dir: Path):
        self.watch_dir = watch_dir
        self.processed_files = set()  # 이미 처리한 파일 추적
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
        print(f"파일 감시 시작: {watch_dir}")
    
    def on_created(self, event):
        """새 파일이 생성되었을 때"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # 이미지 파일인지 확인
        if file_path.suffix.lower() not in self.image_extensions:
            return
        
        # 이미 처리한 파일이거나 결과 파일인지 확인
        if file_path.name in self.processed_files or '-detected' in file_path.name:
            return
        
        # 파일이 완전히 쓰여질 때까지 잠시 대기
        time.sleep(0.5)
        
        # 파일이 존재하고 크기가 0이 아닌지 확인
        if not file_path.exists() or file_path.stat().st_size == 0:
            return
        
        print(f"\n{'='*60}")
        print(f"새 이미지 파일 감지: {file_path.name}")
        print(f"{'='*60}")
        
        # 얼굴 감지 실행
        try:
            result = detect_faces_opencv_haar(str(file_path))
            if result:
                self.processed_files.add(file_path.name)
                print(f"처리 완료: {file_path.name}")
        except Exception as e:
            print(f"처리 중 오류 발생 ({file_path.name}): {e}")


def watch_folder():
    """폴더 감시 시작"""
    # 현재 스크립트의 디렉토리 기준으로 data/yolo 폴더 경로 설정
    current_dir = Path(__file__).resolve().parent
    watch_dir = current_dir.parent / "data" / "yolo"
    
    # 디렉토리가 없으면 생성
    if not watch_dir.exists():
        print(f"디렉토리를 생성합니다: {watch_dir}")
        watch_dir.mkdir(parents=True, exist_ok=True)
    
    # 이벤트 핸들러 생성
    event_handler = ImageFileHandler(watch_dir)
    
    # Observer 생성 및 시작
    observer = Observer()
    observer.schedule(event_handler, str(watch_dir), recursive=False)
    observer.start()
    
    print(f"\n{'='*60}")
    print(f"파일 감시 모드 활성화")
    print(f"감시 폴더: {watch_dir}")
    print(f"새 이미지 파일이 추가되면 자동으로 얼굴 감지를 실행합니다.")
    print(f"종료하려면 Ctrl+C를 누르세요.")
    print(f"{'='*60}\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n파일 감시를 종료합니다...")
        observer.stop()
    
    observer.join()


if __name__ == "__main__":
    import sys
    
    # 명령줄 인자 확인
    if len(sys.argv) > 1 and sys.argv[1] == '--watch':
        # 파일 감시 모드
        watch_folder()
    else:
        # 단일 파일 처리 모드
        image_path = "family.jpg" if len(sys.argv) < 2 else sys.argv[1]
        
        print("=" * 50)
        print("얼굴 감지 방법 선택:")
        print("1. YOLO 기반 (person 클래스 감지 후 얼굴 영역 추정)")
        print("2. OpenCV Haar Cascade (더 정확한 얼굴 감지)")
        print("=" * 50)
        
        # OpenCV Haar Cascade 방법 사용 (더 정확함)
        print("\n[OpenCV Haar Cascade 방법 사용]")
        result = detect_faces_opencv_haar(image_path)
        
        if result:
            print("\n얼굴 감지 완료!")
        
        print("\n파일 감시 모드를 사용하려면: python yolo_detection.py --watch")

