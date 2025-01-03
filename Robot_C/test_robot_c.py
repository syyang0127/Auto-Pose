import time
from pymcprotocol import Type3E
from indy_utils import indydcp_client as client  # Indy 로봇 제어 라이브러리

# PLC 설정
PLC_IP = "192.168.0.100"
PLC_PORT = 5000

# 각 로봇의 IP와 이름
robot_c_ip = "192.168.3.5"
robot_c_name = "NRMK-Indy7"

class RobotC:
    def __init__(self, robot_ip, robot_name):
        self.robot = client.IndyDCPClient(robot_ip, robot_name)

        # Pick & Place 작업 위치 정의
        self.joint_pick_apprch_pos = [-52.22, -18.11, -71.79, -0.09, -90.19, -142.66]
        self.task_pick_target_pos = [0.14, -0.50, 0.23, -0.81, 178.98, 90.45]
        
        self.joint_place_apprch_pos = [6.10, -28.63, -64.11, 1.59, -89.31, 6.07]
        self.task_place_target_pos = [0.57, -0.11, 0.30, -1.37, -177.87, 0.01]

    def connect(self):
        self.robot.connect()
        print("로봇C 연결")

    def disconnect(self):
        if self.robot.is_connected():
            self.robot.disconnect()
            print("로봇C 해제")

    def move_done_check(self, timeout=10):
        start_time = time.time()
        while not self.robot.get_robot_status().get('movedone', False):
            if time.time() - start_time > timeout:
                raise TimeoutError("동작확인 실패")
            time.sleep(0.5)

    def move_to(self, joint_pos=None, task_pos=None):
        if joint_pos:
            self.robot.joint_move_to(joint_pos)
        elif task_pos:
            self.robot.task_move_to(task_pos)
        self.move_done_check()

    def gripper(self, hold):
        self.robot.set_do(2, hold)

    def pick_lid(self): # 뚜껑을 흡착툴툴로 짚기
        self.move_to(joint_pos=self.joint_pick_apprch_pos)
        self.move_done_check()
        self.move_to(task_pos=self.task_pick_target_pos)
        self.move_done_check()
        self.gripper(True)
        time.sleep(1)
        self.move_to(joint_pos=self.joint_pick_apprch_pos)
        self.move_done_check()

    def place_lid(self):
        self.move_to(joint_pos=self.joint_place_apprch_pos)
        self.move_done_check()
        self.move_to(task_pos=self.task_place_target_pos)
        self.move_done_check()
        self.gripper(False)
        time.sleep(1)
        self.move_to(joint_pos=self.joint_place_apprch_pos)
        self.move_done_check()

    def go_home(self):
        self.robot.go_home()
        self.move_done_check()


def run_robot_c():
    # PLC 연결
    mc = Type3E()
    mc.setaccessopt(commtype="binary")
    mc.connect(PLC_IP, PLC_PORT)
    print("PLC 연결 완료.")

    # Robot_C 객체 생성
    robot_c = RobotC(robot_c_ip, robot_c_name)
    robot_c.connect()

    try:
        while True:

            flag = None
            # X100 비트 읽기
            bit_data = mc.batchread_bitunits(headdevice="X100", readsize=1)
            if bit_data[0]:  # X100이 True인 경우
                # 로봇 작업 실행
                print("on goint to pick lid")
                robot_c.pick_lid()
                print("on goint to place lid")
                robot_c.place_lid()
                print("lid is closed")                
                robot_c.go_home()
                print("waiting for next task")

                flag = True
                if flag==True:
                    mc.batchwrite_wordunits(headdevice="M100", values=['lid is closed']) # ex) m100 에 lid is closed 쓰기기

                    return flag == False
                
            time.sleep(0.5)  # 0.5초 주기
    except KeyboardInterrupt:
        print("작업 중단")

    finally:
        # 연결 해제
        robot_c.disconnect()
        mc.close()
        print("PLC 연결 해제")


if __name__ == "__main__":
    run_robot_c()
