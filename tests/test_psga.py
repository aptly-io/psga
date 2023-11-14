from typing import Callable
from unittest.mock import MagicMock

import psga


def test_action_implicit_key():
    @psga.action()
    def my_action(_):
        pass

    assert isinstance(my_action, Callable)
    assert hasattr(my_action, "key")
    assert getattr(my_action, "key") == my_action.key


def test_action_explicit_key():
    @psga.action(key="my_action")
    def my_action(_):
        pass

    assert isinstance(my_action, Callable)
    assert hasattr(my_action, "key")
    assert getattr(my_action, "key") == "my_action"
    assert getattr(my_action, "key") == my_action.key


def test_dispatcher_register_one():
    handler1_invoked = 0

    @psga.action(key="event")
    def hander1(_):
        nonlocal handler1_invoked
        handler1_invoked += 1

    dispatcher = psga.Dispatcher()
    dispatcher.register(hander1)

    assert not dispatcher.dispatch("wrong_event", {})
    assert handler1_invoked == 0

    assert dispatcher.dispatch("event", {})
    assert handler1_invoked == 1

    assert dispatcher.dispatch(hander1.key, {})
    assert handler1_invoked == 2


def test_dispatcher_register_multiple():
    handler1_invoked = handler2_invoked = 0

    @psga.action()
    def handler1(_):
        nonlocal handler1_invoked
        handler1_invoked += 1

    @psga.action(handler1.key)
    def handler2(_):
        nonlocal handler2_invoked
        handler2_invoked += 1

    dispatcher = psga.Dispatcher()
    dispatcher.register(handler1).register(handler2)

    assert not dispatcher.dispatch("wrong_event", {})
    assert handler1_invoked == 0
    assert handler2_invoked == 0

    assert dispatcher.dispatch(handler1.key, {})
    assert handler1_invoked == 1
    assert handler2_invoked == 1

    assert dispatcher.dispatch(handler2.key, {})
    assert handler1_invoked == 2
    assert handler2_invoked == 2


def test_controller():
    class _MyController(psga.Controller):
        answer = 0

        @psga.action(key="universial_question")
        def on_ask(self, values):
            _MyController.answer = values

    dispatcher = psga.Dispatcher()
    controller = _MyController(dispatcher)

    assert controller.answer == 0
    dispatcher.dispatch(controller.on_ask.key, 42)
    assert controller.answer == 42


def test_dispatcher_loop():
    mock_window = MagicMock(return_value=[("Ok", {}), ("Exit", {})])

    mock_window = MagicMock()
    mock_window.configure_mock(
        **{
            "read.side_effect": [
                ("Ok", {}),
                ("Unknown", {}),
                (("-UNKNOWN TABLE KEY-", "+CICKED+", (3, 3)), {}),
                ("Unknown menu::unknown_menu_key", {}),
                ("Exit", {}),
            ],
        }
    )

    handler1_invoked = 0

    @psga.action(key="Ok")
    def hander1(_):
        nonlocal handler1_invoked
        handler1_invoked += 1

    dispatcher = psga.Dispatcher()
    dispatcher.register(hander1)

    dispatcher.loop(mock_window)

    assert handler1_invoked == 1
