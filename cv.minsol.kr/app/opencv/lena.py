import cv2
import os


class LenaModel:

    def __init__(self):
        # 파일 경로를 절대 경로로 설정
        base_dir = os.path.dirname(os.path.abspath(__file__))
        opencv_data_dir = os.path.join(base_dir, "..", "data", "opencv")
        self.fname = os.path.join(opencv_data_dir, "lena.jpg")
        self._cascade = os.path.join(opencv_data_dir, "haarcascade_frontalface_alt.xml")

    @staticmethod
    def read_file():
        # 파일 경로를 절대 경로로 설정
        base_dir = os.path.dirname(os.path.abspath(__file__))
        opencv_data_dir = os.path.join(base_dir, "..", "data", "opencv")
        fname = os.path.join(opencv_data_dir, "lena.jpg")
        cascade_path = os.path.join(opencv_data_dir, "haarcascade_frontalface_alt.xml")
        
        # 이미지 파일 확인
        if not os.path.exists(fname):
            print(f"이미지 파일을 찾을 수 없습니다: {fname}")
            return
        
        # Cascade XML 파일 확인
        if not os.path.exists(cascade_path):
            print(f"Cascade 파일을 찾을 수 없습니다: {cascade_path}")
            return
        
        cascade = cv2.CascadeClassifier(cascade_path)
        img = cv2.imread(fname)
        
        if img is None:
            print("이미지를 불러올 수 없습니다.")
            return
        
        # 얼굴 인식 시도 (minSize를 작게 설정하여 더 잘 감지되도록)
        face = cascade.detectMultiScale(img, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        if len(face) == 0:
            print("얼굴을 찾을 수 없습니다.")
            return
        
        print(f"얼굴 {len(face)}개를 찾았습니다.")
        
        # 원본 이미지 복사 (얼굴 영역만 회색으로 변환하기 위해)
        result_img = img.copy()
        
        # 흑백 이미지 생성 (얼굴 영역만 사용하기 위해)
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 얼굴이 감지된 영역만 회색으로 변환
        for idx, (x, y, w, h) in enumerate(face):
            print("얼굴인식 인덱스: ", idx)
            print("얼굴인식 좌표: ", x, y, w, h)
            
            # 얼굴 영역만 회색으로 변환 (흑백 이미지의 해당 영역을 BGR로 변환)
            face_gray = gray_img[y:y+h, x:x+w]
            face_gray_bgr = cv2.cvtColor(face_gray, cv2.COLOR_GRAY2BGR)
            result_img[y:y+h, x:x+w] = face_gray_bgr
        
        # 결과 이미지 저장
        cv2.imwrite("lena-face-gray.png", result_img)
        print("얼굴 영역만 회색으로 변환된 이미지 저장: lena-face-gray.png")
        
        # 결과 표시
        cv2.imshow("Lena - Face Area Grayscale", result_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()   

    def execute(self):
        # 이미지 파일 확인
        if not os.path.exists(self.fname):
            print(f"이미지 파일을 찾을 수 없습니다: {self.fname}")
            return
        
        original = cv2.imread(self.fname, cv2.IMREAD_COLOR)
        gray = cv2.imread(self.fname, cv2.IMREAD_GRAYSCALE)
        unchanged = cv2.imread(self.fname, cv2.IMREAD_UNCHANGED)

        # 이미지 로드 확인
        if original is None or gray is None or unchanged is None:
            print(f"이미지를 불러올 수 없습니다: {self.fname}")
            return

        """
        이미지 읽기에는 위 3가지 속성이 존재함.
        대신에 1, 0, -1 을 사용해도 됨.
        """
        cv2.imshow('Original', original)
        cv2.imshow('Gray', gray)
        cv2.imshow('Unchanged', unchanged)
        cv2.waitKey(0)
        cv2.destroyAllWindows() # 윈도우종료

if __name__ == "__main__":
    LenaModel.read_file()  # 얼굴 인식 및 얼굴 영역만 회색 변환 (@staticmethod 사용)