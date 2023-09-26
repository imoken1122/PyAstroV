import cv2
from queue import Queue
import threading
import time 
import numpy as np

from camera_device.interface import CameraObject, CameraInfo, ControlCaps, ControlType, ImgType, ROIFormat
def num_mock_camera():
    return 2

    
class MockCamera : 
    def __init__(self,idx) -> None:
        self.idx=idx
        self.w = 1912 
        self.h = 1304
        self.is_capture = False
        self.info = CameraInfo(name="Mock Camera",idx=0,max_width=self.w,max_height=self.h,supported_img_type=[ImgType.RAW8],supported_bins=[1],is_coolable=False)
        self.roi = ROIFormat(startx=0,starty=0,width=self.w,height=self.h,bin=1)
        self.img_type = ImgType.RAW8
        self.sleep_time = 1
        self.ctrltype_mapper = {    ControlType.GAIN : ControlCaps(name="GAIN",max_value=100,min_value=0,default_value=50,is_auto_supported=1,is_writable=1,control_type=0),
                                    ControlType.EXPOSURE : ControlCaps(name="EXPOSURE",max_value=100,min_value=0,default_value=50,is_auto_supported=1,is_writable=1,control_type=1),
                                    ControlType.CONTRAST : ControlCaps(name="CONTRAST",max_value=100,min_value=0,default_value=50,is_auto_supported=1,is_writable=1,control_type=2),}
    def set_roi(self,startx : int,starty : int,width : int,height : int,bin : int,img_type : ImgType):
        pass
    def set_img_type(self,img_type : ImgType):
        pass
    def get_roi(self) -> ROIFormat:
        return ROIFormat(startx=0,starty=0,width=self.w,height=self.h,bin=1)
    def get_img_type(self) -> ImgType:
        return ImgType.RAW8
    def start_capture(self):
        self.is_capture = True
    def stop_capture(self):
        self.is_capture = False

    def get(self,):
        a = np.random.randint(0,255,self.w*self.h).astype(np.uint8)
        for i in range(100000000):
            pass
        return a
    def get_frame(self,):
        buf = self.get()
        buf = buf.reshape(self.h,self.w)
        #if buf.shape[0]>1080 and buf.shape[1]>1980:
        #    buf = cv2.resize(buf,(1980,1080))
        img = cv2.cvtColor(buf, cv2.COLOR_BayerGR2RGB)  # パターンに応じて適切な変換を選択
        #return img
        _, img = cv2.imencode(".jpg", img)
        return img
    def get_control_value(self,control_type : ControlType):
        return 0
    def set_control_value(self,control_type : ControlType,value : int,is_auto : int):
        self.sleep_time = value 
    def close(self):
        pass
    def __del__(self):
        self.stop_capture()

