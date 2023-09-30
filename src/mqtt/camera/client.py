
import paho.mqtt.client as  mqtt_client
import paho.mqtt.publish as mqtt_pub
import paho.mqtt.subscribe as mqtt_sub
import threading
from mqtt_config import MQTTBase, CameraTopics, formatter,CameraCmd
import base64
from collections import deque
import asyncio
CAMERA_DATA_STORE= {"roi" : {},"info" : {},"ctrlv" : {},"frame" : deque([],maxlen = 10)}

class MQTTCameraClient(MQTTBase):
    def __init__(self):
        super().__init__()
        self.store = {}

    def on_message(self, mqttc, obj, msg):
        asyncio.sleep(0.1)
        print(f"Received `{len(msg.payload.decode())}` from `{msg.topic}` topic")
        msg = json.loads(msg.payload.decode())
        data = json.loads(msg["data"])
        camera_idx = msg["camera_idx"]
        cmd_idx = int(msg["cmd_idx"])
        #print(msg)

        match cmd_idx:
            case CameraCmd.Init.value:
                print("Init ")
                num = int(data["num_device"])
                for i in range(num):
                    self.store[str(i)] = CAMERA_DATA_STORE.copy()

            case CameraCmd.GetInfo.value:
                self.store[camera_idx]["info"] = data
        
            case CameraCmd.GetRoi.value:
                self.store[camera_idx]["roi"] = data
        
            case CameraCmd.GetCtrlVal.value:
                self.store[camera_idx]["ctrlv"] = data
        
            case CameraCmd.StartCapture.value:
                self.store[camera_idx]["frame"].append(data["frame"])
   
            case CameraCmd.StopCapture.value:
                print("StopCapture")
                return

            case CameraCmd.SetRoi.value:
                return
            case CameraCmd.SetCtrlVal.value:
                print("SetCtrlVal")
                return
            case CameraCmd.GetStatus.value:
                print("GetStatus")
                return
            case _:
                print("Invalid command")
                return

    def publish_instruction(self, camera_idx, cmd_idx, data):
        json_msg = formatter(camera_idx, cmd_idx, data)
        self.publish_single(CameraTopics.Instr.value, json_msg)
        #print("store : " ,mqttc.store)

import time

import numpy as np
import json
mqttc = MQTTCameraClient()

mqttc.start_subscribe(CameraTopics.Responce.value)

mqttc.loop_start()  
b = False
idx= 0
msg = {"camera_idx":-1,
                    "cmd_idx" : -1,
                    "data" : {}}
s = time.time()
while  mqttc.store == {}:
    time.sleep(0.1)
    mqttc.publish_single( CameraTopics.Init.value, json.dumps(msg))
e = time.time()
print(e-s)


msg = {"camera_idx":0,
                    "cmd_idx" : CameraCmd.SetCtrlVal.value,
                    "data" : {"ctrl_type":"1","value":"4000000","is_auto":"0"}}
mqttc.publish_single( CameraTopics.Instr.value, json.dumps(msg))

time.sleep(0.1)
msg = {"camera_idx":1,
                    "cmd_idx" : CameraCmd.StartCapture.value,
                    "data" : {}}

mqttc.publish_single( CameraTopics.Instr.value, json.dumps(msg))
time.sleep(3)
msg = {"camera_idx":0,
                    "cmd_idx" : CameraCmd.SetRoi.value,
                    "data" : {"startx":"0","starty":"0","width":"640","height":"480","bin":"1","img_type": "0"}}
mqttc.publish_single( CameraTopics.Instr.value, json.dumps(msg))

msg = {"camera_idx":0,
                    "cmd_idx" : CameraCmd.GetRoi.value,
                    "data" : {}}
mqttc.publish_single( CameraTopics.Instr.value, json.dumps(msg))
time.sleep(4)
msg = {"camera_idx":1,
                "cmd_idx" : CameraCmd.StopCapture.value,
                    "data" : {}}
mqttc.publish_single( CameraTopics.Instr.value, json.dumps(msg))

print("=====================================")
print(mqttc.store)
while 1:
    time.sleep(1)