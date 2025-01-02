# 경로 추가하는 기능 'sys.path.append("경로")' 을 이용하기 위한 라이브러리리
import sys 
from indy_utils import indydcp_client as client

# 모듈듈 가져오기

from Robot_A import RobotA
from Robot_B import RobotB
from Robot_C import RobotC

from roi_capture import ROICapture

# 경로 지정

sys.path.appenc("C:\Auto_Pose_test\Robot_A")
sys.path.appenc("C:\Auto_Pose_test\Robot_B")
sys.path.append("C:\Auto_Pose_test\Robot_C")

sys.path.append("C:\Auto_Pose_test\Webcam")





def main():
    try:
        # 로봇 제어 설정
        indy = client.Indy()  # Indy 로봇 객체 생성

        Robot_A = RobotA(indy)
        Robot_B = RobotB(indy)
        Robot_C = RobotC(indy)

        """로봇 B"""
        # 로봇B 연결
        Robot_B.connect()

        # 로봇 속도 설정
        Robot_B.set_task_velocity(1)
        Robot_B.set_joint_velocity(1)

        # 동작부분 추가해야함
        # Robot_B.
        # Robot_B.

        # 홈 포지션 이동
        Robot_B.go_home()

        """로봇 C"""
        # 로봇C 연결
        Robot_C.connect()

        # 로봇 속도 설정
        Robot_C.set_task_velocity(1)
        Robot_C.set_joint_velocity(1)

        # 뚜껑 pick & place
        print("start pick & place of lid")
        Robot_C.pick_lid()
        Robot_C.place_lid()

        # 홈 포지션 이동
        Robot_C.go_home()


        """웹캠 파트"""
        ## B 구간 웹캠 ##


        ## C 구간 웹캠 ##
        # ROI 캡처 설정
        roi_capture = ROICapture(save_dir="C:\Auto_Pose_test\captured", roi_size=300)
        
        # 웹캠 초기화
        roi_capture.initialize_camera()

        # ROI 영역 선택
        roi_capture.select_roi()

        # ROI 영역에서 95% 이상 변화 시에 저장
        roi_capture.track_and_save()

        # ROI 완료 후 리소스 해제
        roi_capture.release_resources()

    except Exception as e:
        print(f"작업 중 에러 발생: {e}")

    finally:
        # 로봇 연결 해제
        if 'Robot_A' in locals():
            Robot_A.disconnect()

        if 'Robot_B' in locals():
            Robot_B.disconnect()

        if 'Robot_C' in locals():
            Robot_C.disconnect()


if __name__ == "__main__":
    main()
