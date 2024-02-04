# PySimpleGUI's Actions (PSGA) simplify event handling

<p align="center">
<a href="https://github.com/aptly-io/psga/actions"><img alt="Actions Status" src="https://github.com/aptly-io/psga/actions/workflows/CI.yaml/badge.svg"></a>
<a href="https://pypi.org/project/psga/"><img alt="License" src="https://img.shields.io/pypi/l/psga.svg"></a>
<a href="https://pypi.python.org/pypi/psga/"><img alt="PyPi Version" src="https://img.shields.io/pypi/v/psga.svg"></a>
</p>

## install

```bash
python3 -mpip install psga
```

To run the demo, checkout the repository and install the required modules:

```bash
git clone https://github.com/aptly-io/psga.git
cd psga
python3 -mvenv .venv
. .venv/bin/activate
python3 -mpip install -e .
python3 -mpip install -e .[demo]

python demos/tabs_and_tables/main.py 
```

## Intro

PySimpleGUI is like the _View_ in the _Model-View-Controller_ paradigm.
For less complex user interfaces, PySimpleGui's typical _if-event then-action loop_
(that is a bit a _Controller_), works fine.
However the event-loop's if-then-else becomes difficult to maintain
for user interfaces with a large number of elements.

_PSGA_ mitigates this by adding the following:
- The `@psga.action()` decorator turns a python method (or function) in an `Action`.
  This action wraps both the handler and an event name (accessible through the property `name`)
  to respectively handle and name the PySimpleGui event.
  Since VSC's intellisense recognizes this `name` property,
  are typo errors in the PySimpleGui's `key` less likely to happen.
  The optional `keys` decorator parameter allows for additional keys that invoke the associated handler.
- A `Controller` class groups and registers related handlers for processing
  user interaction and updating the corresponding view.
  This could hold your business/logic state.
  With a `Controller` the source code becomes more maintainable and structured.
- A `Dispatcher` class has a loop that reads the events from a `sg.Window`.
  Each event's value is then dispatched to the handler
  that was prior registered by its `Controller`('s).
  Manual registering is also possible (see the examples).

It is easy to gradually refactor existing source code with the _PSGA_ feature.

Note that PySimpleGUI's documentation mentions it avoids concepts like _call-backs_, _classes_...
_PSGA_, with its `action` and `Controller` brings that back (so you might not like _PSGA_'s concepts?).


## Examples

All examples are sprinkled with comments to highlight _PSGA_'s usage.
Grep for `# PSGA: ` to find these.


### Hello world

PySimpleGUI shows the classic _hello world_ in its [Jump-Start section](https://www.PySimpleGui.org/en/latest/).

The source code below illustrates how _PSGA_ _could_ fit in this _hello world_ example:
1. Define a function that acts when the _Ok_ button is clicked.
2. Instantiate the dispatcher that will trigger the handler whenever the _Ok_ event is fired.

Note that this simple example does not use a `Controller`.
Note that the `demos/hello_world.py` example usage _PSGA_ in a slightly different way
(all roads lead to Rome).

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

It shows _PSGA_'s `Controller`, `action()` and `Dispatcher` concepts
(without introducing any PySimpleGUI functionality).

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

QUESTION = "What is the answer to the Ultimate Question of Life?"
dispatcher.dispatch(controller.on_answer.name, QUESTION)
assert controller.answer == QUESTION
```


### Tabs and tables

The `demo/tabs_and_tables` is a larger PySimpleGui example program.

It shows 2 `sg.Tables`, each in a `sg.Tab`, that get their data from a Model.
The model in turn uses REST requests to manage the data.
Right-click for the context menu that allows to add or delete table rows.

Notice how `main.py` is kept lean and clean.
_PSGA_ simplifies the event processing in a single line of code: `dispatcher.loop(window)`.
Each functional program part is succintly grouped in its Controller.


## For development

Following illustrates how to setup for _PSGA_ development.

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
python demos/tabs_and_tables/main.py

# build the wheel and upload to pypi.org (uses credentials in ~/.pypirc)
rm -rf dist/
python -m build
twine check --strict dist/*
twine upload dist/*
```

Note that on Mac OS one needs to install tkinter separately with _brew_:

```bash
brew install python-tk@3.11
```
