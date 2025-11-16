from nicegui import ui


def show_error(message: str):
    """
    Displays a persistent error message to the user.
    """
    ui.notify(message, color="negative", close_button="OK", multi_line=True)


def show_success(message: str):
    """
    Displays a short-lived success message to the user.
    """
    ui.notify(message, color="positive")
