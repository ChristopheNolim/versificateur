"""
@file mainframe.py

Contains the main frame of the application.

"""


from tkinter import YES, BOTH, SUNKEN, WORD, RIGHT, LEFT, Y, END, INSERT
from tkinter import SEL_FIRST, SEL_LAST, X, TOP, BOTTOM, W, E, N, S
from tkinter import Scrollbar, Text, Button, StringVar, Pack, Grid, Place
from tkinter import Frame, Label
import tkinter
import tkinter.filedialog as filedialog
import tkinter.simpledialog as simpledialog
import tkinter.messagebox as messagebox
import tkinter.scrolledtext as scrolledtext

import random

from tkinter import PhotoImage


from tex_editor.text import TexFormattedText, ButtonPanel

from mainframe.data_manager import DataManager
from mainframe.action_handler import ActionHandler
from magicbutton.magicbutton import do_magic

import os


#=================================

MAIN_TITLE = "Versificateur 1.0"

BUTTON_NEW = "Nouveau"
BUTTON_OPEN = "Ouvrir"

BUTTON_SAVE = "Sauvegarder"
BUTTON_SAVE_NEW = "Sauvegarder dans"
BUTTON_FIND = "Chercher"

BUTTON_CUT = "Couper"
BUTTON_PASTE = "Coller"
BUTTON_COPY = "Copier"

BUTTON_SYN = "Synonymes"
BUTTON_CT = "Comptage"
BUTTON_CHANGE_COUNT = "Changer compt."
BUTTON_RI = "Rimes"
BUTTON_READ = "Relire"

FONT_BUTTONS = 'helvetica', 12, "bold"
FONT_LABELS = 'helvetica', 12, 'bold'
FONT = 'times', 14, 'normal'



#==================================



class MainFrame(Frame):
    """
    @class MainFrame

    The main frame of the application.
    """

    def __init__(self, master=None):
        super().__init__(master)
        self.grid(row=0, column=0)

        # the main text zone
        self.text = TexFormattedText(self, undo=True)
        self.text.grid(row=2, column=0, columnspan=5, rowspan=5)
        self.text['font'] = FONT

        # output of the functions
        self.output = scrolledtext.ScrolledText(self, undo=False)
        self.output.grid(row=2, column=6, columnspan=3, rowspan=5, sticky=E+W+N+S)

        # action handler (actions on the text zone and output of these actions)
        self.action_handler = ActionHandler(self.text, self.output)

        # data manager (file saving and loading)
        self.data_manager = DataManager(self.text)

        # bind the main controls to the frame
        self._root().bind('<Control-q>', self.on_closing)
        # self._root().bind('<Control-o>', self.data_manager.on_open)
        self._root().bind('<Control-n>', self.data_manager.on_new)
        self._root().bind('<Control-s>', self.data_manager.on_save)

        # label attached to the data (current file)
        self.cf = self.data_manager.get_stringvar()
        self.cf_label = Label(self, font=FONT_LABELS,
                                text="FICHIER :                      ",
                                textvariable=self.cf)
        self.cf_label.grid(row=0, column=7, rowspan=1, sticky=W)

        # label attached to the current action
        self.sw = self.action_handler.get_stringvar()
        self.sw_label = Label(self, font=FONT_LABELS,
                            text="ACTION :     ",
                            textvariable=self.sw)
        self.sw_label.grid(row=1, column=7, rowspan=1, sticky=W)

        # contents of the text zone
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

        # buttons
        currentdir = os.path.dirname(os.path.abspath(__file__))
        # fpath = os.path.join(currentdir, "icons")
        # self._new = PhotoImage(file="icons/new.png")
        # self._open = PhotoImage(file="icons/open.png")
        # self._save = PhotoImage(file="icons/save.png")
        # self._saveas = PhotoImage(file="icons/saveas.png")
        # TODO
        self._new = PhotoImage(file=os.path.join(currentdir, "icons/new.png"))
        self._open = PhotoImage(file=os.path.join(currentdir, "icons/open.png"))
        self._save = PhotoImage(file=os.path.join(currentdir, "icons/save.png"))
        self._saveas = PhotoImage(file=os.path.join(currentdir, "icons/saveas.png"))
        Button(self,
               image=self._new,
               width=50,
               command=self.data_manager.on_new).grid(row=0, column=0, sticky=E+W+N+S)
        Button(self,
               image=self._open,
               width=50,
               command=self.data_manager.on_open).grid(row=1, column=0, sticky=E+W+N+S)
        Button(self,
               image=self._save,
               width=50,
               command=self.data_manager.on_save).grid(row=0, column=1, sticky=E+W+N+S)
        Button(self,
               image=self._saveas,
               width=50,
               command=self.data_manager.on_save_new).grid(row=1, column=1, sticky=E+W+N+S)

        Button(self, font=FONT_BUTTONS,
               text=BUTTON_SYN,
               command=self.action_handler.on_syn).grid(row=0, column=2, sticky=E+W+N+S)
        Button(self, font=FONT_BUTTONS,
               text=BUTTON_RI,
               command=self.action_handler.on_ri).grid(row=1, column=2, sticky=E+W+N+S)

        Button(self, font=FONT_BUTTONS,
               text=BUTTON_CT,
               command=lambda e=None:self.action_handler.on_ct(self.data_manager.params["compt"])).grid(row=0, column=3, sticky=E+W+N+S)

        Button(self,
               text=BUTTON_CHANGE_COUNT,
               command=self.data_manager.on_change_count).grid(row=1, column=3, sticky=E+W+N+S)



        Button(self, font=FONT_BUTTONS,
                text=BUTTON_READ,
                command=self.action_handler.on_read).grid(row=0, column=4, sticky=E+W+N+S)

        Button(self, font=FONT_BUTTONS,
               text="Oublier les erreurs",
               command=self.action_handler.on_remove_error_tags
               ).grid(row=1, column=4, sticky=E+W+N+S)

        Button(self, font=FONT_BUTTONS,
               text="Export tex",
               command=self.data_manager.on_export_tex).grid(row=0, column=5, rowspan=2, sticky=E+W+N+S)

        Button(self, font=FONT_BUTTONS,
               text="Magic button",
               command=do_magic).grid(row=0, column=6, rowspan=2, sticky=E+W+N+S)

        # the panel of buttons attached to the main text zone
        bp = ButtonPanel(self, width=50)
        bp.grid(row=2, column=5, rowspan=5, sticky=E+W+N+S)
        bp.attach(self.text)

        self._root().protocol("WM_DELETE_WINDOW", self.on_closing)




    def on_closing(self, event=None):
        self.data_manager.on_closing()
        self.action_handler.on_closing()
        self._root().destroy()
