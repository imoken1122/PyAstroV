import flet as ft


def Dropdown(label, items,value=None,key="" ,on_change=None,width=150, height=45, text_size=13,margin=10):

   return ft.Container(
        margin=margin,
        content = ft.Dropdown(

            label=label,
            width=width,
            height=height,
            text_size=text_size,
            value = value,
            key=key,
            on_change=on_change,
            options = [ft.dropdown.Option(item) for item in items],
        ),
    )

def Text(label, width=150, height=30, text_size=20,margin=5,style=ft.TextThemeStyle.TITLE_MEDIUM,alignment=ft.alignment.center):
    return ft.Container(
        alignment=alignment,
        margin = margin,
        height=height,
        width=width,
        content=ft.Text(label,style=style, text_align=ft.TextAlign.CENTER)
    )