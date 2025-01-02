import time
from indy_utils import indydcp_client as client  # Indy 로봇 제어 라이브러리

# 로봇의 IP와 이름
robot_a_ip = "192.168.3.7"
robot_a_name = "NRMK-Indy7"


class RobotA:
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
        # Robot_A 객체 생성
        robot_a = RobotA(robot_a_ip, robot_a_name)

        # 로봇 연결
        robot_a.connect()

        # 홈 포지션 이동
        robot_a.go_home()

    except Exception as e:
        print(f"작업 중 에러 발생: {e}")
    finally:
        # 로봇 연결 해제
        if 'robot_a' in locals():
            robot_a.disconnect()
