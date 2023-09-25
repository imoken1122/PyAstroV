from multiprocessing import shared_memory
import base64
import cv2
import numpy as np
import multiprocessing.sharedctypes
import time
from PIL import Image
import flet as ft
from camera_manager import CameraManager
from multiprocessing import Process, Manager
from  camera_device.interface import ControlType, ImgType


camera_manager = CameraManager()
camera_manager.conect_camera()
class MPCamera(multiprocessing.Process):
    def __init__(self, buf_event, is_capture, shm):
        super().__init__()

        self.buf_event = buf_event
        self.is_capture = is_capture
        self.shm = shm
        self.cm = camera_manager 
    def run(self):
        camera_if = self.cm.devices[0]
        camera_if.set_roi(0,0,1912,1304,1)
        camera_if.set_img_type(ImgType.RAW8)
        camera_if.set_control_value(ControlType.EXPOSURE ,600000,0)
        camera_if.start_capture()
        print("start capture",self.is_capture.value)
        while True:
            if self.is_capture.value == 1:
                frame = camera_if.get_frame()
                buffer = np.ndarray(frame.shape, dtype=frame.dtype, buffer=self.shm.buf)
                print(frame.shape)
                self.buf_event.clear()
                buffer[:] = frame
                self.buf_event.set()
            else:
                camera_if.stop_capture()
                #self.camera_if.close()
                print("stop capture")
                break
        #self.camera_if.set_control_value(ctl_type, value, 0)

def worker1(shm,camera_if,buf_event,is_capture):
    camera_if.start_capture()
    while True:
        if is_capture.value == 1:
            #frame = cv2.imread("img5.png")
            #frame = np.array(cv2.resize(frame,(1912,1304)).astype(np.uint8))
            #print(type(frame))
            #frame = np.random.randint(0,255, (4000,2800,3 )).astype(np.uint8)

            frame = camera_if.get_frame()
            buffer = np.ndarray(frame.shape, dtype=frame.dtype, buffer=shm.buf)
            print(frame.shape)
            buf_event.clear()
            #memoryview(buf).cast("B")[:] = memoryview(frame).cast("B")[:]
            buffer[:] = frame
            buf_event.set()
        else:
      # 終わるときは CTRL + C を押す
            camera_if.stop_capture()
            camera_if.close()
            print("stop capture")
            break

class App(ft.UserControl):
    def __init__(self):

        super().__init__()
        self.is_capture = False
        self.gain_text = ft.TextField(
                                label="",
                                label_style={"size" : 13},
                                text_size=13,
                                value = 1,
                                on_submit=self.slider_changed,
                            )
        self.gain_slider = ft.Slider(min=1, max=200,value=14, on_change=self.slider_changed,on_change_end=self.value_changed ,active_color=ft.colors.AMBER_800,data="gain")
        self.init_img = open("base64.txt","r",encoding="ascii" ).read()[:-1]
        self.img_view= ft.Image(
                            src_base64=self.init_img,
                            width= 600,
                            height=400,
                            fit=ft.ImageFit.SCALE_DOWN,
                    )    
    def build(self):
        return ft.Container( 
            content=ft.Column( [self.img_view,
                             ft.FloatingActionButton(icon="camera",on_click=self.capture),
                             ft.FloatingActionButton(icon="camera" ,on_click=self.stop)
                             ,ft.Row([self.gain_text,self.gain_slider]),
                             ])
        )
    def stop(self,e):
        self.is_capture = False
        self.update()
    def slider_changed(self,e):
        self.gain_text.value = int(e.control.value) 
        ## set gain to camera interface
        self.update()
    def value_changed(self,e):
        print("value_changed")
        self.camera_if.set_control_value(ControlType.GAIN,int(e.control.value),0)
        print(self.camera_if.get_control_value(ControlType.GAIN))
        self.update()
    def capture(self,e):
        print("capture")
        self.is_capture = True
        #self.main_worker()
        self.render()
        self.update()   

    def main_worker(self,):
        print("start main worker")
        size = 1912*1304*3
#        buf1 = multiprocessing.sharedctypes.RawArray('B', size)

        shm = shared_memory.SharedMemory(create=True, size=size)

        buf_event = multiprocessing.Event()
        buf_event.clear()
        is_capture = multiprocessing.Value('i', self.is_capture)
        mpcamera = MPCamera( buf_event, is_capture, shm)

        mpcamera.start()
        n =0
        t = []
        #img  = np.empty(( 1304,1912,3),dtype=np.uint8)
        while is_capture.value==1:
            buf_event.wait()
            s= time.time()
            #img[:,:,:] = np.frombuffer(bytes(shm.buf),dtype=np.uint8).reshape( 1304,1912,3)
            img = np.ndarray(( 1304,1912,3), dtype=np.uint8, buffer=shm.buf)
            buf_event.clear()
            e= time.time()
            print(e-s)
            t.append(e-s)
            #img  = cv2.cvtColor(img, cv2.COLOR_BayerGR2BGR) 

            _, encoded = cv2.imencode(".jpg", img)
            #self.img_view.src_base64 = base64.b64encode(encoded).decode("ascii")
            #self.update()
            #time.sleep(1)
            print("=============== main process ")
            #Image.fromarray(img).save("output.png", "png")
            n += 1
            is_capture.value = self.is_capture
            if n == 10:
                print("set exposure")
                mpcamera.set_control_value(ControlType.EXPOSURE,2000000)
            yield base64.b64encode(encoded).decode("ascii")

        print("mean",np.mean(t))
        mpcamera.join(10)
        
        shm.close()
        shm.unlink()
        print("end")
    def render(self, ):
        print("render")
        for src in self.main_worker():
            self.img_view.src_base64 = src 
            self.update()
        self.img_view.src_base64 = self.init_img
        self.update()
def main(page: ft.Page):

    page.window_min_width=800
    page.window_min_height=200
    page.window_resizable = True
    page.title = "Camera App"

    page.update()
    app = App()
    page.add(app)


if __name__ == '__main__':
    ft.app(target=main)
    