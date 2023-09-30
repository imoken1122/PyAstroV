import flet as ft
from flet_core.control import OptionalNumber
import numpy as np
import base64
import cv2
from datetime import datetime
from PIL import Image
import time
from flet import theme
from camera_device.manager import CameraManager
from  mqtt.camera_cli.interface import ControlType, ImgType
import ft_part
import threading
from queue import Queue

WINDOW_WIDTH = 1980
WINDOW_HEIHG= 1080

camera_manager = CameraManager()
camera_manager.conect_camera()
camera_if = camera_manager.devices[0]

class CameraViewPanel(ft.UserControl):
    def __init__(self , width : int  , height : int ) :
        super().__init__()
        self.img_view = None
        self.width = width
        self.height = height

        self.init_img = open("base64.txt","r",encoding="ascii" ).read()[:-1]

    def build(self,) :
        self.img_view= ft.Image(
                            src_base64=self.init_img,
                            width=self.width,
                            height=self.height,
                            fit=ft.ImageFit.SCALE_DOWN,
                    )    
        return self.img_view 

    def start_capture(self,e):
        camera_if.start_capture()
        self.get_frame(e)
    def get_frame(self,e):
        q = Queue()
        while True :
        
            if camera_if.is_capture: 

                buf = camera_if.get_frame()
                self.img_view.src_base64 = self.to_base64( buf)

                self.update()
            else:
                self.img_view.src_base64 = self.init_img
                self.update()
                break
            
        
    def stop_capture(self,e):
        camera_if.stop_capture()
        self.update()

    def to_base64(self, buf :bytes) : 
        return base64.b64encode(buf).decode("ascii")

class CameraSettingPanel(ft.UserControl):
    def __init__(self,camera_view_panel : CameraViewPanel):
        super().__init__()
        self.camera_view_panel = camera_view_panel

        ## 本当はここで定義するものではなくて、有効なカメラから取得する
        info = camera_if.info
        self.max_width=info.max_width
        self.max_height=info.max_height 
        self.able_bins = [f"{b}×{b}" for b in info.supported_bins if b!=0]
        self.able_img_types = info.supported_img_type

        # current setting
        roi = camera_if.roi
        self.cur_width = roi.width
        self.cur_height = roi.height
        self.cur_bin = roi.bin
        self.cur_img_type = camera_if.img_type

    def build(self):
        return ft.Container(

                width=500,
                height=300,
                padding=0,
                bgcolor=ft.colors.BLUE_GREY_900,
                border_radius=5,

                content=ft.Column(
                    alignment = ft.MainAxisAlignment.SPACE_EVENLY,

                    controls=[
                        ft_part.Text("Camera Setting"),
                    ### The container is selecting camera and capturing button 
                        ft.Row(
                            alignment = ft.MainAxisAlignment.CENTER,
                            spacing=5,
                            controls=[
                                ft_part.Dropdown("Camera",["ASI 585MC","SV404CC"]),
                              ## start or stop to capture button 
                                  ft.Container(
                                        content= ft.IconButton(
                                            icon= ft.icons.PLAY_CIRCLE_FILL_OUTLINED,
                                            selected_icon=ft.icons.PAUSE_CIRCLE_FILLED_ROUNDED,
                                            selected=False,
                                            on_click=self.capture_clicked,
                                            icon_size= 50,
                                            style=ft.ButtonStyle(color={"selected": ft.colors.AMBER_800, "": ft.colors.GREEN}),
                                            )
                                  )
                            ]
                        ),
                        ft.Row(

                            alignment = ft.MainAxisAlignment.CENTER,
                            controls=[
                                ### TODO get info camera interface
                                ft_part.Dropdown("Resolution",
                                                ["4144x2822","3760x2564","2560x1748","1912x1310","1296x890",  "640x480","320x240"],
                                                value="4144x2822", key="resolution", on_change = self.roi_value_changed),
                                ft_part.Dropdown("ImageType",["RAW8","RAW16"],
                                                 value = "RAW8",
                                                 key="img_type",
                                                 on_change = self.roi_value_changed
                                                 ),
                            ],

                        ),
                        ft.Row(

                            alignment = ft.MainAxisAlignment.CENTER,
                            controls=[
                                ### TODO get info camera interface
                                ft_part.Dropdown("Demosaic",["Bilinear","Nearest","Cubic"],value="Bilinear"),
                                ft_part.Dropdown("Bin", ["1x1","2x2","3x3","4x4"], value="1x1", key="bin", on_change = self.roi_value_changed),
                            ],

                        )


                        ],
                    ),
            )
    def capture_clicked(self,e):
        ## IconButton state "e" 
        e.control.selected = not e.control.selected
        e.control.update()

        # capture start
        if e.control.selected:
            camera_if.set_roi(0,0,self.cur_width,self.cur_height,self.cur_bin)
            camera_if.set_img_type(self.cur_img_type)
            roi = camera_if.get_roi()
            print(roi.width,roi.height,roi.bin)
            self.camera_view_panel.start_capture(e)

        else:
            self.camera_view_panel.stop_capture(e)
        self.update() 



    def roi_value_changed(self,e):
        match e.control.key:
            case "resolution":
                selected_width,selected_height = e.control.value.split("x")
                self.cur_height = int(selected_height)
                self.cur_width = int(selected_width)
            case "img_type":
                match e.control.value:
                    case "RAW8": self.cur_img_type = ImgType.RAW8
                    case "RAW16": self.cur_img_type = ImgType.RAW16

            case "bin":
                selected_bin = e.control.value.split("x")[0]
                self.cur_bin = int(selected_bin)

        self.update()
    
class CameraControlPanel(ft.UserControl):
    def __init__(self,camera_view_panel : CameraViewPanel):
        super().__init__()
        self.camera_view_panel = camera_view_panel

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
        if not camera_if.is_capture: return

        frame = cv2.imdecode(camera_if.get_frame(),cv2.IMREAD_UNCHANGED)
        now = datetime.now()
        cv2.imwrite(f"{now.strftime('%Y%m%d_%H%M%S')}.png",frame)

        print("save image")

    def adjust_white_balance_clicked(self,e):
        camera_if.adjust_white_balance()
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
    def ctrl_value_changed(self,e):
        if e.control.data == "gain":
            camera_if.set_control_value(ControlType.GAIN,int(e.control.value),0)
        elif e.control.data == "exposure":
            micro_sec = int(e.control.value * 1000000)
            camera_if.set_control_value(ControlType.EXPOSURE,micro_sec,0)
        elif e.control.data == "contrast":
            camera_if.set_control_value(ControlType.CONTRAST,int(e.control.value),0)
        self.update()

class ControlPanel(ft.UserControl):
    def __init__(self,camera_view_panel : CameraViewPanel):
        super().__init__()
        self.camera_view_panel = camera_view_panel
        
    def build(self):
        return ft.Column(
        height=1080,
        width=500,
            scroll=ft.ScrollMode.ALWAYS,
            controls=[
                CameraSettingPanel(self.camera_view_panel),
                CameraControlPanel(self.camera_view_panel),
            ]
        )
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
    

class AstroViewer(ft.UserControl):
    def __init__(self, ): 
        super().__init__()
        self.camera_view_panel = CameraViewPanel(4000,2000)
        self.status_panel = StatusPanel()
        self.ctrl_panel = ControlPanel(self.camera_view_panel)
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

    page.update()
    app = AstroViewer()
    page.add(app)

ft.app(target=main)