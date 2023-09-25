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


def formatter(camera_idx, method, contents):
    msg = {
        "camera_idx" : camera_idx,
        "method" : method,
        "contents" : contents
    }
    return json.dumps(msg)

class CameraTopics(Enum):
    Roi = "camera/roi"
    Control = "camera/ctrl"
    Capture = "camera/capture"
    Info = "camera/info"
    Status = "camera/status"
    Props = "camera/props"

class Method(Enum):
    Get = 0
    Set = 1

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


    def continue_sub(self,topic):
        self.subscribe(topic, 0)
        self.loop_start()
        rc = 0
        return rc 

    def pub_single(self, topic, msg):
        
        mqtt_pub.single(topic, msg, hostname=BROKER)
        #res = self.publish(topic, msg, 0, False,)
    def on_log(mqttc, obj, level, string):
        print(string)

    def __del__(self) -> None:
        return super().__del__()

    @abstractmethod
    def on_message(self, mqttc, obj, msg):
        pass
