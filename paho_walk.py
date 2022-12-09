import paho.mqtt.client as mqtt
from random import randrange, uniform
import time
import struct
mqttBroker ="192.168.12.1"

client = mqtt.Client("Stick Data out")
client.connect(mqttBroker)
client.loop_start()


#client.publish("/controller/stick", struct.pack('ffff', 1,0,0,0))
client.publish("/controller/run", "ok")
client.publish("/controller/action", "standDown")
