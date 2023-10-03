import flet as ft
from view_panel.base  import CameraViewPanel
import pyastrov.ui.ft_part as ft_part
from pyastrov.core import AstroVCore
from pyastrov.camera.interface import ControlType
from pyastrov.procimg import utils
import asyncio
idx = 0
class CameraWBPanel(ft.UserControl):
    def __init__(self,core :AstroVCore ):
        super().__init__()
        self.core = core
        self.wb_r_slider= ft_part.TextWithSlider("R",128,0,511,self.slider_changed,self.ctrl_value_changed,ft.colors.RED ,data="r")
        self.wb_b_slider= ft_part.TextWithSlider("B",128,0,511,self.slider_changed,self.ctrl_value_changed,ft.colors.BLUE ,data="b")  
        self.wb_g_slider= ft_part.TextWithSlider("G",128,0,511,self.slider_changed,self.ctrl_value_changed,ft.colors.GREEN,data="g")
        self.auto_btn =ft.ElevatedButton(text="Auto", on_click=self.auto_wb_clicked, color=ft.colors.BLACK,bgcolor=ft.colors.GREEN,
                                         )
        self.is_auto = False

      
    def build(self,):
        return ft.Container(
                width=500,
                height=500,
                padding=20,
                bgcolor=ft.colors.BLUE_GREY_900,
                border_radius=5,


                content=ft.Column(

                    alignment = ft.MainAxisAlignment.START,
                    controls=[
                        ft.Row ( 
                            controls = [
                                ft_part.Text("White Balance",alignment=ft.alignment.bottom_left),

                                ft.Container(
                                    height=40,
                                    width= 100,
                                    alignment=ft.alignment.bottom_right,
                                    content =ft.ElevatedButton(text="Adjust", on_click=self.adjust_white_balance_clicked, 
                                    ),
                                ),

                                ft.Container(
                                    height=40,
                                    width= 100,
                                    alignment=ft.alignment.bottom_right,
                                    content =self.auto_btn,
                                    )
                                        ]
                        ),
                        ft.Column(

                            alignment = ft.MainAxisAlignment.START,
                            controls=[
                                ### TODO get info camera interface
                                ## gain value
                                #ft_part.Text("Red",alignment=ft.alignment.bottom_left),
                                self.wb_r_slider.build(),
                                #ft_part.Text("Green",alignment=ft.alignment.bottom_left),
                                self.wb_g_slider.build(),
                                #ft_part.Text("Blue",alignment=ft.alignment.bottom_left),
                                self.wb_b_slider.build(),

                                    ]
                                 ),

                    ]
                )

        )
    async def update_rgb(self):
        wb_r = await self.core.camera_api.get_ctrl_value_i(idx,ControlType.WB_R)
        await asyncio.sleep(0.5)
        wb_g = await self.core.camera_api.get_ctrl_value_i(idx,ControlType.WB_G)
        await asyncio.sleep(0.5)
        wb_b = await self.core.camera_api.get_ctrl_value_i(idx,ControlType.WB_B)
        await asyncio.sleep(0.5)
        wb_b = await self.core.camera_api.get_ctrl_value_i(idx,ControlType.WB_B)
        self.wb_r_slider.slider.value = wb_r
        self.wb_g_slider.slider.value = wb_g
        self.wb_b_slider.slider.value = wb_b
        self.wb_r_slider.text.value = wb_r
        self.wb_g_slider.text.value = wb_g
        self.wb_b_slider.text.value = wb_b
        print("update rgb", wb_r,wb_g,wb_b)
        await self.update_async()

    async def adjust_white_balance_clicked(self,e):
        await self.core.camera_api.adjust_white_balance_i(idx)
        await asyncio.sleep(0.2)
        await self.update_rgb()
        print("adjust white balance")

    async def auto_wb_clicked(self,e):
        self.is_auto = not self.is_auto
        self.auto_btn.bgcolor = ft.colors.RED if self.is_auto else ft.colors.GREEN
        await self.core.camera_api.set_ctrl_value_i(idx,ControlType.WB_R,127,int(self.is_auto)) 
        await asyncio.sleep(0.1)
        await self.core.camera_api.set_ctrl_value_i(idx,ControlType.WB_G,127,int(self.is_auto)) 
        await asyncio.sleep(0.1)
        await self.core.camera_api.set_ctrl_value_i(idx,ControlType.WB_B,127,int(self.is_auto))
        await asyncio.sleep(0.1)
        await self.update_async()

        while self.is_auto : 
            await self.update_rgb()
            await asyncio.sleep(1)

    async def slider_changed(self,e):
        if e.control.data == "r":
            self.wb_r_slider.text.value= int(e.control.value)
        elif e.control.data == "g":
            self.wb_g_slider.text.value= int(e.control.value)
        elif e.control.data == "b":
            self.wb_b_slider.text.value= int(e.control.value)

        await self.update_async()

    async def ctrl_value_changed(self,e):
        if e.control.data == "r":
            await self.core.camera_api.set_ctrl_value_i(idx,ControlType.WB_R,int(e.control.value),0)
        elif e.control.data == "g":
            await self.core.camera_api.set_ctrl_value_i(idx,ControlType.WB_G,int(e.control.value),0)
        elif e.control.data == "b":
            await self.core.camera_api.set_ctrl_value_i(idx,ControlType.WB_B,int(e.control.value),0)
        await self.update_async()