import flet as ft
from pyastrov.core import AstroVCore
from pyastrov.procimg.stack import ImageStacker
import asyncio
from pyastrov.logger import  setup_logger
from  pyastrov.ui import ft_part 
import numpy as np
from multiprocessing import Process, Manager,shared_memory
import multiprocessing as mp
logger = setup_logger(__name__)
idx = 0
class StackSettingPanel(ft.UserControl):
    def __init__(self,core : AstroVCore):
        super().__init__()
        self.core = core
        self.cur_img = None
    def build(self):
        return ft.Container(
                width=500,
                height=300,
                padding=20,
                bgcolor=ft.colors.BLUE_GREY_900,
                border_radius=5,
                content=ft.Column(
                    controls=[
                        ft_part.Text("Stacking",alignment=ft.alignment.bottom_left),
                       ft.Container(
                                        content= ft.IconButton(
                                            icon= ft.icons.PLAY_CIRCLE_FILL_OUTLINED,
                                            selected_icon=ft.icons.PAUSE_CIRCLE_FILLED_ROUNDED,
                                            selected=False,
                                            on_click=self.stack_clicked,
                                            icon_size= 50,
                                            style=ft.ButtonStyle(color={"selected": ft.colors.AMBER_800, "": ft.colors.GREEN}),
                                            )
                                  ) ,
                       ft.Container(
                                        content= ft.IconButton(
                                            icon= ft.icons.COLLECTIONS,
                                            selected_icon=ft.icons.IMAGE,
                                            selected=False,
                                            on_click=self.show_frame_clicked,
                                            icon_size= 50,
                                            style=ft.ButtonStyle(color={"selected": ft.colors.AMBER_800, "": ft.colors.GREEN}),
                                            )
                                  ) ,

                    ]
                )
        )
    
    async def show_frame_clicked(self,e):
        self.core.state_manager.set("is_show_frame",e.control.selected)
        e.control.selected = not e.control.selected
        await e.control.update_async()
        logger.info(self.core.state_manager.get("is_show_frame"))

    async def stack_clicked(self,e) :

        if not self.core.state_manager.contains("cur_img") or not self.core.camera_api.is_capture_i(idx): 
            logger.error("camera is not capturing")
            return 

        e.control.selected = not e.control.selected
        await e.control.update_async()


        while self.core.camera_api.is_capture_i(idx) and e.control.selected:
            img = self.core.state_manager.get("cur_img")
            if not np.array_equal(img ,self.cur_img):
                logger.info("stacking now...")
                self.core.stacker.run(img)
                self.cur_img = img
                print(len(self.core.stacker.buffer))

            await asyncio.sleep(0.5)

        logger.info("stacking is done")