"""
@file src/tex_editor/text.py
@version 1.0
@author CN
@author Gudule
@date jan 2017

Contains the classes that implement the small TeX editor.
It uses the package tkinter.


"""


from tkinter import END, INSERT, SEL, Tk
from tkinter import SEL_FIRST, SEL_LAST, X, TOP, BOTTOM, W, E, N, S
from tkinter import Scrollbar, Text, Button, StringVar, Pack, Grid, Place
from tkinter import Frame, Label, LEFT, RIGHT, CENTER
import tkinter
from tkinter import PhotoImage, Canvas

import tkinter as tk
import tkinter.ttk as ttk

import os
import json

try:
    from tex_editor.tex_parser import tex_parse, tags_to_tex
    from tex_editor.utils import SpecialText
except Exception as e:
    from tex_parser import tex_parse, tags_to_tex
    from utils import SpecialText

#===================================

FONT_NORMAL = 'times', 14, 'normal'
FONT_BOLD = 'times', 14, 'bold'
FONT_IT = 'times', 14, 'italic'

FONT_CHAPTER = 'helvetica', 19, 'bold'
FONT_SECTION = 'helvetica', 15, 'bold'

FONT_NOTE = 'helvetica', 10, 'normal'
FONT_SMALL_CAPS = 'times', 12, 'normal'
# FONT_NOTE_BOLD = 'helvetica', 10, 'bold'
# FONT_NOTE_IT = 'helvetica', 10, 'italic'

FONT_BUTTONS = 'helvetica', 12, 'bold'


# TODO : implement more complex tags, make available the combinations of tags

# usual tex tags
TAGS = ["BOLD", "ITAL", "FOOTNOTE", "SECTION", "CHAPTER",
    "SMALLCAPS", "CENTER", "FLUSHRIGHT", "FLUSHLEFT", "UNDERLINE"]

# TAGS_BEHAVIORS = {
# "ITAL" : { "donotchangeif" : ["CHAPTER", "SECTION", "FOOTNOTE"], "remove" : ["BOLD"], "combine" : [] }
# ""
#
#
# }

#=========================================

