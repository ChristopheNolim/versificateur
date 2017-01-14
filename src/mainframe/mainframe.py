"""
@file src/mainframe/mainframe.py
@version 1.1
@author CN
@author Gudule
@date jan 2017

Contains the main frame of the application.

"""


from tkinter import W, E, N, S
from tkinter import Button
from tkinter import Frame, Label
import tkinter
import tkinter.filedialog as filedialog
import tkinter.simpledialog as simpledialog
import tkinter.messagebox as messagebox
import tkinter.scrolledtext as scrolledtext

import random

from tex_editor.text import TexFormattedText

from mainframe.data_manager import DataManager
from actions.action_handler import FrenchActionHandler
from actions.action_binder import ActionBinder
from mainframe.main_buttons import FileButtonPanel, ActionsButtonPanel

from magicbutton.magicbutton import do_magic

from tex_editor.buttons import ButtonPanel
from resources import RESOURCE, LANG

import os


#=================================

FONT_BUTTONS = 'helvetica', 12, "bold"
FONT_LABELS = 'helvetica', 12, 'bold'

#==================================


class MainFrame(Frame):
    """
    @class MainFrame

    The main frame of the application. Contains all the components.
    """

    def __init__(self, master=None):
        super().__init__(master)
        self.grid(row=0, column=0)

        # the main text zone
        self.text = TexFormattedText(self, undo=True)
        # self.text['font'] = FONT

        # the output text zone
        self.output = scrolledtext.ScrolledText(self, undo=False)

        # action handler (actions on the text zone and output of these actions)
        self.action_handler = FrenchActionHandler()
        # action binder
        self.action_binder = ActionBinder(self.action_handler, self.text, self.output)
        # data manager (file saving and loading)
        self.data_manager = DataManager(self.text)

        # bind the main controls to the frame
        self._root().bind('<Control-q>', self.on_closing)
        # self._root().bind('<Control-o>', self.data_manager.on_open)
        self._root().bind('<Control-n>', self.data_manager.on_new)
        self._root().bind('<Control-s>', self.data_manager.on_save)

        self._root().protocol("WM_DELETE_WINDOW", self.on_closing)

        # label attached to the data (current file)
        self.cf = self.data_manager.get_stringvar()
        self.cf_label = Label(self, font=FONT_LABELS,
                                text="FICHIER :                      ",
                                textvariable=self.cf)

        # label attached to the current action
        self.sw = self.action_binder.get_stringvar()
        self.sw_label = Label(self, font=FONT_LABELS,
                            text="ACTION :     ",
                            textvariable=self.sw)

        # contents of the text zone
        # TODO improve this code
        try:
            currentdir = os.path.dirname(os.path.abspath(__file__))
            fpath = os.path.join(currentdir, "output_text.txt")
            with open(fpath, "r") as f:
                self.output.insert(1.0, f.read())

            fpath = os.path.join(currentdir, "selection_citation.txt")
            with open(fpath, "r") as f:
                lines = [l for l in f]
                self.output.insert(END, "\n" + lines[random.randrange(len(lines))])
        except Exception as e:
            pass
            # print("Could not open file output_text.txt")

        # button panel of file actions
        fbp = FileButtonPanel(self.data_manager, master=self)
        # button panel of actions
        abp = ActionsButtonPanel(self.data_manager, self.action_binder, master=self)
        # magic button !
        mbutton = Button(self, font=FONT_BUTTONS,
               text=LANG.magicbutton,
               command=do_magic)
        # the panel of buttons attached to the main text zone
        bp = ButtonPanel(self.text, master=self, width=50)

        # grid all the components
        # TODO improve the griding
        fbp.grid(row=0, column=0, rowspan=2, columnspan=1, sticky=E+W+N+S)
        abp.grid(row=0, column=1, rowspan=2, columnspan=1, sticky=E+W+N+S)
        mbutton.grid(row=0, column=2, rowspan=2, columnspan=1, sticky=E+W+N+S)
        self.sw_label.grid(row=1, column=3, rowspan=1, sticky=W)
        self.cf_label.grid(row=0, column=3, rowspan=1, sticky=W)

        self.text.grid(row=2, column=0, columnspan=2, rowspan=4, sticky=E+W+N+S)
        bp.grid(row=2, column=2, rowspan=4, sticky=E+W+N+S)
        self.output.grid(row=2, column=3, columnspan=2, rowspan=4, sticky=E+W+N+S)


    def on_closing(self, event=None):
        """
        Closes the application.
        This will close, in this order :
        - the data manager
        - the action binder
        - the frame
        """
        self.data_manager.on_closing()
        self.action_binder.on_closing()
        self._root().destroy()
