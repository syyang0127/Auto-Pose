import cv2
import datetime
import os
import time  # 시간 추적을 위한 모듈

class ROICapture:
    def __init__(self, save_dir="E:\\captured", roi_size=400):
        self.save_dir = save_dir
        self.roi_size = roi_size
        self.roi_position = [100, 100]
        self.dragging = False
        self.start_drag = (0, 0)
        self.roi_selected = False
        self.image_saved = False  # 이미지 저장 여부 플래그
        self.last_capture_time = 0  # 마지막 캡처 시간을 저장
        self.cap = None
        os.makedirs(self.save_dir, exist_ok=True)

    def initialize_camera(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("웹캠을 열 수 없습니다.")
            exit()

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:  # 마우스 왼쪽 버튼 눌림
            x1, y1 = self.roi_position
            x2, y2 = x1 + self.roi_size, y1 + self.roi_size
            if x1 <= x <= x2 and y1 <= y <= y2:
                self.dragging = True
                self.start_drag = (x, y)

        elif event == cv2.EVENT_MOUSEMOVE and self.dragging:  # 드래그 중
            dx = x - self.start_drag[0]
            dy = y - self.start_drag[1]

            self.roi_position[0] = min(max(0, self.roi_position[0] + dx), self.frame.shape[1] - self.roi_size)
            self.roi_position[1] = min(max(0, self.roi_position[1] + dy), self.frame.shape[0] - self.roi_size)
            self.start_drag = (x, y)

        elif event == cv2.EVENT_LBUTTONUP:  # 마우스 왼쪽 버튼 떼기
            self.dragging = False

    def select_roi(self):
        cv2.namedWindow("Webcam")
        cv2.setMouseCallback("Webcam", self.mouse_callback)

        while True:
            ret, self.frame = self.cap.read()
            if not ret:
                print("프레임을 읽을 수 없습니다.")
                break

            x1, y1 = self.roi_position
            x2, y2 = x1 + self.roi_size, y1 + self.roi_size
            cv2.rectangle(self.frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            cv2.imshow("Webcam", self.frame)

            key = cv2.waitKey(1) & 0xFF

            if key == 27:  # ESC
                break
            elif key == ord('r'):  # 'r' 키
                self.roi_selected = True
                print("ROI 영역이 설정됐습니다.")
                break

    def track_and_save(self):
        if not self.roi_selected:
            print("ROI가 설정되지 않았습니다.")
            return

        print("컨베이어 물체 추적을 시작합니다.")

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        _, initial_frame = self.cap.read()
        initial_gray = cv2.cvtColor(initial_frame, cv2.COLOR_BGR2GRAY)
        initial_gray = cv2.GaussianBlur(initial_gray, (21, 21), 0)

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            current_time = time.time()

            # 캡처 후 1초 동안 감지 중지
            if self.image_saved and current_time - self.last_capture_time < 1:
                cv2.imshow("Webcam", frame)
                if cv2.waitKey(1) & 0xFF == 27:  # ESC 키로 종료
                    break
                continue

            x1, y1 = self.roi_position
            x2, y2 = x1 + self.roi_size, y1 + self.roi_size
            roi_frame = frame[y1:y2, x1:x2]
            roi_gray = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)
            roi_gray = cv2.GaussianBlur(roi_gray, (21, 21), 0)

            frame_delta = cv2.absdiff(initial_gray[y1:y2, x1:x2], roi_gray)
            thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            roi_area = self.roi_size * self.roi_size
            detected_area = 0

            for contour in contours:
                detected_area += cv2.contourArea(contour)

            # ROI 영역 내 검출된 영역이 95% 이상이고 이미지가 저장되지 않았을 때 저장
            if detected_area / roi_area >= 0.95 and not self.image_saved:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(self.save_dir, f"finished_{timestamp}.jpg")
                cv2.imwrite(filename, roi_frame)
                print(f"저장됨: {filename}")
                self.image_saved = True
                self.last_capture_time = current_time  # 마지막 캡처 시간 기록

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.imshow("Webcam", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                break

            # 이미지 저장 플래그 리셋 (1초 대기 후 다시 감지 가능)
            if current_time - self.last_capture_time >= 3:
                self.image_saved = False

    def release_resources(self):
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    roi_capture = ROICapture(roi_size=400)  # ROI 크기 설정
    roi_capture.initialize_camera()
    roi_capture.select_roi()
    roi_capture.track_and_save()
    roi_capture.release_resources()
