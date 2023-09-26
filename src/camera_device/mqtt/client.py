
import paho.mqtt.client as  mqtt_client
import paho.mqtt.publish as mqtt_pub
import paho.mqtt.subscribe as mqtt_sub
import threading
import base64
from mqtt_config import MQTTBase, CameraTopics, formatter,CameraCmd

class MQTTCameraClient(MQTTBase):
    def on_message(self, mqttc, obj, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        msg = json.loads(msg.payload.decode())
        print("camera_idx: ", msg["camera_idx"])

import time

import numpy as np
import json
mqttc = MQTTCameraClient()
print(CameraTopics.Responce.value)
mqttc.start_subscribe(CameraTopics.Responce.value)
mqttc.loop_start()
b = False
idx= 0
time.sleep(0.01)
"""
msg = {"camera_idx":0,
                    "cmd" : CameraCmd.StartCapture.value,
                    "contents" : json.dumps({"startx":0,"starty":0,"width":640,"height":480,"bin":1,"img_type": json.dumps(ControlType.RAW8.name) })}
mqttc.publish_single( CameraTopics.Instr.value, json.dumps(msg))
msg = {"camera_idx":1,
                    "cmd" : CameraCmd.StartCapture.value,
                    "contents" : json.dumps({"startx":0,"starty":0,"width":640,"height":480,"bin":1,"img_type":"RAW8" })}
mqttc.publish_single( CameraTopics.Instr.value, json.dumps(msg))

time.sleep(10)
"""
msg = {"camera_idx":1,
                    "cmd" : CameraCmd.SetRoi.value,
                    "contents" : json.dumps({"startx":0,"starty":0,"width":640,"height":480,"bin":1,"img_type":"RAW8" })}
mqttc.publish_single( CameraTopics.Instr.value, json.dumps(msg))

msg = {"camera_idx":1,
                    "cmd" : CameraCmd.GetRoi.value,
                    "contents" : json.dumps({"startx":0,"starty":0,"width":640,"height":480,"bin":1,"img_type":"RAW8" })}
mqttc.publish_single( CameraTopics.Instr.value, json.dumps(msg))
time.sleep(10)
print("stop")
msg = {"camera_idx":0,
                "cmd" : CameraCmd.StopCapture.value,
                    "contents" : json.dumps({})}
mqttc.publish_single( CameraTopics.Instr.value, json.dumps(msg))
time.sleep(1)
msg = {"camera_idx":1,
                "cmd" : CameraCmd.StopCapture.value,
                    "contents" : json.dumps({})}
mqttc.publish_single( CameraTopics.Instr.value, json.dumps(msg))

while 1:
    time.sleep(1)