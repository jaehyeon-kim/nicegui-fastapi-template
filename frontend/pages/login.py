import httpx
from nicegui import app, ui
from frontend import state
from frontend.components import notifications


@ui.page("/login")
def login_page():
    if state.get_auth():
        ui.navigate.to("/items")
        return

    async def handle_login():
        """
        Sends user credentials to the backend. This is only called when the
        login button is enabled (i.e., both fields have content).
        """
        if not email.validate() or not password.validate():
            return

        data = {"username": email.value, "password": password.value}
        try:
            url = "http://localhost:8000/login/access-token"
            async with httpx.AsyncClient() as client:
                response = await client.post(url, data=data)

            if response.status_code == 200:
                state.set_auth(response.json())
                app.storage.user["is_superuser"] = email.value == "admin@example.com"
                ui.navigate.to("/items")
            else:
                notifications.show_error(response.json().get("detail", "Login failed."))
        except httpx.RequestError:
            notifications.show_error("Could not connect to the backend.")

    def update_button_state() -> None:
        """Enable the login button only if both fields have a non-empty value."""
        if email.value and password.value:
            login_button.enable()
        else:
            login_button.disable()

    with ui.card().classes("absolute-center w-full max-w-md p-8"):
        ui.label("Login").classes("text-h4")
        email = (
            ui.input("Email")
            .props("autocomplete=username outlined")
            .classes("w-full")
            .on("keydown.enter", handle_login)
            .on("value_change", update_button_state)
        )

        password = (
            ui.input("Password")
            .props("type=password autocomplete=current-password outlined")
            .classes("w-full")
            .on("keydown.enter", handle_login)
            .on("value_change", update_button_state)
        )

        login_button = (
            ui.button("Log in", on_click=handle_login)
            .props("color=primary")
            .classes("w-full")
        )

    # Set the initial disabled state of the button
    update_button_state()
