from SQLite import RoboticArmDB
from Robotic_Arm.rm_robot_interface import *
import pandas as pd
import sqlite3
from ultralytics import YOLO
import pyrealsense2 as rs
import numpy as np
import cv2

robot = RoboticArm(rm_thread_mode_e.RM_TRIPLE_MODE_E)
handle = robot.rm_create_robot_arm("192.168.110.118", 8080)
if handle:
        print(handle.id)
else:
        print("连接失败，错误码：", handle)
#初始化位姿
robot.rm_movej([0, 0, 0, 0, 0, 0], 20, 0, 0, 1) 

# 配置RealSense管道
pipeline = rs.pipeline()
config = rs.config()

# 启用深度和RGB流
# config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# 开始流
pipeline.start(config)

# 加载模型
model = YOLO('/home/trn/yolov8/yolov8n.pt')  # 使用 YOLOv8n 模型

try:
    while True:
        # 等待一帧数据
        frames = pipeline.wait_for_frames()

        # 获取深度帧和RGB帧
        # depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()

        # if not depth_frame or not color_frame:
        #     continue
        if not color_frame:
            continue

        # 将深度帧和RGB帧转换为numpy数组
        # depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
         
        # 运行预测
        results = model.predict(
            source=color_image,  # 摄像头
            task='detect',  # 指定任务为检测
            show=True,  # 显示结果
            conf=0.5,  # 置信度阈值
        )
        
        annotated_frame = results[0].plot()  # 获取标注后的帧
        cv2.imshow('YOLO Detection', annotated_frame)  # 显示标注后的帧
        
        # # 可视化深度图像（将深度值归一化到0-255范围）
        # depth_colormap = cv2.applyColorMap(
        #     cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET
        # )

        # 显示RGB和深度图像
        # images = np.hstack((color_image , depth_frame))
        # images = np.hstack((color_image))
        # cv2.imshow('D435i RGB and Depth', images)

        # 按下 'q' 键退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("关闭成功")
            break
finally:
    # 停止流和关闭窗口
    pipeline.stop()
    cv2.destroyAllWindows()
        
# i=0
# robot = RoboticArm(rm_thread_mode_e.RM_TRIPLE_MODE_E)
# handle = robot.rm_create_robot_arm("192.168.110.118", 8080)
# if handle:
#         print(handle.id)
# else:
#         print("连接失败，错误码：", handle)
# robot.rm_movej([0, 0, 0, 0, 0, 0], 20, 0, 0, 1) 
# db = RoboticArmDB()
    
    
#     # results = db.get_data_for_function(name=str(i))
#     # print("Results:", results)
#     # print("Type of results:", type(results))
#     # if results:
#     # # 提取 joint 矩阵
#     #     joint_matrix = [row['joint'] for row in results]  # 直接提取 joint 列的数据
#     #     print("Joint Matrix:", joint_matrix)
#     #     for joint in joint_matrix:
#     #         robot.rm_movej(joint, 20, 0, 0, 1)
#     # else:
#     #     print("No data found.")
#     #     robot.rm_movej([0, 0, 0, 0, 0, 0], 20, 0, 0, 1)
            
# while i<=8:
#         results = db.get_data_for_function(name=str(i))
#         print("Results:", results)
#         print("Type of results:", type(results))
#         if results:
#     # 提取 joint 矩阵
#             joint_matrix = [row['joint'] for row in results]  # 直接提取 joint 列的数据
#             print("Joint Matrix:", joint_matrix)
#             for joint in joint_matrix:
#                 robot.rm_movej(joint, 20, 0, 0, 1)
#         else:
#             print("No data found.")
#             robot.rm_movej([0, 0, 0, 0, 0, 0], 20, 0, 0, 1)
#         i +=1  
# robot.rm_delete_robot_arm()


# 停止流
pipeline.stop()
cv2.destroyAllWindows()