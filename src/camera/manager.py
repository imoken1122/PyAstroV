
import base64
from dataclasses import asdict
from mqtt.camera_cli.interface import ControlType, ImgType, ROIFormat
from camera.mqtt.client import MQTTCameraClient
from camera.mqtt.config import CameraCmd, CameraTopics
import asyncio
from .logger import setup_logger

logger = setup_logger()

class CameraManager : 
    frame_buffer = []
    conected_camera : list[str]=[]
    devices = []
    is_captures = []
    def __init__ (self, mqttc):
        self.conected_camera=[]
        self.is_captures = []
        self.mqttc = mqttc

    def init_client(self):
        self.mqttc.init()

    def get_num_camera(self):
        return self.mqttc.num_camera
    def get_info_i(self,idx : int) -> dict:
        if self.mqttc.num_camera <= idx:
            logger.error(f"camera idx {idx} out of range")
            return None
        return self.mqttc.store[str(idx)]["info"]

    def get_roi_i(self,idx : int) -> dict:
        if self.mqttc.num_camera <= idx:
            logger.error(f"camera idx {idx} out of range")
            return None
        return self.mqttc.store[str(idx)]["roi"]

    def set_roi_i(self,idx : int,  data : dict):
        if self.mqttc.num_camera <= idx:
            logger.error(f"camera idx {idx} out of range")
            return None
        self.mqttc.publish_instruction(idx, CameraCmd.SetRoi.value, data)

    async def get_ctrl_value_i(self,idx : int, data) -> dict:
        if self.mqttc.num_camera <= idx:
            logger.error(f"camera idx {idx} out of range")
            return None
        self.mqttc.publish_instruction(idx, CameraCmd.GetCtrlVal.value, data)
        ctrl_type = int(data["ctrl_type"])
        while not ctrl_type in  self.mqttc.store[idx]["ctrlv"].keys():
            await asyncio.sleep(0.1)
        res = self.mqttc.store[idx]["ctrlv"][ctrl_type]
        del self.mqttc.store[idx]["ctrlv"][ctrl_type]  
        return res


    def set_ctrl_value_i(self,idx : int, data):
        if self.mqttc.num_camera <= idx:
            logger.error(f"camera idx {idx} out of range")
            return None
        self.mqttc.publish_instruction(idx, CameraCmd.SetCtrlVal.value, data)

    def start_capture_i(self,idx : int):
        if self.mqttc.num_camera <= idx:
            logger.error(f"camera idx {idx} out of range")
            return None
        self.mqttc.publish_instruction(idx, CameraCmd.StartCapture.value, {})

    def get_frame_i(self,idx : int):
        if self.mqttc.num_camera <= idx:
            logger.error(f"camera idx {idx} out of range")
            return None
        frame = self.devices[idx].get_frame()
        return {"frame" : self.to_base64(frame)}


    def stop_capture_i(self,idx : int):
        if self.mqttc.num_camera <= idx:
            logger.error(f"camera idx {idx} out of range")
            return None
        self.mqttc.publish_instruction(idx, CameraCmd.StopCapture.value, {})
