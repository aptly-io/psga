# PySimpleGUI's Actions (PSGA) simplify event handling

<p align="center">
<a href="https://github.com/aptly-io/psga/actions"><img alt="Actions Status" src="https://github.com/aptly-io/psga/actions/workflows/CI.yaml/badge.svg"></a>
<a href="https://pypi.org/project/psga/"><img alt="License" src="https://img.shields.io/pypi/l/psga.svg"></a>
<a href="https://pypi.python.org/pypi/psga/"><img alt="PyPi Version" src="https://img.shields.io/pypi/v/psga.svg"></a>
</p>


## Intro

PySimpleGUI is like the _View_ in the _Model-View-Controller_ paradigm.
For less complex user interfaces its typical if-event-then-action loop
(that takes the role of _Controller_) works fine.
However the event-loop's if-then-else becomes difficult to maintain
for user interfaces with a large number of elements.

PSGA tries to mitigate this by adding the following:
- The `@psga.action()` decorator turns a method (or function) in an `Action`.
  This action wraps both a handler and a event name (`name`)
  to respectively handle and name the event (recognized by intellisense).
  The optional `keys` decorator parameter allows for additional keys to invoke the handler.
- A `Controller` class groups and registers related handlers for processing
  user interaction and updating the corresponding view.
  This could hold your business/logic state.
  Using controllers the source code is more maintainable, structured.
- A `Dispatcher` class has a loop that reads the events from a `sg.Window`.
  Each event's value is then dispatched to the handler
  that was prior registered by its `Controller`('s).
  Manual registering is also possible (see the examples).

It is easy to gradually refactor existing source code with the _PSGA_ feature.

PySimpleGUI avoids concepts like _call-backs_, _classes_...
In a way, `action` and `Controller` brings that back (so you might not like PSGA's concept).


## Examples

### Hello world

PySimpleGUI shows the classic _hello world_ in its [Jump-Start section](https://www.pysimplegui.org/en/latest/).

The source code below illustrates how PSGA _could_ fit in:
1. Define a function that acts when the _Ok_ button is clicked.
2. Instantiate the dispatcher that will trigger the handler whenever the _Ok_ event is fired.

Note that this simple example does not use a `Controller`.
Note that the `demos/hello_world.py` example does the same in a slightly different way.

```python
import PySimpleGUI as sg
import psga

# PSGA: define an action for the Ok button
@psga.action(name="Ok")
def on_ok(values):
    print('You entered ', values[0])

sg.theme('DarkAmber')   # Add a touch of color
# All the stuff inside your window.
layout = [  [sg.Text('Some text on Row 1')],
            [sg.Text('Enter something on Row 2'), sg.InputText()],
            [sg.Button('Exit'), sg.Button('Ok')] ]

# Create the Window
window = sg.Window('Window Title', layout)

# PSGA: initiate the dispatcher, register the handler and process the window's events
psga.Dispatcher().register(on_ok).loop(window)

window.close()
```


### Example with a Controller

It shows PSGA's concept without using any PySimpleGUI functionality.
It illustrates the use of a `Controller` in combination with
the `action` decorator and a `Dispatcher`.

```python
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

dispatcher.dispatch("universal_question", 42)
assert controller.answer == 42

QUESTION = "Answer to the Ultimate Question of Life"
dispatcher.dispatch(controller.on_answer.name, QUESTION)
assert controller.answer == QUESTION
```


## For development

Illustrates how to setup for _PSGA_ development.

```bash
python3.11 -mvenv .venv
. .venv/bin/activate

# install module's dependencies
pip install -e .

# optionally install test features
pip install -e .[test]

# format, lint and test the code
isort demos tests src
black demos tests src
pylint src
pytest

# run the demos
export PYTHONPATH=src
python demos/hello_world.py
python demos/no_ui.py

# build the wheel and upload to pypi.org (uses credentials in ~/.pypirc)
rm -rf dist/
python -m build
twine check --strict dist/*
twine upload dist/*
```

Note that on Mac OS one needs to install tkinter separately with _brew_:

```bash
brew install python-tk@3.11
brew install python-gdbm@3.11
```
