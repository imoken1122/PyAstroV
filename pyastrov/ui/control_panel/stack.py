import flet as ft
from pyastrov.core import AstroVCore
from pyastrov.procimg.stack import ImageStacker
import asyncio
from pyastrov.logger import  setup_logger
from  pyastrov.ui import ft_part 
import numpy as np
from collections import deque
from multiprocessing import Process, Manager,shared_memory
import multiprocessing as mp
logger = setup_logger(__name__)
idx = 0
class StackSettingPanel(ft.UserControl):
    def __init__(self,core : AstroVCore,camera_view_panel : ft.UserControl):
        super().__init__()
        self.core = core
        self.camera_view_panel = camera_view_panel
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
                                            icon= ft.icons.IMAGE,
                                            selected_icon=ft.icons.COLLECTIONS,
                                            selected=False,
                                            on_click=self.show_frame_clicked,
                                            icon_size= 50,
                                            style=ft.ButtonStyle(color={"selected": ft.colors.AMBER_700,"": ft.colors.WHITE70 }),
                                            )
                                  ) ,

                    ]
                )
        )
    
    async def show_frame_clicked(self,e):

        e.control.selected = not e.control.selected
        self.camera_view_panel.is_show_stack = e.control.selected
        await e.control.update_async()
        await self.camera_view_panel.show_stack()
        await self.update_async()

    async def stack_clicked(self,e) :
        
        if e.control.selected:
            e.control.selected = False
            await e.control.update_async()
            self.core.stacker.is_stacking = False
            logger.info("stacking is done")
        else:
            if len(self.core.stacker.new_image_buffer) > 0 and self.core.camera_api.is_capture_i(idx):
                e.control.selected = True
                await e.control.update_async()
                await self.core.stacker.run_stack()
            else:
                logger.error("camera is not capturing")
        await self.update_async()
        return