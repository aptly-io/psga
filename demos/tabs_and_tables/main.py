# Copyright 2024 Francis Meyvis <psga@mikmak.fun>

"""A more realistic example on how to use PSGA"""

# pylint: disable=no-member,import-error,too-few-public-methods

import logging

import PySimpleGUI as sg
from model import Model
from rest import Server
from tab_one import TabOneCtr
from tab_two import TabTwoCtr

import psga

logging.basicConfig(level=logging.DEBUG)

# PSGA: use logging.DEBUG to monitor the PySimpleGui-events
logging.getLogger("PSGA").setLevel(logging.INFO)


class RootCtr(psga.Controller):
    """A MVC-controller that manages the root layout's tab-group"""

    def __init__(self, dispatcher: psga.Dispatcher, window: sg.Window):
        super().__init__(dispatcher)
        self._window = window
        self._tab = None

    @psga.action()
    def on_tab_group(self, values):
        """Triggers the activated tab to populate its model-data"""
        if self._tab != (tab := values[self.on_tab_group.name]):
            self._tab = tab
            self._window.write_event_value(tab, None)

    @staticmethod
    def layout():
        return [
            [
                [
                    sg.TabGroup(
                        [[TabOneCtr.layout(), TabTwoCtr.layout()]],
                        tab_location="topleft",
                        expand_x=True,
                        expand_y=True,
                        # PSGA: the TabGroup's key and corresponding handler are obvious; typo are unlikely
                        k=RootCtr.on_tab_group.name,
                        enable_events=True,
                    )
                ]
            ]
        ]


def main():
    """Setup the UI and process the PySimpleGui UI events"""

    sg.set_options(font=("Arial-black", 12))
    sg.change_look_and_feel("DarkTeal11")

    window = sg.Window("Breathtaking places", RootCtr.layout(), resizable=True, finalize=True)

    # PSGA: to dispatches all events to the registered handlers
    dispatcher = psga.Dispatcher()

    # PSGA: the model uses PSGA's dispatcher to handle PySimpleGui's background thread events
    model = Model(dispatcher, window)

    # PSGA: controllers register their action handlers with the given dispatcher
    RootCtr(dispatcher, window)
    TabOneCtr(dispatcher, window, model)
    TabTwoCtr(dispatcher, window, model)

    # PSGA: inject an event that makes the first tab load its table
    window.write_event_value(RootCtr.on_tab_group.name, TabOneCtr.on_tab.name)

    dispatcher.loop(window)  # PSGA: process the PySimpleGui-events; very simple "event loop"

    window.close()


if __name__ == "__main__":
    with Server.make_server().run_in_thread():
        main()
