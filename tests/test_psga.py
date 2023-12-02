import logging
from typing import Callable
from unittest.mock import MagicMock

import psga


def test_action_implicit_name():
    @psga.action()
    def my_action(_):
        pass

    assert isinstance(my_action, Callable)
    assert hasattr(my_action, "name")
    assert getattr(my_action, "name") == my_action.name

    assert hasattr(my_action, "keys")
    assert getattr(my_action, "keys") == None


def test_action_explicit_name():
    @psga.action(name="my_action")
    def my_action(_):
        pass

    assert isinstance(my_action, Callable)
    assert hasattr(my_action, "name")
    assert getattr(my_action, "name") == "my_action"
    assert getattr(my_action, "name") == my_action.name

    assert hasattr(my_action, "keys")
    assert getattr(my_action, "keys") == None


def test_action_explicit_keys():
    KEYS = ["my_key"]

    @psga.action(keys=KEYS)
    def my_action(_):
        pass

    assert isinstance(my_action, Callable)
    assert hasattr(my_action, "name")
    assert getattr(my_action, "name") == my_action.name

    assert hasattr(my_action, "keys")
    assert getattr(my_action, "keys") == KEYS


def test_action_explicit_name_explicit_keys():
    KEYS = ["my_key"]

    @psga.action(name="my_action", keys=KEYS)
    def my_action(_):
        pass

    assert isinstance(my_action, Callable)
    assert hasattr(my_action, "name")
    assert getattr(my_action, "name") == "my_action"
    assert getattr(my_action, "name") == my_action.name

    assert hasattr(my_action, "keys")
    assert getattr(my_action, "keys") == KEYS


def test_dispatcher_register_one():
    handler1_invoked = 0

    @psga.action(name="event")
    def handler1(values):
        nonlocal handler1_invoked
        handler1_invoked += 1
        assert values == {1: 1}

    dispatcher = psga.Dispatcher()
    dispatcher.register(handler1)

    assert not dispatcher.dispatch("wrong_event", {1: 1})
    assert handler1_invoked == 0

    assert dispatcher.dispatch("event", {1: 1})
    assert handler1_invoked == 1

    assert dispatcher.dispatch(handler1.name, {1: 1})
    assert handler1_invoked == 2


def test_dispatcher_register_multiple():
    handler1_invoked = handler2_invoked = 0

    @psga.action()
    def handler1(values):
        nonlocal handler1_invoked
        handler1_invoked += 1
        assert values == {1: 1}

    @psga.action(handler1.name)
    def handler2(values):
        nonlocal handler2_invoked
        handler2_invoked += 1
        assert values == {1: 1}

    dispatcher = psga.Dispatcher()
    dispatcher.register(handler1).register(handler2)

    assert not dispatcher.dispatch("wrong_event", {1: 1})
    assert handler1_invoked == 0
    assert handler2_invoked == 0

    assert dispatcher.dispatch(handler1.name, {1: 1})
    assert handler1_invoked == 1
    assert handler2_invoked == 1

    assert dispatcher.dispatch(handler2.name, {1: 1})
    assert handler1_invoked == 2
    assert handler2_invoked == 2


def test_controller():
    class _MyController(psga.Controller):
        answer = 0

        @psga.action(name="universal_question")
        def on_ask(self, values):
            _MyController.answer = values

    dispatcher = psga.Dispatcher()
    controller = _MyController(dispatcher)

    assert controller.answer == 0
    dispatcher.dispatch(controller.on_ask.name, 42)
    assert controller.answer == 42


def test_dispatcher_loop():
    logging.getLogger("PSGA").setLevel(logging.DEBUG)

    mock_window = MagicMock()
    mock_window.configure_mock(
        **{
            "read.side_effect": [
                ("Ok", {1: 1}),
                ("Unknown", {2: 2}),
                ("Unregistered", {3: 3}),
                (("-TABLE KEY-", "+CLICKED+", (3, 3)), {4: 4}),
                ("Unknown menu::menu_key", {5: 5}),
                ("-INPUT 1-", {6: 6}),
                ("-BUTTON SAVE-", {6: 6}),
                ("Exit", {6: 6}),
            ]
        }
    )

    handler1_invoked = 0
    handler2_invoked = 0
    handler3_invoked = 0
    handler4_invoked = 0
    handler5_invoked = 0

    @psga.action(name="Ok")
    def handler1(values):
        nonlocal handler1_invoked
        handler1_invoked += 1
        assert values == {1: 1}

    @psga.action(name="Unregistered")
    def handler4(values):
        nonlocal handler4_invoked
        handler4_invoked += 1
        assert values == {3: 3}

    @psga.action(name="-TABLE KEY-")
    def handler2(values):
        nonlocal handler2_invoked
        handler2_invoked += 1
        assert values == {4: 4}

    @psga.action(name="menu_key")
    def handler3(values):
        nonlocal handler3_invoked
        handler3_invoked += 1
        assert values == {5: 5}

    @psga.action(keys=["-INPUT 1-", "-BUTTON SAVE-"])
    def handler5(values):
        nonlocal handler5_invoked
        handler5_invoked += 1
        assert values == {6: 6}

    dispatcher = psga.Dispatcher()
    dispatcher.register(handler1)
    dispatcher.register(handler2)
    dispatcher.register(handler3)
    dispatcher.register(handler5)

    dispatcher.loop(mock_window)

    assert handler1_invoked == 1
    assert handler2_invoked == 1
    assert handler3_invoked == 1
    assert handler4_invoked == 0
    assert handler5_invoked == 2
