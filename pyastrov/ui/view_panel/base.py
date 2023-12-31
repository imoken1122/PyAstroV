import flet as ft

from pyastrov.core import AstroVCore
import asyncio
from pyastrov.procimg import utils
import time
class CameraViewPanel(ft.UserControl):


    def __init__(self ,core : AstroVCore, width : int  , height : int ) :
        super().__init__()
        self.core = core
        self.params = {"gamma":1,"saturation":0, "r":128,"g":128,"b":128}
        self.img_view = None
        self.width = width
        self.height = height
        self.is_show_stack = False
        self.init_img = open("/Users/momo/Desktop/AstroViewer/pyastrov/ui/view_panel/logo_base64.txt","r",encoding="ascii" ).read()[:-1]

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
        await self.core.camera_api.start_capture_i(idx)
        img_w,img_h = self.core.camera_api.get_roi_i(idx)["width"],self.core.camera_api.get_roi_i(idx)["height"]

        while self.core.camera_api.is_capture_i(idx):
            
            encoded_frame= self.core.camera_api.get_frame_i(idx)
            if encoded_frame:
                buf= utils.base64_to_bytes(encoded_frame)
                img = utils.buf_to_img(buf,img_w,img_h)
                img = utils.cvt_img(img,self.params)
                img = utils.auto_adjust_rgb(img)

                self.core.stacker.new_image_buffer.appendleft(img)
                #if self.core.stacker.is_stackking():
                    #stack_t = asyncio.create_task(self.core.stacker.run_stack(img))
                    #await stack_t
                #    await self.core.stacker.run_stack(img)

                if not self.is_show_stack:
                    self.img_view.src_base64 = utils.encode_img_for_flet(img)  
            await self.update_async()

            await asyncio.sleep(0.1)
            
        self.img_view.src_base64 = self.init_img
        await self.update_async()
    
    async def show_stack(self):

        while True:
            if not self.is_show_stack :break            
            stack_img = self.core.stacker.get_latest_stacked()

            #stack_img = utils.cvt_img(stack_img,self.params)
            
            if not stack_img is None:
                encoded = utils.encode_img_for_flet(stack_img)
                self.img_view.src_base64 = encoded
            await self.update_async()
            await asyncio.sleep(0.5)
        self.img_view.src_base64 = self.init_img
        await self.update_async()
        
    async def close(self,e):
        idx=0
        await self.core.camera_api.stop_capture_i(idx)


    def cvt_src_img(self, cvt_func, *args):
        encoded = self.img_view.src_base64
        img = utils.decode_img_from_flet(encoded)
        img = cvt_func(img,*args)
        self.img_view.src_base64 =  utils.encode_img_for_flet(img)