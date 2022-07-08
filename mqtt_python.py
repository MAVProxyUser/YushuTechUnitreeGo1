#!/usr/bin/python

import sys
import paho.mqtt.client as mqtt

mqttc = mqtt.Client(transport='websockets')   

#mqttc.connect("192.168.123.161", 9801, 60)
#mqttc.connect("192.168.123.161", 80, 60)
#mqttc.connect("192.168.12.1", 9801, 60)
mqttc.connect("192.168.12.1", 80, 60)

mqttc.publish("programming/code", "import os; os.system('touch /tmp/uhhh')");
mqttc.publish("programming/action", "start");

