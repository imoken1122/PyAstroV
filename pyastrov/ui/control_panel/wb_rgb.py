import flet as ft
from view_panel.base  import CameraViewPanel
import pyastrov.ui.ft_part as ft_part
from pyastrov.core import AstroVCore
from pyastrov.camera.interface import ControlType
from pyastrov.procimg import utils
import asyncio
idx = 0
class CameraWBPanel(ft.UserControl):
    def __init__(self,core :AstroVCore,camera_view_panel : CameraViewPanel ):
        super().__init__()
        self.core = core
        self.camera_view_panel = camera_view_panel
        self.wb_r_slider= ft_part.TextWithSlider("R",128,0,511,self.slider_changed,self.ctrl_value_changed,ft.colors.RED ,data="r")
        self.wb_b_slider= ft_part.TextWithSlider("B",128,0,511,self.slider_changed,self.ctrl_value_changed,ft.colors.BLUE ,data="b")  
        self.wb_g_slider= ft_part.TextWithSlider("G",128,0,511,self.slider_changed,self.ctrl_value_changed,ft.colors.GREEN,data="g")

      
    def build(self,):
        return ft.Container(
                width=500,
                height=300,
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
        await asyncio.sleep(0.2)
        wb_g = await self.core.camera_api.get_ctrl_value_i(idx,ControlType.WB_G)
        await asyncio.sleep(0.2)
        wb_b = await self.core.camera_api.get_ctrl_value_i(idx,ControlType.WB_B)
        await asyncio.sleep(0.2)
        self.wb_r_slider.slider.value = wb_r
        self.wb_g_slider.slider.value = wb_g
        self.wb_b_slider.slider.value = wb_b
        self.wb_r_slider.text.value = wb_r
        self.wb_g_slider.text.value = wb_g
        self.wb_b_slider.text.value = wb_b
        self.camera_view_panel.params["b"] = wb_b
        self.camera_view_panel.params["r"] = wb_r
        self.camera_view_panel.params["g"] = wb_g
        print("update rgb", wb_r,wb_g,wb_b)
        await self.update_async()

    async def adjust_white_balance_clicked(self,e):
        await self.core.camera_api.adjust_white_balance_i(idx)
        await asyncio.sleep(0.2)
        await self.update_rgb()
        print("adjust white balance")

  
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
            self.camera_view_panel.params["r"] = int(e.control.value)
        elif e.control.data == "g":
            self.camera_view_panel.params["g"] = int(e.control.value)
        elif e.control.data == "b":
            self.camera_view_panel.params["b"] = int(e.control.value)
        await self.update_async()