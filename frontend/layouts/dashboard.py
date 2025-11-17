from contextlib import contextmanager
from nicegui import app, ui
from frontend import state
from frontend.state import clear_auth


@contextmanager
def dashboard_frame(title: str):
    """
    A layout for all protected dashboard pages.
    - It checks for authentication and redirects to /login if the user is not logged in.
    - It provides a consistent header and a full-height drawer.
    """
    if not state.get_auth():
        ui.navigate.to("/login")
        return

    async def handle_logout():
        clear_auth()
        app.storage.user.clear()
        ui.navigate.to("/login")

    with ui.header(elevated=True).classes("items-center justify-between"):
        with ui.row().classes("items-center"):
            ui.button(on_click=lambda: left_drawer.toggle(), icon="menu").props(
                "flat color=white"
            )
            ui.label(title).classes("text-h5")

    with ui.left_drawer(value=True, elevated=True).classes("bg-white") as left_drawer:
        with ui.column().classes("w-full h-full flex flex-col justify-between no-wrap"):
            with ui.list().classes("w-full"):
                with (
                    ui.item(on_click=lambda: ui.navigate.to("/items"))
                    .props("clickable")
                    .classes("w-full")
                ):
                    with ui.item_section().props("avatar"):
                        ui.icon("list", color="gray-500")
                    with ui.item_section():
                        ui.label("Items").classes("text-gray-700")

                if app.storage.user.get("is_superuser"):
                    with (
                        ui.item(on_click=lambda: ui.navigate.to("/users/create"))
                        .props("clickable")
                        .classes("w-full")
                    ):
                        with ui.item_section().props("avatar"):
                            ui.icon("person_add", color="gray-500")
                        with ui.item_section():
                            ui.label("Create User").classes("text-gray-700")

            with ui.list().classes("w-full"):
                ui.separator().classes("my-2")
                with (
                    ui.item(on_click=handle_logout).props("clickable").classes("w-full")
                ):
                    with ui.item_section().props("avatar"):
                        ui.icon("logout", color="gray-500")
                    with ui.item_section():
                        ui.label("Logout").classes("text-gray-700")

    with ui.column().classes("w-full p-4 md:p-8 items-center"):
        yield
