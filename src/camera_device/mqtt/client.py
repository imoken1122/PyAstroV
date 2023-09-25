
import paho.mqtt.client as  mqtt_client
import paho.mqtt.publish as mqtt_pub
import paho.mqtt.subscribe as mqtt_sub

import threading
import base64
from mqtt_config import MQTTCameraBase

class MQTTCameraClient(MQTTCameraBase):
    def on_message(self, mqttc, obj, msg):
        print(f"Received `{len(msg.payload.decode())}` from `{msg.topic}` topic")

import time

import numpy as np
import json
mqttc = CameraMQTT()
mqttc.sub_stream("testTopic2")
mqttc.loop_start()

d = {"value":10000}
while 1 : 
    time.sleep(3)
    print(mqttc.rcv_data[:10])
    mqttc.pub_single( "set_value", json.dumps(d))
    print("hello ==============")