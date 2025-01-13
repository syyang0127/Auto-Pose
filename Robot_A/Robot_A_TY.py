from indy_utils import indydcp_client as client

import json
import time
from time import sleep
import threading
import numpy as np
import pymcprotocol

PLC_1 = pymcprotocol.Type3E(plctype="Q")
PLC_1.connect("192.168.3.140", 1025)
sleep(0.2)
PLC_1.close()

robot_ip = "192.168.3.7"  # Robot (Indy) IP
robot_name = "NRMK-Indy7"  # Robot name (Indy7)
# robot_name = "NRMK-IndyRP2"  # Robot name (IndyRP2)

indy = client.IndyDCPClient(robot_ip, robot_name)
sleep(0.2)

indy.connect()

#Basket zig offset
offset_x = 0.03
offset_y = 0.03
offset_z = 0.05 #approach point distance

pos_slider_joint = [55.60271460163073, -16.40313266722732, -91.0462888607369, 20.49379858640296, -88.360861598861, 52.55359007580791]
pos_basket_joint = [15.951467466749504, -17.02794603079916, -93.81684106244163, 0.022679697168937137, -69.35995271890927, 15.849138014388421]

#Item slider position
item1_pos_task = [0.2459332584538153, 0.2989074630844614, 0.3291932675169128, -180, -25, 180]
item2_pos_task = [0.24793540741466555, 0.3313195051488558, 0.3324394443552351, -180, -25, 180]
item3_pos_task = [0.24337313474463015, 0.3639865605366091, 0.33074740959203125, -180, -25, 180]

#Item slider position + approach point
circle = [item1_pos_task, [item1_pos_task[0], item1_pos_task[1], item1_pos_task[2] + offset_z, *item1_pos_task[3:]]]
triangle = [item2_pos_task, [item2_pos_task[0], item2_pos_task[1], item2_pos_task[2] + offset_z, *item2_pos_task[3:]]]
rectangle = [item3_pos_task, [item3_pos_task[0], item3_pos_task[1], item3_pos_task[2] + offset_z, *item3_pos_task[3:]]]

# Basket 3x3 격자 생성 (z 값 변형 포함)
pos_center = [0.5226623473192746, -0.13559073494980176, 0.3328998093475133, 180, 0, 180]
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

        PLC_1.batchwrite_bitunits(headdevice="M2150", values=[1])
        
        
    print("Robot A done loading")

while True:
    PLC_1.connect("192.168.3.140", 1025)
    M2100 = PLC_1.batchread_bitunits(headdevice = "M2100", readsize =1)
    M2150 = PLC_1.batchread_bitunits(headdevice = "M2150", readsize =1)
    print(f"M2100 대기중 : {M2100}")
    load = 0
    if M2100 == [1] and M2150 == [0]:
        basket_load(circle,1,triangle,1,rectangle,1)

    elif M2150 == [1]:
        PLC_1.close()
        time.sleep(0.5)
        break
    PLC_1.close()
    time.sleep(0.5)

indy.disconnect()
