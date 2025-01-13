import sys
import time
from indy_utils import indydcp_client as client  # Indy 로봇 제어 라이브러리
import fixed_cordinates as pos
import object_detection_rev as oj_detect

# 각 로봇의 IP와 이름
robot_b_ip = "192.168.3.6"
robot_b_name = "NRMK-Indy7"

class RobotB:
    def __init__(self, ip, name):
        self.ip = ip
        self.name = name
        self.robotB = client.IndyDCPClient(ip, name)

    def connect(self):
        """로봇 연결"""
        self.robotB.connect()
        if self.robotB.connect():
            print(f"Robot B ({self.name}) 연결 완료")

    def disconnect(self):
        """로봇 연결 해제"""
        if self.robotB.connect():
            self.robotB.disconnect()
            print(f"Robot B ({self.name}) 연결 해제")

    def adsorber(self, hold):
        """
        흡착 툴 활성화/비활성화
        hold (bool): True - 흡착 툴 ON, False - 흡착 툴 OFF
        """
        self.robotB.set_do(2, hold)               # 흡착툴 세팅
        status = "ON" if hold else "OFF"
        print(f"Adsorber {status}")
  
    def move_done_check():
        while True:
            status = RobotB.get_robot_status()
            time.sleep(0.1)
            if status['movedone']:
                break

    def eliminate_obj(self, area):
        """
        불량품 수거 작업
        area: 문제가 발생한 영역 번호
        """
        print(f"영역 {area}에서 불량품 수거 중...")
        self.robotB.joint_move_to(pos.jig_positions[1][area])         # area번호의 joint_approach 좌표
        RobotB.move_done_check()
        self.robotB.task_move_to(pos.jig_positions[0][area])          # area번호의 task_target 좌표
        RobotB.move_done_check()
        self.adsorber(True)                                           # 흡착툴 ON
        RobotB.move_done_check()
        self.robotB.task_move_to(pos.jig_positions[2][area])          # area번호의 task_approach 좌표
        RobotB.move_done_check()
        self.robotB.joint_move_to(pos.elimination_position[0])        # 불량품 수거 위치로 이동
        RobotB.move_done_check()
        self.adsorber(False)                                          # 흡착툴 OFF
        RobotB.move_done_check()

        print(f"영역 {area}에서 불량품 수거 완료")

    def replace_obj(self, area, expected_shape):
        """
        새로운 오브젝트 배치 작업
        area: 문제가 발생한 영역 번호
        expected_shape: 올바른 오브젝트
        """
        print(f"영역 {area}에 {expected_shape} 배치 중...")
        self.robotB.joint_move_to(pos.supplier_positions[expected_shape][0][0]) # 공급대 ready 좌표 jointmove로 이동
        RobotB.move_done_check()
        self.robotB.task_move_to(pos.supplier_positions[expected_shape][1][1]) # 공급대 approach 좌표 taskmove
        RobotB.move_done_check()
        self.robotB.task_move_to(pos.supplier_positions[expected_shape][2][1]) # 공급대 target 좌표 taskmove
        RobotB.move_done_check()
        self.adsorber(True)                                                    # 흡착툴 ON
        RobotB.move_done_check()
        self.robotB.task_move_to(pos.supplier_positions[expected_shape][1][1]) # 공급대 approach 좌표 taskmove로 이동
        RobotB.move_done_check()
        self.robotB.joint_move_to(pos.jig_positions[1][area])                  # jig approach 좌표 jointmove
        RobotB.move_done_check()
        self.robotB.task_move_to(pos.jig_positions[0][area])                   # jig target 좌표 taskmove
        RobotB.move_done_check()
        self.adsorber(False)                                                   # 흡착툴 OFF
        RobotB.move_done_check()
        self.robotB.task_move_to(pos.jig_positions[2][area])                   # jig approach 좌표 taskmove
        RobotB.move_done_check()
        print(f"영역 {area}에 {expected_shape} 배치 완료")

    def go_home(self):
        """로봇을 홈 포지션으로 이동"""
        self.go_home()
        print("Robot B 홈 포지션으로 이동 완료")


if __name__ == "__main__":
    try:
        # Robot B 객체 생성
        robot_b = RobotB(robot_b_ip, robot_b_name)

        # 로봇 연결
        robot_b.connect()

        # 문제 처리 작업 예제 (problem_objects는 외부에서 제공됨)
        # problem_object = oj_detect.check_for_problem()
        # # problem_objects = [(1, "Expected_Item_1"), (3, "Expected_Item_3")]  # 예제 리스트
        # for area, expected_shape in problem_objects:
        #     robot_b.eliminate_obj(area)  # 불량품 수거
        #     robot_b.replace_obj(area, expected_shape)  # 올바른 오브젝트 배치

        # 홈 포지션으로 이동
        robot_b.go_home()

    except Exception as e:
        print(f"작업 중 에러 발생: {e}")
    finally:
        # 로봇 연결 해제
        if 'robot_b' in locals():
            robot_b.disconnect()