class ButtonPanel(Frame):
    """
    @class ButtonPanel

    A panel of buttons that can be attached to a text widget that is a subclass
    of SpecialText (to have all the methods needed).

    The formatting buttons control which tag is set and which ones automatically
    removed.

    @see SpecialText
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grid(row=0,column=0)

        currentdir = os.path.dirname(os.path.abspath(__file__))
        fpath = os.path.join(currentdir, "icons")

        # self._im1 = PhotoImage(file="icons/format-text-italic.png")
        # self._im2 = PhotoImage(file="icons/format-text-bold.png")
        # self._im3 = PhotoImage(file="icons/format-text-underline.png")
        # self._im4 = PhotoImage(file="icons/format-justify-center.png")
        # self._im5 = PhotoImage(file="icons/format-justify-left.png")
        # self._im6 = PhotoImage(file="icons/format-justify-right.png")


        self._im1 = PhotoImage(file=os.path.join(currentdir, "icons/format-text-italic.png"))
        self._im2 = PhotoImage(file=os.path.join(currentdir, "icons/format-text-bold.png"))
        self._im3 = PhotoImage(file=os.path.join(currentdir, "icons/format-text-underline.png"))
        self._im4 = PhotoImage(file=os.path.join(currentdir, "icons/format-justify-center.png"))
        self._im5 = PhotoImage(file=os.path.join(currentdir, "icons/format-justify-left.png"))
        self._im6 = PhotoImage(file=os.path.join(currentdir, "icons/format-justify-right.png"))

        Button(self,
               font=FONT_BUTTONS,
               width=50, height=50,
               image=self._im1,
               command=lambda: self._textw._add_remove_tags("ITAL", ["BOLD", "FOOTNOTE", "SMALLCAPS"])
               ).grid(row=0, column=0, sticky=E+W+N+S)
        Button(self,
               font=FONT_BUTTONS,
               width=50, height=50,
               image=self._im2,
               command=lambda: self._textw._add_remove_tags("BOLD", ["ITAL", "FOOTNOTE", "SMALLCAPS"])
               ).grid(row=1, column=0, sticky=E+W+N+S)
        Button(self,
               font=FONT_BUTTONS,
               width=50, height=50,
               image=self._im3,
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
               image=self._im5,
               command=lambda: self._textw._add_mult_line_tag("", ["FLUSHRIGHT", "CENTER"])
               ).grid(row=0, column=1, sticky=E+W+N+S)
        Button(self,
               font=FONT_BUTTONS,
               width=50, height=50,
               image=self._im6,
               command=lambda: self._textw._add_mult_line_tag("FLUSHRIGHT", ["FLUSHLEFT", "CENTER"])
               ).grid(row=1, column=1, sticky=E+W+N+S)
        Button(self,
               font=FONT_BUTTONS,
               width=50, height=50,
               image=self._im4,
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


    def attach(self, textwidget):
        self._textw = textwidget


class TexFormattedText(SpecialText):
    """
    @class TexFormattedText

    A subclass of SpecialText that contains a TeX / LateX formatted text.

    """

    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.tag_configure("BOLD", font=FONT_BOLD)
        self.bind("<Control-b>", lambda x: self._add_remove_tags("BOLD", ["ITAL", "UNDERLINE"]))
        self.tag_configure("ITAL", font=FONT_IT)
        # self.bind("<Control-j>", lambda x: self._add_remove_tags("ITAL", ["BOLD", "UNDERLINE"]))
        self.tag_configure("CHAPTER", font=FONT_CHAPTER)
        # self.bind()
        self.tag_configure("SECTION", font=FONT_SECTION)

        self.tag_configure("FLUSHLEFT", justify=LEFT)
        # self.bind("<Control-l>", lambda x: self._add_remove_tags("FLUSHLEFT", ["FLUSHRIGHT", "CENTER"]))
        self.tag_configure("FLUSHRIGHT", justify=RIGHT)
        # self.bind("<Control-r>", lambda x: self._add_remove_tags("FLUSHRIGHT", ["FLUSHLEFT", "CENTER"]))
        self.tag_configure("CENTER", justify=CENTER)
        # self.bind("<Control-k>", lambda x: self._add_remove_tags("CENTER", ["FLUSHLEFT", "FLUSHRIGHT"]))

        self.tag_configure("FOOTNOTE", font=FONT_NOTE)
        # self.tag_configure("FOOTNOTE_BOLD", font=FONT_NOTE_BOLD)
        # self.tag_configure("FOOTNOTE_ITAL", font=FONT_NOTE_ITAL)

        # self.bind("<Control-k>", lambda x: self._add_remove_tags("FOOTNOTE", ["CENTER", "FLUSHLEFT", "FLUSHRIGHT"]))
        self.tag_configure("UNDERLINE", underline=True)

        self.tag_configure("SMALLCAPS", font=FONT_SMALL_CAPS)
        # self.bind("<Control-u>", lambda x: self._add_remove_tags("UNDERLINE", ["BOLD", "ITAL"]))
        # self.bind("<Control-w>", lambda x: self._add_remove_tags(None, ["BOLD", "ITAL", "UNDERLINE"]))

        self.register_structure_tag("CHAPTER")
        self.register_structure_tag("SECTION")

    def _add_mult_line_tag(self, tag, tags, event=None):
        try:
            p1 = "%s linestart" % SEL_FIRST
            p2 = "%s lineend" % SEL_LAST
            # str(self.index(SEL_FIRST)[0]) + ".0"
            # p2 = str(self.index(SEL_LAST)[0]) + ".0"
            for t in tags:
                self.tag_remove(t, p1, p2)
            if tag:
                self.tag_add(tag, p1, p2)

            # self.on_change()
        except Exception as e:
            pass

    def _add_remove_tags(self, tag, tags, event=None):
        """
        Add a tag and remove others on the current selection of the text.
        No multi-line selection is allowed here.
        """
        try:
            selection = self.get(SEL_FIRST, SEL_LAST)
            if "\n" in selection:
                # no multi-line selection allowed
                return
            for t in tags:
                self.tag_remove(t, SEL_FIRST, SEL_LAST)
            if tag:
                self.tag_add(tag, SEL_FIRST, SEL_LAST)

            # self.on_change()
        except Exception as e:
            pass

    def _add_small_caps_tag(self, tags, event=None):
        try:
            pos1 = self.index(SEL_FIRST)
            pos2 = self.index(SEL_LAST)
            selection = self.get(pos1, pos2)

            if "\n" in selection:
                # no multi-line selection allowed
                return
            for t in tags:
                self.tag_remove(t, pos1, pos2)

            self.delete(pos1, pos2)
            self.insert(pos1, selection.upper())
            self.tag_add("SMALLCAPS", pos1, pos2)

            # self.on_change()
        except Exception as e:
            pass

    def input_formatted_text(self, inpt):
        """
        Input text formatted using TeX / LateX, setting the right tags.
        The text is first parsed through a special parser, that
        deciphers all the commands used and translates to tags.

        @see tex_parser.py
        """
        self.delete(1.0, END)
        formatted = tex_parse(inpt)
        # print(formatted)
        if not formatted: return

        last_position = self.index(INSERT)
        current_tags = set()
        for f, tags in formatted:
            self.insert(INSERT, f)
            # print(last_position)
            if set(tags) != current_tags:
                for tag in tags:
                    self.tag_add(tag, last_position, INSERT)
            last_position = self.index(INSERT)

    def input_tex_with_comments(self, inpt):
        lines = inpt.split("\n")
        comments = [l for l in lines if l.startswith("%")]
        tex = '\n'.join([l for l in lines if not l.startswith("%")])
        self.input_formatted_text(tex)
        try:
            for l in comments:
                if l.startswith("%-CURSOR-%"):
                    cursor = l[11:]
                    # print("Cursor is in position %s" % cursor)
                    self.mark_set(INSERT, cursor)
                    self.see(INSERT)
                elif l.startswith("%-TAG-%"):
                    d = json.loads(l[7:])
                    if d["t"] in self.tag_names():
                        self.tag_add(d["t"], d["b"], d["e"])
                    else:
                        print("Warning : unknown tag name %s" % d["t"])
        except Exception as e:
            print("Error while processing tags")

    def get_tex_formatted_text(self, verbose=False):
        """
        Formats the text contained in this zone to TeX / LateX.
        """
        formatted = self.dump(1.0, END, tag=True, text=True)
        return tags_to_tex(formatted)

    def output_tex_with_comments(self, verbose=False):
        tmp = self.get_tex_formatted_text(self)
        lines = [ "%-CURSOR-% " + str(self.index(INSERT)) ]
        for t in self.tag_names():
            if t != "sel" and t not in TAGS:
                r = self.tag_ranges(t)
                i = 0
                while i < len(r):
                    begin = r[i]
                    end = r[i+1]
                    i += 2
                    d = dict()
                    d["t"] = t
                    d["b"] = str(begin)
                    d["e"] = str(end)
                    lines.append("%-TAG-% " + json.dumps(d))
        return "\n".join(lines) + "\n" + tmp


    def export_tex(self):
        """
        Exports the contents of this text zone to a TeX file.
        Therefore, adds some additional commands to make the file
        immediately compilable.
        """
        res = ""
        with open("tex_editor/model.tex", 'r') as f:
            for line in f:
                if line.startswith("% INSERT CONTENT HERE"):
                    res += self.get_tex_formatted_text()
                else:
                    res += line
        return res



if __name__ == '__main__':

    root = Tk()
    root.title("Test")
    text = TexFormattedText(root)
    buttons = ButtonPanel(root)
    buttons.attach(text)
    text.insert(1.0, "Normally, this sould display a working text zone, with line nbrs and scroll bar.")
    text.insert(END, "Also, try the ctrl + A and ctrl + F commands.")
    text.grid(row=0,column=0, sticky=E+W+N+S)
    buttons.grid(row=0, column=1, sticky=E+W+N+S)
    root.mainloop()
