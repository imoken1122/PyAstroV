import flet
import flet as ft
from flet import (
    Checkbox,
    Column,
    FloatingActionButton,
    IconButton,
    Page,
    Row,
    Tab,
    Tabs,
    TextField,
    UserControl,
    colors,
    icons,
)


class Task(UserControl):
    def __init__(self, task_name, todo_app_updater, task_delete):
        super().__init__()
        self.completed = False
        self.task_name = task_name
        self.todo_app_updater = todo_app_updater
        self.task_delete = task_delete

    def build(self):
        self.display_task = Checkbox(
            value=False, label=self.task_name, on_change=self.status_changed
        )
        self.edit_name = TextField(expand=1)

        self.display_view = Row(
            alignment="spaceBetween",
            vertical_alignment="center",
            controls=[
                self.display_task,
                Row(
                    spacing=0,
                    controls=[
                        IconButton(
                            icon=icons.CREATE_OUTLINED,
                            tooltip="Edit To-Do",
                            on_click=self.edit_clicked,
                        ),
                        IconButton(
                            icons.DELETE_OUTLINE,
                            tooltip="Delete To-Do",
                            on_click=self.delete_clicked,
                        ),
                    ],
                ),
            ],
        )

        self.edit_view = Row(
            visible=False,
            alignment="spaceBetween",
            vertical_alignment="center",
            controls=[
                self.edit_name,
                IconButton(
                    icon=icons.DONE_OUTLINE_OUTLINED,
                    icon_color=colors.GREEN,
                    tooltip="Update To-Do",
                    on_click=self.save_clicked,
                ),
            ],
        )
        return Column(controls=[self.display_view, self.edit_view])

    def edit_clicked(self, e):
        self.edit_name.value = self.display_task.label
        self.display_view.visible = False
        self.edit_view.visible = True
        self.update()

    def save_clicked(self, e):
        self.display_task.label = self.edit_name.value
        self.display_view.visible = True
        self.edit_view.visible = False
        self.update()

    def status_changed(self, e):
        self.completed = self.display_task.value
        self.todo_app_updater(self)

    def delete_clicked(self, e):
        self.task_delete(self)


class TodoApp(UserControl):
    def build(self):
        self.left_task = ft.Text("0 items left")
        self.new_task = TextField(hint_text="Whats needs to be done?", expand=True)
        self.tasks = Column()

        self.filter = Tabs(
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[Tab(text="all"), Tab(text="active"), Tab(text="completed")],
        )

        # application's root control (i.e. "view") containing all other controls
        return Column(
            width=600,
            controls=[
                 ft.Row([ ft.Text(value="Todos", style="headlineMedium")], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row(

                    controls=[
                        self.new_task,
                        FloatingActionButton(icon=icons.ADD, on_click=self.add_clicked),
                    ],
                ),
                ft.Column(
                    spacing=25,
                    controls=[
                        self.filter,
                        self.tasks,
                   
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                self.left_task,
                                ft.OutlinedButton(
                                    text = "Clear", on_click=self.clear_clicked
                                ),
                        ]
                    )
                    ]
                )
            ]
        )

    def add_clicked(self, e):
        task = Task(self.new_task.value, self.todo_app_updater, self.task_delete)
        self.tasks.controls.append(task)
        self.new_task.value = ""
        self.update()

    def todo_app_updater(self, task):
        self.update()

    def task_delete(self, task):
        self.tasks.controls.remove(task)
        self.update()

    def update(self):
        status = self.filter.tabs[self.filter.selected_index].text
        c = 0
        for task in self.tasks.controls:
            task.visible = (
                status == "all"
                or (status == "active" and task.completed == False)
                or (status == "completed" and task.completed)
            )
            if not task.completed : c += 1
        self.left_task.value = f"{c} active item(s) left"
        super().update()

    def tabs_changed(self, e):
        self.update()
    def clear_clicked(self, e):
        for task in self.tasks.controls[:]:
            if task.completed:
                self.task_delete(task)
def main(page: Page):
    page.title = "ToDo App"
    page.horizontal_alignment = "center"
    page.scroll = "adaptive"
    page.update()

    # create application instance
    app = TodoApp()

    # add application's root control to the page
    page.add(app)


flet.app(target=main)
