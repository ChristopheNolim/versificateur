"""
@file src/mainframe/main_buttons.py
@version 1.1
@author CN
@author Gudule
@date jan 2017

Defines two button panels used in the application's main frame.

"""

from tkinter import Button, Frame, PhotoImage, E, W, S, N
from resources import RESOURCE, LANG

FONT_BUTTONS = 'helvetica', 12, 'bold'


class ActionsButtonPanel(Frame):
    """
    @class ActionsButtonPanel

    This panel of buttons is attached to a DataManager and an ActionBinder
    objects. It activates the behaviors of the ActionBinder :
    - looking for syns
    - looking for rimes
    - counting the verses in the selected zone
    - changing the verse count to apply (uses the DataManager)
    - re-read the selected zone
    - forget the error tags in the selected zone
    """

    def __init__(self, data_manager, action_binder, *args, **kwargs):
        """
        Initialize the panel and create the buttons.

        @param data_manager            A DataManager object
        @param action_binder           An ActionBinder object
        """
        super().__init__(*args, **kwargs)
        self.action_binder = action_binder
        self.data_manager = data_manager

        Button(self, font=FONT_BUTTONS,
               width=18,
               text=LANG.syn,
               command=self.action_binder.on_syn).grid(row=0, column=0, sticky=E+W+N+S)
        Button(self, font=FONT_BUTTONS,
               width=18,
               text=LANG.ri,
               command=self.action_binder.on_ri).grid(row=1, column=0, sticky=E+W+N+S)
        Button(self, font=FONT_BUTTONS,
               width=18,
               text=LANG.ct,
               command=lambda e=None:self.action_binder.on_ct(self.data_manager.params["compt"])).grid(row=0, column=1, sticky=E+W+N+S)
        Button(self,
               width=18,
               text=LANG.change_ct,
               command=self.data_manager.on_change_count).grid(row=1, column=1, sticky=E+W+N+S)
        Button(self, font=FONT_BUTTONS,
               width=18,
                text=LANG.read,
                command=self.action_binder.on_read).grid(row=0, column=2, sticky=E+W+N+S)
        Button(self, font=FONT_BUTTONS,
               width=18,
               text=LANG.forget,
               command=self.action_binder.on_remove_error_tags
               ).grid(row=1, column=2, sticky=E+W+N+S)


class FileButtonPanel(Frame):
    """
    @class FileButtonPanel

    This button panel provides the behaviors concerning files and provided
    by a DataManager attached to a text zone :
    - creating a new document
    - opening a file
    - saving the current file
    - saving to a new file
    - exporting to a full TeX file

    @see DataManager
    """

    def __init__(self, data_manager, *args, **kwargs):
        """
        Initialize the panel and create the buttons.

        @param data_manager     A DataManager object.
        """
        super().__init__(*args, **kwargs)
        self.data_manager = data_manager
        self._new = PhotoImage(file=RESOURCE.new)
        self._open = PhotoImage(file=RESOURCE.open)
        self._save = PhotoImage(file=RESOURCE.save)
        self._save_as = PhotoImage(file=RESOURCE.save_as)

        Button(self,
               width=100, height=30,
               image=self._new,
               command=self.data_manager.on_new).grid(row=0, column=0, sticky=E+W+N+S)
        Button(self,
               width=100, height=30,
               image=self._open,
               command=self.data_manager.on_open).grid(row=1, column=0, sticky=E+W+N+S)
        Button(self,
               width=100, height=30,
               image=self._save,
               command=self.data_manager.on_save).grid(row=0, column=1, sticky=E+W+N+S)
        Button(self,
               width=100, height=30,
               image=self._save_as,
               command=self.data_manager.on_save_new).grid(row=1, column=1, sticky=E+W+N+S)
        Button(self, font=FONT_BUTTONS,
               width=18,
               text=LANG.export_tex,
               command=self.data_manager.on_export_tex).grid(row=0, column=2, rowspan=2, sticky=E+W+N+S)

