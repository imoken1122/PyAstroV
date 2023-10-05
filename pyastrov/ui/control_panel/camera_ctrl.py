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
        self.gain_slider= ft_part.TextWithSlider("Gain",1,1,550,self.slider_changed,self.ctrl_value_changed,ft.colors.AMBER_800,data=ControlType.GAIN)

        self.exp_slider= ft_part.TextWithSlider("Exp",1,1,60,self.slider_changed,self.ctrl_value_changed,ft.colors.AMBER_800,data=ControlType.EXPOSURE)

        self.contrast_slider= ft_part.TextWithSlider("Contrust",50,1,100,self.slider_changed,self.ctrl_value_changed,ft.colors.AMBER_800,data=ControlType.CONTRAST)

        self.satulate_slider = ft_part.TextWithSlider("Satulate",50,1,100,self.slider_changed,self.ctrl_value_changed,ft.colors.AMBER_800,data=ControlType.SATURATION)
        self.gamma_slider = ft_part.TextWithSlider("Gamma",50,1,1000,self.slider_changed,self.ctrl_value_changed,ft.colors.AMBER_800,data=ControlType.GAMMA)
    def build(self,):
        return ft.Container(
                width=500,
                height=400,
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
                                #ft_part.Text("Satulate",alignment=ft.alignment.bottom_left),
                                self.satulate_slider.build(),
                                #ft_part.Text("Gamma",alignment=ft.alignment.bottom_left),
                                self.gamma_slider.build(),


                                    ]
                                 ),
                     
                    ]
                )

        )
    
    
    async def slider_changed(self,e):
       
        match e.control.data : 
            case ControlType.GAIN:
                self.gain_slider.text.value= int(e.control.value) 
            case ControlType.EXPOSURE:
                self.exp_slider.text.value= int(e.control.value)
            case ControlType.CONTRAST:
                self.contrast_slider.text.value= int(e.control.value)
            case ControlType.SATURATION:
                self.satulate_slider.text.value= int(e.control.value)
            case ControlType.GAMMA:
                self.gamma_slider.text.value= int(e.control.value)

        #await self.ctrl_value_changed(e)
        await self.update_async()


    async def ctrl_value_changed(self,e):
        if e.control.data == ControlType.EXPOSURE:
            value = int(e.control.value * 1000000)
        else:
            value = int(e.control.value)


        await self.core.camera_api.set_ctrl_value_i(idx,e.control.data,value,0)
        await self.update_async()