from multiprocessing import shared_memory
import base64
import cv2
import numpy as np
import multiprocessing.sharedctypes
import time
from PIL import Image
import flet as ft
from camera_manager import CameraManager
from  camera_device.interface import ControlType, ImgType

def worker1(buf,buf_ready,is_capture):
    camera_manager = CameraManager()
    camera_manager.conect_camera()
    camera_if = camera_manager.devices[0]
    camera_if.set_roi(0,0,1912,1310,1)
    camera_if.set_img_type(ImgType.RAW8)
    camera_if.set_control_value(ControlType.EXPOSURE ,500000,0)
    camera_if.set_control_value(ControlType.GAIN,5,0)
    camera_if.start_capture()
    while True:
        if is_capture.value == 1:
            #frame = cv2.imread("img5.png")
            #frame = np.array(cv2.resize(frame,(1912,1304)).astype(np.uint8))
            #print(type(frame))
            #frame = np.random.randint(0,255, (4000,2800,3 )).astype(np.uint8)
            frame = camera_if.get_frame()
            #cv2.imwrite("img.png",frame)
            print(frame.shape)
            buf_ready.clear()
            memoryview(buf).cast("B")[:] = memoryview(frame).cast("B")[:]
            buf_ready.set()
        else:
      # 終わるときは CTRL + C を押す
            camera_if.stop_capture()
            camera_if.close()
            print("stop capture")
            break

class App(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.gain_text = ft.TextField(
                                label="",
                                label_style={"size" : 13},
                                text_size=13,
                                value = 1,
                                on_submit=self.slider_changed,
                            )
        self.gain_slider = ft.Slider(min=1, max=500,value=14, on_change=self.slider_changed,active_color=ft.colors.AMBER_800,data="gain")
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
                             ft.FloatingActionButton(icon="camera",on_click=self.capture)
                             ,self.gain_text,self.gain_slider,
                             ])
        )
    def slider_changed(self,e):
        self.gain_text.value = int(e.control.value) 
        ## set gain to camera interface
        self.update()
    def capture(self,e):
        print("capture")

        self.main_worker()
        self.update()   

    def main_worker(self):
        size = 1912*1304*3
        buf1 = multiprocessing.sharedctypes.RawArray('B', size)

        buf1_ready = multiprocessing.Event()
        buf1_ready.clear()
        is_capture = multiprocessing.Value('i', 1)
        p1 = multiprocessing.Process(target=worker1, args=(buf1, buf1_ready,is_capture),daemon=True)
        p1.start()
        n =0
        img  = np.empty(( 1304,1912,3),dtype=np.uint8)
        t = []
        while True:
            buf1_ready.wait()
            s = time.time()
            img[:,:,:] = np.reshape(buf1 , (1304,1912,3))
            buf1_ready.clear()
            e = time.time()
            print(e-s)
            t.append(e-s)
            #img  = cv2.cvtColor(img, cv2.COLOR_BayerGR2BGR) 
            _, encoded = cv2.imencode(".jpg", img)
            #print(len(encoded))
            self.img_view.src_base64 = base64.b64encode(encoded).decode("ascii")

            self.update()
            print("=============== main process ")
            #Image.fromarray(img).save("output.png", "png")
            time.sleep(1)
            n += 1
            if n > 20:
                print(np.mean(t))
                is_capture.value = 0
                p1.join(10)
                break

        exit(0)
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
    