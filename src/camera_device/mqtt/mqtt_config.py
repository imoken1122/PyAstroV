from enum import Enum
import paho.mqtt.client as  mqtt_client
import paho.mqtt.publish as mqtt_pub
import paho.mqtt.subscribe as mqtt_sub
from abc import ABC, abstractmethod
import json
#BROKER= 'broker.emqx.io'
BROKER= 'localhost'
PORT = 1883
CLIENT_ID = "camera_device"


def formatter(camera_idx, cmd, contents):
    msg = {
        "camera_idx" : camera_idx,
        "cmd" : cmd,
        "contents" : contents
    }
    return json.dumps(msg)

class CameraTopics(Enum):
    Instr="camera/instr"
    Responce="camera/responce"


class CameraCmd(Enum):
    GetInfo = "getinfo"
    GetProps = "getprops"
    GetStatus = "getstatus"
    GetRoi = "getroi"
    SetRoi = "setroi"
    GetCtrlVal = "getctrlval"
    SetCtrlVal = "setctrlval"
    StartCapture = "startcap"
    StopCapture = "stopcap"





class MQTTBase(mqtt_client.Client,ABC):
    def __init__(self,):
        super().__init__()
        self.topics_buf = {topic.name: topic.value for topic in CameraTopics}
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

    def __del__(self) -> None:
        return super().__del__()

    @abstractmethod
    def on_message(self, mqttc, obj, msg):
        pass
