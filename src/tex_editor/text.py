"""
@file src/tex_editor/text.py
@version 1.1
@author CN
@author Gudule
@date jan 2017

Contains the classes that implement the small TeX editor.

"""


from tkinter import END, INSERT, SEL, Tk
from tkinter import SEL_FIRST, SEL_LAST, X, TOP, BOTTOM, W, E, N, S
from tkinter import Scrollbar, Text, Button, StringVar, Pack, Grid, Place
from tkinter import Frame, Label, LEFT, RIGHT, CENTER
import tkinter
from tkinter import PhotoImage, Canvas

import tkinter as tk
import tkinter.ttk as ttk

from resources import TEX_MODEL

try:
    from tex_editor.tex_parser import tex_parse, tags_to_tex
    from tex_editor.utils import SpecialText, pairwise
    from tex_editor.tags import Tag
except Exception as e:
    from tex_parser import tex_parse, tags_to_tex
    from utils import SpecialText, pairwise
    from tags import Tag

#===================================

# Font of the normal text
FONT_NORMAL = 'times', 14, 'normal'

# Font for bold text
FONT_BOLD = 'times', 14, 'bold'

# font for italic text
FONT_IT = 'times', 14, 'italic'

# Font for chapters
FONT_CHAPTER = 'helvetica', 19, 'bold'

# Font for sections
FONT_SECTION = 'helvetica', 15, 'bold'

# Font for footnotes
FONT_NOTE = 'helvetica', 10, 'normal'

# Font for small caps
FONT_SMALL_CAPS = 'times', 12, 'normal'

# TODO : implement more complex tags, make available the combinations of tags

# usual tex tags
TAGS = ["BOLD", "ITAL", "FOOTNOTE", "SECTION", "CHAPTER",
    "SMALLCAPS", "CENTER", "FLUSHRIGHT", "FLUSHLEFT", "UNDERLINE"]


#=========================================

class TexFormattedText(SpecialText):
    """
    @class TexFormattedText

    A subclass of SpecialText that contains TeX / LateX formatted text.

    """

    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self["font"] = FONT_NORMAL
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

        @todo this does a lot of adding / removing tags, hences fires a lot of
        <<change>> events (and a lot of redraws). Better way ?
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
        """
        The small caps tag is a special one, since we need to put the text
        tagged in small caps.
        """
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
        """
        Input tex that contains comments. The comments are searched for
        additional information, such as the cursor position %-CURSOR-%
        or additional tags %%-TAG-%%.
        """
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
                elif l.startswith("%%-TAG-%%"):
                    tmp = Tag.from_str(l)
                    # tmp.loads(l)
                    if tmp.name in self.tag_names():
                        a,b = tmp.to_tkinter_pos()
                        self.tag_add(tmp.name, a, b)

                    else:
                        print("Warning : unknown tag name %s" % tmp.name)
        except Exception as e:
            print("Error while processing tags")
            print(e)

    def get_tex_formatted_text(self, verbose=False):
        """
        Formats the text contained in this zone to TeX / LateX.
        """
        formatted = self.dump(1.0, END, tag=True, text=True)
        return tags_to_tex(formatted)

    def output_tex_with_comments(self, verbose=False):
        """
        Output tex, with comments that will describe the cursor position
        in the text zone, and all error / additional tags.
        """
        tmp = self.get_tex_formatted_text(self)
        lines = [ "%-CURSOR-% " + str(self.index(INSERT)) ]
        for t in self.get_error_tags() + self.get_additional_tags():
            r = self.tag_ranges(t)
            for a,b in pairwise(r):
                tmp2 = Tag.from_tkinter_pos(t, a, b)
                lines.append(tmp2.dumps())

        return "\n".join(lines) + "\n" + tmp

    def export_tex(self):
        """
        Exports the contents of this text zone to a TeX file.
        Therefore, adds some additional commands to make the file
        immediately compilable.
        """
        res = ""
        with open(TEX_MODEL, 'r') as f:
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
