import httpx
from nicegui import ui
from frontend.layouts.dashboard import dashboard_frame
from frontend.components import notifications
from frontend import state


@ui.page("/items")
def items_page():
    with dashboard_frame(title="My Items"):
        items_grid = ui.grid(columns=3).classes("w-full gap-4")

        async def load_items():
            token = state.get_token()
            if not token:
                return
            try:
                headers = {"Authorization": token}
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        "http://localhost:8000/api/v1/items/", headers=headers
                    )

                if response.status_code == 200:
                    items_grid.clear()
                    with items_grid:
                        for item in response.json():
                            with ui.card():
                                ui.label(item["title"]).classes("text-bold")
                                ui.label(item["description"])
                else:
                    notifications.show_error("Failed to load items.")
            except httpx.RequestError:
                notifications.show_error("Could not connect to the backend.")

        with ui.dialog() as dialog, ui.card():
            ui.label("Create New Item").classes("text-h6")
            title_input = ui.input("Title")
            desc_input = ui.textarea("Description")

            async def perform_create():
                token = state.get_token()
                if not token:
                    return
                data = {"title": title_input.value, "description": desc_input.value}
                headers = {"Authorization": token}
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            "http://localhost:8000/api/v1/items/",
                            json=data,
                            headers=headers,
                        )

                    if response.status_code == 200:
                        notifications.show_success("Item created successfully!")
                        await load_items()
                        dialog.close()
                    elif response.status_code == 409:
                        notifications.show_error(
                            f"Conflict: {response.json().get('detail')}"
                        )
                    else:
                        notifications.show_error(
                            f"Error: {response.json().get('detail')}"
                        )
                except httpx.RequestError:
                    notifications.show_error("Could not connect to the backend.")

            ui.button("Create", on_click=perform_create)

        ui.button("Create Item", on_click=dialog.open, icon="add").props(
            "color=primary"
        )

        ui.timer(0.1, load_items, once=True)
