"""Reworked PySimpleGUI's hello world with the PSGA feature"""

import PySimpleGUI as sg

import psga


# PSGA: define an action for the Ok button
@psga.action()
# PSGA: The action generates a unique name value (if the decorator has no explicit name argument)
def _on_ok(values):
    # PSGA: The action has a handler: simply print a value
    print("You entered ", values[0])


sg.theme("DarkAmber")  # Add a touch of color
# All the stuff inside your window.
layout = [
    [sg.Text("Some text on Row 1")],
    [sg.Text("Enter something on Row 2"), sg.InputText()],
    [
        sg.Button("Exit"),
        # PSGA: assign the action's name value to the element (with intellisense no typo mismatches)
        sg.Button("Ok", key=_on_ok.name),
    ],
]

# Create the Window
window = sg.Window("Window Title", layout)

# PSGA: initiate the dispatcher, register the action and loop (until the Exit event is read)
psga.Dispatcher().register(_on_ok).loop(window)

window.close()
