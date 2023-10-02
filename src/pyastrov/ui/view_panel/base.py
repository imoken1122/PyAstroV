import flet as ft

from pyastrov.core import AstroVCore
import asyncio
from pyastrov.procimg import utils

class CameraViewPanel(ft.UserControl):


    def __init__(self ,core : AstroVCore, width : int  , height : int ) :
        super().__init__()
        self.core = core

        self.img_view = None
        self.width = width
        self.height = height

        self.init_img = open("/Users/momo/Desktop/AstroViewer/src/pyastrov/ui/view_panel/base64.txt","r",encoding="ascii" ).read()[:-1]

    def build(self,) :
        self.img_view= ft.Image(
                            src_base64=self.init_img,
                            width=self.width,
                            height=self.height,
                            fit=ft.ImageFit.SCALE_DOWN,
                    )    
        return self.img_view 

    async def open(self,e):
        idx= 0
        self.core.camera_api.start_capture_i(idx)

        while self.core.camera_api.is_capture_i(idx):
        
            buf = self.core.camera_api.get_frame_i(idx)
            if buf:
                self.img_view.src_base64 = utils.to_flet_img(buf)
                await self.update_async()

            await asyncio.sleep(0.1)
            
        self.img_view.src_base64 = self.init_img
        await self.update_async()
            
        
    async def close(self,e):
        idx=0
        self.core.camera_api.stop_capture_i(idx)
        await self.update_async()

