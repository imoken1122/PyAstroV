import flet as ft
from view_panel.base  import CameraViewPanel
import ft_part
from pyastrov.core import AstroVCore
from pyastrov.camera.interface import ImgType


class CameraSettingPanel(ft.UserControl):
    def __init__(self,core : AstroVCore ,camera_view_panel : CameraViewPanel):
        super().__init__()
        self.core = core

        self.camera_view_panel = camera_view_panel
        idx = 0
        ## 本当はここで定義するものではなくて、有効なカメラから取得する
        info = self.core.camera_api.get_info_i(idx)
        self.max_width= info["max_width"]
        self.max_height=info["max_height"]
        self.able_bins = [f"{b}×{b}" for b in info["supported_bins"] if b!=0]
        self.able_img_types = info["supported_img_type"]

        # current setting
        roi = self.core.camera_api.get_roi_i(idx)
        self.cur_width = roi["width"]
        self.cur_height = roi["height"]
        self.cur_bin = roi["bin"]
        self.cur_img_type = ImgType.from_int(int(roi["img_type"]))

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
    async def capture_clicked(self,e):
        ## IconButton state "e" 
        e.control.selected = not e.control.selected
        await e.control.update_async()
        idx=0
        # capture start
        if e.control.selected:
            
            await self.core.camera_api.set_roi_i(idx,0,0,self.cur_width,self.cur_height,self.cur_bin,self.cur_img_type)
            roi = self.core.camera_api.get_roi_i(idx)
            print(roi)
            await self.camera_view_panel.open(e)

        else:
            await self.camera_view_panel.close(e)
        await self.update_async() 



    async def roi_value_changed(self,e):
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

        await self.update_async()
