import sys
import time
import logging
from indy_utils import indydcp_client as client

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] - %(message)s")
logger = logging.getLogger()

class RobotC:
    def __init__(self, robot_ip, robot_name):
        self.robot_ip = robot_ip
        self.robot_name = robot_name
        self.indy = client.IndyDCPClient(robot_ip, robot_name)
        self.indy.connect()
        self.pick_index = 0  # task_pick 리스트의 인덱스를 관리

    def __del__(self):
        self.indy.disconnect()

    def move_done_check(self):
        while True:
            status = self.indy.get_robot_status()
            time.sleep(0.1)
            if status['movedone']:
                break

    def griffer_off(self):
        self.indy.set_do(1, False)
        self.indy.set_do(0, True)

    def griffer_on(self):
        self.indy.set_do(1, True)
        self.indy.set_do(0, False)

    def lid_pick_place(self):
        # Coordinates
        joint_pick_apprch = [-56.47149708645775, -19.165059239412418, -94.31817172973246, 0.013814491800743485, -66.81732479889054, 33.40365872524972]
        task_pick_apprch = [0.10281376154204955, -0.4927232129626567, 0.35755398260536947, -179.84510959420842, -0.2578832983671999, 90.11892425224596]
        
        task_pick = [
            [0.10273390705794429, -0.49303327871852914, 0.2420868589660376, -179.81085650293033, -0.2584700363007016, 90.05646204445641],
            [0.10273390705794429, -0.49303327871852914, 0.2268295059266855, -179.86586882796627, -0.1868485118276776, 90.07007473836315],
            [0.10307300857275054, -0.49262093542151364, 0.2139410452756723, -179.7954068868283, -0.3342839834304611, 90.15659252225679],
            [0.10270950575551444, -0.4928284658643753, 0.19968587373558983, -179.8824867285986, -0.19571664044893441, 90.0549428239375],
            [0.10285445795223637, -0.49279087982812886, 0.18742762479029937, -179.91245081441227, -0.15479626346677797, 90.13214277493068]
        ]

        joint_place_apprch = [7.442238547585717, -28.021583241866516, -80.62875290548052, -0.051178884978344955, -71.62955406869284, 7.210240128017182]
        task_place_apprch = [0.5615868539869184, -0.11492118514717709, 0.35747242332507333, 0.0834067075064624, -179.72777213607554, 0.24795358105290077]
        task_place_target_1 = [0.5628986608707184, -0.1155612422051988, 0.24767875760225608, 0.0006432162371938033, -179.99359124299235, 0.0021138593018605314]
        task_place_target_2 = [0.5628986608707184, -0.1155612422051988, 0.23567875760225608, 0.0006432162371938033, -179.99359124299235, 0.0021138593018605314]

        # 작업 순서
        self.indy.go_home()
        self.move_done_check()
        
        self.indy.joint_move_to(joint_pick_apprch)
        self.move_done_check()

        # task_pick 좌표 사용 및 인덱스 증가
        if self.pick_index < len(task_pick):
            self.indy.task_move_to(task_pick[self.pick_index])
            self.move_done_check()
            
            self.griffer_on()
            self.move_done_check()
            
            self.indy.task_move_to(task_pick_apprch)
            self.move_done_check()
            
            self.indy.joint_move_to(joint_place_apprch)
            self.move_done_check()
            
            self.indy.task_move_to(task_place_target_1)
            self.move_done_check()
            
            self.indy.task_move_to(task_place_target_2)
            self.move_done_check()
            
            self.griffer_off()
            self.indy.task_move_to(task_place_apprch)
            self.move_done_check()
            
            # 인덱스 증가
            self.pick_index += 1

            if self.pick_index == 5 :
                self.pick_index = 0
        else:
            logger.info("모든 task_pick 작업이 완료되었습니다.")
        
        self.indy.go_home()
        self.move_done_check()

if __name__ == "__main__":
    robot_ip = "192.168.3.5"  # Robot (Indy) IP
    robot_name = "NRMK-Indy7"  # Robot name (Indy7)

    robot = RobotC(robot_ip, robot_name)
    try:
        robot.lid_pick_place()
    except Exception as e:
        logger.error(f"에러 발생: {e}")
    finally:
        del robot
