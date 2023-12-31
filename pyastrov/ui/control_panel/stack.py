import flet as ft
from pyastrov.core import AstroVCore
from pyastrov.procimg.stack import ImageStacker
import asyncio
from pyastrov.logger import setup_logger
from pyastrov.ui import ft_part
import numpy as np
from collections import deque
from multiprocessing import Process, Manager, shared_memory
import multiprocessing as mp
import pathlib
from datetime import datetime
logger = setup_logger(__name__)
idx = 0


class StackSettingPanel(ft.UserControl):
    def __init__(self, core: AstroVCore, camera_view_panel: ft.UserControl):
        super().__init__()
        self.core = core
        self.camera_view_panel = camera_view_panel

        self.num_stack_txt = ft_part.StateText( f"Num Stacked : {self.core.stacker.num_stacked}", alignment=ft.alignment.bottom_left, style=ft.TextThemeStyle.LABEL_LARGE)
    def build(self):
        return ft.Container(
            width=500,
            height=300,
            padding=20,
            bgcolor=ft.colors.BLUE_GREY_900,
            border_radius=5,
            content=ft.Column(
                controls=[
                    ft_part.Text(
                        "Stacking", alignment=ft.alignment.bottom_left),
                    self.num_stack_txt,
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.IconButton(
                                    icon=ft.icons.PLAY_CIRCLE_FILL_OUTLINED,
                                    selected_icon=ft.icons.PAUSE_CIRCLE_FILLED_ROUNDED,
                                    selected=False,
                                    on_click=self.stack_clicked,
                                    icon_size=50,
                                    style=ft.ButtonStyle(
                                        color={"selected": ft.colors.AMBER_800, "": ft.colors.GREEN}),
                                )
                            ),
                            ft.Container(
                                content=ft.IconButton(
                                    icon=ft.icons.IMAGE,
                                    selected_icon=ft.icons.COLLECTIONS,
                                    selected=False,
                                    on_click=self.show_frame_clicked,
                                    icon_size=50,
                                    style=ft.ButtonStyle(
                                        color={"selected": ft.colors.WHITE38, "": ft.colors.WHITE70}),
                                )
                            ),
                        ]
                    ),
                    ft.Row(
                        controls=[

                            ft.Container(
                                content=ft.IconButton(
                                    icon=ft.icons.DELETE,
                                    selected=False,
                                    on_click=self.rm_clicked,
                                    icon_size=30,
                                    style=ft.ButtonStyle(
                                        color={"": ft.colors.RED_700}),
                                )
                            ),
                            ft.Container(
                                content=ft.IconButton(
                                    icon=ft.icons.DOWNLOAD,
                                    selected=False,
                                    on_click=self.save_clicked,
                                    icon_size=30,
                                    style=ft.ButtonStyle(
                                        color={"": ft.colors.WHITE70}),
                                )
                            ),
                        ]
                       
                    )

                ]
            )
        )

    async def save_clicked(self, e):
        output_dir = pathlib.Path('pyastro_output/stack')
        now = datetime.now()
        date_dir = output_dir / now.strftime('%Y-%m-%d')

        if not date_dir.exists():
            date_dir.mkdir(parents=True)

        now = now.strftime("%Y%m%d_%H%M%S")
        filename = f"stack_{now}.jpg"
        self.core.stacker.save_stacked(0, str(date_dir / filename))
        await self.update_async()

    async def rm_clicked(self, e):
        self.core.stacker.clear_buffer()
        await self.num_stack_txt.set_text(f"Num Stacked : {self.core.stacker.num_stacked}")
        return

    async def show_frame_clicked(self, e):
        if self.core.stacker.num_stacked == 0:
            logger.error("stacked buffer is empty")
            return
        e.control.selected = not e.control.selected
        self.camera_view_panel.is_show_stack = e.control.selected
        await e.control.update_async()

        t = asyncio.create_task(self.camera_view_panel.show_stack())
        await t
        await self.update_async()

    async def stack_clicked(self, e):

        e.control.selected = not e.control.selected
        await e.control.update_async()

        if not e.control.selected:
            self.core.stacker.stop_stack()
            logger.info("stacking is done")
        else:
            if self.core.camera_api.is_capture_i(idx) and len(self.core.stacker.new_image_buffer) > 0:

                self.core.stacker.start_stack()
                t1 = asyncio.create_task( self.core.stacker.run_stack())
                t2 = asyncio.create_task(self.update_num_stack_txt())
                await t1,t2
            else:
                logger.error("camera is not capturing")
        await self.update_async()
        return
    
    async def update_num_stack_txt(self,):
        while self.core.stacker.is_stacking:
            await self.num_stack_txt.set_text(f"Num Stacked : {self.core.stacker.num_stacked}")
            await asyncio.sleep(1)