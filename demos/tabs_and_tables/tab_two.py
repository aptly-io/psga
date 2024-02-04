# Copyright 2024 Francis Meyvis <psga@mikmak.fun>

"""MVC-controller that mediates between a layout and data model for trails"""

# pylint: disable=no-member,import-error

import json

import PySimpleGUI as sg
from model import Model
from tab_controller import TabController

import psga


class TabTwoCtr(TabController):
    """MVC-controller that mediates between the view and the city data model"""

    headings = ["id", "name", "location", "description"]

    def __init__(self, dispatcher: psga.Dispatcher, window: sg.Window, model: Model):
        super().__init__(
            dispatcher,
            window,
            model,
            TabTwoCtr._on_data.name,
            TabTwoCtr._on_table_click.name,
            self.headings,
        )

    @psga.action()
    def on_tab(self, _):
        """refresh the data"""
        self.refresh()

    @psga.action(name="demo/cities")
    def _on_data(self, values):
        self.on_data_handler(values[self._on_data.name])

    @psga.action()
    def _on_table_click(self, values):
        menus = [
            f"!Copy::{self._on_copy.name}",
            "---",
            f"!Create…::{self._on_create.name}",
            f"!Delete…::{self._on_delete.name}",
        ]
        indices = values[self.table_name]
        if 0 == len(indices):
            menu_indices = [2]
        elif 1 == len(indices):
            menu_indices = [0, 2, 3]
        else:
            menu_indices = [0, 2]
        for index in menu_indices:
            menus[index] = menus[index][1:]
        self._window[self.table_name].set_right_click_menu(["", [menus]])

    @psga.action()
    def _on_copy(self, values):
        sg.clipboard_set(
            json.dumps([self._data[index] for index in values[self.table_name]], indent=4)
        )

    @psga.action()
    def _on_create(self, _):
        if (result := self.create_dialog("Create a new city")) is not None:
            self._model.create(self._on_data.name, **result)

    @psga.action()
    def _on_delete(self, values):
        if 1 == len(indices := values[self.table_name]):
            selection = self._data[indices[0]]
            if (result := self.delete_dialog("Delete this city?", selection)) is not None:
                self._model.delete(self._on_data.name, result)

    @staticmethod
    def layout() -> sg.Element:
        return sg.Tab(
            "Awsome Cities",
            [
                [
                    sg.Table(
                        key=TabTwoCtr._on_table_click.name,
                        font=("Arial", 12),
                        values=[[]],
                        headings=TabTwoCtr.headings,
                        col_widths=[3, 20, 20, 40],
                        # only implemented in unreleased 4.61 on github
                        # cols_justification=["c", "c", "l"],
                        auto_size_columns=False,
                        display_row_numbers=False,
                        justification="center",
                        row_height=40,
                        max_col_width=50,
                        enable_events=True,
                        expand_x=False,
                        expand_y=True,
                        vertical_scroll_only=False,
                        enable_click_events=True,
                        # right_click_menu=, # set by detecting right click
                        right_click_selects=True,
                        select_mode=sg.TABLE_SELECT_MODE_EXTENDED,
                        tooltip="Right-click to open the menu",
                        num_rows=5,
                    )
                ]
            ],
            k=TabTwoCtr.on_tab.name,
        )
