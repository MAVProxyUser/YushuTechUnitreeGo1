#coding=utf-8  
import hashlib  
import sys
import paho.mqtt.client as mqtt #import the client1
import time
import os
import subprocess
import struct

receivedBytes = 0
md5ok = False
fileSize = -1

def on_connect(client,userdata,flags,rc):
    client.subscribe("firmware/upgrade/progress")
    client.subscribe("firmware/upgrade/md5ok")
def on_message(client, userdata, msg):
    if(msg.topic == "firmware/upgrade/progress"):
        global receivedBytes
        receivedBytes = int.from_bytes(msg.payload, byteorder='little')
    if(msg.topic == "firmware/upgrade/progress"):
        global md5ok
        md5ok = int.from_bytes(msg.payload, byteorder='little') > 0

def mqtt_print(msg):
    client.publish("usys/info", msg)
    client.loop()


broker_address="localhost"
client = mqtt.Client("firmware_upgrade") 
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_address)

client.publish("firmware/upgrade/trigger", "start")
client.loop()

md5result = ""
continueUpdate = False

if len(sys.argv) == 2:  
    try :
        fileSize = os.path.getsize(sys.argv[1])
        mqtt_print("File Size: " + str(fileSize) + "\n")
        md5hex = hashlib.md5(open(sys.argv[1],'rb').read()).hexdigest()
        mqtt_print("MD5: " + str(md5hex) + "\n")
        md5result = bytes.fromhex(md5hex)
        continueUpdate = True
    except :
        mqtt_print("\033[0;31m\033[1m...Error: Incorrect File\033[0m\n")
else:  
    mqtt_print("\033[0;31m\033[1m...Error: Incorrect File\033[0m\n")


if continueUpdate: 
    client.publish("firmware/upgrade/md5", md5result)
    client.publish("firmware/upgrade/size", struct.pack('i',int(fileSize)), 1,True)
    client.loop()
    atftp = "sleep 5; atftp -p -l " + sys.argv[1] + " 192.168.123.10 --tftp-timeout 10;"
    mqtt_print("\033[0;32m\033[1m...Sending data using atftp\033[0m\n")
    subprocess.call(atftp, shell=True)
    w = 0
    while w<30:
        time.sleep(1)
        w=w+1
        if w%5 == 0:
            mqtt_print("...Please wait...\n")
        else: 
            client.loop()
        if receivedBytes == fileSize: 
            break
    mqtt_print("...Received Bytes:" + str(receivedBytes) + " | File Size:" + str(fileSize) + "\n")

    if receivedBytes != fileSize:
        mqtt_print("\033[0;31m\033[1m...Error: Atftp Transfer Error\033[0m\n")
        continueUpdate = False

if continueUpdate: 
    if not md5ok:
        mqtt_print("\033[0;31m\033[1m...Error: md5 Error\033[0m\n")
        continueUpdate = False

if continueUpdate: 
    mqtt_print("\033[0;32m\033[1m# Firmware Update Success\n")
    client.publish("usys/updating", '', 1,True)
    client.loop()
    time.sleep(2)
    mqtt_print("\033[0;32m\033[1m# Please restart your robot\n")
    subprocess.call("rm -rf ../temp", shell=True)
else:
    mqtt_print("\033[0;31m\033[1m# Firmware Update Failed\n")


