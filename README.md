# HangZhou Yushu Tech Unitree Go1
宇树科技 HangZhou Yushu Technology (Unitree) go1 development notes

* [Go1 series Product Matrix](#go1-series-product-matrix)
   * [Go1 (TM?)](#go1-tm)
   * [Go1 Air](#go1-air)
   * [Go1 Pro](#go1-pro)
   * [Go1 Pro MAX](#go1-pro-max)
   * [Go1 Nx](#go1-nx)
   * [Go1 MAX](#go1-max)
   * [Go1 Edu](#go1-edu)
   * [Go1 Edu Explorer](#go1-edu-explorer)
   * [Go1 Edu Plus](#go1-edu-plus)
* [Robot Internal Architecture](#robot-internal-architecture)
* [Programming interface](#programming-interface)
* [Update interface](#update-interface)
* [Upload interface](#upload-interface)
* [Passwords](#passwords)
* [Power Output](#power-output)
* [Installing TCPdump on the RasPi](#installing-tcpdump-on-the-raspi)
* [STM32 MicroROS?](#stm32-microros)
* [45 / 5G support](#45--5g-support)
* [Bluetooth](#bluetooth)

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

The difference between the EDU and the EDU Explorer is basically those features that comes with the integration of the Lidar (2D/3D): Basically
- Obstacle avoidance
- Mapping and navigation planning
- Support for developing gesture recognition
- VSLAM and other secondary development
- With the 3D Lidar, also the Dynamic Obstacle Avoidance.

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
In Go1_2022_05_11_e0d0e617/raspi/Unitree/autostart/programming we find programming.py<br>
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
In Go1_2021_12_10_d799e0c3/raspi/Unitree/autostart/updateDependencies we find startup_manager.py<br>
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
In Go1_2021_12_10_d799e0c3/raspi/Unitree/autostart/updateDependencies we find startup_uploader.py<br>
It outlines how to accept update packages. They must be .zip files, or they will be rejected

```
$ cat test.txt 
------------------------------4ebf00fbcf09
Content-Disposition: form-data; name="file"; filename="/tmp/out.zip"

filecontent here

------------------------------4ebf00fbcf09

$ curl -X POST -H "Content-Type: multipart/form-data; boundary=----------------------------4ebf00fbcf09"   --data-binary @test.txt http://localhost:9800
{'info':'File '/tmp/out.zip' upload success!'}
```

# Passwords
unitree / 123 (Nano)<br>
raspberry / 123 (RasPi)<br>
root / 123 (RasPi)<br>

# Power Output 
On the dogs belly is a 24v pass though assumed to be 2A max.

# Installing TCPdump on the RasPi

Download from the mirror
```
$ wget https://mirrors.tuna.tsinghua.edu.cn/debian/pool/main/t/tcpdump/tcpdump_4.9.3-1~deb10u2_arm64.deb 
--2022-07-06 15:30:55--  https://mirrors.tuna.tsinghua.edu.cn/debian/pool/main/t/tcpdump/tcpdump_4.9.3-1~deb10u2_arm64.deb
Resolving mirrors.tuna.tsinghua.edu.cn (mirrors.tuna.tsinghua.edu.cn)... 101.6.15.130, 2402:f000:1:400::2
Connecting to mirrors.tuna.tsinghua.edu.cn (mirrors.tuna.tsinghua.edu.cn)|101.6.15.130|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 378080 (369K) [application/octet-stream]
Saving to: ‘tcpdump_4.9.3-1~deb10u2_arm64.deb’

tcpdump_4.9.3-1~deb 100%[===================>] 369.22K   290KB/s    in 1.3s    

2022-07-06 15:31:00 (290 KB/s) - ‘tcpdump_4.9.3-1~deb10u2_arm64.deb’ saved [378080/378080]
```

Scp to the raspi, and install. 

```
$ scp tcpdump_4.9.3-1~deb10u2_arm64.deb pi@192.168.123.161:/tmp/
pi@192.168.123.161's password: 
tcpdump_4.9.3-1~deb10u2_arm64.deb                                                    100%  369KB   
```

Make yourself root and install the package. 
```
root@raspberrypi:/home/pi# dpkg -i /tmp/tcpdump_4.9.3-1~deb10u2_arm64.deb 
Selecting previously unselected package tcpdump.
(Reading database ... 171570 files and directories currently installed.)
Preparing to unpack .../tcpdump_4.9.3-1~deb10u2_arm64.deb ...
Unpacking tcpdump (4.9.3-1~deb10u2) ...
Setting up tcpdump (4.9.3-1~deb10u2) ...
Processing triggers for man-db (2.8.5-2) ...
```

# STM32 MicroROS?

The device at 192.168.123.10 may be an STM32 running MicroROS

https://micro.ros.org/docs/overview/hardware/<br>
https://www.youtube.com/watch?v=Sz-nllmtcc8<br>
https://github.com/micro-ROS/micro_ros_stm32cubemx_utils<br>

# 45 / 5G support

Quectel EG25-G is connected to the RasPI
https://www.quectel.com/wp-content/uploads/pdfupload/EP-FMEG25GMPCIs_Specification_V1.0-1609137.pdf
https://www.t-mobile.com/content/dam/tfb/pdf/tfb-iot/Quectel_EG25-G_LTE_Standard_Specification_V1.3.pdf
https://fccid.io/XMR201903EG25G/User-Manual/user-manual-4219711.pdf

It includes a GNSS function. The GPS antenna in the Go1 is connected to this device. 

5G support is assumed to be provided by a Quctel RM5 series chipset. 
https://www.quectel.com/product/5g-rm50xq-series
https://www.quectel.com/product/5g-rm510q-gl
https://www.quectel.com/wp-content/uploads/2021/02/Quectel_Product_Brochure_EN_V6.1.pdf

While connected to the 45/5g the dog does call home. 

# Bluetooth 

The transmitter appears to be Bluetooth based. 

