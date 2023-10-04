
import base64
from dataclasses import asdict
from ..interface import CameraAPI, ControlType, ImgType, ROIFormat
from .client import MQTTCameraClient
from .config import CameraCmd, CameraTopics
import asyncio
from pyastrov.logger import setup_logger
import threading 
from collections import deque

logger = setup_logger("mqtt-client-api")

class MQTTCameraAPI(CameraAPI) : 
    frame_buffer = []
    is_captures = []
    def __init__ (self ):
        self.is_captures = []
        self.mqttc = MQTTCameraClient() 
        self.lock = threading.Lock()
        self.info = None

    async def init(self):
        await self.mqttc.init()
        num = self.get_num_camera()
        self.is_captures = [False for i in range(num)]
        
    def is_capture_i(self,idx) -> bool:
        return self.is_captures[idx]
    def get_num_camera(self):
        return self.mqttc.num_camera

    def get_info_i(self,idx : int) -> dict:
        if self.mqttc.num_camera <= idx:
            logger.error(f"camera idx {idx} out of range")
            return None
        logger.debug(self.mqttc.store[idx]["info"])
        return self.mqttc.store[idx]["info"]

    def get_roi_i(self,idx : int) -> dict:
        if self.mqttc.num_camera <= idx:
            logger.error(f"camera idx {idx} out of range")
            return None
        return self.mqttc.store[idx]["roi"]

    async def set_roi_i(self,idx : int,  startx : int, starty : int, width : int, height : int, bin : int, img_type : ImgType):
        if self.mqttc.num_camera <= idx:
            logger.error(f"camera idx {idx} out of range")
            return None
        img_t = img_type.value[0]
        data = { "startx" : str(startx), "starty" : str(starty), "width" : str(width), "height" : str(height), "bin" : str(bin), "img_type" : str(img_t)}
        await self.mqttc.publish_instruction(idx, CameraCmd.SetRoi.value, data)

    async def get_ctrl_value_i(self,idx : int, ctrl_type :  ControlType   ) -> dict:
        if self.mqttc.num_camera <= idx:
            logger.error(f"camera idx {idx} out of range")
            return None

        data = { "ctrl_type" : str(ctrl_type.value)}
        ctrl_type = int(data["ctrl_type"])


        if ctrl_type in self.mqttc.store[idx]["ctrlv"].keys():
            return self.mqttc.store[idx]["ctrlv"][ctrl_type]
        
        await self.mqttc.publish_instruction(idx, CameraCmd.GetCtrlVal.value, data)

        return self.mqttc.store[idx]["ctrlv"][ctrl_type]


    async def set_ctrl_value_i(self,idx : int, ctrl_type :  ControlType, value : int  , is_auto : int ) -> dict:
        if self.mqttc.num_camera <= idx:
            logger.error(f"camera idx {idx} out of range")
            return None
        data = { "ctrl_type" : str(ctrl_type.value), "value" : str(value), "is_auto" : str(is_auto)}    
        await self.mqttc.publish_instruction(idx, CameraCmd.SetCtrlVal.value, data)

    async def start_capture_i(self,idx : int):
        if self.mqttc.num_camera <= idx:
            logger.error(f"camera idx {idx} out of range")
            return None
        self.is_captures[idx] = True
        await self.mqttc.publish_instruction(idx, CameraCmd.StartCapture.value, {})

    def get_frame_i(self,idx : int):
        if self.mqttc.num_camera <= idx:
            logger.error(f"camera idx {idx} out of range")
            return None
        if self.is_captures[idx] == False:
            self.lock.acquire()
            self.mqttc.store[idx]["frames"] = deque([],maxlen = 10)
            self.lock.release()
        
        self.is_captures[idx] = True

        self.lock.acquire()
        try:
            buf = self.mqttc.store[idx]["frames"].pop()
        except Exception as e   :
            buf = None
        self.lock.release()
        return buf


    async def stop_capture_i(self,idx : int):
        if self.mqttc.num_camera <= idx:
            logger.error(f"camera idx {idx} out of range")
            return None
        self.is_captures[idx] = False 
        await self.mqttc.publish_instruction(idx, CameraCmd.StopCapture.value, {})
    async def adjust_white_balance_i(self,idx : int):
        if self.mqttc.num_camera <= idx:
            logger.error(f"camera idx {idx} out of range")
            return None
        await self.mqttc.publish_instruction(idx, CameraCmd.AdjustWB.value, {})
        

async def test_api():

    mqttc = MQTTCameraAPI()

    await mqttc.init()    

    while True:
        cmd = input( "cmd : ")
        match cmd :
            case 'q': break
            case 'i':
                await mqttc.init()
            case'sc':
                data={"ctrl_type":"1","value":"4000000","is_auto":"0"}
                await mqttc.set_ctrl_value_i(1,data)
            case 'gc':
                data={"ctrl_type":"1"}
                await mqttc.get_ctrl_value_i(1,data)
            case 'gi':
                data={}
                mqttc.get_info_i(1)
            case 'sr':
                data={"startx":"0","starty":"0","width":"1912","height":"1304","bin":"1","img_type":"0"}
                await mqttc.set_roi_i(1,data)
            case 'gf':
                data={}
                await mqttc.start_capture_i(1)
                await mqttc.start_capture_i(0)
            case 'sf':
                data={}
                await mqttc.stop_capture_i(1)
                await asyncio.sleep(1)
                await mqttc.stop_capture_i(0)

        await asyncio.sleep(0.1)
        logger.info(mqttc.mqttc.store[1])
if __name__ == "__main__":
    asyncio.run(test_api())
    #