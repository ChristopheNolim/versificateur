"""
@file src/tex_editor/buttons.py
@version 1.1
@author CN
@author Gudule
@date jan 2017

Provides buttons for the commands attached to a TeX editor text zone.

"""

from tkinter import Button, Frame, PhotoImage, E, W, S, N
from resources import RESOURCE

FONT_BUTTONS = 'helvetica', 12, 'bold'

class ButtonPanel(Frame):
    """
    @class ButtonPanel

    A panel of buttons that can be attached to a text widget that is a subclass
    of SpecialText (to have all the methods needed).

    The formatting buttons control which tag is set and which ones automatically
    removed.

    @see SpecialText
    """

    def __init__(self, textwidget, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._textw = textwidget
        self.grid(row=0,column=0)

        self._italic = PhotoImage(file=RESOURCE.italic)
        self._bold = PhotoImage(file=RESOURCE.bold)
        self._underline = PhotoImage(file=RESOURCE.underline)
        self._center = PhotoImage(file=RESOURCE.center)
        self._right = PhotoImage(file=RESOURCE.right)
        self._left = PhotoImage(file=RESOURCE.left)

        Button(self,
               font=FONT_BUTTONS,
               width=50, height=50,
               image=self._italic,
               command=lambda: self._textw._add_remove_tags("ITAL", ["BOLD", "FOOTNOTE", "SMALLCAPS"])
               ).grid(row=0, column=0, sticky=E+W+N+S)
        Button(self,
               font=FONT_BUTTONS,
               width=50, height=50,
               image=self._bold,
               command=lambda: self._textw._add_remove_tags("BOLD", ["ITAL", "FOOTNOTE", "SMALLCAPS"])
               ).grid(row=1, column=0, sticky=E+W+N+S)
        Button(self,
               font=FONT_BUTTONS,
               width=50, height=50,
               image=self._underline,
               command=lambda: self._textw._add_remove_tags("UNDERLINE", [])
               ).grid(row=2, column=0, sticky=E+W+N+S)


        Button(self, font=FONT_BUTTONS,
               text="œ",
               command=lambda: self._textw.insert_text("œ")
               ).grid(row=3, column=0, sticky=E+W+N+S)
        Button(self, font=FONT_BUTTONS,
               text="«",
               command=lambda: self._textw.insert_text("« ")
               ).grid(row=4, column=0, sticky=E+W+N+S)
        Button(self, font=FONT_BUTTONS,
               text="»",
               command=lambda: self._textw.insert_text("»")
               ).grid(row=5, column=0, sticky=E+W+N+S)
        Button(self, font=FONT_BUTTONS,
               text="…",
               command=lambda: self._textw.insert_text("…")
               ).grid(row=6, column=0, sticky=E+W+N+S)

        # TODO warning : flusleft is a bit special in LateX
        # for now no flushleft here !
        Button(self,
               font=FONT_BUTTONS,
               width=50, height=50,
               image=self._left,
               command=lambda: self._textw._add_mult_line_tag("", ["FLUSHRIGHT", "CENTER"])
               ).grid(row=0, column=1, sticky=E+W+N+S)
        Button(self,
               font=FONT_BUTTONS,
               width=50, height=50,
               image=self._right,
               command=lambda: self._textw._add_mult_line_tag("FLUSHRIGHT", ["FLUSHLEFT", "CENTER"])
               ).grid(row=1, column=1, sticky=E+W+N+S)
        Button(self,
               font=FONT_BUTTONS,
               width=50, height=50,
               image=self._center,
               command=lambda: self._textw._add_mult_line_tag("CENTER", ["FLUSHRIGHT", "FLUSHLEFT"])
               ).grid(row=2, column=1, sticky=E+W+N+S)

        Button(self,
               font=FONT_BUTTONS,
               text="Note",
               command=lambda: self._textw._add_remove_tags("FOOTNOTE", ["ITAL", "BOLD", "SMALLCAPS"])
               ).grid(row=3, column=1, sticky=E+W+N+S)
        Button(self,
               font=FONT_BUTTONS,
               text="Déformater",
               command=lambda: self._textw._add_remove_tags(None, ["BOLD", "ITAL", "UNDERLINE", "CHAPTER", "SECTION", "FOOTNOTE", "SMALLCAPS"])
               ).grid(row=4, column=1, sticky=E+W+N+S)
        Button(self,
               font=FONT_BUTTONS,
               text="Chapitre",
               command=lambda: self._textw._add_remove_tags("CHAPTER", ["SECTION", "FOOTNOTE", "BOLD", "ITAL", "SMALLCAPS"])
               ).grid(row=5, column=1, sticky=E+W+N+S)
        Button(self,
               font=FONT_BUTTONS,
               text="Section",
               command=lambda: self._textw._add_remove_tags("SECTION", ["CHAPTER", "FOOTNOTE", "BOLD", "ITAL", "SMALLCAPS"])
               ).grid(row=6, column=1, sticky=E+W+N+S)
        Button(self, font=FONT_BUTTONS,
               text="Copier",
               command=lambda: self._textw.on_copy()
               ).grid(row=7, column=1, sticky=E+W+N+S)
        Button(self, font=FONT_BUTTONS,
               text="Couper",
               command=lambda: self._textw.on_cut()
               ).grid(row=8, column=1, sticky=E+W+N+S)
        Button(self, font=FONT_BUTTONS,
               text="Coller",
               command=lambda: self._textw.on_paste()
               ).grid(row=9, column=1, sticky=E+W+N+S)
        Button(self, font=FONT_BUTTONS,
               text="Chercher",
               command=lambda: self._textw.on_find()
               ).grid(row=10, column=1, sticky=E+W+N+S)
        Button(self, font=FONT_BUTTONS,
               text="Petites maj.",
               command=lambda: self._textw._add_small_caps_tag(["BOLD", "ITAL", "FOOTNOTE"])
               ).grid(row=11, column=1, sticky=E+W+N+S)

