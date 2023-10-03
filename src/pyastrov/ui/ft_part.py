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


class TextWithSlider : 
    def __init__(self, label,default_value, min,max, on_changed, on_change_end,active_color,data:str):
        self.slider = ft.Slider(min=min, max=max,value = default_value, on_change=on_changed, on_change_end=on_change_end, active_color=active_color,data=data)  
        self.text= ft.TextField(
                                label=label,
                                value =default_value ,
                                label_style={"size" : 13},
                                text_size=13,
                                on_submit=on_changed,
                            )
    def build(self):  
        return ft.Row( 
            alignment = ft.MainAxisAlignment.CENTER,
            spacing=1,
            controls=[
                ft.Container(width = 55,height=40, content=self.text),
                ft.Container(width = 330, content=self.slider),
            ]
            )