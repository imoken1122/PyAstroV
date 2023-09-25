
import time
import numpy as np
import json
import base64

from mqtt_config import MQTTBase, CameraTopics, Method,formatter
from manager import CameraManager

'''
msg = {
    "camera_idx" : 0,
    "method" : get/set,
    "contents" : {}
}
'''



class MQTTCameraServer(MQTTBase):
    def __init__(self):
        super().__init__()
        self.camera_manger = CameraManager()
        self.camera_manger.connect()

    def on_message(self, mqttc, obj, msg):
        print(f"Received `{len(msg.payload.decode())}` from `{msg.topic}` topic")

        msg = json.loads(msg.payload.decode())
        camera_idx = msg["camera_idx"]
        method = msg["method"]
        contents=  json.loads(msg["contents"])

        match msg.topic:
            case CameraTopics.Status.value:
                #publish status
                pass
            case CameraTopics.Roi.value:
                #get roi
                match method:
                    case Method.Get:
                        res = self.camera_manger.get_roi_i(camera_idx)
                        res = formatter(camera_idx, None, res)
                        self.pub_single(CameraTopics.Roi.value, res)
                    case Method.Set:
                        self.camera_manger.set_roi_i(camera_idx, contents)


            case CameraTopics.Control.value:
                match method:
                    case Method.Get:
                        res  = self.camera_manger.get_ctrl_value_i(camera_idx)
                        res = formatter(camera_idx, None, res)
                        self.pub_single(CameraTopics.Control.value, res)
                    case Method.Set:
                        self.camera_manger.set_ctrl_value_i(camera_idx,contents)
                
            case CameraTopics.Capture.value:
                if contents["is_capture"]:
                    self.camera_manger.start_capture_i(camera_idx)
                    res = self.camera_manger.get_frame_i(camera_idx)
                    res = formatter(camera_idx, None, res)
                    self.pub_single(CameraTopics.Capture.value, res)
                else:
                    self.camera_manger.stop_capture_i(camera_idx)


            case CameraTopics.Info.value:

                res = self.camera_manger.get_info_i(camera_idx)
                res = formatter(camera_idx, None, res)
                self.pub_single(CameraTopics.Info.value,res)

            case CameraTopics.Props.value:
                res = self.camera_manger.get_props_i(camera_idx)
                res = formatter(camera_idx, None, res)
                self.pub_single(CameraTopics.Props.value,res)

            case _:
                pass


