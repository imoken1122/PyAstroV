import flet as ft
from view_panel.base  import CameraViewPanel
import ft_part
from pyastrov.core import AstroVCore
from pyastrov.camera.interface import ControlType
from pyastrov.procimg import utils

class CameraControlPanel(ft.UserControl):
    def __init__(self,core :AstroVCore ):
        super().__init__()
        self.core = core


        self.gain_text = ft.TextField(
                                label="",
                                label_style={"size" : 13},
                                text_size=13,
                                value = 1,
                                on_submit=self.slider_changed,
                            )
        self.gain_slider = ft.Slider(min=1, max=500,value=14, on_change=self.slider_changed,on_change_end=self.ctrl_value_changed,active_color=ft.colors.AMBER_800,data="gain")
        self.exp_text = ft.TextField(
                                label="",
                                label_style={"size" : 13},
                                text_size=13,
                                value = 1,
                                on_submit=self.slider_changed,
                            )
        self.exp_slider = ft.Slider(min=1, max=60,value = 100000, on_change=self.slider_changed, on_change_end=self.ctrl_value_changed ,active_color=ft.colors.AMBER_800,data="exposure")
        self.contrast_text = ft.TextField(
                                label="",  
                                label_style={"size" : 13},
                                value = 1,
                                text_size=13,
                                on_submit=self.slider_changed,
                            )
        self.contrast_slider = ft.Slider(min=1, max=100,value = 50, on_change=self.slider_changed, on_change_end=self.ctrl_value_changed ,active_color=ft.colors.AMBER_800,data="contrast")  
        self.contrast_text= ft.TextField(
                                label="",
                                value =50 ,
                                label_style={"size" : 13},
                                text_size=13,
                                on_submit=self.slider_changed,
                            )
      
    def build(self,):
        return ft.Container(
                width=500,
                height=600,
                padding=20,
                bgcolor=ft.colors.BLUE_GREY_900,
                border_radius=5,


                content=ft.Column(

                    alignment = ft.MainAxisAlignment.SPACE_EVENLY,
                    controls=[
                        ft_part.Text("Camera Parameter",alignment=ft.alignment.bottom_left),
                        ft.Column(

                            alignment = ft.MainAxisAlignment.START,
                            controls=[
                                ### TODO get info camera interface
                                ## gain value
                                ft_part.Text("Gain",alignment=ft.alignment.bottom_left),
                                ft.Row( 
                                    alignment = ft.MainAxisAlignment.CENTER,
                                    spacing=1,
                                    controls=[
                                        ft.Container(width = 55,height=40, content=self.gain_text),
                                        ft.Container(width = 350, content=self.gain_slider),
                                    ]
                                 ),
                                ## exposure value
                                ft_part.Text("Exposure",alignment=ft.alignment.bottom_left),
                                ft.Row( 
                                    alignment = ft.MainAxisAlignment.CENTER,
                                    height=45,
                                    spacing=1,
                                    controls=[
                                        ft.Container(width = 55,height=40, content=self.exp_text),
                                        ft.Container(width = 350, content=self.exp_slider),
                                    ]
                                 ),
                                 ft_part.Text("Contrast",alignment=ft.alignment.bottom_left),
                                ft.Row( 
                                    alignment = ft.MainAxisAlignment.CENTER,
                                    spacing=1,
                                    controls=[
                                        ft.Container(width = 55,height=40, content=self.contrast_text),
                                        ft.Container(width = 350, content=self.contrast_slider),
                                    ]
                                 ),



                            ],

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
                                   
                                ft.Container(
                                    height=40,
                                    width= 100,
                                    content = ft.FloatingActionButton(text="Adjust White Balance",
                                                                    on_click=self.adjust_white_balance_clicked, 
                                                                    bgcolor=ft.colors.AMBER_800),
                                ),
                            ]

                        ),
                    ]
                )

        )
    
    def save_clicked(self,e):
        idx=0
        if not self.core.camera_api.is_captures[idx]: return
        utils.save_img(self.core.camera_api.get_frame(idx))

        print("save image")

    def adjust_white_balance_clicked(self,e):
        #self.core.camera_api.adjust_white_balance()
        print("adjust white balance")

    def slider_changed(self,e):
        if e.control.data == "gain":
            self.gain_text.value = int(e.control.value) 
        elif e.control.data == "exposure":
            self.exp_text.value = int(e.control.value)
        elif e.control.data == "contrast":
            self.contrast_text.value = int(e.control.value)


        ## set gain to camera interface
        self.update()
    async def ctrl_value_changed(self,e):
        idx = 0
        if e.control.data == "gain":
            await self.core.camera_api.set_ctrl_value_i( idx,ControlType.GAIN,int(e.control.value),0)
        elif e.control.data == "exposure":
            micro_sec = int(e.control.value * 1000000)
            await self.core.camera_api.set_ctrl_value_i(idx,ControlType.EXPOSURE,micro_sec,0)
        elif e.control.data == "contrast":
            await self.core.camera_api.set_ctrl_value_i(idx,ControlType.CONTRAST,int(e.control.value),0)
        await self.update_async()