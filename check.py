import pandas as pd
from SQLite import RoboticArmDB
from Robotic_Arm.rm_robot_interface import *



# 使用示例
if __name__ == "__main__":
    robot = RoboticArm(rm_thread_mode_e.RM_TRIPLE_MODE_E)
    handle = robot.rm_create_robot_arm("192.168.110.119", 8080)
    if  handle :
        print(handle.id)
    else:
        print("连接失败，错误码：", handle)
    # 初始化数据库（自动创建表）
    db = RoboticArmDB()
    
    state = robot.rm_get_current_arm_state()
    if state:
        print("机械臂状态：", state)
    else:
        print("获取机械臂状态失败，错误码：", state)  
    print("-------------------------------------------------")
    
    # 模拟插入数据（假设有6个关节）
    # sample_data = [1,1,1,1,1,1]
    # db.insert_data(sample_data)

    # 读取所有数据
    
    all_data = db.get_all_data()
    print("所有历史数据：")
    for record in all_data:
        print(f"{record['timestamp']} -> 关节角度：{record['joint1']},{record['joint2']},{record['joint3']},{record['joint4']},{record['joint5']},{record['joint6']}")
    
    # 可视化数据
    # db = JointDataDB()
    #df = pd.DataFrame(db.get_all_data())
    #print(df.describe())  # 显示统计信息
    
    db.delete_data()
    