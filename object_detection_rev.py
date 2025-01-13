import cv2
import numpy as np
from ultralytics import YOLO
import time
import logging
import threading

logging.getLogger("ultralytics").setLevel(logging.ERROR)  # YOLO 라이브러리 로그 레벨 제한
model = YOLO('best.pt')

# 전역 플래그
problem_flag = threading.Event()

# 3x3 그리드에 맞게 객체를 매핑
def map_to_grid(boxes, frame_width, frame_height):
    grid_size = 3  # 3x3 그리드
    grid = [['Empty' for _ in range(grid_size)] for _ in range(grid_size)]  # 초기화

    cell_width = frame_width // grid_size
    cell_height = frame_height // grid_size

    for box in boxes:
        x_min, y_min, x_max, y_max, label = box
        center_x = (x_min + x_max) / 2
        center_y = (y_min + y_max) / 2

        # 셀 좌표 계산
        grid_x = int(center_x // cell_width)
        grid_y = int(center_y // cell_height)

        if 0 <= grid_x < grid_size and 0 <= grid_y < grid_size:
            grid[grid_y][grid_x] = label  # 그리드에 라벨 할당

    detection_dict = {i: grid[row][col] for i, (row, col) in enumerate([(r, c) for r in range(grid_size) for c in range(grid_size)])}
    return detection_dict

cropping = False
triggering = False
selecting_trigger = True
started = False
x_start, y_start, x_end, y_end = 0, 0, 0, 0
tx_start, ty_start, tx_end, ty_end = 0, 0, 0, 0
previous_trigger_area = None
last_crop_time = 0

def mouse_crop(event, x, y, flags, param):
    global x_start, y_start, x_end, y_end, cropping
    global tx_start, ty_start, tx_end, ty_end, triggering
    global selecting_trigger

    if event == cv2.EVENT_LBUTTONDOWN:
        if selecting_trigger:
            tx_start, ty_start, tx_end, ty_end = x, y, x, y
            triggering = True
        else:
            x_start, y_start, x_end, y_end = x, y, x, y
            cropping = True

    elif event == cv2.EVENT_MOUSEMOVE:
        if triggering:
            tx_end, ty_end = x, y
        elif cropping:
            x_end, y_end = x, y

    elif event == cv2.EVENT_LBUTTONUP:
        if triggering:
            tx_end, ty_end = x, y
            triggering = False
            selecting_trigger = False
        elif cropping:
            x_end, y_end = x, y
            cropping = False

cap = cv2.VideoCapture(0)
cv2.namedWindow("Video")
cv2.setMouseCallback("Video", mouse_crop)

def check_for_problem(detection_dict, order_data, problem_detected):
    """
    문제를 확인하고 문제 플래그를 설정하며, 문제 리스트에 영역 및 예상 도형 정보를 추가.
    
    Args:
        detection_dict - 검출된 데이터 딕셔너리 (영역 번호: 모양양).
        order_data - 주문 데이터 딕셔너리
        problem_detected - 결함 발생 여부.
    
    Returns:
        list: 문제 항목 리스트.
    """
    global problem_flag
    problem_list = []

    for area, detected_shape in detection_dict.items():
        expected_shape = order_data.get(area, 'Empty')  # 예상 도형 가져오기
        if detected_shape != expected_shape or problem_detected:
            print(f"문제 발생: 영역 {area} - 검출: {detected_shape} (주문모양양: {expected_shape}, 결함: {problem_detected})")
            problem_flag.set()  # 문제 플래그 활성화

            # 문제 항목 리스트에 추가
            problem_list.append({
                "area": area,
                "detected_shape": detected_shape,
                "expected_shape": expected_shape,
                "defective": problem_detected
            })

    return problem_list

# 주요 코드 수정
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_copy = frame.copy()
    cv2.imshow("Video", frame_copy)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('s') and not started:
        started = True
        print("Detection started...")

    if started:
        trigger_area = frame[ty_start:ty_end, tx_start:tx_end]
        if trigger_area.size != 0:
            if previous_trigger_area is None:
                previous_trigger_area = trigger_area

            difference = cv2.absdiff(trigger_area, previous_trigger_area)
            non_zero_count = np.count_nonzero(difference)

            if non_zero_count > 0 and (time.time() - last_crop_time) > 2:
                results = model(trigger_area)
                if len(results) > 0 and len(results[0].boxes) > 0:
                    cropped_frame = frame[y_start:y_end, x_start:x_end]
                    if cropped_frame.size != 0:
                        results = model(cropped_frame)

                        boxes = []
                        problem_detected = False  # 초기화

                        for box in results[0].boxes:
                            if box.conf[0] > 0.7:  # 신뢰도 필터링
                                x_min, y_min, x_max, y_max = box.xyxy[0]
                                cls = int(box.cls[0])
                                label = model.names[cls]

                                # 문제 조건 : Defection 또는 Empty
                                if label == "Defection" or label == "Empty":
                                    problem_detected = True
                                
                                boxes.append((x_min, y_min, x_max, y_max, label))

                        frame_height, frame_width = cropped_frame.shape[:2]
                        detection_dict = map_to_grid(boxes, frame_width, frame_height)

                        # order_data = qr로 부터 받아온

                        # 문제 확인 및 문제 리스트 생성
                        problem_list = check_for_problem(detection_dict, order_data, problem_detected)

                        # 문제 리스트 출력 (디버깅용)
                        if problem_list:
                            print("Detected Problems:")
                            for problem in problem_list:
                                print(problem)

            previous_trigger_area = trigger_area

    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
