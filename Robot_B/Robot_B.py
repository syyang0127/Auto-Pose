import time
from indy_utils import indydcp_client as client  # Indy 로봇 제어 라이브러리

# 각 로봇의 IP와 이름
robot_b_ip = "192.168.3.6"
robot_b_name = "NRMK-Indy7"


class RobotB:
    def __init__(self, robot_ip, robot_name):
        """
        Robot 클래스 초기화.

        Args:
            robot_ip (str): 로봇 IP 주소.
            robot_name (str): 로봇 이름.
        """
        self.robot = client.IndyDCPClient(robot_ip, robot_name)  # Indy 로봇 객체

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

    def adsorber(self, hold):
        """
        흡착툴
        hold (bool): True - 흡착툴 on, False - 흡착툴 off.
        """
        self.robot.set_do(2, hold) # 흡착툴 번호 확인해서 바꿔야함함

    def pick_lid(self):
        """뚜껑을 집는 작업."""
        self.move_to(joint_pos=self.joint_pick_apprch_pos)
        self.move_to(task_pos=self.task_pick_target_pos)
        self.adsorber(True)
        self.move_to(task_pos=self.task_pick_apprch_pos)

    def place_lid(self):
        """뚜껑을 놓는 작업."""
        self.move_to(joint_pos=self.joint_place_apprch_pos)
        self.move_to(task_pos=self.task_place_target_pos)
        self.adsorber(False)

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
        # Robot_B 객체 생성
        robot_b = RobotB(robot_b_ip, robot_b_name)

        # 로봇 연결
        robot_b.connect()

        # 작업 실행
        robot_b.pick_lid()
        robot_b.place_lid()

        # 홈 포지션 이동
        robot_b.go_home()

    except Exception as e:
        print(f"작업 중 에러 발생: {e}")
    finally:
        # 로봇 연결 해제
        if 'robot_b' in locals():
            robot_b.disconnect()
