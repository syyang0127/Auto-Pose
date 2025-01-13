import cv2
import numpy as np
from ultralytics import YOLO
import time
import logging

logging.getLogger("ultralytics").setLevel(logging.ERROR)  # YOLO 라이브러리 로그 레벨 제한
model = YOLO('best.pt')

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

    # 1차원 딕셔너리 반환
    mapped_detection_dict = {i: grid[row][col] for i, (row, col) in enumerate([(r, c) for r in range(grid_size) for c in range(grid_size)])}
    return mapped_detection_dict

# 모양 카운팅 함수
def count_shapes(mapped_detection_dict):
    shape_counts = {'Circle': 0, 'Triangle': 0, 'Rectangle': 0, 'defection': 0, 'Empty': 0}
    for label in mapped_detection_dict.values():
        shape_counts[label] += 1
    return shape_counts

# 감지 결과 분석 함수
def analyze_detections(shape_counts, qr_order_data, mapped_detection_dict):
    eliminate_list = []
    excess_shapes = {shape: max(0, shape_counts[shape] - qr_order_data.get(shape, 0)) for shape in shape_counts if shape != 'Empty'}

    # defection 제거 및 초과 모양 제거
    for area, label in mapped_detection_dict.items():
        if label == 'defection' or (label in excess_shapes and excess_shapes[label] > 0):
            eliminate_list.append(area)
            if label != 'defection':
                excess_shapes[label] -= 1

    return eliminate_list

# QR 데이터 예제
qr_order_data = {'Circle': 3, 'Triangle': 2, 'Rectangle': 2}

# 전역 변수
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

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_copy = frame.copy()

    # 트리거 박스 표시
    if triggering or not selecting_trigger:
        cv2.rectangle(frame_copy, (tx_start, ty_start), (tx_end, ty_end), (255, 0, 0), 2)
    # 크롭 대상 박스 표시
    if cropping or not selecting_trigger:
        cv2.rectangle(frame_copy, (x_start, y_start), (x_end, y_end), (0, 255, 0), 2)

    cv2.imshow("Video", frame_copy)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('s') and not (cropping or triggering) and not started:
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

                        # 결과 출력 및 이미지 표시
                        for result in results:
                            detection_img = np.squeeze(result.plot())  # 디텍션 결과 이미지

                            # 크롭된 영역에 디텍션 결과 표시
                            cv2.imshow('Detection', detection_img)
                            cv2.waitKey(1)

                        # 결과 저장
                        boxes = [(int(box.xyxy[0][0]), int(box.xyxy[0][1]), int(box.xyxy[0][2]), int(box.xyxy[0][3]), model.names[int(box.cls[0])]) for box in results[0].boxes if box.conf[0] > 0.7]

                        frame_height, frame_width = cropped_frame.shape[:2]
                        mapped_detection_dict = map_to_grid(boxes, frame_width, frame_height)
                        shape_counts = count_shapes(mapped_detection_dict)

                        print("Mapped Detection Dictionary:", mapped_detection_dict)
                        print("Shape Counts:", shape_counts)

                        eliminate_list = analyze_detections(shape_counts, qr_order_data, mapped_detection_dict)
                        print("Eliminate List:", eliminate_list)

                        last_crop_time = time.time()

            previous_trigger_area = trigger_area

    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
