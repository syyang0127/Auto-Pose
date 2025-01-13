from indy_utils import indydcp_client as client

import json
import time
from time import sleep
import threading
import numpy as np

robot_ip = "192.168.3.7"  # Robot (Indy) IP
robot_name = "NRMK-Indy7"  # Robot name (Indy7)
# robot_name = "NRMK-IndyRP2"  # Robot name (IndyRP2)

indy = client.IndyDCPClient(robot_ip, robot_name)
sleep(1)

indy.connect()

#Basket zig offset
offset_x = 0.031
offset_y = 0.031
offset_z = 0.03 #approach point distance

pos_slider_joint = [87.92480973173359, -0.5254370318956958, -111.38570486022171, 0.04182418974319583, -68.41148452003854, 87.93277551632696]
pos_basket_joint = [20.579934868932142, -13.462746360086115, -96.59974153377445, -0.2603542214573191, -70.24299243889696, 20.57075727104096]

#Item slider position
item1_pos_task = [0.18590751100902442, 0.36718133245047757, 0.3536054851654807, -180, -23, 180]
item2_pos_task = [0.181386960075633, 0.5482425497483345, 0.3451090011717526, -180, -23, 180]
item3_pos_task = [0.22931479626152027, 0.5913640834751501, 0.3543532063254496, 170, -14, 180]

#Item slider position + approach point
circle = [item1_pos_task, [item1_pos_task[0], item1_pos_task[1], item1_pos_task[2] + offset_z, *item1_pos_task[3:]]]
triangle = [item2_pos_task, [item2_pos_task[0], item2_pos_task[1], item2_pos_task[2] + offset_z, *item2_pos_task[3:]]]
rectangle = [item3_pos_task, [item3_pos_task[0], item3_pos_task[1], item3_pos_task[2] + offset_z, *item3_pos_task[3:]]]

# Basket 3x3 격자 생성 (z 값 변형 포함)
pos_center = [0.5200724163809812, -0.13001499017914542, 0.3416199448926611, -180, 0, 180]
basket_3x3 = []
for i in range(3):  # y 방향으로 0, 1, 2
    for j in range(3):  # x 방향으로 0, 1, 2
        x = pos_center[0] + j * offset_x  # x 방향 오프셋
        y = pos_center[1] + i * offset_y  # y 방향 오프셋
        z = pos_center[2]  # z 좌표
        roll, pitch, yaw = pos_center[3], pos_center[4], pos_center[5]  # 오리엔테이션

        # 기본 위치
        base_point = [x, y, z, roll, pitch, yaw]
        # z값 오프셋 추가된 위치
        offset_point = [x, y, z + offset_z, roll, pitch, yaw]
        # 두 위치를 리스트로 저장
        basket_3x3.append([base_point, offset_point])

def move_done_check():
    while True:
        status = indy.get_robot_status()
        sleep(0.1)
        if status['movedone'] == True:
            break
    
def gripper(hold):
    if hold == True:
        indy.set_do(2, True)
        sleep(1)

    elif hold == False:
        indy.set_do(2, False)
        sleep(1)


def basket_load(item1,cycle1,item2,cycle2,item3,cycle3):
    for i in range(cycle1):
        indy.task_move_to(item1[1])
        move_done_check()
        indy.task_move_to(item1[0])
        move_done_check()
        gripper(True)
        indy.task_move_to(item1[1])
        move_done_check()

        #joint move + work space jump point
        indy.joint_move_to(pos_slider_joint)
        move_done_check()
        indy.joint_move_to(pos_basket_joint)
        move_done_check()

        indy.task_move_to(basket_3x3[i][1])
        move_done_check()
        indy.task_move_to(basket_3x3[i][0])
        move_done_check()
        gripper(False)
        indy.task_move_to(basket_3x3[i][1])
        move_done_check()

        indy.joint_move_to(pos_basket_joint)
        move_done_check()
        indy.joint_move_to(pos_slider_joint)
        move_done_check()


    for j in range(cycle2):
        indy.task_move_to(item2[1])
        move_done_check()
        indy.task_move_to(item2[0])
        move_done_check()
        gripper(True)
        indy.task_move_to(item2[1])
        move_done_check()

        #joint move + work space jump point
        indy.joint_move_to(pos_slider_joint)
        move_done_check()
        indy.joint_move_to(pos_basket_joint)
        move_done_check()


        indy.task_move_to(basket_3x3[cycle1+j][1])
        move_done_check()
        indy.task_move_to(basket_3x3[cycle1+j][0])
        move_done_check()
        gripper(False)
        indy.task_move_to(basket_3x3[cycle1+j][1])
        move_done_check()

        indy.joint_move_to(pos_basket_joint)
        move_done_check()
        indy.joint_move_to(pos_slider_joint)
        move_done_check()

    for k in range(cycle3):
        indy.task_move_to(item3[1])
        move_done_check()
        indy.task_move_to(item3[0])
        move_done_check()
        gripper(True)
        indy.task_move_to(item3[1])
        move_done_check()

        #joint move + work space jump point
        indy.joint_move_to(pos_slider_joint)
        move_done_check()
        indy.joint_move_to(pos_basket_joint)
        move_done_check()

        indy.task_move_to(basket_3x3[cycle1+cycle2+k][1])
        move_done_check()
        indy.task_move_to(basket_3x3[cycle1+cycle2+k][0])
        move_done_check()
        gripper(False)
        indy.task_move_to(basket_3x3[cycle1+cycle2+k][1])
        move_done_check()

        indy.joint_move_to(pos_basket_joint)
        move_done_check()
        indy.joint_move_to(pos_slider_joint)
        
        
    print("Robot A done loading")

basket_load(circle,2,triangle,2,rectangle,2) #basket loading sequence

indy.disconnect()