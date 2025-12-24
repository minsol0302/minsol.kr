"""
YOLO11 기본 예제 - 기본 이미지 객체 감지
"""
from ultralytics import YOLO

if __name__ == "__main__":
    # YOLO11 모델 로드
    model = YOLO('yolo11n.pt')
    
    # YOLO 기본 예제 이미지 사용 (URL 또는 기본 이미지)
    # ultralytics는 기본적으로 예제 이미지를 제공합니다
    results = model('https://ultralytics.com/images/bus.jpg')
    
    # 결과 표시
    results[0].show()  # 기본 이미지 표시
    
    # 또는 저장
    # results[0].save('yolo_result.jpg')

