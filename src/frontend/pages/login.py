from fastapi import HTTPException
from nicegui import app, ui
from src.repositories.user import user_repo
from src.core import security
from src.db.session import get_db_context
from src.frontend import state
from src.frontend.components.form_utils import enable_button_on_user_inputs
from src.frontend.components import notifications


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
    try:
        with get_db_context() as db:
            user = user_repo.authenticate(
                db=db, email=email_input.value, password=password_input.value
            )
            auth_data = {
                "access_token": security.create_access_token(user.id),
                "token_type": "bearer",
            }
            state.set_auth(auth_data)
            app.storage.user["is_superuser"] = user.is_superuser
            ui.navigate.to("/items")
    except HTTPException as e:
        notifications.show_error(e.detail)
    except Exception as e:
        notifications.show_error(f"An unexpected error occurred: {e}")
