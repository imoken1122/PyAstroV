
import flet as ft
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
        self.init_img = open("base64.txt","r",encoding="ascii" ).read()[:-1]
        self.gain_slider = ft.Slider(min=1, max=200,value=14, on_change=self.slider_changed ,active_color=ft.colors.AMBER_800,data="gain")
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
    def capture(self,e):
        print("capture")
        get()
        self.is_capture = True
        #self.main_worker()
        self.render()
        self.update()   
    def render(self, ):
        
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
    
from queue import Queue 
def get():
    q =  Queue()
    th = threading.Thread(target=other, args=(q,))
    th.start()
    while True:
        a = q.get()
        print(a)
def other(q):
    import time 
    while True:
        time.sleep(4)
        q.put([1,2,3])

import threading
if __name__ == '__main__':
    threading.Thread(target = ft.app(target=main))
    