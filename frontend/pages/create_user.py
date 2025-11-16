import httpx
from nicegui import app, ui
from frontend.layouts.dashboard import dashboard_frame
from frontend.components import notifications
from frontend import state


@ui.page("/users/create")
def create_user_page():
    with dashboard_frame(title="Create New User"):
        if not app.storage.user.get("is_superuser"):
            ui.label("You don't have permission to access this page.").classes(
                "text-red-500"
            )
            return

        with ui.card().classes("w-full max-w-md"):
            ui.label("Create a New User").classes("text-h5")
            email = ui.input("Email")
            password = ui.input("Password").props("type=password")
            is_superuser = ui.checkbox("Is Superuser?")

            async def handle_create():
                token = state.get_token()
                if not token:
                    return

                data = {
                    "email": email.value,
                    "password": password.value,
                    "is_superuser": is_superuser.value,
                }
                headers = {"Authorization": token}
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            "http://localhost:8000/api/v1/users/",
                            json=data,
                            headers=headers,
                        )

                    if response.status_code == 200:
                        notifications.show_success(f"User {email.value} created!")
                        email.value = ""
                        password.value = ""
                        is_superuser.value = False
                    else:
                        notifications.show_error(response.json().get("detail"))
                except httpx.RequestError:
                    notifications.show_error("Could not connect to backend.")

            ui.button("Create User", on_click=handle_create).props("color=primary")
