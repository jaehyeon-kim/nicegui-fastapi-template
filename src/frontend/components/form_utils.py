from typing import List
from nicegui import ui


def enable_button_on_user_inputs(inputs: List[ui.input], button: ui.button) -> None:
    """
    Enables a button if all provided input fields have a non-empty value.
    Disables it otherwise.
    """
    if all(inp.value for inp in inputs):
        button.enable()
    else:
        button.disable()
