# Copyright 2023 Francis Meyvis <psga@mikmak.fun>

"""Simple check psga features"""

from psga import Controller, Dispatcher, action


class _MyController(Controller):
    answer = 0

    @action(name="universal_question")
    def on_ask(self, values):
        """with explicit name"""
        _MyController.answer = values

    @action()
    def on_answer(self, values):
        """with implicit name"""
        _MyController.answer = values


dispatcher = Dispatcher()
controller = _MyController(dispatcher)

assert controller.answer == 0
dispatcher.dispatch("universal_question", 42)
assert controller.answer == 42

QUESTION = "Answer to the Ultimate Question of Life"
dispatcher.dispatch(controller.on_answer.name, QUESTION)
assert controller.answer == QUESTION
