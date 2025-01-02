import time
from indy_utils import indydcp_client as client  # Indy 로봇 제어 라이브러리

# 각 로봇의 IP와 이름
robot_c_ip = "192.168.3.5"
robot_c_name = "NRMK-Indy7"


class RobotC:
    def __init__(self, robot_ip, robot_name):
        """
        Robot 클래스 초기화.

        Args:
            robot_ip (str): 로봇 IP 주소.
            robot_name (str): 로봇 이름.
        """
        self.robot = client.IndyDCPClient(robot_ip, robot_name)  # Indy 로봇 객체

        # 기본 Pick & Place 작업을 위한 위치 정의 (Robot C 기준)
        self.joint_pick_apprch_pos = [-52.22, -18.11, -71.79, -0.09, -90.19, -142.66]
        self.task_pick_apprch_pos = [0.15, -0.50, 0.50, -0.03, -179.85, 0.17]
        self.joint_pick_target_pos = [-52.93, -30.36, -100.81, -0.06, -50.12, -143.34]
        self.task_pick_target_pos = [0.14, -0.50, 0.23, -0.81, 178.98, 90.45]
        self.joint_place_apprch_pos = [6.10, -28.63, -64.11, 1.59, -89.31, 6.07]
        self.task_place_apprch_pos = [0.57, -0.11, 0.44, -1.36, -177.77, 0.00]
        self.joint_place_target_pos = [6.09, -33.30, -80.61, 1.71, -68.05, 5.43]
        self.task_place_target_pos = [0.57, -0.11, 0.30, -1.37, -177.87, 0.01]

    def connect(self):
        """로봇 연결."""
        self.robot.connect()
        print("로봇 연결 완료.")

    def disconnect(self):
        """로봇 연결 해제."""
        if self.robot.is_connected():
            self.robot.disconnect()
            print("로봇 연결 해제.")

    def move_done_check(self, timeout=10):
        """
        로봇 움직임 완료 상태 확인.

        Args:
            timeout (int): 최대 대기 시간 (초).

        Raises:
            TimeoutError: 이동 완료 신호를 받지 못한 경우.
        """
        start_time = time.time()
        while not self.robot.get_robot_status().get('movedone', False):
            if time.time() - start_time > timeout:
                raise TimeoutError("로봇 이동 완료 신호를 받지 못했습니다.")
            time.sleep(0.5)

    def move_to(self, joint_pos=None, task_pos=None):
        """
        지정된 위치로 이동.

        Args:
            joint_pos (list): 관절 위치.
            task_pos (list): 작업 위치.
        """
        if joint_pos:
            self.robot.joint_move_to(joint_pos)
        elif task_pos:
            self.robot.task_move_to(task_pos)
        self.move_done_check()

    def gripper(self, hold):
        """
        그리퍼 동작.

        Args:
            hold (bool): True - 그리퍼 닫기, False - 그리퍼 열기.
        """
        self.robot.set_do(2, hold)

    def pick_lid(self):
        """뚜껑을 집는 작업."""
        self.move_to(joint_pos=self.joint_pick_apprch_pos)
        self.move_to(task_pos=self.task_pick_target_pos)
        self.gripper(True)
        self.move_to(task_pos=self.task_pick_apprch_pos)

    def place_lid(self):
        """뚜껑을 놓는 작업."""
        self.move_to(joint_pos=self.joint_place_apprch_pos)
        self.move_to(task_pos=self.task_place_target_pos)
        self.gripper(False)

    def go_home(self):
        """홈 위치로 이동."""
        self.robot.go_home()
        self.move_done_check()

    def set_task_velocity(self, level):
        """Task move 속도 설정."""
        self.robot.set_task_vel_level(level)

    def set_joint_velocity(self, level):
        """Joint move 속도 설정."""
        self.robot.set_joint_vel_level(level)


if __name__ == "__main__":
    try:
        # Robot_C 객체 생성
        robot_c = RobotC(robot_c_ip, robot_c_name)

        # 로봇 연결
        robot_c.connect()

        # 작업 실행
        robot_c.pick_lid()
        robot_c.place_lid()

        # 홈 포지션 이동
        robot_c.go_home()

    except Exception as e:
        print(f"작업 중 에러 발생: {e}")
    finally:
        # 로봇 연결 해제
        if 'robot_c' in locals():
            robot_c.disconnect()
