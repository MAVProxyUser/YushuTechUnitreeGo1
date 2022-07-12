# HangZhou Yushu Tech Unitree Go1
宇树科技 HangZhou Yushu Technology (Unitree) go1 development notes

* [HangZhou Yushu Tech Unitree Go1](#hangzhou-yushu-tech-unitree-go1)
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
* [Bluetooth](#bluetooth)
* [Mobile App](#mobile-app)
* [45 / 5G support](#45--5g-support)
* [4G use in the USA](#4g-use-in-the-usa)
* [GPS from 4G module](#gps-from-4g-module)
* [Wifi backdoor](#wifi-backdoor)
* [Autostart items](#autostart-items)
* [PDB emergency shut off (backdoor? no way to disable)](#pdb-emergency-shut-off-backdoor-no-way-to-disable)
* [What talks to the STM at 192.168.123.10?](#what-talks-to-the-stm-at-19216812310)
* [MIT Cheetah code](#mit-cheetah-code)
* [Sniffing MQTT traffic on the dog](#sniffing-mqtt-traffic-on-the-dog)
* [Sending MQTT commands to the dog.](#sending-mqtt-commands-to-the-dog)
* [TFTP to RTOS](#tftp-to-rtos)
* [Troubleshooting](#troubleshooting)

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
*unknown* 

## Go1 Nx
*unknown* 

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

When upgrading to the 2D or 3D LiDAR versions of the GO1 EDU, one of the three Jetson Nanos is upgraded to a Jetson Xavier NX. As a result, the robot is capable of dynamic obstacle avoidance, navigation planning, map building, self-positioning and more. This also supports your ability to develop gesture recognition, VSLAM, deep learning, machine learning, etc.

## Go1 Edu Plus
2D LiDAR Upgrade (Plus)

## Go1 Edu Explorer
3D LiDAR Upgrade (Explorer)

The difference between the EDU and the EDU Explorer is basically those features that comes with the integration of the Lidar (2D/3D): 
Basically<br>
- Obstacle avoidance<br>
- Mapping and navigation planning<br>
- Support for developing gesture recognition<br>
- VSLAM and other secondary development<br>
- With the 3D Lidar, also the Dynamic Obstacle Avoidance.<br>

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
It imports ./build/robot_interface_high_level.cpython-37m-aarch64-linux-gnu.so in order to call the UDP listen functions. 
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
compile() method is used if the Python code is in string form or is an AST object, and you want to change it to a code object.
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
root@raspberrypi:/home/pi$ dpkg -i /tmp/tcpdump_4.9.3-1~deb10u2_arm64.deb 
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

# Bluetooth 

The transmitter appears to be Bluetooth based. 

# Mobile App
The mobile app uses MQTT over websocket

On an iOS device you can use RVI utils to sniff the connection
https://developer.apple.com/documentation/network/recording_a_packet_trace

$ rvictl -s 0000xxxx-yourdeviceuuid

Starting device 0000xxxx-yourdeviceuuid [SUCCEEDED] with interface rvi0

$ sudo tcpdump -i rvi0 -xX -s2000 host 192.168.12.1 and not port domain -w tcpdump.pcap

The initial connection hits /mqtt on the web server. 

```
GET /mqtt HTTP/1.1
Host: 192.168.12.1
Pragma: no-cache
Accept: */*
Sec-WebSocket-Key: qoldXnNLZu0GftYE7x+XgA==
Sec-WebSocket-Version: 13
Sec-WebSocket-Extensions: permessage-deflate
Sec-WebSocket-Protocol: mqtt
Cache-Control: no-cache
Accept-Language: en-US,en;q=0.9
Origin: capacitor://localhost
User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148
Connection: Upgrade
Accept-Encoding: gzip, deflate
Upgrade: websocket
```

It immediately switches to Websocket protocol. 

```
HTTP/1.1 101 Switching Protocols
Server: nginx/1.14.2
Date: Sat, 06 Nov 2021 02:17:43 GMT
Connection: upgrade
Upgrade: WebSocket
Sec-WebSocket-Accept: aLEJi/WW+zQ1NjZiE5SszGyjI+4=
Sec-WebSocket-Protocol: mqtt

```

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

CVE-2021-31698: Quectel EG25-G devices through 202006130814 allow executing arbitrary code remotely by using an AT command to place shell metacharacters in quectel_handle_fumo_cfg input in atfwd_daemon.<br>
https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-31698
"Code execution as root via AT commands on the Quectel EG25-G modem"
https://nns.ee/blog/2021/04/03/modem-rce.html

While connected to the 45/5g the dog does call home. Here is an example of it calling the Zhexi cloud

```
pi@raspberrypi:~ $ netstat -ap | grep ESTABLISHED | grep 100.100.57.114
(Not all processes could be identified, non-owned process info
 will not be shown, you would have to be root to see it all.)
tcp        0      0 100.100.57.114:53570    124.156.140.55:5670     ESTABLISHED -                   
tcp        0      0 100.100.57.114:52582    124.156.140.55:http     ESTABLISHED -                   
tcp        0      0 100.100.57.114:52578    124.156.140.55:http     ESTABLISHED -                   
tcp        0      0 100.100.57.114:55788    134.175.175.55:9998     ESTABLISHED -                   
```

<p align="center">
<img
src="https://github.com/MAVProxyUser/YushuTechUnitreeGo1/blob/main/zhexi.png"><br>
<img
src="https://github.com/MAVProxyUser/YushuTechUnitreeGo1/blob/main/dns.png"><br>
</p>

You can disbale the tunnel by killing the cloudsail daemon
```
root@raspberrypi:/home/pi/Unitree/autostart# systemctl disable CSClientDaemon
Removed /etc/systemd/system/multi-user.target.wants/CSClientDaemon.service.
```

Also move the auto start "tunnel" out of the way so it is unable to autostart
```
root@raspberrypi:/home/pi/Unitree/autostart# mv tunnel/ /root/tunnel_disabled/

```

# 4G use in the USA

Support provided by Quectel EC25<br>
https://osmocom.org/projects/quectel-modems/wiki/EC25_Linux<br>
Known to be ridden with FOTA backdoors<br>
https://penthertz.com/blog/mobile-iot-modules-FOTA-backdooring-at-scale.html<br>
"All the 4G Modules Could be Hacked" talk from Defcon 2019<br>
https://i.blackhat.com/USA-19/Wednesday/us-19-Shupeng-All-The-4G-Modules-Could-Be-Hacked.pdf

Get a T-Mobile SIM card. 

Edit the config file for the Unitree configNetwork autostart service, at the very least the APN needs to be changed off China Unicom.
```
root@raspberrypi:/home/pi/Unitree/autostart/configNetwork/ppp# grep 3gnet . -r
./quectel-pppd.sh:QL_APN=3gnet
./quectel-chat-connect:# Insert the APN provided by your network operator, default apn is 3gnet
./quectel-chat-connect:OK AT+CGDCONT=1,"IP","3gnet",,0,0
```

You'll need to add the libqmi tools. 

```
root@raspberrypi:/home/pi$ apt-get update
root@raspberrypi:/home/pi$ apt-get install libqmi-utils
```

The mmcli tool will help get basic informaiton that you may need to give your cellular provider such as IMEI, and ESN. You can also make sure the device is not SIM locked. 

```

root@raspberrypi:/home/pi$ mmcli -m 0
  --------------------------------
  General  |            dbus path: /org/freedesktop/ModemManager1/Modem/0
           |            device id: 
  --------------------------------
  Hardware |         manufacturer: QUALCOMM INCORPORATED
           |                model: QUECTEL Mobile Broadband Module
           |             revision: 
           |         h/w revision: 10000
           |            supported: gsm-umts, lte
           |                       cdma-evdo, lte
           |                       lte
           |                       cdma-evdo, gsm-umts, lte
           |              current: cdma-evdo, gsm-umts, lte
           |         equipment id: 
  --------------------------------
  System   |               device: /sys/devices/platform/soc/fe980000.usb/usb1/1-1/1-1.3
           |              drivers: option1, qmi_wwan
           |               plugin: Quectel
           |         primary port: cdc-wdm0
           |                ports: ttyUSB0 (qcdm), ttyUSB2 (at), cdc-wdm0 (qmi), wwan0 (net), 
           |                       ttyUSB3 (at)
  --------------------------------
  Status   |                 lock: sim-pin2
           |       unlock retries: sim-pin (3), sim-pin2 (10), sim-puk (10), sim-puk2 (10)
           |                state: disabled
           |          power state: on
           |       signal quality: 0% (cached)
  --------------------------------
  Modes    |            supported: allowed: 2g; preferred: none
           |                       allowed: 3g; preferred: none
           |                       allowed: 2g, 3g; preferred: 3g
           |                       allowed: 2g, 3g; preferred: 2g
           |                       allowed: 2g, 4g; preferred: 4g
           |                       allowed: 2g, 4g; preferred: 2g
           |                       allowed: 3g, 4g; preferred: 3g
           |                       allowed: 3g, 4g; preferred: 4g
           |                       allowed: 2g, 3g, 4g; preferred: 4g
           |                       allowed: 2g, 3g, 4g; preferred: 3g
           |                       allowed: 2g, 3g, 4g; preferred: 2g
           |              current: allowed: 2g, 3g, 4g; preferred: 4g
  --------------------------------
  Bands    |            supported: egsm, dcs, utran-1, utran-8, eutran-1, eutran-3, eutran-5, 
           |                       eutran-8, eutran-34, eutran-38, eutran-39, eutran-40, eutran-41, 
           |                       cdma-bc0
           |              current: egsm, dcs, utran-1, utran-8, eutran-1, eutran-3, eutran-5, 
           |                       eutran-8, eutran-34, eutran-38, eutran-39, eutran-40, eutran-41, 
           |                       cdma-bc0
  --------------------------------
  IP       |            supported: ipv4, ipv6, ipv4v6
  --------------------------------
  3GPP     |                 imei: 313376969187
  --------------------------------
  3GPP EPS | ue mode of operation: csps-2
  --------------------------------
  CDMA     |                 meid: DEADBEEFCAFEBABE
           |                  esn: BEEFCAFE
           |           activation: not-activated
  --------------------------------
  SIM      |            dbus path: /org/freedesktop/ModemManager1/SIM/0
```

If you need to double check the bearer information you can. 

```
root@raspberrypi:/home/pi$ mmcli -b 0
  --------------------------------
  General            |  dbus path: /org/freedesktop/ModemManager1/Bearer/0
                     |       type: default
  --------------------------------
  Status             |  connected: yes
                     |  suspended: no
                     |  interface: wwan0
                     | ip timeout: 20
  --------------------------------
  Properties         |        apn: fast.t-mobile.com
                     |    roaming: allowed
  --------------------------------
  IPv4 configuration |     method: static
                     |    address: 5.4.3.1
                     |     prefix: 30
                     |    gateway: 5.4.3.2
                     |        dns: 1.1.0.4, 1.1.0.2
                     |        mtu: 1500
  --------------------------------
  Statistics         |   duration: 330
```

You can use qmicli to verify the APN profile setting slots

```
root@raspberrypi:/home/pi$ qmicli -p -d /dev/cdc-wdm0 --wds-get-profile-list=3gpp
Profile list retrieved:
	[1] 3gpp - 
		APN: 'fast.t-mobile.com'
		PDP type: 'ipv4'
		PDP context number: '1'
		Username: ''
		Password: ''
		Auth: 'none'
		No roaming: 'no'
		APN disabled: 'no'
	[2] 3gpp - 
		APN: 'ims'
		PDP type: 'ipv4-or-ipv6'
		PDP context number: '2'
		Username: ''
		Password: ''
		Auth: 'none'
		No roaming: 'no'
		APN disabled: 'no'
	[3] 3gpp - 
		APN: ''
		PDP type: 'ipv4-or-ipv6'
		PDP context number: '3'
		Username: ''
		Password: ''
		Auth: 'none'
		No roaming: 'no'
		APN disabled: 'no'

``` 

Scanning for available networks is a good way to troubleshoot as well 

```
root@raspberrypi:/home/pi$ mmcli -m 0 --3gpp-scan --timeout=300
  ---------------------
  3GPP scan | networks: 312250 - T-Mobile (lte, current)
            |           311490 - 311 490 (lte, available)
            |           311882 - 311 882 (lte, available)
            |           312530 - 312 530 (lte, available)
            |           310120 - Sprint (lte, available)

```

# GPS from 4G module

```
root@raspberrypi:/home/pi$ mmcli -m 0 --location-status
  ------------------------
  Location | capabilities: 3gpp-lac-ci, gps-raw, gps-nmea, cdma-bs, agps
           |      enabled: 3gpp-lac-ci, cdma-bs
           |      signals: no
  ------------------------
  GPS      | refresh rate: 30 seconds
root@raspberrypi:/home/pi$ mmcli -m 0 --location-enable-gps-raw --location-enable-gps-nmea
successfully setup location gathering
root@raspberrypi:/home/pi$ mmcli -m 0 --location-get
  --------------------------
  3GPP |      operator code: XX
       |      operator name: YY
       | location area code: ZZ
       | tracking area code: AA
       |            cell id: 0000000000
  --------------------------
  GPS  |               nmea: $GPGGA,,,,,,0,,,,,,,,*66
       |                     $GPGSA,A,1,,,,,,,,,,,,,,,,*32
       |                     $GPVTG,,T,,M,,N,,K,N*2C
       |                     $GPRMC,,V,,,,,,,,,,N*53
       |                     $GPGSV,1,1,02,00,,,00,00,,,00,1*68 

```

# Wifi backdoor
There is an autoconnect network called "Unitree-2.4G" in the wpa supplicant config. 

```

pi@raspberrypi:/etc $ cat ./wpa_supplicant/wpa_supplicant.conf
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US
 
network={
	ssid="Unitree-5G"
	psk="Unitree#9035"
	key_mgmt=WPA-PSK
	disabled=1
}
 
network={
	ssid="Unitree-WiFi-5G"
	psk="Unitree#9035"
	key_mgmt=WPA-PSK
	disabled=1
}
 
network={
	ssid="Unitree-2.4G"
	psk="Unitree#9035"
	key_mgmt=WPA-PSK
}
```

Supplicant auto starts at boot

```
pi@raspberrypi:/etc $ ps -ax | grep wpa
  470 ?        Ss     0:00 /sbin/wpa_supplicant -u -s -O /run/wpa_supplicant
  756 ?        Ss     0:00 wpa_supplicant -B -c/etc/wpa_supplicant/wpa_supplicant.conf -iwlan0 -Dnl80211,wext
 8444 pts/1    S+     0:00 grep --color=auto wpa
```

If you are quick you can catch it to login to the dog. 

```
$ ping 192.168.1.115
PING 192.168.1.115 (192.168.1.115): 56 data bytes
Request timeout for icmp_seq 0
Request timeout for icmp_seq 1
Request timeout for icmp_seq 2
Request timeout for icmp_seq 3
Request timeout for icmp_seq 4
Request timeout for icmp_seq 5
Request timeout for icmp_seq 6
ping: sendto: No route to host
Request timeout for icmp_seq 7
ping: sendto: Host is down
Request timeout for icmp_seq 8
ping: sendto: Host is down
Request timeout for icmp_seq 9
ping: sendto: Host is down
Request timeout for icmp_seq 10
ping: sendto: Host is down
Request timeout for icmp_seq 11
ping: sendto: Host is down
Request timeout for icmp_seq 12
Request timeout for icmp_seq 13
64 bytes from 192.168.1.115: icmp_seq=14 ttl=64 time=5.955 ms
64 bytes from 192.168.1.115: icmp_seq=15 ttl=64 time=2.563 ms
64 bytes from 192.168.1.115: icmp_seq=16 ttl=64 time=3.939 ms
64 bytes from 192.168.1.115: icmp_seq=17 ttl=64 time=3.791 ms
64 bytes from 192.168.1.115: icmp_seq=18 ttl=64 time=3.299 ms
Request timeout for icmp_seq 19
Request timeout for icmp_seq 20
Request timeout for icmp_seq 21
Request timeout for icmp_seq 22
Request timeout for icmp_seq 23
Request timeout for icmp_seq 24

Roughly 40 seconds into the boot process this is available for literally 5 seconds. 

```

Default credentials work as expected 


```

$ ssh -o StrictHostKeyChecking=accept-new -v pi@192.168.1.115 "hostname;id;exit"
OpenSSH_8.6p1, LibreSSL 3.3.6
...
debug1: Connecting to 192.168.1.115 [192.168.1.115] port 22.
debug1: Connection established.
...
debug1: Local version string SSH-2.0-OpenSSH_8.6
debug1: Remote protocol version 2.0, remote software version OpenSSH_7.9p1 Debian-10+deb10u2+rpt1
debug1: compat_banner: match: OpenSSH_7.9p1 Debian-10+deb10u2+rpt1 pat OpenSSH* compat 0x04000000
debug1: Authenticating to 192.168.1.115:22 as 'pi'
...
debug1: Next authentication method: password
pi@192.168.1.115's password: 
debug1: Authentication succeeded (password).
Authenticated to 192.168.1.115 ([192.168.1.115]:22).
...
debug1: Sending command: hostname;id;exit
...
raspberrypi
uid=1000(pi) gid=1000(pi) groups=1000(pi),4(adm),20(dialout),24(cdrom),27(sudo),29(audio),44(video),46(plugdev),60(games),100(users),105(input),109(netdev),997(gpio),998(i2c),999(spi)
debug1: client_input_channel_req: channel 0 rtype exit-status reply 0
debug1: client_input_channel_req: channel 0 rtype eow@openssh.com reply 0
debug1: channel 0: free: client-session, nchannels 1
Transferred: sent 2992, received 2892 bytes, in 0.1 seconds
Bytes per second: sent 27756.4, received 26828.7
debug1: Exit status 0

```

# Autostart items

The default uses GNOME autostart<br>
/home/pi/.config/autostart/*

```
pi@raspberrypi:~ $ cat /home/pi/.config/autostart/unitree.desktop 
[Desktop Entry]
Name=unitree
Comment=unitree autostart
Exec=bash /home/pi/UnitreeUpgrade/start.sh
Terminal=false
Type=Application
Categories=System;Utility;Archiving;
StartupNotify=false
NoDisplay=true

pi@raspberrypi:~ $ cat /home/pi/UnitreeUpgrade/start.sh
#!/bin/bash
cd /home/pi/UnitreeUpgrade
python3 ./startup_manager.py  &
python3 ./startup_uploader.py &

cd /home/pi/Unitree/autostart
./update.sh 
```

# PDB emergency shut off (backdoor? no way to disable)

"Under the developer mode, if the robot is out of control, you can cut off the power of the built-in PDB"<br>

<p align="center">
<img src="https://github.com/MAVProxyUser/YushuTechUnitreeGo1/blob/main/PDB.jpg">
<img src="https://github.com/MAVProxyUser/YushuTechUnitreeGo1/blob/main/remote.png">
<img src="https://github.com/MAVProxyUser/YushuTechUnitreeGo1/blob/main/frame.jpg">
<img src="https://github.com/MAVProxyUser/YushuTechUnitreeGo1/blob/main/warn.jpg">
</p>
<br>

https://www.youtube.com/watch?v=gDnDbuFLjys

# What talks to the STM at 192.168.123.10?

Two apps:
/Unitree/autostart/sportMode/bin/Legged_sport
/Unitree/autostart/appTransit/build/appTransit

```
root@raspberrypi:/home/pi# netstat -ap | grep 192.168.123.10
...
udp     5504      0 192.168.123.161:8008    192.168.123.10:8007     ESTABLISHED 1460/./bin/Legged_s 
udp        0      0 192.168.123.161:8093    192.168.123.10:8007     ESTABLISHED 1752/./build/appTra 

root@raspberrypi:/home/pi# fuser -n udp 8008
8008/udp:             1460
root@raspberrypi:/home/pi# fuser -n udp 8093
8093/udp:             1752
root@raspberrypi:/home/pi# ps -ax | grep 1460 
 1460 ?        SLl    3:08 ./bin/Legged_sport
root@raspberrypi:/home/pi# ps -ax | grep 1752
 1752 ?        Sl     0:02 ./build/appTransit

```

Look familiar? 

https://github.com/unitreerobotics/unitree_legged_sdk/blob/master/include/unitree_legged_sdk/udp.h#L32

```
constexpr int UDP_CLIENT_PORT = 8080;                       // local port
constexpr int UDP_SERVER_PORT = 8007;                       // target port
constexpr char UDP_SERVER_IP_BASIC[] = "192.168.123.10";    // target IP address
constexpr char UDP_SERVER_IP_SPORT[] = "192.168.123.161";   // target IP address
```

# MIT Cheetah code

printf("[Backflip DataReader] Setup for mini cheetah\n");<br>
printf("[Cheetah Test] Test initialization is done\n");<br>

https://github.com/search?q=org%3Amit-biomimetics+%22Cheetah+Test%22&type=code
https://github.com/search?q=org%3Amit-biomimetics+%22Setup+for+mini+cheetah%22&type=code

This code is MIT license. 
https://github.com/mit-biomimetics/Cheetah-Software/blob/master/LICENSE

# Sniffing MQTT traffic on the dog 

Install mosquitto-clients

```
pi@raspberrypi:~ $ sudo apt-get install mosquitto-clients
pi@raspberrypi:~ $ mosquitto_sub -v -t "#"
usys/run ok
usys/uuid xxx-xxx-xxx-xxx-xxx
usys/version/app 1.38.0
usys/version/nano3 
updateDependencies:1.0.1;ipconfig:1.0.0;gencamparams:1.0.0;camerarosnode:1.0.0;03persontrack:2.1.0;imageai:1.0.2;faceLightServer:1.0.1;slamDetector:1.0.0;wsaudio:1.0.0;faceLightMqtt:1.0.0
usys/version/raspi 
updateDependencies:1.0.1;roscore:1.0.0;configNetwork:1.0.0;sportMode:1.38.0;triggerSport:1.5.0;webMonitor:1.4.0;appTransit:1.5.0;07obstacle:1.1.0;utrack:3.9.4;programming:1.0.0;tunnel:1.0.0
usys/version/nano2 
updateDependencies:1.0.1;ipconfig:1.0.0;gencamparams:1.0.0;camerarosnode:1.0.0;03persontrack:2.1.0;imageai:1.0.2;faceLightServer:1.0.1;slamDetector:1.0.0;wsaudio:1.0.0;faceLightMqtt:1.0.0
usys/version/nano1 
updateDependencies:1.0.1;ipconfig:1.0.0;gencamparams:1.0.0;camerarosnode:1.0.0;03persontrack:2.1.0;imageai:1.0.2;faceLightServer:1.0.1;slamDetector:1.0.0;wsaudio:1.0.0;faceLightMqtt:1.0.0
controller/run ok
programming/run on
programming/current_action stop
robot/state ??.??.????.??.??aH?lR??'<M?1??>??>$???#?9?E?:C???
robot/state ??.??.????.??.??aH?lR??'<M?1??>??>$???#?9?E?:C???
robot/state ??.??.????.??.??aH?lR??'<M?1??>??>$???#?9?E?:C???
bms/state 
firmware/version 	%%!$$!$#"$$!$FA
controller/current_action (null)

```

You can also sniff the stick movements. 
```
mosquitto_sub  -h 192.168.12.1 -t "controller/stick" 
```

# Sending MQTT commands to the dog. 

You can send these MQTT commands to control the bot always

```
mosquitto_pub -h 192.168.12.1 -d -t "controller/action" -m "standUp"
mosquitto_pub -h 192.168.12.1 -d -t "controller/action" -m "standDown"
mosquitto_pub -h 192.168.12.1 -d -t "controller/action" -m "run"
mosquitto_pub -h 192.168.12.1 -d -t "controller/action" -m "walk"
mosquitto_pub -h 192.168.12.1 -d -t "controller/action" -m "climb"
```

You must be in SDK mode 2 to send these (L1+L2 & start)
```
mosquitto_pub -h 192.168.12.1 -d -t "controller/action" -m "dance1"
mosquitto_pub -h 192.168.12.1 -d -t "controller/action" -m "dance2"
mosquitto_pub -h 192.168.12.1 -d -t "controller/action" -m "jumpYaw"
mosquitto_pub -h 192.168.12.1 -d -t "controller/action" -m "straightHand1"
```

These commands seem to be somehow black listed on the go1
```
mosquitto_pub -h 192.168.12.1 -d -t "controller/action" -m "backflip"
mosquitto_pub -h 192.168.12.1 -d -t "controller/action" -m "dance3
mosquitto_pub -h 192.168.12.1 -d -t "controller/action" -m "dance4
```

These commands control the stick movement
```
mosquitto_pub -h 192.168.12.1 -d -t "controller/stick" -m <unknown at this time>
```

# TFTP to RTOS

The STM RTOS has tftp enabled for updates. 
./autostart/updateDependencies/update_firmware.py:    atftp = "sleep 5; atftp -p -l " + sys.argv[1] + " 192.168.123.10 --tftp-timeout 10;"


It is assumed to be a variants of IAP over tftp per ST spec
https://www.st.com/resource/en/application_note/an3376-stm32f2x7-inapplication-programming-iap-over-ethernet-stmicroelectronics.pdf

If you tftp to 192.168.161.10, the bot will immediately drop. 

```
pi@raspberrypi:~ $ atftp -g -r "*.bin" 192.168.123.10 69 --trace  --verbose
Trace mode on.
Verbose mode on.
sent RRQ <file: *.bin, mode: octet <>>
received DATA <block: 1, size: 0>
sent ACK <block: 1>
```

# Troubleshooting

If you accidentally delete /etc/hosts, or remove the "localhost" entry, the dog will not stand. 

```
pi@raspberrypi:~ $ journalctl -u nginx.service
-- Reboot --
Jul 11 11:26:56 raspberrypi systemd[1]: Starting A high performance web server and a reverse proxy server...
Jul 11 11:26:58 raspberrypi nginx[676]: nginx: [emerg] host not found in upstream "localhost" in /etc/nginx/sites-enabled/default:11
Jul 11 11:26:58 raspberrypi nginx[676]: nginx: configuration file /etc/nginx/nginx.conf test failed
Jul 11 11:26:58 raspberrypi systemd[1]: nginx.service: Control process exited, code=exited, status=1/FAILURE
Jul 11 11:26:58 raspberrypi systemd[1]: nginx.service: Failed with result 'exit-code'.
Jul 11 11:26:58 raspberrypi systemd[1]: Failed to start A high performance web server and a reverse proxy server.
-- Reboot --
```

General errors can be found in  /home/pi/.cache/lxsession/LXDE-pi/run.log and /home/pi/.ros/log

You can check the status of the system services for degraded stats with 

```
root@raspberrypi:/home/pi# systemctl status
● raspberrypi
    State: degraded
     Jobs: 0 queued
   Failed: 1 units
...

root@raspberrypi:/home/pi# systemctl 
  UNIT                                                                                                LOAD   ACTIVE SUB       DESCRIPTION               
...
● nginx.service                                                                                       loaded failed failed    A high performance web server and a 
reverse proxy server                              
...
pi@raspberrypi:~ $ systemctl list-units --failed
  UNIT          LOAD   ACTIVE SUB    DESCRIPTION                                             
● nginx.service loaded failed failed A high performance web server and a reverse proxy server

```
