"""
@file src/tex_editor/utils.py
@version 1.1
@author CN
@author Gudule
@date jan 2017

Contains classes useful for the TeX editor.

The goal of this file is to define the SpecialText text zone.

@todo separate this file into 2 / 3

"""


from tkinter import SEL_FIRST, SEL_LAST, W, E, N, S, END, INSERT, SEL
from tkinter import Scrollbar, Text, StringVar, Grid, Place, Pack
from tkinter import Frame, Label, Toplevel, GROOVE, Tk, Canvas
from tkinter.simpledialog import askstring

import tkinter.ttk as ttk

from tkinter import SINGLE, Listbox, VERTICAL, BROWSE

def pairwise(iterable):
    "s -> (s0, s1), (s2, s3), (s4, s5), ..."
    a = iter(iterable)
    return zip(a, a)


#=============================================

FONT_LINE_NUMBERS = 'helvetica', 9, 'bold'
FONT_TIP = 'helvetica', 10, 'normal'

#==============================================


#==============================================

class _TextLineNumbers(Canvas):
    """
    @class _TextLineNumbers

    A tkinter widget that displays the line numbers of a Text zone.
    It can be attached to any text widget.

    @see SpecialText
    """
    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None

    def attach(self, text_widget):
        self.textwidget = text_widget

    def redraw(self, *args):
        """
        Redraw line numbers.
        """
        # print("Redrawing")
        self.delete("all")

        i = self.textwidget.index("@0,0")
        while True :
            dline= self.textwidget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(10,y + 2,anchor="nw", text=linenum,
                            font=FONT_LINE_NUMBERS)
            i = self.textwidget.index("%s+1line" % i)


