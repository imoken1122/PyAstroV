
import paho.mqtt.client as mqtt_client
import paho.mqtt.publish as mqtt_pub
import paho.mqtt.subscribe as mqtt_sub
import threading
from .config import MQTTBase, CameraTopics, CameraCmd
import base64
import json
import cv2
from collections import deque
import asyncio
from pyastrov.logger import setup_logger
import hashlib
import threading
from datetime import datetime
# get file name
logger = setup_logger("mqtt-client")


CAMERA_DATA_STORE = {"roi": {}, "info": {},
                     "ctrlv": {}, "frames": deque([], maxlen=10)}


class MQTTCameraClient(MQTTBase):
    def __init__(self):
        super().__init__()
        self.store = {}
        self.num_camera = 0
        self.lock = threading.Lock()

    def formatter(self, transaction_id: str, camera_idx: int, cmd_idx: int, data: dict):
        msg = {
            # generate unique transaction id by hash and max length 100
            "transaction_id": transaction_id,
            "camera_idx": camera_idx,
            "cmd_idx": cmd_idx,
            "data": data
        }
        return json.dumps(msg)

    async def init(self):

        logger.info("MQTTCameraClient initializing...")
        # start subscribe mqtt camera server responce topic
        self.start_subscribe(CameraTopics.Responce.value)
        # run mqtt client loop
        self.loop_start()

        self.store = {}
        logger.info("Waiting for camera server connection...")
        # publish init instruction, This instruction connects or reconnects the camera to the mqtt server side.
        await self.publish_instruction(-1, -1, {}, CameraTopics.Init.value)
        await asyncio.sleep(3)

        

        self.num_camera = len(self.store.keys())
        # get camera info and roi
        for i in range(len(self.store.keys())):
            await self.publish_instruction(i, CameraCmd.GetInfo.value, {}, )
            await asyncio.sleep(0.1)
            await self.publish_instruction(i, CameraCmd.GetRoi.value, {}, )
        for i in range(len(self.store.keys())):
            # logged connected camera info
            logger.info(f"Connected camera {i} : {self.store[i]['info']}")

    def on_message(self, mqttc, obj, msg):
        msg = json.loads(msg.payload.decode())
        try:
            data = json.loads(msg["data"])
        except:
            logger.error(f"Failed to decode body data :  {data}")
            return
        camera_idx = int(msg["camera_idx"])
        cmd_idx = int(msg["cmd_idx"])
        # print(msg)
        logger.info(f"CameraIdx : {camera_idx} ")
        logger.info(f"CameraCmd : {CameraCmd(cmd_idx)} ")

        match cmd_idx:
            case CameraCmd.Init.value:
                num = int(data["num_device"])
                for i in range(num):
                    self.store[i] = CAMERA_DATA_STORE.copy()

            case CameraCmd.GetInfo.value:
                self.store[camera_idx]["info"] = data

            case CameraCmd.GetRoi.value:
                self.lock.acquire()
                self.store[camera_idx]["roi"] = data
                self.lock.release()

            case CameraCmd.SetRoi.value:
                self.lock.acquire()
                self.store[camera_idx]["roi"] = data
                self.lock.release()

            case CameraCmd.GetCtrlVal.value:
                ctrl_type = int(data["ctrl_type"])
                self.store[camera_idx]["ctrlv"][ctrl_type] = int(data["value"])

            case CameraCmd.StartCapture.value:
                if data == {}:
                    self.store[camera_idx]["frames"].clear()
                    return
                logger.info(f"Capturing now camera_idx : {camera_idx} ....")
                self.lock.acquire()
                self.store[camera_idx]["frames"].append(data["frame"])
                self.lock.release()
                # The design does not push StartCapture command transaction_id to wait_responce, so it returns early
                return

            case CameraCmd.StopCapture.value:
                logger.info(f"Stop capturing camera_idx : {camera_idx}")
                self.lock.acquire()
                self.store[camera_idx]["frames"].clear()
                self.lock.release()

            case CameraCmd.SetCtrlVal.value:
                ctrl_type = int(data["ctrl_type"])
                self.store[camera_idx]["ctrlv"][ctrl_type] = int(data["value"])

            case CameraCmd.GetStatus.value:
                pass
            case CameraCmd.AdjustWB.value:
                pass
            case _:
                logger.error("Invalid command")

        self.wait_responces.remove(msg["transaction_id"])

    async def publish_instruction(self, camera_idx: int, cmd_idx: int, data: dict, topic: str = CameraTopics.Instr.value):
        transaction_id = hashlib.sha256(
            str(datetime.now()).encode()).hexdigest()[:100]
        json_msg = self.formatter(transaction_id, camera_idx, cmd_idx, data)
        await self.publish_single(transaction_id, topic, json_msg)

        # if CmaeraCmd.StartCapture.value then not wait responce
        if cmd_idx == CameraCmd.StartCapture.value:
            return
        # add transaction_id to wait_responces
        # wait until responce
        self.wait_responces.add(transaction_id)
        await self.wait(transaction_id)


async def test_mqttc():

    mqttc = MQTTCameraClient()

    await mqttc.init()

    while True:
        cmd = input("cmd : ")
        match cmd:
            case 'q': break
            case 'init':
                data = {}
                await mqttc.publish_instruction(-1, CameraCmd.Init.value, data, CameraTopics.Init.value)
            case'sc':
                data = {"ctrl_type": "1", "value": "4000000", "is_auto": "0"}
                await mqttc.publish_instruction(1, CameraCmd.SetCtrlVal.value, data)
            case 'gc':
                data = {"ctrl_type": "1"}
                await mqttc.publish_instruction(1, CameraCmd.GetCtrlVal.value, data)
            case 'si':
                data = {}
                await mqttc.publish_instruction(1, CameraCmd.GetInfo.value, data)
            case 'sr':
                data = {"startx": "0", "starty": "0", "width": "1912",
                        "height": "1304", "bin": "1", "img_type": "0"}
                await mqttc.publish_instruction(1, CameraCmd.SetRoi.value, data)
            case 'gf':
                data = {}
                await mqttc.publish_instruction(1, CameraCmd.StartCapture.value, data)
            case 'sf':
                data = {}
                await mqttc.publish_instruction(1, CameraCmd.StopCapture.value, data)

        await asyncio.sleep(0.1)
        logger.info(mqttc.store[1])
if __name__ == "__main__":
    asyncio.run(test_mqttc())
    #
