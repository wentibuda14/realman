from SQLite import RoboticArmDB
from Robotic_Arm.rm_robot_interface import *
import pandas as pd
import sqlite3
from ultralytics import YOLO
import pyrealsense2 as rs
import numpy as np
import cv2


i=0
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

# 加载YOLO模型
model = YOLO('/home/trn/yolov8/yolov8n.pt')  # 使用 YOLOv8n 模型
# 启用深度和RGB流
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
# 创建数据库对象
db = RoboticArmDB()
    
while True:
    results = db.get_data_for_function(name=str(i)) 
    print("Results:", results)
    print("----------------------------------------------------------")
    if results:
    # 提取 joint 矩阵
        joint_matrix = [row['joint'] for row in results]  # 直接提取 joint 列的数据
        print("Joint Matrix:", joint_matrix)
        for joint in joint_matrix:
             robot.rm_movej(joint, 20, 0, 0, 1)
    else:
        print("No data found.")
        robot.rm_movej([0, 0, 0, 0, 0, 0], 20, 0, 0, 1)
        break
        
    # 开始流
    pipeline.start(config)
        
    try:
        # 获取一帧数据
        frames = pipeline.wait_for_frames()
        
        # 获取RGB帧
        color_frame = frames.get_color_frame()
        if not color_frame:
            raise RuntimeError("未能捕获到图像")
        
        # 将RGB帧转换为numpy数组
        color_image = np.asanyarray(color_frame.get_data())
        
        # 保存图像（可选）   
        cv2.imwrite(f'/home/trn/realman/detectdata/captured_image_{i}.jpg', color_image)
    finally:
        # 停止流
        pipeline.stop()
        cv2.destroyAllWindows()
        # 运行预测
    results = model.predict(
    source=f'/home/trn/realman/detectdata/captured_image_{i}.jpg',  # 预测图片
    task='detect',  # 指定任务为检测
    show=True,  # 显示结果
    conf=0.5,  # 置信度阈值
    show_labels=False,  # 隐藏标签 true隐藏 false显示
    ) 
        
    # print(results)
            
    # 初始化标志位
    detected_bottle = False
     
    # 遍历检测结果
    for result in results[0].boxes:
        if result is not None:  # 确保 result 有效
            cls = result.cls  # 类别索引
            conf = float(result.conf)  # 置信度

        # 确保类别索引有效
            if cls is not None:
                label = model.names[int(cls)]  # 获取类别名称

            # 检测到目标物体且置信度较高
                if label == 'bottle' and conf > 0.7:  # 置信度阈值为 0.7
                # 解包边界框坐标
                    x_min, y_min, x_max, y_max = result.xyxy.cpu().numpy().flatten().astype(int)
                    center_x = (x_min + x_max) / 2
                    center_y = (y_min + y_max) / 2

                # 获取屏幕中心区域
                    frame_height, frame_width, _ = color_image.shape
                    screen_center_x = frame_width / 2
                    screen_center_y = frame_height / 2
                    tolerance = 0.2  # 中心区域的容忍度（20%）

                # 判断目标是否在屏幕中心区域
                    if (screen_center_x * (1 - tolerance) <= center_x <= screen_center_x * (1 + tolerance) and
                        screen_center_y * (1 - tolerance) <= center_y <= screen_center_y * (1 + tolerance)):
                        detected_bottle = True
                        print(f"检测到 {label} 在屏幕中心，置信度：{conf:.2f}")
                    else:
                        detected_bottle = False
                        print(f"检测到 {label}，但不在屏幕中心，置信度：{conf:.2f}")
            else:
                print("类别索引无效，跳过此检测结果")
        else:
            print("检测结果无效，跳过")    
    # 显示检测结果
    annotated_frame = results[0].plot()  # 绘制检测结果
    cv2.imshow('YOLO Detection', annotated_frame)
    # cv2.waitKey(0)  # 等待按键

    if detected_bottle:
        print("检测到瓶子")
        i = 0
        break
    else:
        print("未检测到瓶子,进入下一姿态")
        i += 1
robot.rm_movej([0, 0, 0, 0, 0, 0], 20, 0, 0, 1)

robot.rm_delete_robot_arm()


