import flet as ft
import pysvb as svb
import numpy as np

from pysvb import PyControlType, PyDemosaic ,PyImgType
import base64
import cv2
from datetime import datetime
from PIL import Image
import time


class Camera : 
    def init_(self) -> None:
        self.w = 4000
        self.h = 2800
        self._is_capture = True

    def __init__(self,camera_idx):
        self.camera = svb.PyCamera(camera_idx)
        self.camera.init()

        self.camera.set_img_type(0) 
        self.camera.set_roi_format(0,0,1900,1200,1)
        roi = self.camera.get_roi_format()
        self.w = roi.width
        self.h = roi.height
        self._is_capture = False
    def start_capture(self):
        self._is_capture = True
        self.camera.start_video_capture()
    def stop_capture(self):
        self._is_capture = False
        self.camera.stop_video_capture()

    def get_frame(self):
        buf = self.camera.get_video_frame()
        buf = svb.debayer_buffer(self.camera,buf, PyDemosaic.Linear)
        buf = self.to_array(buf).reshape(self.h,self.w,3)
        #img = cv2.cvtColor(buf, cv2.COLOR_BayerGR2RGB)  # パターンに応じて適切な変換を選択
        _, img = cv2.imencode(".jpg", buf)
        #buf = self.to_array(buf)
        return self.to_base64(img)


    def get(self):
        return np.random.randint(0,255,self.w*self.h).astype(np.uint8)
    def get_dummy_frame(self):
        buf = self.get().reshape(self.h,self.w)
        img = cv2.cvtColor(buf, cv2.COLOR_BayerGR2RGB)  # パターンに応じて適切な変換を選択
        print(img.shape)
        _, img = cv2.imencode(".jpg", img)
        #img = self.to_image(buf)
        return self.to_base64(img)
    def to_array(self, buf,img_type :PyImgType=PyImgType.RAW8):
        np_img_type = np.uint8
        if img_type == PyImgType.RAW16:
            np_img_type = np.uint16
        img = np.frombuffer(bytes(buf) , dtype=np_img_type)#.reshape(self.h,self.w)
        return img 
    def to_base64(self, buf ) : 
        return base64.b64encode(buf).decode("ascii")
    @property
    def is_capture(self):
        return self._is_capture
    def __del__(self):
        self.stop_capture()
        self.camera.close()
    

def main(page: ft.Page):
    #全体レイアウト
    page.window_max_width=10000
    page.window_max_height=10000
    page.title = "Camera App"

    num = svb.get_num_of_camera()
    device = Camera(0)

    device.camera.set_ctl_value( 1,10000, 0)
    device.camera.set_ctl_value( 0,120, 0)
    print(device.camera.get_ctl_value( 1))
    print(device.camera.get_ctl_value( 0))

    #roi = device.camera.get_roi_format()
    #w,h = roi.width,roi.height


    device.start_capture()

    image=ft.Image(
                src_base64=device.get_frame(),
                width=device.w,
                height=device.h,
                fit=ft.ImageFit.SCALE_DOWN,
                )    
    start_button = ft.TextButton("start", on_click=device.start_capture)
    stop_button = ft.TextButton("stop", on_click=device.stop_capture)
    #save_button = ft.TextButton("save", on_click=camera.save_image)
    row = ft.Row(spacing=0, controls=[start_button,stop_button])
    view = ft.Column(
            controls= [
                    image,
                     row

        ]
    )
    page.add(view)

    print("start loop")
    #描写のループ
    while True:
        time.sleep(0.5)
        if device.is_capture: 
            image.src_base64=device.get_frame()
            page.update()
ft.app(target=main)