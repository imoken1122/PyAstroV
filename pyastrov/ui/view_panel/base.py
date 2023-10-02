import flet as ft

from pyastrov.core import AstroVCore

class CameraViewPanel(ft.UserControl):


    def __init__(self ,core : AstroVCore, width : int  , height : int ) :
        super().__init__()
        self.core = core

        self.img_view = None
        self.width = width
        self.height = height

        self.init_img = open("base64.txt","r",encoding="ascii" ).read()[:-1]

    def build(self,) :
        self.img_view= ft.Image(
                            src_base64=self.init_img,
                            width=self.width,
                            height=self.height,
                            fit=ft.ImageFit.SCALE_DOWN,
                    )    
        return self.img_view 

    def open(self,e):
        self.core.camera_api.start_capture()
        self.get_frame(e)
    def get_frame(self,e):
        while True :
        
            if self.core.camera_api.is_capture: 

                buf = self.core.camera_api.get_frame()
                self.img_view.src_base64 = self.to_base64( buf)

                self.update()
            else:
                self.img_view.src_base64 = self.init_img
                self.update()
                break
            
        
    def close(self,e):
        self.core.camera_api.stop_capture()
        self.update()

