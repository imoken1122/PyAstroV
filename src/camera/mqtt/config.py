from enum import Enum
import asyncio
import paho.mqtt.client as  mqtt_client
import paho.mqtt.publish as mqtt_pub
import paho.mqtt.subscribe as mqtt_sub
from abc import ABC, abstractmethod
from ..logger import setup_logger
import threading

logger = setup_logger("mqtt-client")
BROKER= 'localhost'
PORT = 1883
CLIENT_ID = "mqtt-camera-client"

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
        self.wait_responces = set()

    async def wait(self,transaction_id:str ):

        while True:
            if transaction_id not in self.wait_responces: break
            await asyncio.sleep(0.1)

    def on_connect(self, mqttc, obj, flags, rc):
        if rc == 0 : 
            logger.info("Connected to MQTT Broker!")
        else:
            logger.error("Failed to connect, return code %d\n", rc)
    def on_disconnect(client, userdata, rc):
        if rc != 0:
            logger.error("Unexpected disconnection.")

    def start_subscribe(self,topic:str):
        self.subscribe(topic, 0)
        #self.loop_forever()
        rc = 0
        return rc 

    async def publish_single(self,transaction_id:str, topic, msg):
        logger.info(f"Publish to topic : {topic}, msg : {msg}")
        mqtt_pub.single(topic, msg, hostname=BROKER)




    @abstractmethod
    def on_message(self, mqttc, obj, msg):
        pass
