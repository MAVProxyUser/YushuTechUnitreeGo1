#!/usr/bin/python
import time
import paho.mqtt.client as mqtt
from multiprocessing import Process, Pipe
# import os
import sys
sys.path.append('/home/pi/Unitree/autostart/programming/build') # Edit the path to "build" folder on your computer
import robot_interface_high_level as robot_interface

class Unitree_Robot():
    unitree_go1 = robot_interface.RobotInterface()
    robot_state = robot_interface.HighState()
    
    # 类初始化
    def __init__(self):
        self.cmd_init()

    # 初始化命令
    def cmd_init(self):
        self.mode = 0
        self.gaitType = 0
        self.speedLevel = 0
        self.footRaiseHeight = 0.0
        self.forwardSpeed = 0.0
        self.sidewaySpeed = 0.0
        self.rotateSpeed = 0.0
        self.bodyHeight = 0.0
        self.yaw = 0.0
        self.pitch = 0.0
        self.roll = 0.0
        
    # 机器人控制函数
    def robot_update(self):
        self.unitree_go1.robotControl(self.mode, self.gaitType, self.speedLevel,
                                    self.footRaiseHeight, self.bodyHeight, 
                                    self.roll, self.pitch, self.yaw,
                                    self.forwardSpeed, self.sidewaySpeed, self.rotateSpeed)
        self.unitree_go1.UDPSend()
        self.unitree_go1.UDPRecv()
        self.robot_state = self.unitree_go1.getState()

    def reset(self):
        self.cmd_init()
        self.robot_update()
    
    def wait(self,seconds):
        t_end= time.time() + seconds
        while time.time() < t_end:
            self.robot_update()
    
    def stand_up(self): 
        self.cmd_init()
        self.bodyHeight = 0.1
        self.mode = 1
        self.robot_update()

    def stand_down(self):
        self.cmd_init()
        self.bodyHeight = -0.1
        self.mode = 1
        self.robot_update()
    
    def pitch_up(self):
        self.cmd_init()
        self.mode = 1
        self.pitch = -0.2
        self.robot_update()
    
    def pitch_down(self):
        self.cmd_init()
        self.mode = 1
        self.pitch = +0.2
        self.robot_update()

    def yaw_left(self):
        self.cmd_init()
        self.mode = 1
        self.yaw = -0.15
        self.bodyHeight = -0.05
        self.robot_update()
    
    def yaw_right(self):
        self.cmd_init()
        self.mode = 1
        self.yaw = 0.15
        self.bodyHeight = -0.05
        self.robot_update()

    def roll_left(self):
        self.cmd_init()
        self.mode = 1
        self.roll = 0.2
        self.robot_update()
    
    def roll_right(self):
        self.cmd_init()
        self.mode = 1
        self.roll = -0.2
        self.robot_update()
    
    def test(self):
        self.robot_update()
        print(self.robot_state.imu.rpy)


current_action = "stop"
code = ""

def on_connect(client,userdata,flags,rc):
    print("Unitree Programming Module")
    #状态切换：播放、停止、暂停
    client.subscribe("programming/action")
    #程序，JSON数组
    client.subscribe("programming/code")
    #编程模块开启信号
    client.publish("programming/run",'on',1,True)
    client.publish("programming/current_action", "stop", retain=True)

def on_message(client, userdata, msg):
    global current_action, code, process
    msg_str = str(msg.payload,'utf-8')
    if(msg.topic == "programming/action" and msg_str == "stop"):
        if (process.is_alive()):
            process.terminate()
    elif(msg.topic == "programming/code"):
        if not (process.is_alive()):
            code = msg_str
            process = Process(target=executor, args=(code, child_conn),daemon=True)
            process.start()


client = mqtt.Client()
client.will_set("programming/run","",1,True)

client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost",1883,60)
parent_conn, child_conn = Pipe()

def executor(code,child_conn):
    go1 = Unitree_Robot()
    go1.robot_update()
    time.sleep(1)
    print("executing code ...")
    program = compile(code,"","exec")
    exec(program)
    print("execution finished")

def change_light(r,g,b):
    global client
    client.publish("face_light/color", bytes([r,g,b]))

process = Process(target=executor, args=(code, child_conn), daemon=True)

client.loop_start()
while True:
    if(parent_conn.poll()):
        block_code = parent_conn.recv()
        try:
            block = compile(block_code,"","eval")
            eval(block)
        except: 
            print(block_code)
    if(current_action == "stop" and process.is_alive()):
        current_action = "run"
        print(current_action)
        client.publish("programming/current_action", current_action, retain=True)
    if(current_action == "run" and (process.is_alive() == False)):
        current_action = "stop"
        print(current_action)
        client.publish("programming/current_action", current_action, retain=True)


