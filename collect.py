import pandas as pd
from SQLite import RoboticArmDB
from Robotic_Arm.rm_robot_interface import *
import pyrealsense2 as rs
import numpy as np
import cv2

if __name__ == "__main__":
    # 初始化机械臂
    robot = RoboticArm(rm_thread_mode_e.RM_TRIPLE_MODE_E)
    handle = robot.rm_create_robot_arm("192.168.110.118", 8080)
    if handle:
        print(f"机械臂连接成功，ID: {handle.id}")
    else:
        print(f"机械臂连接失败，错误码: {handle}")
        exit()

    # 初始化数据库
    db = RoboticArmDB()
    i = 0  # 数据记录计数器

    # 配置 RealSense 管道
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    # 开始 RealSense 流
    pipeline.start(config)

    try:
        while True:
            # 获取视频帧
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            if not color_frame:
                continue

            # 转换为 numpy 数组
            color_image = np.asanyarray(color_frame.get_data())

            # 显示视频
            cv2.imshow('D435i RGB Stream', color_image)

            # 检测用户输入
            key = cv2.waitKey(1) & 0xFF
            if key == ord('s'):  # 按下 's' 键保存机械臂位姿
                state = robot.rm_get_current_arm_state()
                if state:
                    print("机械臂状态：", state)
                    state_data = state[1]  # 提取元组的第二个元素
                    sample_data = {
                        'joint': state_data['joint'],  # 关节数据
                        'pose': state_data['pose']    # 位姿数据
                    }
                    db.insert_data(sample_data, custom_name=f"{i}")
                    print(f"已保存机械臂位姿，记录编号: {i}")
                    i += 1
                else:
                    print("获取机械臂状态失败")
            elif key == ord('q'):  # 按下 'q' 键退出程序
                print("退出程序")
                break

    finally:
        # 停止 RealSense 流和关闭窗口
        pipeline.stop()
        cv2.destroyAllWindows()
    print("--------------------------------")
    # 查询数据
    #不传数据则查询所有 传入数据按照数据来查询 比如(name="calibration_test_1")按名字查询
    results = db.query_data() 
    print("查询到的数据:", results)
    # 使用 pandas 显示数据
    
    # 定义列名（与数据库表结构一致）
    columns = ['id', 'name', 'timestamp', 'joint1', 'joint2', 'joint3', 'joint4', 'joint5', 'joint6',
               'pose1', 'pose2', 'pose3', 'pose4', 'pose5', 'pose6' , 'extra_column']
    
     # 转换为 DataFrame
    df = pd.DataFrame(results, columns=columns)
    print("---------------------------------")
     # 显示 DataFrame
    print(df)


    # 可视化数据
    # db.visualize_data()

    # 获取函数可用数据格式
    # function_data = db.get_data_for_function(name="calibration_test_1")
    # print("Function-ready data:", function_data)

    # 删除数据（按名称）
    # db.delete_data()
    # db.close()