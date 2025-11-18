from nicegui import ui


def create_footer() -> None:
    """Creates the application footer."""
    with ui.footer(elevated=True).classes(
        "bg-slate-700 text-white items-center justify-center p-4"
    ):
        ui.label("© 2025 MyApp Name. All rights reserved.")
