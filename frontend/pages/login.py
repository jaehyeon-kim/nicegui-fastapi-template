import httpx
from nicegui import app, ui
from frontend import state
from frontend.components import notifications
from backend.core.config import settings


@ui.page("/login")
def login_page():
    if state.get_auth():
        ui.navigate.to("/items")
        return

    async def handle_login():
        data = {"username": email.value, "password": password.value}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:8000/login/access-token", data=data
                )

            if response.status_code == 200:
                state.set_auth(response.json())
                app.storage.user["is_superuser"] = (
                    email.value == settings.FIRST_SUPERUSER
                )
                ui.navigate.to("/items")
            else:
                notifications.show_error(response.json().get("detail", "Login failed."))
        except httpx.RequestError:
            notifications.show_error("Could not connect to the backend.")

    with ui.card().classes("absolute-center"):
        ui.label("Login").classes("text-h4")
        email = ui.input("Email").props("autocomplete=username")
        password = ui.input("Password").props(
            "type=password autocomplete=current-password"
        )
        ui.button("Log in", on_click=handle_login).props("color=primary")
