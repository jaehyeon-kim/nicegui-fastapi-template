from contextlib import contextmanager
from nicegui import ui
from frontend import state
from frontend.components import header


@contextmanager
def dashboard_frame(title: str):
    """
    A layout for all protected dashboard pages.
    - It checks for authentication and redirects to /login if the user is not logged in.
    - It provides a consistent header and page structure.
    """
    if not state.get_auth():
        ui.navigate.to("/login")
        return

    with header.main_header(title):
        with ui.column().classes("w-full p-4 md:p-8 items-center"):
            yield
