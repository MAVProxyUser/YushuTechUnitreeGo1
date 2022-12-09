import paho.mqtt.client as mqtt
import binascii
import struct

def on_connect(client, userdata, flags, rc):
    print("Connected with result code {0}".format(str(rc)))
#    client.subscribe("controller/stick")
    client.subscribe("#")

def on_message(client, userdata, msg):
#    [lx,rx,ry,ly] = struct.unpack('ffff', msg.payload)
#    print("Message received-> " + msg.topic + " " + str([lx,rx,ry,ly]))
    print("Message received-> " + msg.topic + " " + str(binascii.hexlify(msg.payload)) )

client = mqtt.Client("Stick Data")
client.on_connect = on_connect
client.on_message = on_message
client.connect("192.168.12.1", 1883, 60)
client.loop_forever()
