from camera_device.interface import CameraObject, CameraInfo, ControlCaps, ControlType, ImgType, ROIFormat
import asyncio 
from pysvb import SVBControlType, PyDemosaic ,SVBImgType
import pysvb as svb
import numpy as np
import cv2
import base64
import logging as log
import time
from queue import Queue
import threading
def to_svb_ctrl_type(ctrl_type : ControlType):

    svb_ctrl_t = None
    match ctrl_type :
        case ControlType.CONTRAST: svb_ctrl_t = SVBControlType.CONTRAST
        case ControlType.GAIN: svb_ctrl_t = SVBControlType.GAIN
        case ControlType.GAMMA: svb_ctrl_t = SVBControlType.GAMMA
        case ControlType.SATURATION: svb_ctrl_t = SVBControlType.SATURATION
        case ControlType.SHARPNESS: svb_ctrl_t = SVBControlType.SHARPNESS
        case ControlType.EXPOSURE: svb_ctrl_t = SVBControlType.EXPOSURE
        case ControlType.WB_R: svb_ctrl_t = SVBControlType.WB_R
        case ControlType.WB_B: svb_ctrl_t = SVBControlType.WB_B
        case ControlType.WB_G: svb_ctrl_t = SVBControlType.WB_G
        case ControlType.FLIP : svb_ctrl_t = SVBControlType.FLIP
        case ControlType.FRAME_SPEED_MODE: svb_ctrl_t = SVBControlType.FRAME_SPEED_MODE
        case ControlType.AUTO_TARGET_BRIGHTNESS: svb_ctrl_t = SVBControlType.AUTO_TARGET_BRIGHTNESS
        case ControlType.BLACK_LEVEL: svb_ctrl_t = SVBControlType.BLACK_LEVEL
        case ControlType.COOLER_ENABLE: svb_ctrl_t = SVBControlType.COOLER_ENABLE
        case ControlType.TARGET_TEMPERATURE: svb_ctrl_t = SVBControlType.TARGET_TEMPERATURE
        case ControlType.BAD_PIXEL_CORRECTION_ENABLE: svb_ctrl_t = SVBControlType.BAD_PIXEL_CORRECTION_ENABLE
        case _ : 
            log.error(f"Invalid control type : {ctrl_type}")
            return
        #case ControlType.CURRENT_TEMPERATURE: svb_ctrl_t = SVBControlType.CURRENT_TEMPERATURE
        #case ControlType.COOLER_POWER: svb_ctrl_t = SVBControlType.COOLER_POWER
    return svb_ctrl_t

def get_num_svb_camera():
    return svb.get_num_of_camera()

