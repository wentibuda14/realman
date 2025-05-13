from SQLite import RoboticArmDB
from Robotic_Arm.rm_robot_interface import *
import pandas as pd
import sqlite3
        
        
# 使用示例
if __name__ == "__main__":
    i=0
    robot = RoboticArm(rm_thread_mode_e.RM_TRIPLE_MODE_E)
    handle = robot.rm_create_robot_arm("192.168.110.118", 8080)
    if handle:
        print(handle.id)
    else:
        print("连接失败，错误码：", handle)
    robot.rm_movej([0, 0, 0, 0, 0, 0], 20, 0, 0, 1) 
    robot.rm_delete_robot_arm()