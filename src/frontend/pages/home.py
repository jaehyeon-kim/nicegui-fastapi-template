from nicegui import ui
from src.frontend import state


@ui.page("/")
async def home_page():
    """
    Redirects the user based on their authentication status.
    - Authenticated users are sent to the items dashboard.
    - Unauthenticated users are sent to the login page.
    """
    if not state.get_auth():
        ui.navigate.to("/login")
    else:
        ui.navigate.to("/items")
