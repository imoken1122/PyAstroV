import flet as ft
import cv2
import base64
from datetime import datetime
def main(page: ft.Page):

    page.windwo
    view = ft.Row(
        [ft.Container(
                    content=ft.Text("Non clickable"),
                    margin=10,
                    padding=20,
                    alignment=ft.alignment.top_left,
                    bgcolor=ft.colors.AMBER,
                    width=330,
                    height=150,
                    border_radius=10,
                ),
                ft.Container(
                    content=ft.Text("Clickable without Ink"),
                    margin=10,
                    padding=10,
                    alignment=ft.alignment.center,
                    bgcolor=ft.colors.GREEN_200,
                    width=150,
                    height=150,
                    border_radius=10,
                    on_click=lambda e: print("Clickable without Ink clicked!"),
                ),
        ]
    )
    page.add(view)
ft.app(target=main)
#ウェブアプリの場合