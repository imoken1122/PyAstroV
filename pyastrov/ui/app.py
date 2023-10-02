import flet as ft
import numpy as np
import base64
import cv2
from datetime import datetime
from PIL import Image
import time
from flet import theme
import threading
from queue import Queue
from pyastrov.core import AstroVCore
from control_panel.base import ControlPanel 
from view_panel.base import CameraViewPanel 
from pyastrov.core import AstroVCore
WINDOW_WIDTH = 1980
WINDOW_HEIHG= 1080

    

class StackSettingPanel(ft.UserControl):
    def __init__(self):
        super().__init__()

    def build(self):
        return ft.Container(
                width=500,
                height=600,
                padding=20,
                bgcolor=ft.colors.BLUE_GREY_900,
                border_radius=5,
        )

class StatusPanel(ft.UserControl):
    def __init__(self):
        super().__init__()

    def build(self):
        return ft.Container(
            alignment=ft.alignment.center,
            bottom=0,
            height= 50,
            width= 1400,
            bgcolor=ft.colors.BLUE_GREY_900,
            content=ft.Row(
               
            )
        )
    

class App(ft.UserControl):
    def __init__(self, core : AstroVCore): 
        super().__init__()
        self.camera_view_panel = CameraViewPanel(core,4000,2000)
        self.status_panel = StatusPanel()
        self.ctrl_panel = ControlPanel(core,self.camera_view_panel)
    def build(self):
        return ft.ResponsiveRow(
            [

                ### image view
               ft.Container(
                    width=1500,
                    height=880,

                     bgcolor=ft.colors.BLACK54,
                     border_radius=5,
                    col={ "md" : 6.5,"lg" :7.5 ,"xl":8.5 },
                    content = ft.Stack(
                       [ self.camera_view_panel,
                                self.status_panel
                        ]
                    ),
                ),
                
                ### control panel
                ft.Container(
                    col={ "md" : 5.5,"lg" :4.5,"xl":3.5},
                    content=self.ctrl_panel
                ),
               
            ]
        )




def main(page: ft.Page):

    page.window_max_width=WINDOW_WIDTH
    page.window_max_height=WINDOW_HEIHG
    page.window_min_width=800
    page.window_min_height=200
    page.window_resizable = True
    page.title = "Camera App"
    app = App(AstroVCore())
    page.update()

ft.app(target = main)