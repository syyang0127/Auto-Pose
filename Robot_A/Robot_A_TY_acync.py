import asyncio
import pymysql
from indy_utils import indydcp_client as client
from qr import detect_qr_from_cam
from time import sleep
import pymcprotocol

plc_01 = pymcprotocol.Type3E(plctype="Q")
plc_01.connect("192.168.3.150", 5100)
print(plc_01)

hover_Jpos_slider = [60.10502082257628, -15.519051039515487, -88.13236961680592, 21.493771996830006, -89.47211237237595, 57.40340128983979]
hover_Jpos_basket = [17.921379656832276, -17.30446555397841, -94.01087232858316, 0.0008158164449257963, -68.6945184386648, 17.92136617226294]

async def take_qr_from_plc():
    data = plc_01.batchread_wordunits(headdevice="D2010", readsize=4)
    qr_code_chars = []  # QR 코드 문자를 저장할 리스트
    for word in data:
        high_byte = (word >> 8) & 0xFF  # 상위 바이트 추출
        low_byte = word & 0xFF  # 하위 바이트 추출
        qr_code_chars.append(chr(low_byte))
        qr_code_chars.append(chr(high_byte)) 

    qr_data = ''.join(qr_code_chars)
    return qr_data

async def fetch_order_by_orderNo(JigNo):
    connection = None
    try:
        connection = pymysql.connect(
            host="192.168.3.111",
            port=3306,
            user="inteldx",
            password="intel2024!",
            database="test_bm",
            cursorclass=pymysql.cursors.DictCursor
        )
        with connection.cursor() as cursor:
            query = "SELECT Product1Qty, Product2Qty, Product3Qty FROM orders WHERE JigNo = %s"
            cursor.execute(query, (JigNo,))
            rows = cursor.fetchall()
        return rows
    except pymysql.MySQLError as err:
        print(f"Error: {err}")
        return None
    finally:
        if connection:
            connection.close()

async def move_done_check(indy):
    while True:
        status = indy.get_robot_status()
        await asyncio.sleep(0.1)
        if status['movedone']:
            break

async def gripper(indy, hold):
    indy.set_do(2, hold)
    await asyncio.sleep(1)

async def basket_load(indy, basket_3x3, item1, cycle1, item2, cycle2, item3, cycle3):
    for i in range(cycle1):
        await perform_task(indy, item1, basket_3x3[i])

    for j in range(cycle2):
        await perform_task(indy, item2, basket_3x3[cycle1 + j])

    for k in range(cycle3):
        await perform_task(indy, item3, basket_3x3[cycle1 + cycle2 + k])

async def perform_task(indy, item, basket):
    indy.task_move_to(item[1])
    await move_done_check(indy)
    indy.task_move_to(item[0])
    await move_done_check(indy)
    await gripper(indy, True)
    indy.task_move_to(item[1])
    await move_done_check(indy)

    indy.joint_move_to(hover_Jpos_slider)
    await move_done_check(indy)
    indy.joint_move_to(hover_Jpos_basket)
    await move_done_check(indy)

    indy.task_move_to(basket[1])
    await move_done_check(indy)
    indy.task_move_to(basket[0])
    await move_done_check(indy)
    await gripper(indy, False)
    indy.task_move_to(basket[1])
    await move_done_check(indy)

    indy.joint_move_to(hover_Jpos_basket)
    await move_done_check(indy)
    indy.joint_move_to(hover_Jpos_slider)
    await move_done_check(indy)

async def work_robot_A():
    robot_ip = "192.168.3.7"
    robot_name = "NRMK-Indy7"
    indy = client.IndyDCPClient(robot_ip, robot_name)

    offset_x = 0.029
    offset_y = 0.029
    offset_z = 0.05

    pos_center = [0.5226623473192746, -0.13559073494980176, 0.3328998093475133, 180, 0, 180]
    basket_3x3 = []
    for i in range(3):
        for j in range(3):
            x = pos_center[0] + j * offset_x
            y = pos_center[1] + i * offset_y
            z = pos_center[2]
            roll, pitch, yaw = pos_center[3], pos_center[4], pos_center[5]
            base_point = [x, y, z, roll, pitch, yaw]
            offset_point = [x, y, z + offset_z, roll, pitch, yaw]
            basket_3x3.append([base_point, offset_point])

    while True:
        indy.connect()
        plc_01.connect("192.168.3.150", 5100)
        plc_01_M2100 = plc_01.batchread_bitunits(headdevice="M2100", readsize=1)
        print(plc_01_M2100)
        if plc_01_M2100 == [1]:
            qr_data = take_qr_from_plc()
            if qr_data:
                print(f"Detected QR Code: {qr_data}")
                result = await fetch_order_by_orderNo(qr_data)
                if result:
                    product1_cycle = result[0]['Product1Qty']
                    product2_cycle = result[0]['Product2Qty']
                    product3_cycle = result[0]['Product3Qty']

                    item1_pos_task = [0.2459332584538153, 0.2989074630844614, 0.3291932675169128, -180, -25, 180]
                    item2_pos_task = [0.24236016387703746, 0.3301108106459974, 0.3312259599817894, -180, -25, 180]
                    item3_pos_task = [0.24408739462966056, 0.36295176030567794, 0.3325214343269048, -180, -25, 180]

                    circle = [item1_pos_task, [item1_pos_task[0] + offset_x, item1_pos_task[1], item1_pos_task[2] + offset_z, *item1_pos_task[3:]]]
                    triangle = [item2_pos_task, [item2_pos_task[0] + offset_x, item2_pos_task[1], item2_pos_task[2] + offset_z, *item2_pos_task[3:]]]
                    rectangle = [item3_pos_task, [item3_pos_task[0] + offset_x, item3_pos_task[1], item3_pos_task[2] + offset_z , *item3_pos_task[3:]]]

                    await basket_load(indy, basket_3x3, circle, product1_cycle, triangle, product2_cycle, rectangle, product3_cycle)
                    plc_01.batchwrite_bitunits(headdevice="M2150", values=[1])
                    await asyncio.sleep(1)
                    plc_01.close()
                    indy.disconnect()
                    print(f"Work of {qr_data} is done.")
                else:
                    print("No result found in the database.")
            else:
                print("QR code not detected.")

        plc_01.close()
        indy.disconnect()
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(work_robot_A())