class SVBCamera(CameraObject) :
    '''SVBONY Camera Interface'''
    def __init__(self,camera_idx :int):
        '''
        Initialize SVBCamera instance
        1. Create SVBCamera instance
        2. Register camera info
        3. Register camera roi
        4. Register capability of each control type

        Args : 
            camera_idx (int) : camera index
        '''

        super().__init__()

        self.camera = svb.SVBCamera(camera_idx)
        self.camera.init()
        info = self.camera.get_info() 
        prop = self.camera.get_prop()
        

        ## register camera info
        sup_img_t = [] 
        for it in prop.supported_video_formats:
            if it == -1: break
            match it:
                case SVBImgType.RAW8: sup_img_t.append("RAW8")
                case SVBImgType.RAW16: sup_img_t.append("RAW16")
                case SVBImgType.RGB24: sup_img_t.append("RGB24")

        self.info = CameraInfo(
                        name= info.friendly_name,
                        idx=camera_idx,
                        max_width=prop.max_width,
                        max_height=prop.max_height,
                        supported_img_type= sup_img_t,
                        supported_bins= prop.supported_bins,
                        is_coolable = True
                    )
        

        ## register camera roi
        self.roi = ROIFormat(startx=0, starty=0, width=prop.max_width, height=prop.max_height, bin=1,) 
        self.img_type=self.camera.get_img_type()

        ## register capability of each control type
        self.ctrltype_mapper = {}
        for i in range(self.camera.get_num_of_controls()):
            caps = self.camera.get_ctl_caps(i)
            self.ctrltype_mapper[ControlType(caps.control_type)] = ControlCaps(
                                        name=caps.name,
                                        max_value=caps.max_value,
                                        min_value=caps.min_value,
                                        default_value=caps.default_value,
                                        is_auto_supported=caps.is_auto_supported,
                                        is_writable=caps.is_writable,
                                        control_type=caps.control_type
                                    )



        self.is_capture = False
        self.camera.adjust_white_balance()
        self.camera.set_ctl_value(int(SVBControlType.FLIP),3,0)



    def set_control_value(self,ctrl_type : ControlType,value : int, is_auto : int):
        '''
            specify control type and value to set control value

            Args:
                ctrl_type (ControlType) : control type
                value (int) : value to set
        '''
        if self.ctrltype_mapper[ctrl_type].is_writable == 0:
            log.error(f"Control type {ctrl_type} is not writable")
            return
        svb_ctrl_t = to_svb_ctrl_type(ctrl_type)
        self.camera.set_ctl_value(int(svb_ctrl_t),value,is_auto)
    def get_control_value(self,ctrl_type : ControlType) -> int:
        '''
            specify control type and get control value

            Args:
                ctrl_type (ControlType) : control type
            Returns:
                int : control value
        '''
        svb_ctrl_t = to_svb_ctrl_type(ctrl_type)
        value,is_auto = self.camera.get_ctl_value(int(svb_ctrl_t))
        return value

    def set_img_type(self, img_type: ImgType):
        # convert ImgType to SVBImgType
        svb_img_t = SVBImgType.RAW8
        match img_type :
            case ImgType.RAW8: svb_img_t = SVBImgType.RAW8
            case ImgType.RAW16: svb_img_t = SVBImgType.RAW16
            case ImgType.RGB24: svb_img_t = SVBImgType.RGB24
        
        self.img_type = img_type
        return self.camera.set_img_type(int(svb_img_t))

    def set_roi(self, startx: int, starty: int, width: int, height: int, bins: int, img_type: ImgType):
        # 8bit alignment
        width = width - width % 8
        height = height - height % 8

        self.camera.set_roi_format(startx,starty,width,height,bins)
        self.roi = ROIFormat(startx=startx, starty=starty, width=width, height=height, bin=bins, )

        self.set_img_type(img_type)

    def get_roi(self,) -> ROIFormat:
        return self.camera.get_roi_format()
    def get_frame(self,):
        s = time.time()
        #buf = np.array(self.camera.get_raw_frame(),dtype=np.uint8).reshape(self.roi.height,self.roi.width)
        buf = self.to_array(self.camera.get_raw_frame())
        #buf = self.camera.get_raw_frame()
        #buf = svb.debayer_buffer(self.camera,buf, PyDemosaic.Cubic)
        #buf= np.array(buf, dtype=np.uint8).reshape(self.roi.height,self.roi.width,3)

        buf = cv2.cvtColor(buf, cv2.COLOR_BayerGR2BGR) 
        #buf = self.to_img(buf)
        #buf  = cv2.cvtColor(buf, cv2.COLOR_RGB2BGR) 
        #print(buf[:10,:10,0])
        #return buf
        _, encoded = cv2.imencode(".png", buf)
        #q.put(encoded)
        e = time.time()
        print(e-s)
        return encoded

    def to_array(self, buf):
        np_img_t = np.uint8
        if self.img_type == ImgType.RAW16:
            np_img_t = np.uint16
        img = np.frombuffer(bytes(buf) , dtype=np_img_t).reshape(self.roi.height,self.roi.width)
        return img 
    
    def start_capture(self):
        self.is_capture = True
        self.camera.start_video_capture()

    def stop_capture(self):
        self.is_capture = False
        self.camera.stop_video_capture()


    def close(self):
        self.camera.close()
    def adjust_white_balance(self):
        self.camera.adjust_white_balance()
    def __del__(self):
        print("del")
        if self.is_capture: self.stop_capture()
        self.close()


def test_capture():
    n = svb.get_num_of_camera()
    print(n)
    camera_if = SVBCamera(0)
    camera_if.set_control_value(ControlType.EXPOSURE  ,500000,0)

    camera_if.start_capture()
    while  True:
        img = camera_if.get_frame()

        print(img[:10,:10,0])
        break
       
    camera_if.stop_capture()

def test_set_ctrl_value():
    n = svb.get_num_of_camera()
    camera_if = SVBCamera(0)
    camera_if.set_control_value(ControlType.EXPOSURE,1000,0)
    camera_if.set_control_value(ControlType.GAIN,122,0)

    assert abs(camera_if.get_control_value(ControlType.EXPOSURE) - 1000) < 5
    assert camera_if.get_control_value(ControlType.GAIN) == 122

def test_set_roi():
    n= svb.get_num_of_camera()
    print(n)
    camera =SVBCamera(0)
    roi = camera.get_roi()
    print(roi)
    assert roi.startx == 0
    assert roi.starty == 0
    assert roi.width == 4144
    assert roi.height == 2822
    assert roi.bin == 1 

    camera.set_roi(0,0,4080,2080,1)
    roi = camera.get_roi()
    print(roi)
    assert roi.startx == 0
    assert roi.starty == 0
    assert roi.width == 4080
    assert roi.height == 2080
    assert roi.bin == 1 

    camera.set_roi(0,0,2001,1203,2)
    roi = camera.get_roi()
    assert  roi.width == 2000 
    assert  roi.height == 1200 
    assert  roi.bin ==2 