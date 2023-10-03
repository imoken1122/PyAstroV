import flet as ft
from view_panel.base  import CameraViewPanel
import pyastrov.ui.ft_part as ft_part
from pyastrov.core import AstroVCore
from pyastrov.camera.interface import ControlType
from pyastrov.procimg import utils

idx = 0
class CameraControlPanel(ft.UserControl):
    def __init__(self,core :AstroVCore ):
        super().__init__()
        self.core = core
        self.gain_slider= ft_part.TextWithSlider("Gain",14,1,550,self.slider_changed,self.ctrl_value_changed,ft.colors.AMBER_800,data="gain")

        self.exp_slider= ft_part.TextWithSlider("Expo",100000,1,60,self.slider_changed,self.ctrl_value_changed,ft.colors.AMBER_800,data="exposure")

        self.contrast_slider= ft_part.TextWithSlider("Contrust",50,1,100,self.slider_changed,self.ctrl_value_changed,ft.colors.AMBER_800,data="contrast")

      
    def build(self,):
        return ft.Container(
                width=500,
                height=600,
                padding=20,
                bgcolor=ft.colors.BLUE_GREY_900,
                border_radius=5,


                content=ft.Column(

                    alignment = ft.MainAxisAlignment.START,
                    controls=[
                        ft_part.Text("Camera Parameter",alignment=ft.alignment.bottom_left),
                        ft.Column(

                            alignment = ft.MainAxisAlignment.START,
                            controls=[
                                ### TODO get info camera interface
                                ## gain value
                                #ft_part.Text("Gain",alignment=ft.alignment.bottom_left,style=ft.TextThemeStyle.LABEL_MEDIUM),
                                self.gain_slider.build(),
                                #ft_part.Text("Exposure",alignment=ft.alignment.bottom_left),
                                self.exp_slider.build(),
                                #ft_part.Text("Contrast",alignment=ft.alignment.bottom_left),
                                self.contrast_slider.build(),

                                    ]
                                 ),

                        ft.Row(
                            [
                                
                                ft.Container(
                                    height=40,
                                    width= 100,
                                    content = ft.FloatingActionButton(text="SnapShot",
                                                                    on_click=self.save_clicked, 
                                                                    bgcolor=ft.colors.AMBER_800),
                                ),
                                   
                            ]

                        ),
                    ]
                )

        )
    
    def save_clicked(self,e):
        if not self.core.camera_api.is_captures[idx]: return
        utils.save_img(self.core.camera_api.get_frame_i(idx))

        print("save image")
    async def slider_changed(self,e):
        if e.control.data == "gain":
            self.gain_slider.text.value= int(e.control.value) 
        elif e.control.data == "exposure":
            self.exp_slider.text.value= int(e.control.value)
        elif e.control.data == "contrast":
            self.contrast_slider.text.value= int(e.control.value)


        await self.ctrl_value_changed(e)
        await self.update_async()


    async def ctrl_value_changed(self,e):
        if e.control.data == "gain":
            await self.core.camera_api.set_ctrl_value_i( idx,ControlType.GAIN,int(e.control.value),0)
        elif e.control.data == "exposure":
            micro_sec = int(e.control.value * 1000000)
            await self.core.camera_api.set_ctrl_value_i(idx,ControlType.EXPOSURE,micro_sec,0)
        elif e.control.data == "contrast":
            await self.core.camera_api.set_ctrl_value_i(idx,ControlType.CONTRAST,int(e.control.value),0)
        await self.update_async()