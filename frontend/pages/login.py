import httpx
from nicegui import app, ui
from frontend import state
from frontend.components.form_helpers import enable_button_on_user_inputs
from frontend.components import notifications


@ui.page("/login")
def login_page():
    """Defines the page for login."""
    if state.get_auth():
        ui.navigate.to("/items")
        return

    with ui.card().classes("absolute-center w-full max-w-md p-8"):
        ui.label("Login").classes("text-h4")

        email = (
            ui.input("Email").props("autocomplete=username outlined").classes("w-full")
        )
        password = (
            ui.input("Password")
            .props("type=password autocomplete=current-password outlined")
            .classes("w-full")
        )
        login_button = ui.button("Log in").props("color=primary").classes("w-full")

        login_button.on("click", lambda: perform_login(email, password))
        email.on("keydown.enter", lambda: perform_login(email, password))
        password.on("keydown.enter", lambda: perform_login(email, password))

        email.on(
            "update:model-value",
            lambda: enable_button_on_user_inputs([email, password], login_button),
        )
        password.on(
            "update:model-value",
            lambda: enable_button_on_user_inputs([email, password], login_button),
        )

        # Set the initial disabled state of the button
        enable_button_on_user_inputs([email, password], login_button)


async def perform_login(email_input: ui.input, password_input: ui.input):
    """Sends user credentials to the backend."""
    if not email_input.validate() or not password_input.validate():
        return
    data = {"username": email_input.value, "password": password_input.value}
    try:
        url = "http://localhost:8000/login/access-token"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data)
        if response.status_code == 200:
            state.set_auth(response.json())
            app.storage.user["is_superuser"] = email_input.value == "admin@example.com"
            ui.navigate.to("/items")
        else:
            notifications.show_error(response.json().get("detail", "Login failed."))
    except httpx.RequestError:
        notifications.show_error("Could not connect to the backend.")