class TagsScroller(Frame):
    """
    @class TagsScroller

    A tkinter wigdet that contains a listbox. It can be attached to a text zone.
    Then, the listbox keeps a list of all ranges of certain registered tags
    and allows to browse through them.

    @todo add a tool tip if the tag (e.g chapter name) is too wide
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grid(column=0,row=0)

        self.scrollbar = Scrollbar(self, orient=VERTICAL)
        self.scrollbar.grid(column=1, row=0, sticky=E+W+N+S)
        self.textw = None
        self.lbox = Listbox(self, selectmode=SINGLE, yscrollcommand=self.scrollbar.set)
        self.lbox.grid(column=0, row=0, sticky=E+W+N+S)
        self.scrollbar.config(command=self.lbox.yview)

        self.lbox.bind("<ButtonRelease-1>", self.on_mouse_select)

        self._chapters = dict()

        self.registered = set()
        self.selection = 0

        self.lbox.select_set(self.selection)

        self.lbox.bind("<Down>", self.on_down)
        self.lbox.bind("<Up>", self.on_up)

    def on_down(self, event):
        if self.selection < self.lbox.size()-1:
            self.lbox.select_clear(self.selection)
            self.selection += 1
            self.lbox.select_set(self.selection)
            self.on_select()

    def on_up(self, event):
        if self.selection > 0:
            self.lbox.select_clear(self.selection)
            self.selection -= 1
            self.lbox.select_set(self.selection)
            self.on_select()

    def attach(self, textw):
        self.textw = textw

    def register_tag(self, t):
        self.registered.add(t)

    def on_mouse_select(self, event=None):
        sel = self.lbox.curselection() # tuple object
        if sel:
            self.selection = sel[0]
        self.on_select(event)

    def on_select(self, event=None):
        sel = self.lbox.curselection() # tuple object
        if sel:
            position = self._chapters[sel[0]]
            self.textw.mark_set(INSERT, position)
            self.textw.see(position)
            # self.lbox.focus()
            # self.textw.focus()

    def redraw(self, *args):
        self.lbox.delete(0, END)
        r = []
        for t in self.registered:
            tag_ranges = self.textw.tag_ranges(t)
            tmp = list()
            for a in tag_ranges:
                tmp2 = str(a).split(".")
                tmp.append( (int(tmp2[0]), int(tmp2[1])) )
            r += pairwise(tmp)
            # for a,b in pairwise(list(tag_ranges)):
            #     r.append((a,b))
        i = 0

        for a,b in sorted(r):
            self._chapters[i] = str(a[0]) + "." + str(a[1])
            toinsert = self.textw.get(str(a[0]) + "." + str(a[1]), str(b[0]) + "." + str(b[1]))
            self.lbox.insert(END, toinsert if len(toinsert) < 25 else toinsert[:20] + " ...")
            i += 1


class _SelfDestroyingToolTip:
    """
    @class _SelfDestroyingToolTip

    A tooltip that appears at the given position on its master
    and self-destroys after one second.
    """

    def __init__(self, master=None, posx=0, posy=0, text="text"):

        self.tip = Toplevel(master)
        self.tip.withdraw()
        self.tip.wm_overrideredirect(True)

        label = ttk.Label(self.tip, text=text, padding=1,
                background="lightyellow", wraplength=480,
                relief=GROOVE,
                font=FONT_TIP)
        label.grid(column=0, row=0, sticky=E+W+N+S)

        self.y = posy + master.winfo_rooty()
        self.x = posx + master.winfo_rootx()

        self.tip.wm_geometry("+{}+{}".format(self.x, self.y))
        self.tip.deiconify()
        if master.winfo_viewable():
            self.tip.transient(master)
        self.tip.update_idletasks()

        # destroy after 1 second
        self.tip.after(1000, lambda: self.tip.destroy())


class SpecialText(Text):
    """
    @class SpecialText
    A subclass of Text, scrollable, with line numbers, that adds commands :
    - copy
    - cut
    - paste
    - find
    - select all

    And two displayers for structure tags and error tags.

    It fires automatically <<Change>> events when the text is modified (any
    key pressed, or tags added or remove). It redraws the line numbers upon
    scrolling.

    @todo separate this code into two parts (yet another subclass)
    """

    def __init__(self, master=None, *args, **kwargs):
        self.frame = Frame(master)
        self.vbar = Scrollbar(self.frame)
        self.vbar.grid(column=2, row=0, rowspan=2, sticky=E+W+N+S)

        # Override the scroll command to make it generate a custom event
        kwargs.update({'yscrollcommand': self.on_scroll})
        super().__init__(self.frame, **kwargs)

        self.grid(column=1, row=0, rowspan=2, sticky=E+W+N+S)
        self.vbar['command'] = self.yview

        self.linenumbers = _TextLineNumbers(self.frame, width=50)
        self.linenumbers.attach(self)
        self.linenumbers.grid(column=0, row=0, rowspan=2, sticky=E+W+N+S)

        self.structurescroller = TagsScroller(self.frame)
        self.structurescroller.attach(self)
        self.structurescroller.grid(column=3, row=0, sticky=E+W+N+S)

        self.errorscroller = TagsScroller(self.frame)
        self.errorscroller.attach(self)
        self.errorscroller.grid(column=3, row=1, sticky=E+W+N+S)

        # WARNING : some of this code was copied from the Scrolledtext of tkinter itself
        # Copy geometry methods of self.frame without overriding Text
        # methods -- hack!
        text_meths = vars(Text).keys()
        methods = vars(Pack).keys() | vars(Grid).keys() | vars(Place).keys()
        methods = methods.difference(text_meths)

        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))

        # NOPE : do not add these bindings, as they are already implemented
        # in the Text object (however, we need these methods to bind to buttons)
        # self.bind('<Control-c>', self.on_copy)
        # self.bind('<Control-x>', self.on_cut)
        # self.bind('<Control-v>', self.on_paste)
        self.bind("<KeyRelease>", self.on_key)
        self.bind('<Control-f>', self.on_find)
        self.bind("<<Change>>", self.on_change)
        # self.bind("<<Scroll>>", self.when_scroll)

        self.tag_configure("Find", background="yellow")

        self.bind("<Control-a>", self.on_select_all)
        self.bind("<Control-A>", self.on_select_all)

        self.additional_tags = set()

    def show_tooltip_at_clicked_position(self, event, text):
        """
        Show a tooltip with the text given in argument, at the position
        that was clicked in the text zone.
        """
        tooltip = _SelfDestroyingToolTip(self, posx=event.x, posy=event.y, text=text)

    def register_structure_tag(self, tag):
        """
        Registers a tag that concerns the structure of the text (e.g chapter and sections)
        """
        self.structurescroller.register_tag(tag)

    def register_error_tag(self, tag):
        """
        Registers an error tag.
        """
        self.errorscroller.register_tag(tag)

    def register_additional_tag(self, tag):
        """
        Registers an additional tag.
        """
        self.additional_tags.add(tag)

    def get_error_tags(self):
        """
        Returns the error tags of this text zone, as a list.
        """
        return list(self.errorscroller.registered)

    def get_additional_tags(self):
        """
        Returns additional tags of this text zone, as a list.
        """
        return list(self.additional_tags)

    def remove_error_tags(self, begin, end):
        for t in self.errorscroller.registered:
            self.tag_remove(t, begin, end)

    def remove_additional_tags(self, begin, end):
        for t in self.additional_tags:
            self.tag_remove(t, begin, end)

    def on_change(self, event=None):
        """
        On a change : redraws the line numbers and the two structure displayers.
        """
        self.linenumbers.redraw()
        self.structurescroller.redraw()
        self.errorscroller.redraw()

    def tag_add(self, *args, **kwargs):
        """
        Overrides the tag_add method to fire a <<Change>> event (redraw the structure
        displayer).
        """
        super().tag_add(*args, **kwargs)
        self.event_generate("<<Change>>")

    def tag_remove(self, *args, **kwargs):
        """
        Overrides the tag_remove method to fire a <<Change>> event (redraw the structure
        displayer).
        """
        super().tag_remove(*args, **kwargs)
        self.event_generate("<<Change>>")

    def on_scroll(self, *args, **kwargs):
        """
        Redraws the line numbers on scrolling.
        """
        self.linenumbers.redraw()
        # self.event_generate("<<Scroll>>")
        self.vbar.set(*args, **kwargs)

    def on_select_all(self, event=None):
        """
        Select the whole content of the text zone.
        """
        self.tag_add(SEL, 1.0, END)
        self.mark_set(INSERT, 1.0)
        self.see(INSERT)
        return "break" # don't do any more events in tkinter


    def __str__(self):
        return str(self.frame)

    def on_key(self, event=None):
        """
        Generate a <<Change>> event when any key is pressed, to redraw line
        numbers and scroll panel.
        """
        self.event_generate("<<Change>>")


    def insert_text(self, t, event=None):
        """
        Insert text at the position INSERT and fire a <<Change>> event.
        """
        self.insert(INSERT, t)
        self.event_generate("<<Change>>")

    #================================
    # The copy, cut and paste functions are available, but they shouldn't
    # be attached to keys : the text zone already has copy, cut and paste behaviors
    # implemented
    #====================================

    def on_copy(self, event=None):
        """
        Copy the selection in the clipboard.
        """
        try:
            text = self.get(SEL_FIRST, SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(text)
        except Exception as e:
            # in that case, nothing is selected
            pass

    def on_cut(self, event=None):
        """
        Cut the selection in the clipboard.
        """
        try:
            self.on_copy()
            self.delete(SEL_FIRST, SEL_LAST)
            self.event_generate("<<Change>>")
        except Exception as e:
            # nothing is selected
            pass


    def on_paste(self, event=None):
        """
        Paste the clipboard's contents.
        """
        try:
            text = self.selection_get(selection='CLIPBOARD')
            self.insert(INSERT, text)
            self.event_generate("<<Change>>")
        except Exception as e:
            # ??
            pass


    def on_find(self, event=None):
        """
        The method has two behaviors :
        - if some text is selected, search and find in this part only
        - if no text is selected, search in the whole text
        """
        target = askstring(
                                'Chercher un motif',
                                'Sélectionnez un motif :',
                                initialvalue="")
        if target:
            self.tag_remove("Find", 1.0, END)
            begin, end = None, None
            try:
                text = self.get(SEL_FIRST, SEL_LAST)
                # if there is an exception here : no selection. Search in the
                # whole text
                begin, end = SEL_FIRST, SEL_LAST
            except Exception as e:
                begin, end = 1.0, END
            where = self.search(target, begin, end, nocase=True)
            while where:
                pastit = '{}+{}c'.format(where, len(target))
                pastit2 = '{}+{}c'.format(where, len(target)-1)
                self.tag_add("Find", where, pastit)
                begin = pastit
                where = self.search(target, begin, end, nocase=True)
                # search has ended
                if not where:
                    self.mark_set(INSERT, pastit2)
                    self.see(INSERT)
                    self.focus()

if __name__ == '__main__':

    root = Tk()
    root.title("Test")
    text = SpecialText(root)
    text.insert(1.0, "Normally, this sould display a working text zone, with line nbrs and scroll bar.")
    text.insert(END, "Also, try the ctrl + A and ctrl + F commands.")
    text.grid(row=0,column=0)
    root.mainloop()
