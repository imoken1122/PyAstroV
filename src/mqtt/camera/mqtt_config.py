from enum import Enum
import paho.mqtt.client as  mqtt_client
import paho.mqtt.publish as mqtt_pub
import paho.mqtt.subscribe as mqtt_sub
from abc import ABC, abstractmethod
import json
from queue import Queue
#BROKER= 'broker.emqx.io'
BROKER= 'localhost'
PORT = 1883
CLIENT_ID = "mqtt-camera-client"

def formatter(camera_idx, cmd_idx, contents):
    msg = {
        "camera_idx" : camera_idx,
        "cmd_idx" : cmd_idx,
        "data" : contents
    }
    return json.dumps(msg)

class CameraTopics(Enum):
    Instr="camera/instr"
    Responce="camera/responce"
    Init="camera/init"


class CameraCmd(Enum):
    GetInfo =0 
    GetStatus = 1
    GetRoi = 2
    GetCtrlVal = 3
    SetRoi = 4
    SetCtrlVal = 5
    StartCapture = 6
    StopCapture = 7
    Init = 8
    NotImplemented = -1 



class MQTTBase(mqtt_client.Client,ABC):
    def __init__(self,):
        super().__init__()
        self.connect(BROKER, PORT, 60)

    def on_connect(self, mqttc, obj, flags, rc):
        if rc == 0 : 
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)


    def start_subscribe(self,topic:str):
        self.subscribe(topic, 0)
        #self.loop_forever()
        rc = 0
        return rc 

    def publish_single(self, topic, msg):
        
        mqtt_pub.single(topic, msg, hostname=BROKER)
        #res = self.publish(topic, msg, 0, False,)
    def on_log(mqttc, obj, level, string):
        print(string)


    @abstractmethod
    def on_message(self, mqttc, obj, msg):
        pass
