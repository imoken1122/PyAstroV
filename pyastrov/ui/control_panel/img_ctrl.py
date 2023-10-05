import flet as ft
from view_panel.base  import CameraViewPanel
import pyastrov.ui.ft_part as ft_part
from pyastrov.core import AstroVCore
from pyastrov.camera.interface import ControlType
from pyastrov.procimg import utils

idx = 0
class ImgCtrlPanel(ft.UserControl):
    def __init__(self,core :AstroVCore, camera_view_panel : CameraViewPanel ):
        super().__init__()
        self.core = core
        self.camera_view_panel = camera_view_panel

        self.gamma_slider = ft_part.TextWithSlider("Gamma×0.1",50,1,100,self.slider_changed,self.ctrl_value_changed,ft.colors.AMBER_800,data=ControlType.GAMMA)
        self.satulate_slider = ft_part.TextWithSlider("Satulate",50,1,255,self.slider_changed,self.ctrl_value_changed,ft.colors.AMBER_800,data=ControlType.SATURATION)
    def build(self,):
        return ft.Container(
                width=500,
                height=400,
                padding=20,
                bgcolor=ft.colors.BLUE_GREY_900,
                border_radius=5,


                content=ft.Column(
                    controls=[
                        ft_part.Text("Image Processor ",alignment=ft.alignment.bottom_left),
                        ft.Column(
                            controls=[
                                self.gamma_slider.build(),
                                self.satulate_slider.build(),


                                    ]
                                 ),
                     
                        ]
                    )

                )
    
    async def slider_changed(self,e):
        value = int(e.control.value)
        match e.control.data:
            case ControlType.GAMMA:
                self.gamma_slider.text.value = value
            case ControlType.SATURATION:
                self.satulate_slider.text.value= value

        await self.update_async()

    
    async def ctrl_value_changed(self,e,):
        value = int(e.control.value)
        match e.control.data:
            case ControlType.GAMMA:
                self.camera_view_panel.params["gamma"] = value * 0.1
            case ControlType.SATURATION:
                self.camera_view_panel.params["saturation"] = value

        await self.update_async()
