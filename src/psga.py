# Copyright 2023 Francis Meyvis <psga@mikmak.fun>

"""Minimalistic Controller (as in the MVC paradigm) for PySimpleGUI."""

import functools
from typing import Callable, Dict, Protocol
from typing_extensions import Self

import PySimpleGUI as sg


class Action(Protocol):
    """Bundles the event's name and handler"""

    key: str

    def __call__(self, values=None):
        """"""


def action(key: str | None = None):
    """Turns an event handler into an action using given key as event's name"""

    action._counter = getattr(action, "_counter", 0) + 1

    def _decorator_action(handler: Callable) -> Action:
        @functools.wraps(handler)
        def _wrapper_action(*args, **kwargs):
            handler(*args, **kwargs)

        _wrapper_action.key = handler.__name__ + "_" + str(action._counter) if key is None else key

        return _wrapper_action

    return _decorator_action


class Dispatcher:
    """Dispatcher an event's values to a matching handler."""

    def __init__(self):
        self._handlers: Dict[str, Action] = {}

    def register(self, handler: Action) -> Self:
        """Registers given action's handler by its key."""
        self._handlers.setdefault(handler.key, []).append(handler)
        return self

    def dispatch(self, event, values) -> bool:
        """Returns True if a handler was found and invoked for given event."""
        if isinstance(event, tuple):
            # TODO are there other type of "tuple"-events?
            key = event[0] if "+CLICKED+" == event[1] else None
        else:
            if 2 == len(menu_event := event.rsplit(sg.MENU_KEY_SEPARATOR, 1)):
                _, key = menu_event  # extract the key from a menu-item event having a key
            else:
                key = event

        if (handlers := self._handlers.get(key, None)) is not None:
            for handler in handlers:
                handler(values)
            return True
        return False

    def loop(self, window: sg.Window):
        """Process window's events and values until the Exit event."""
        while True:
            event, values = window.read()
            print(f"#### LOOP event: {event} values: {values}\n")

            if event in {sg.WIN_CLOSED, "Exit"}:
                break

            if self.dispatch(event, values):
                continue

            print(f"Unhandled event: {event}, values: {values}")


class Controller:
    """Groups and registers actions to a dispatcher."""

    def __init__(self, dispatcher: Dispatcher, window: sg.Window | None = None):
        self.window = window
        for method in [
            func
            for func in map(lambda name: getattr(self, name), dir(self))
            if callable(func) and hasattr(func, "key")
        ]:
            dispatcher.register(method)
