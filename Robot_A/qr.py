import cv2
from pyzbar.pyzbar import decode

def detect_qr_from_cam():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Cannot access the camera.")
        return None

    print("Scanning for QR code...")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Cannot read frame from the camera.")
            break

        # 화면 중심에서 240x240 크기로 자르기
        height, width, _ = frame.shape
        center_x, center_y = width // 2, height // 2
        cropped_frame = frame[center_y - 120:center_y + 120, center_x - 120:center_x + 120]

        # QR 코드 디코딩
        qr_codes = decode(cropped_frame)

        if qr_codes:
            for qr in qr_codes:
                qr_data = qr.data.decode('utf-8')
                print(f"Detected QR Code: {qr_data}")
                cap.release()
                cv2.destroyAllWindows()
                return qr_data  # QR 코드 데이터 반환

        # 결과 프레임 디스플레이
        cv2.imshow('QR Code Scanner', cropped_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return None