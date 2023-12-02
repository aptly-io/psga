# Copyright 2023 Francis Meyvis <psga@mikmak.fun>

"""Minimalistic Controller (as in the MVC paradigm) for PySimpleGUI."""

import functools
import logging
from typing import Callable, Dict, Hashable, List, Optional, Protocol

import PySimpleGUI as sg
from typing_extensions import Self


class Action(Protocol):
    """Bundles the event's name and handler"""

    # pylint: disable=too-few-public-methods

    name: str
    keys: Optional[List[Hashable]]

    def __call__(self, values=None):
        """"""


def action(name: Optional[str] = None, keys: Optional[List[Hashable]] = None):
    """Turns an event handler into an action using given name as event's name"""
    # pylint: disable=protected-access

    action._counter = getattr(action, "_counter", 0) + 1

    def _decorator_action(handler: Callable) -> Action:
        @functools.wraps(handler)
        def _wrapper_action(*args, **kwargs):
            handler(*args, **kwargs)

        _wrapper_action.name = (
            handler.__name__ + "_" + str(action._counter) if name is None else name
        )
        _wrapper_action.keys = keys

        return _wrapper_action

    return _decorator_action


class Dispatcher:
    """Dispatcher an event's values to a matching handler."""

    def __init__(self):
        self._handlers: Dict[str, Action] = {}

    def register(self, handler: Action) -> Self:
        """Registers given action's handler by its name and keys."""
        self._handlers.setdefault(handler.name, []).append(handler)
        if handler.keys is not None:
            for key in handler.keys:
                self._handlers.setdefault(key, []).append(handler)
        return self

    def dispatch(self, event, values) -> bool:
        """Returns True if a handler was found and invoked for given event."""
        if isinstance(event, tuple):
            # TODO are there other type of "tuple"-events?
            name = event[0] if "+CLICKED+" == event[1] else None
        else:
            if 2 == len(menu_event := event.rsplit(sg.MENU_KEY_SEPARATOR, 1)):
                _, name = menu_event  # extract the key from a menu-item event having a name
            else:
                name = event

        if (handlers := self._handlers.get(name, None)) is not None:
            for handler in handlers:
                handler(values)
            return True
        return False

    def loop(self, window: sg.Window, timeout_ms=None, timeout_key=sg.TIMEOUT_KEY):
        """Process window's events and values until the Exit event or given timeout"""
        log = logging.getLogger("PSGA")
        while True:
            event, values = window.read(timeout_ms, timeout_key)
            log.debug("event %s, values: %s", event, values)

            if event in {sg.WIN_CLOSED, "Exit"}:
                break

            if self.dispatch(event, values):
                continue

            log.warning("Unhandled event: %s", event)


class Controller:
    """Groups and registers actions to a dispatcher."""

    # pylint: disable=too-few-public-methods

    def __init__(self, dispatcher: Dispatcher, window: Optional[sg.Window] = None):
        self.window = window
        for method in [
            func
            for func in map(lambda name: getattr(self, name), dir(self))
            if callable(func) and hasattr(func, "name")
        ]:
            dispatcher.register(method)
