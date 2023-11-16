# PySimpleGUI's Actions (PSGA)

<p align="center">

<a href="https://github.com/aptly-io/psga/actions">
  <img alt="Actions Status" src="https://github.com/aptly-io/psga/actions/workflows/CI.yaml/badge.svg">
</a>
<a href="https://pypi.org/project/psga/">
  <img alt="License" src="https://img.shields.io/pypi/l/psga.svg">
</a>
[PyPi Version](https://img.shields.io/pypi/v/psga.svg)](https://pypi.python.org/pypi/psga/)

</p>


## Intro

PySimpleGUI is like the _View_ in the _Model-View-Controller_ paradigm.
For less complex user interfaces its typical if-event-then-action loop
(that takes the role of _Controller_) works fine.
However this event-loop approach becomes unwieldy for larger user interfaces.

PSGA tries to mitigate this by adding the following:
- The `@psga.action()` decorator turns a method or function into an `Action`.
  An action wraps both the handler and a key to respectively handle and name the event.
- A `Controller` class groups a bunch of handlers for processing
  user input and updating the corresponding views.
- A `Dispatcher` class has a loop that reads the events from a `sg.Window`.
  Each event's value is then dispatched to the handler
  that was prior registered by the `Controller`('s).

The MVC's _Model_ is still for the developer to design and implement.

Note that PySimpleGUI tries to get away with the _call-back_ and _classes_.
But in a way, PSGA brings these back with the _action handler_.

## Examples

### Hello world

PySimpleGUI shows the classic _hello world_ in its [Jump-Start section](https://www.pysimplegui.org/en/latest/).

The source code below illustrates how PSGA _could_ fit in:
1. Define a function that acts when the _Ok_ button is clicked.
2. Instantiate the dispatcher that triggers the handler when the _Ok_ event is found.

Note that this simple example does not use a `Controller`.
Note that the `demos/hello_world.py` example does the same but slightly different.

```python
import PySimpleGUI as sg
import psga

# PSGA: define an action for the Ok button
@psga.action(key="Ok")
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

## For development

```bash
python3.11 -mvenv .venv
. .venv/bin/activate

# install module's dependencies
pip install -e .

# optionally install test features
pip install -e .[test]

# format & lint the code
isort demos tests src
black demos tests src

pylint src

# execute the tests
pytest

# run the demo
export PYTHONPATH=src
python demos/hello_world.py

# build the wheel
python -m build

# check the build
twine check --strict dist/*
```

Note install tkinter separately on MacOS with brew:

```bash
brew install python-tk@3.11
brew install python-gdbm@3.11
```