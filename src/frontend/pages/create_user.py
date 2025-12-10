from fastapi import HTTPException
from nicegui import app, ui
from src.models import UserCreate
from src.db.session import get_db_context
from src.repositories.user import user_repo
from src.frontend.layouts.default import dashboard_frame
from src.frontend.components.auth_utils import get_current_user_from_state
from src.frontend.components.form_utils import enable_button_on_user_inputs
from src.frontend.components import notifications


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
    try:
        with get_db_context() as db:
            current_user = get_current_user_from_state(db)
            if not current_user.is_superuser:
                raise HTTPException(
                    status_code=403, detail="You do not have enough privileges."
                )
            user_in = UserCreate(
                email=email_input.value,
                password=password_input.value,
                is_superuser=is_superuser_checkbox.value,
            )
            user_repo.register(db=db, obj_in=user_in)

        notifications.show_success(f"User '{email_input.value}' created successfully!")
        email_input.value = ""
        password_input.value = ""
        is_superuser_checkbox.value = False
    except HTTPException as e:
        notifications.show_error(e.detail)
    except Exception as e:
        notifications.show_error(f"An unexpected error occurred: {e}")
