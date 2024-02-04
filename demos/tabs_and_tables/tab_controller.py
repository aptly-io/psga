# Copyright 2024 Francis Meyvis <psga@mikmak.fun>

"""Common base for the MVC-controller"""

# pylint: disable=import-error

from typing import List

import PySimpleGUI as sg
from model import Model
from requests import HTTPError

import psga


class TabController(psga.Controller):
    """Common base for the MVC-controllers"""

    def __init__(
        self,
        dispatcher: psga.Dispatcher,
        window: sg.Window,
        model: Model,
        resource: str,
        table_name: str,
        headings=List[str],
    ):
        super().__init__(dispatcher)
        self._window = window
        self._model = model
        self.resource = resource
        self.table_name = table_name
        self.headings = headings
        self._data = []

    def refresh(self):
        """trigger a data model fetch"""
        self._model.read(self.resource)

    def on_data_handler(self, value):
        """handle the data in the REST response"""
        if isinstance(value, HTTPError):
            try:
                text = (
                    f"{value.response.json()['detail']}\n\n"
                    + f"(HTTP status code: {value.response.status_code} - {value.response.reason})"
                )
            except Exception:
                text = value
            sg.popup(text, title="Error", keep_on_top=True)
        elif isinstance(value, Exception):
            sg.popup(f"{value}", title="Error", keep_on_top=True)
        else:
            self._data = value
            data = (
                map(lambda i: [i.get(e, "") for e in self.headings], self._data)
                if self._data
                else []
            )
            self._window[self.table_name].update(values=data)

    def create_dialog(self, title: str):
        """input and confirm a new model data"""
        layout = [
            [sg.T("Identifier:", size=(10, 1)), sg.I("", k="id", expand_x=True)],
            [sg.T("Name:", size=(10, 1)), sg.I("", k="name", expand_x=True)],
            [sg.T("Location:", size=(10, 1)), sg.I("", k="location", expand_x=True)],
            [sg.T("Description:", size=(10, 1))],
            [sg.ML("", k="description", size=(80, 5), expand_x=True, expand_y=True)],
            [sg.Push(), sg.B("Cancel"), sg.B("Create", k="confirm")],
        ]

        window = sg.Window(title, layout, resizable=True, finalize=True, keep_on_top=True)
        window.bind("<Escape>", "-ESCAPE-")

        event, values = window.read()
        window.close()

        if event == "confirm":
            return {
                key: val
                for key, val in values.items()
                if key in ["id", "name", "location", "description"]
            }
        return None

    def delete_dialog(self, title: str, values):
        """confirm removal of model data"""
        layout = [
            [sg.T("Identifier:", size=(10, 1)), sg.I("", k="id", expand_x=True)],
            [sg.T("Name:", size=(10, 1)), sg.I("", k="name", expand_x=True)],
            [sg.T("Description:", size=(10, 1))],
            [sg.Multiline("", k="description", size=(80, 5), expand_x=True, expand_y=True)],
            [sg.Push(), sg.B("Cancel"), sg.B("Delete", button_color="red", k="confirm")],
        ]

        window = sg.Window(title, layout, resizable=True, finalize=True, keep_on_top=True)
        window.bind("<Escape>", "-ESCAPE-")

        for element in window.element_list():
            if element.key in values:
                element.update(values[element.key])

        event, _ = window.read()
        window.close()

        return str(values["id"]) if event == "confirm" else None
