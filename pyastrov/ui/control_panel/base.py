import flet as ft
import ft_part
from view_panel.base  import CameraViewPanel
from control_panel.params import CameraControlPanel
from control_panel.setting import CameraSettingPanel
from pyastrov.core import AstroVCore
class ControlPanel(ft.UserControl):
    def __init__(self,core : AstroVCore,camera_view_panel : CameraViewPanel):
        super().__init__()
        self.core = core
        self.camera_view_panel = camera_view_panel
        
    def build(self):
        return ft.Column(
        height=1080,
        width=500,
            scroll=ft.ScrollMode.ALWAYS,
            controls=[
                CameraSettingPanel(self.core,self.camera_view_panel),
                CameraControlPanel(self.core)
            ]
        )
