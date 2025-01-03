import sys
import time
import asyncio
from pymcprotocol import Type3E                  # Python - PLC 통신 프로토콜 라이브러리리
from indy_utils import indydcp_client as client  # Indy 로봇 제어 라이브러리

# PLC IP
PLC1_IP = "192.168.3.150"  # 1번 PLC
PLC2_IP = "192.168.3.130"  # 2번 PLC
PLC3_IP = "192.168.3.120"  # 3번 PLC
PLC_PORT = 5000            # 모든 PLC 공통 포트

# ROBOT IP
ROBOT_A_IP = "192.168.3.7"  # Robot_A
ROBOT_B_IP = "192.168.3.6"  # Robot_B
ROBOT_C_IP = "192.168.3.5"  # Robot_C

# 경로 추가
sys.path.append("C:\\Auto_Pose_test\\Robot_A")
sys.path.append("C:\\Auto_Pose_test\\Robot_B")
sys.path.append("C:\\Auto_Pose_test\\Robot_C")

sys.path.append("C:\\Auto_Pose_test\\Webcam")

from Robot_A import RobotA
from Robot_B import RobotB
from Robot_C import RobotC

# 플래그 상태
flag_A = False
flag_B = False
flag_C = False


async def run_robot_a():
    """1번 PLC & Robot_A"""
    global flag_A
    mc1 = Type3E()
    mc1.setaccessopt(commtype="binary")
    mc1.connect(PLC1_IP, PLC_PORT)
    print("1번 PLC 연결 완료")

    robot_a = RobotA(ROBOT_A_IP, "NRMK-Indy7")
    robot_a.connect()
    print("로봇 A 연결 완료")

    try:
        while True:
            tmpA_sensor_data = mc1.batchread_bitunits(headdevice="X100", readsize=1)  # sensor_data 이름 변경 및 headdevice의 주소값 변경 필요
            if tmpA_sensor_data[0] and not flag_A:
                print("주문작업 시작")

                # 로봇 작업 실행
                robot_a.tmpA_task()  # tmpA_task()는 임의로 지정. 변경필요.

                # 작업 완료 플래그 설정
                flag_A = True

                # PLC 작업 완료 상태 업데이트
                mc1.batchwrite_bitunits(headdevice="M100", values=[True])
                print("적재완료")

            elif flag_A:
                # 작업 완료 후 플래그 초기화
                await asyncio.sleep(1)
                flag_A = False
                print("작업대기중")

            await asyncio.sleep(0.5)  # 센싱 주기

    except Exception as e:
        print(f"Robot A 작업 중 에러 발생: {e}")

    finally:
        robot_a.disconnect()
        mc1.close()
        print("Robot_A 연결 해제")


async def run_robot_b():
    """2번 PLC & Robot_B"""
    global flag_B
    mc2 = Type3E()
    mc2.setaccessopt(commtype="binary")
    mc2.connect(PLC2_IP, PLC_PORT)
    print("2번 PLC 연결 완료")

    robot_b = RobotB(ROBOT_B_IP, "NRMK-Indy7")
    robot_b.connect()
    print("로봇 B 연결 완료")

    try:
        while True:
            tmpB_sensor_data = mc2.batchread_bitunits(headdevice="X100", readsize=1) # sensor_data 이름 변경 및 headdevice의 주소값 변경 필요
            if tmpB_sensor_data[0] and not flag_B:
                print("Robot_B 작업 시작")

                # 로봇 작업 실행
                robot_b.tmpB_task() # tmpB_task()는 임의로 지정. 변경필요.

                # 작업 완료 플래그 설정
                flag_B = True

                # 작업 완료 상태 업데이트
                mc2.batchwrite_bitunits(headdevice="M100", values=[True]) # M100은 임의의 주소값이므로 수정 필요
                print("Robot B 작업 완료")

            elif flag_B:
                # 작업 완료 후 플래그 초기화
                await asyncio.sleep(1)
                flag_B = False
                print("작업대기중")

            await asyncio.sleep(0.5)  # 센싱 주기

    except Exception as e:
        print(f"Robot B 작업 중 에러 발생: {e}")

    finally:
        robot_b.disconnect()
        mc2.close()
        print("Robot_B 연결 해제")


async def run_robot_c():
    """3번 PLC와 Robot_C 연동"""
    global flag_C
    mc3 = Type3E()
    mc3.setaccessopt(commtype="binary")
    mc3.connect(PLC3_IP, PLC_PORT)
    print("3번 PLC 연결 완료.")

    robot_c = RobotC(ROBOT_C_IP, "NRMK-Indy7")
    robot_c.connect()
    print("로봇 C 연결 완료.")

    try:
        while True:
            sensor_data = mc3.batchread_bitunits(headdevice="X100", readsize=1)
            if sensor_data[0] and not flag_C:
                print("Robot C 작업 시작")

                # 로봇 작업 실행
                robot_c.pick_lid()
                robot_c.place_lid()
                robot_c.go_home()

                # 작업 완료 플래그 설정
                flag_C = True

                # 작업 완료 상태 업데이트
                mc3.batchwrite_bitunits(headdevice="M100", values=[True]) # M100은 임의의 주소값이므로 수정 필요
                print("Robot C 작업완료")

            elif flag_C:
                # 작업 완료 후 플래그 초기화
                await asyncio.sleep(1)
                flag_C = False
                print("작업대기중")

            await asyncio.sleep(0.5)  # 센싱 주기

    except Exception as e:
        print(f"Robot C 작업 중 에러 발생: {e}")

    finally:
        robot_c.disconnect()
        mc3.close()
        print("Robot C 연결해제")
        
async def run_webcam():
    """Webcam 비동기 작업"""
    roi_capture = ROICapture(roi_size=400)
    roi_capture.initialize_camera()

    try:
        await roi_capture.select_roi()  # ROI 선택
        await roi_capture.track_and_save()  # 물체 추적 및 저장
    finally:
        roi_capture.release_resources()


async def main():
    """비동기적으로 모든 로봇과 Webcam 실행"""
    await asyncio.gather(
        run_robot_a(),
        run_robot_b(),
        run_robot_c(),
        run_webcam(),  # Webcam 추가
    )

if __name__ == "__main__":
    asyncio.run(main())
