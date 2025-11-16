from contextlib import contextmanager
from nicegui import app, ui
from frontend.state import clear_auth


@contextmanager
def main_header(title: str):
    """
    A context manager that creates a consistent header for all pages.
    """
    with ui.header(elevated=True).classes(
        "items-center justify-between text-white bg-primary"
    ):
        ui.label(title).classes("text-2xl")
        with ui.row().classes("items-center"):
            if app.storage.user.get("is_superuser"):
                ui.link("Create User", "/users/create").classes("text-white")
            ui.link("Items", "/items").classes("text-white ml-4")

            async def handle_logout():
                clear_auth()
                app.storage.user.clear()
                ui.navigate.to("/login")

            ui.button("Logout", on_click=handle_logout, icon="logout").props(
                "flat color=white"
            )
    yield
