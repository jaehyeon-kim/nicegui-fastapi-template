from nicegui import ui


def create_header(left_drawer: ui.left_drawer, title: str) -> None:
    """Creates the application header."""
    with ui.header(elevated=True).classes("items-center justify-between bg-slate-700"):
        with ui.row().classes("items-center"):
            ui.button(on_click=lambda: left_drawer.toggle(), icon="menu").props(
                "flat color=white"
            )
            ui.label(title).classes("text-h5")
