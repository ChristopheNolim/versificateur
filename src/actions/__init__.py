"""
@package actions
@version 1.1
@author CN
@author Gudule
@date jan 2017

This package provides classes that handle actions : counting syllables,
parsing the texte are actions that require specific behaviors, possibly
an underlying database connection.

Example use :
@code
from tkinter import Text
textzone = Text()
outputzone = Text()
action_handler = FrenchActionHandler()
action_binder = ActionBinder(action_handler, textzone, outputzone)
@endcode

WHile the action handler provides the behavior in itself, the action binder
binds specifically this behaviors to a text zone. It will retrieve, e.g,
the selected text in this zone to apply the behaviors to it.

@see ActionBinder
"""

