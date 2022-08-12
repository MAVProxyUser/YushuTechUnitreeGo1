import paho.mqtt.client as mqtt
import time

def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))

def on_message(mqttc, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid))
    pass

def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mqttc, obj, level, string):
    print(string)

mqttc = mqtt.Client()
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe

mqttc.on_log = on_log

mqttc.connect("192.168.12.1", 1883, 60)

mqttc.loop_start()

infot = mqttc.publish("controller/action", "standDown", qos=2)
infot.wait_for_publish()
time.sleep(2)
infot = mqttc.publish("controller/action", "standUp", qos=2)
infot.wait_for_publish()
time.sleep(2)
infot = mqttc.publish("controller/action", "recoverStand", qos=2)
infot.wait_for_publish()
time.sleep(2)
infot = mqttc.publish("controller/action", "walk", qos=2)
infot.wait_for_publish()
time.sleep(2)
infot = mqttc.publish("controller/stick", "\xac\x4a\x3a\x3e\x00\x00\x00\x00\x00\x00\x00\x00\x2e\x64\x42\x3e", qos=2)
infot.wait_for_publish()
time.sleep(1)
infot = mqttc.publish("controller/stick", "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00x00", qos=2)
infot.wait_for_publish()

