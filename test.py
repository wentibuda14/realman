from ultralytics import YOLO
from 
# 加载模型
model = YOLO('/home/trn/yolov8/yolov8n.pt')  # 使用 YOLOv8n 模型
# model = YOLO('C:/Users/TRN/Desktop/yolov8/runs/detect/train13/weights/best.pt')  # 使用 YOLOv8n 模型

# 运行预测
results = model.predict(
    # source='C:/Users/TRN/Desktop/yolov8/test850.jpg',  # 预测图片
    # source='screen',  # 屏幕
    # source=0,  # 摄像头
    source='/home/trn/captured_image_3 copy.jpg',  # 预测图片
    # task='segment',  # 指定任务为分割
    task='detect',  # 指定任务为检测
    # task='pose',  # 指定任务为姿态估计
    #  task='classify',  # 指定任务为分类
    show=False,  # 显示结果
    conf=0.5,  # 置信度阈值
    save=True,  # 保存结果到 'runs/segment/predict'
    save_txt=True,  # 保存结果到 'runs/segment/predict/labels'
    save_conf=True,  # 在 labels.txt 中保存置信度
    project='/home/trn/yolov8/runs/segment',  # 保存到项目路径
    name='predict',  # 保存结果到项目名称
    exist_ok=False,  # 如果项目名称已存在，true不会覆盖 false会覆盖
    # line_width=2,  # 线条粗细
    # show_labels=False,  # 隐藏标签 true隐藏 false显示
    # show_conf=False,  # 隐藏置信度 true隐藏 false显示
)

for result in results[0].boxes:
    cls = result.cls  # 类别索引
    conf = result.conf  # 置信度
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
            print(f"检测到 {label}，但不在屏幕中心，置信度：{conf:.2f}")