import httpx
from nicegui import ui
from frontend import state
from frontend.components import notifications
from frontend.layouts.dashboard import dashboard_frame


@ui.page("/items")
def items_page():
    """Defines the page for displaying and creating user items."""
    with dashboard_frame(title="My Items"):
        items_grid = ui.grid().classes(
            "w-full gap-4 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4"
        )

        with ui.dialog() as dialog, ui.card().classes("min-w-[600px]"):
            ui.label("Create New Item").classes("text-h6")
            title_input = ui.input("Title").classes("w-full")
            desc_input = ui.textarea("Description").classes("w-full")
            ui.button(
                "Create",
                on_click=lambda: create_item(
                    title_input, desc_input, dialog, items_grid
                ),
            ).classes("w-full")

        ui.button("Create Item", on_click=dialog.open, icon="add").props(
            "color=primary"
        )
        ui.timer(0.1, lambda: load_items(items_grid), once=True)


async def load_items(grid: ui.grid):
    """Fetches items from the API and populates the grid with cards, including action buttons."""
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
            grid.clear()
            with grid:
                for item in response.json():
                    with ui.card().classes("p-0"):
                        ui.image(f"https://picsum.photos/600/400?random={item['id']}")
                        with ui.column().classes("p-4 w-full"):
                            ui.label(item["title"]).classes("text-xl font-semibold")
                            ui.separator().classes("w-full my-1")
                            ui.label(item["description"]).classes(
                                "text-sm line-clamp-3"
                            )

                            with ui.row().classes("w-full justify-end mt-4 gap-2"):
                                # Modify Button - opens its own dialog
                                with (
                                    ui.dialog() as modify_dialog,
                                    ui.card().classes("min-w-[600px]"),
                                ):
                                    ui.label("Modify Item").classes("text-h6")
                                    modify_title = ui.input(
                                        "Title", value=item["title"]
                                    ).classes("w-full")
                                    modify_desc = ui.textarea(
                                        "Description", value=item["description"]
                                    ).classes("w-full")
                                    # The lambda captures the item's specific data for the handler
                                    ui.button(
                                        "Save",
                                        on_click=lambda i=item,
                                        t=modify_title,
                                        d=modify_desc: update_item(
                                            i["id"], t, d, modify_dialog, grid
                                        ),
                                    ).classes("w-full")

                                ui.button(
                                    icon="edit", on_click=modify_dialog.open
                                ).props("flat dense")

                                # Delete Button - opens a confirmation dialog
                                with ui.dialog() as confirm_dialog, ui.card():
                                    ui.label(
                                        f"Are you sure you want to delete '{item['title']}'?"
                                    )
                                    with ui.row().classes("w-full justify-end"):
                                        ui.button(
                                            "Cancel",
                                            on_click=confirm_dialog.close,
                                            color="gray-100",
                                        )
                                        # The lambda captures the specific item_id for the handler
                                        ui.button(
                                            "Yes",
                                            on_click=lambda item_id=item[
                                                "id"
                                            ]: delete_item(item_id, grid),
                                            color="red",
                                        )

                                ui.button(
                                    icon="delete", on_click=confirm_dialog.open
                                ).props("flat dense color=red")
        else:
            notifications.show_error("Failed to load items.")
    except httpx.RequestError:
        notifications.show_error("Could not connect to the backend.")


async def create_item(
    title_input: ui.input,
    desc_input: ui.textarea,
    dialog_to_close: ui.dialog,
    items_grid: ui.grid,
):
    """Sends the new item data from the inputs to the API."""
    token = state.get_token()
    if not token:
        return
    data = {"title": title_input.value, "description": desc_input.value}
    headers = {"Authorization": token}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/v1/item/",
                json=data,
                headers=headers,
            )

        if response.status_code == 200:
            notifications.show_success("Item created successfully!")
            await load_items(items_grid)  # Pass the grid to the load function
            dialog_to_close.close()
        elif response.status_code == 409:
            notifications.show_error(f"Conflict: {response.json().get('detail')}")
        else:
            notifications.show_error(f"Error: {response.json().get('detail')}")
    except httpx.RequestError:
        notifications.show_error("Could not connect to the backend.")


async def update_item(
    item_id: int,
    title_input: ui.input,
    desc_input: ui.textarea,
    dialog: ui.dialog,
    grid: ui.grid,
):
    """Makes an API call to update an item and reloads the grid on success."""
    token = state.get_token()
    if not token:
        return
    data = {"title": title_input.value, "description": desc_input.value}
    try:
        headers = {"Authorization": token}
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"http://localhost:8000/api/v1/item/{item_id}",
                json=data,
                headers=headers,
            )
        if response.status_code == 200:
            notifications.show_success("Item updated successfully.")
            dialog.close()
            await load_items(grid)
        else:
            notifications.show_error(f"Error: {response.json().get('detail')}")
    except httpx.RequestError:
        notifications.show_error("Could not connect to the backend.")


async def delete_item(item_id: int, grid: ui.grid):
    """Makes an API call to delete an item and reloads the grid on success."""
    token = state.get_token()
    if not token:
        return
    try:
        headers = {"Authorization": token}
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"http://localhost:8000/api/v1/item/{item_id}", headers=headers
            )
        if response.status_code == 200:
            notifications.show_success("Item deleted successfully.")
            await load_items(grid)  # Refresh the items grid
        else:
            notifications.show_error(f"Error: {response.json().get('detail')}")
    except httpx.RequestError:
        notifications.show_error("Could not connect to the backend.")
