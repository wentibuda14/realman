import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from Robotic_Arm.rm_robot_interface import *
import pandas as pd

class RoboticArmDB:
    def __init__(self, db_name='/home/trn/realman/arm_data.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()
    
    def create_tables(self):
        """创建数据表结构"""
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS arm_states (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        joint1 REAL, joint2 REAL, joint3 REAL,
                        joint4 REAL, joint5 REAL, joint6 REAL,
                        pose1 REAL, pose2 REAL, pose3 REAL,
                        pose4 REAL, pose5 REAL, pose6 REAL)''')
        self.conn.commit()

    def insert_data(self, data, custom_name="default"):
        """
        插入分割后的数据
        :param data: 原始字典数据（应包含joint和pose字段）
        :param custom_name: 自定义数据名称
        """
        joint = data.get('joint', [0]*6)
        pose = data.get('pose', [0]*6)
        
        cursor = self.conn.cursor()
        cursor.execute('''INSERT INTO arm_states 
                      (name, joint1, joint2, joint3, joint4, joint5, joint6,
                       pose1, pose2, pose3, pose4, pose5, pose6)
                      VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                      (custom_name, *joint, *pose))   
        self.conn.commit()


    def query_data(self, name=None, start_time=None, end_time=None ,):
        """
        查询数据（支持按名称和时间范围查询）
        :return: 查询结果列表
        """
        cursor = self.conn.cursor()
        query = "SELECT * FROM arm_states WHERE 1=1"
        params = []
        
        if name:
            query += " AND name = ?"
            params.append(name)
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time)
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time)
            
        cursor.execute(query, params)
        return cursor.fetchall()
        

    def delete_data(self, name=None, start_time=None, end_time=None):
        """
        删除数据（支持多种删除方式，保持原有功能）
        :return: 删除的行数
        """
        cursor = self.conn.cursor()
        query = "DELETE FROM arm_states WHERE 1=1"
        params = []
        
        if name:
            query += " AND name = ?"
            params.append(name)
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time)
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time)
            
        cursor.execute(query, params)
        self.conn.commit()
        return cursor.rowcount

    def visualize_data(self, name=None, start_time=None, end_time=None):
        """数据可视化（示例：关节角度变化）"""
        data = self.query_data(name, start_time, end_time)
        if not data:
            print("No data to visualize")
            return

        timestamps = [row[2] for row in data]
        joints = [row[3:9] for row in data]  # 提取所有关节数据

        plt.figure(figsize=(12, 8))
        for i in range(6):
            plt.plot(timestamps, [j[i] for j in joints], label=f'Joint {i+1}')

        plt.xlabel('Time')
        plt.ylabel('Angle (degrees)')
        plt.title('Joint Angles Over Time')
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def get_data_for_function(self, name=None, start_time=None, end_time=None):
  
        data_rows = self.query_data(name, start_time, end_time)
        result = []
        for row in data_rows:
            processed = {
                'name': row[1],
                'timestamp': row[2],
                'joint': list(row[3:9]),
                'pose': list(row[9:15])
            }
            result.append(processed)
        return result
    
    def close(self):
        self.conn.close()
        

# 使用示例
if __name__ == "__main__":
    
    i = 0
    q = 1
    robot = RoboticArm(rm_thread_mode_e.RM_TRIPLE_MODE_E)
    handle = robot.rm_create_robot_arm("192.168.110.118", 8080)
    if handle:
        print(handle.id)
    else:
        print("连接失败，错误码：", handle)
           
    # print("State type:", type(state))
    # print("State content:", state)
    # print("State[0] type:", type(state[0]))
    # print("State[0] content:", state[0])
        
    # 初始化数据库
    db = RoboticArmDB()
    
    while True:
    # 插入数据（使用自定义名称）
        user_input = input("输入 's' 保存数据，输入任意键退出：")
        if user_input.lower() == "s":
            state = robot.rm_get_current_arm_state()
            if state:
                print("机械臂状态：", state)
            else:
                print("获取机械臂状态失败，错误码：", state)
            # 确保从元组中提取第一个元素
            state_data = state[1]  # 提取元组的第二个元素
            sample_data = {
                'joint': state_data['joint'],  # 访问字典中的 'joint'
                'pose': state_data['pose']    # 访问字典中的 'pose'
            }
            db.insert_data(sample_data, custom_name=f"{i}")
            i+=1
        else:
            break
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
    

