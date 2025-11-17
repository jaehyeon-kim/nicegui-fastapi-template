import httpx
from nicegui import app, ui
from frontend import state
from frontend.layouts.dashboard import dashboard_frame
from frontend.components.form_helpers import enable_button_on_user_inputs
from frontend.components import notifications


@ui.page("/users/create")
def create_user_page():
    """Defines the page for creating a new user."""
    with dashboard_frame(title="Create a User"):
        if not app.storage.user.get("is_superuser"):
            ui.label("You don't have permission to access this page.").classes(
                "text-red-500"
            )
            return

        with ui.card().classes("w-full max-w-md p-8"):
            ui.label("Create a New User").classes("text-h4")

            email = (
                ui.input("Email")
                .props("autocomplete=username outlined")
                .classes("w-full")
            )
            password = (
                ui.input("Password")
                .props("type=password autocomplete=current-password outlined")
                .classes("w-full")
            )
            is_superuser = ui.checkbox("Is Superuser?").classes("w-full")

            user_button = (
                ui.button("Create User").props("color=primary").classes("w-full")
            )

            user_button.on("click", lambda: create_user(email, password, is_superuser))
            email.on(
                "keydown.enter", lambda: create_user(email, password, is_superuser)
            )
            password.on(
                "keydown.enter", lambda: create_user(email, password, is_superuser)
            )

            email.on(
                "update:model-value",
                lambda: enable_button_on_user_inputs([email, password], user_button),
            )
            password.on(
                "update:model-value",
                lambda: enable_button_on_user_inputs([email, password], user_button),
            )

            # Set initial button state
            enable_button_on_user_inputs([email, password], user_button)


async def create_user(
    email_input: ui.input, password_input: ui.input, is_superuser_checkbox: ui.checkbox
):
    """Creates a new user using data from the input elements."""
    token = state.get_token()
    if not token:
        return
    data = {
        "email": email_input.value,
        "password": password_input.value,
        "is_superuser": is_superuser_checkbox.value,
    }
    headers = {"Authorization": token}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/v1/user/", json=data, headers=headers
            )
        if response.status_code == 200:
            notifications.show_success(f"User {email_input.value} created!")
            email_input.value = ""
            password_input.value = ""
            is_superuser_checkbox.value = False
        else:
            notifications.show_error(response.json().get("detail"))
    except httpx.RequestError:
        notifications.show_error("Could not connect to backend.")
