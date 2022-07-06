# HangZhou Yushu Tech Unitree Go1
宇树科技 HangZhou Yushu Technology (Unitree) go1 development notes

This $2,700 robot dog will carry a single bottle of water for you: Who needs a tote bag when you have a little robot butler?<br>
https://www.theverge.com/2021/6/10/22527413/tiny-robot-dog-unitree-robotics-go1<br>
[![Launch Video](http://img.youtube.com/vi/xdfmhWQyp_8/0.jpg)](https://www.youtube.com/watch?v=xdfmhWQyp_8)<br>

# Go1 series Product Matrix
The full product matrix is not understood, there appear to be regional sub variants that are only sold in certain countries. For example the "Go1 MAX" is supposed to be China exclusive, although it can be easily obtained "cross-border". [Test report details](https://www.tele.soumu.go.jp/giteki/SearchServlet?pageID=jg01_01&PC=018&TC=N&PK=1&FN=220315N018&SN=%94F%8F%D8&LN=15&R1=*****&R2=*****) have given the current understanding of product options. <br>
<p align="center">
<img
src="https://github.com/MAVProxyUser/YushuTechUnitreeGo1/blob/main/JapanTest.png"><br>
<img
src="https://github.com/MAVProxyUser/YushuTechUnitreeGo1/blob/main/ChinaTest.png"><br>
</p>

## Go1 (TM?)
https://www.taobao.com/list/item/657740636451.htm
Early Black variant of the Air? 

https://www.cnbeta.com/articles/tech/1139381.htm
Includes "HAI1" features!
 
<p align="center">
<img 
src="https://github.com/MAVProxyUser/YushuTechUnitreeGo1/blob/main/Go1TM.jpg"><br>
</p>

<p align="center">
<img 
src="https://github.com/MAVProxyUser/YushuTechUnitreeGo1/blob/main/Go1.jpg"><br>
</p>

## Go1 Air
<p align="center">
<img 
src="https://github.com/MAVProxyUser/YushuTechUnitreeGo1/blob/main/Go1Air.png"><br>
</p>

## Go1 Pro
<p align="center">
<img 
src="https://github.com/MAVProxyUser/YushuTechUnitreeGo1/blob/main/Go1Pro.png"><br>
</p>

## Go1 Pro MAX

## Go1 Nx

## Go1 MAX
https://www.taobao.com/list/item/667863152779.htm
<p align="center">
<img 
src="https://github.com/MAVProxyUser/YushuTechUnitreeGo1/blob/main/Go1MAX.png"><br>
</p>

## Go1 Edu
<p align="center">
<img 
src="https://github.com/MAVProxyUser/YushuTechUnitreeGo1/blob/main/Go1EDU.png"><br>
</p>

## Go1 Edu Explorer

Like the Explorer, the Basic version of the Unitree A1 also has an IntelRealsense 3D camera, but the computing operations are performed by a Raspberry Pi in the 
Basic version, whereas an NViDIA TX2 or NX is installed in the Explorer version. Of course, the Raspberry Pi cannot perform full image processing, but is 
usually only the interface between the robot and the third-party device. Thus, the Basic variant is suitable for all those who want to install their own CPU & 
GPU, and the Explorer variant for all those who like to have a complete research platform "out of the box".

## Go1 Edu Plus

# Robot Internal Architecture

<p align="center">
<img 
src="https://github.com/MAVProxyUser/YushuTechUnitreeGo1/blob/main/NetworkLayout.png"><br>
</p>

<p align="center">
<img 
src="https://github.com/MAVProxyUser/YushuTechUnitreeGo1/blob/main/FlowChart.png"><br>
</p>

<p align="center">
<img 
src="https://github.com/MAVProxyUser/YushuTechUnitreeGo1/blob/main/sdk.png"><br>
</p>

<p align="center">
<img 
src="https://github.com/MAVProxyUser/YushuTechUnitreeGo1/blob/main/Ports.png"><br>
</p>

# Programming interface
In Go1_2022_05_11_e0d0e617/raspi/Unitree/autostart/programming we find programming.py
It imports ./build/robot_interface_high_level.cpython-37m-aarch64-linux-gnu.so in order to call the UDP listen 
functions. 
```
import robot_interface_high_level as robot_interface
``` 
...
```
unitree_go1 = robot_interface.RobotInterface()
```

The interface seems to blindly pass user input to exec().
```
The exec() method executes the dynamically created program, which is either a string or a code object.
```

First the code passes through compile()
```
compile() method is used if the Python code is in string form or is an AST object, and you want to change it to 
a code object.
```
This handles all the MIT Scratch code blocks from the mobile client. 

# Update interface
In Go1_2021_12_10_d799e0c3//raspi/Unitree/autostart/updateDependencies we find startup_manager.py 
It declares itself to be "Unitree System Manager", and offers the following functions
```
Functions:
1. run bash files
2. delete uploaded packages
3. run update packages
4. process topics when modules shut down
```

This can also be used to run arbitry commands. 
```
def on_message(client, userdata, msg):
    global updatePackage
    global updateFirmware
    # not doing anything during update
    if(updatePackage !='' or updateFirmware !=''):
        return 
    # run bash file
    if(msg.topic == "usys/sh"):
        bashFile = str(msg.payload,'utf-8')
        print("Running sh " + bashFile)
        process = subprocess.Popen(["sh", bashFile],stdout=subprocess.PIPE)
```

# Upload interface 
In Go1_2021_12_10_d799e0c3//raspi/Unitree/autostart/updateDependencies we find startup_uploader.py
It outlines how to accept update packages. They must be .zip files, or they will be rejected


$ cat test.txt 
------------------------------4ebf00fbcf09
Content-Disposition: form-data; name="file"; filename="/tmp/out.zip"

filecontent here

------------------------------4ebf00fbcf09

$ curl -X POST -H "Content-Type: multipart/form-data; boundary=----------------------------4ebf00fbcf09"   --data-binary @test.txt http://localhost:9800
{'info':'File '/tmp/out.zip' upload success!'}Kevins-MacBook-Air:YushuTechUnitreeGo1 kfinisterre


# Passwords
unitree / 123 (Nano)
raspberry / 123 (RasPi)
root / 123 (RasPi)

# Power Output 
On the dogs belly is a 24v pass though assumed to be 2A max.
