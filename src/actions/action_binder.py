"""
@file src/actions/action_binder.py
@version 1.1
@author CN
@author Gudule
@date jan 2017


@see ActionHandler
"""

from tkinter import StringVar, SEL_FIRST, SEL_LAST, END
from actions.action_handler import ActionHandler


class ActionBinder:
    """
    @class ActionBinder

    This class provides a binding between :
    - the action handler, that handles the behavior of actions
    - an input text zone, where the actions are called and where they have consequences
    - an output text zone, where all relevant messages and results are printed
    """

    def __init__(self, action_handler, text_inpt, text_output):
        """
        Creates an ActionBinder.

        The action_handler in parameter provides some tags (error tags and
        additional tags) ; they are configured in the input text zone.
        """
        self.action_handler = action_handler
        self.text = text_inpt
        self.output = text_output

        for err in self.action_handler.error_tags():
            self.text.tag_configure(err, background='red')
            self.text.tag_lower(err, "sel")
            self.text.register_error_tag(err)

            self.text.tag_bind(err, "<ButtonRelease-1>",
                lambda e, mess=self.action_handler.error_message(err): self.text.show_tooltip_at_clicked_position(e, mess))

        for t in self.action_handler.additional_tags():
            self.text.tag_configure(t, background="blue")
            self.text.tag_lower(t, "sel")
            self.text.register_additional_tag(t)

        self.sw = StringVar()
        self.sw.set("ACTION :       ")
        self.text.bind("<KeyRelease-Return>", lambda e: self.on_hit_return_in_text(e))

    def get_stringvar(self):
        """
        Returns a string variable (tkinter) that describes the current action.
        """
        return self.sw

    def on_hit_return_in_text(self, event=None):
        """
        Behavior to apply when <<Return>> is hit in the text. The former
        line is re-read.
        """
        begin = self.text.index("insert-1line linestart")
        end = self.text.index("insert-1line lineend")
        self.read(begin, end)

    def on_syn(self):
        """
        Behavior to apply when a query for synonyms is made. The action handler
        is queried for synonyms of the current selected word. The results are
        displayed in the output zone.
        """
        try:
            s = self.text.get("insert wordstart", "insert wordend").rstrip().lstrip().lower()
        except Exception as e:
            # no selection
            return
        self.sw.set("ACTION : SYNONYMES")
        self.output.delete(1.0, END)
        out = "\n".join(self.action_handler.syns(s))
        self.output.insert(1.0, out)

    def on_ri(self):
        """
        Behavior to apply when a query for rimes is made. The action handler
        is queried for rimes of the current selected word. The results are
        displayed in the output zone.
        """
        try:
            s = self.text.get("insert wordstart", "insert wordend").rstrip().lstrip().lower()
        except Exception as e:
            return
        self.sw.set("ACTION : RIMES")
        self.output.delete(1.0, END)
        out = "\n".join(self.action_handler.rimes(s))
        self.output.insert(1.0, out)

    def on_ct(self, nb):
        """
        Behavior to apply when a query for counting is made. The verse method
        of ActionHandler is queried on the selection (from the beginning of the
        first line to the end of the last line). All tags returned are applied
        to the input text zone.
        """
        begin = "%s linestart" % SEL_FIRST
        end = "%s lineend" % SEL_LAST

        try:
            s = self.text.get(begin, end)
        except Exception as e:
            return

        if len(s) > 1:
            ind = self.text.index(begin)
            linenb = int(str(ind).split(".")[0])
            build_out, tags_out, possible_errors = self.action_handler.verse(s, nb, ces=True, line_offset=linenb)

            self.sw.set("ACTION : COMPTAGE")
            self.output.delete(1.0, END)

            for t in possible_errors:
                self.text.tag_remove(t, begin, end)

            for tag in tags_out:
                a, b = tag.to_tkinter_pos()
                self.text.tag_add(tag.name, a, b)

            self.output.insert(1.0, build_out)


    def on_read(self, event=None):
        """
        Behavior to apply when a query for reading is made. The read method
        of ActionHandler is queried on the selection (from the beginning of the
        first line to the end of the last line). All tags returned are applied
        to the input text zone.
        """
        begin = "%s linestart" % SEL_FIRST
        end = "%s lineend" % SEL_LAST

        self.read(begin, end)

    def read(self, begin, end):
        try:
            s = self.text.get(begin, end)
        except Exception as e:
            return

        ind = self.text.index(begin)
        linenb = int(str(ind).split(".")[0])
        build_out, tags_out, possible_errors = self.action_handler.read(s, line_offset=linenb)

        self.sw.set("ACTION : RELECTURE")
        self.output.delete(1.0, END)

        for t in possible_errors:
            self.text.tag_remove(t, begin, end)

        for tag in tags_out:
            a, b = tag.to_tkinter_pos()
            self.text.tag_add(tag.name, a, b)

        self.output.insert(1.0, build_out)

    def on_remove_error_tags(self, event=None):
        """
        Removes all relevant tags on the current selection (from the beginning of the
        first line to the end of the last line).

        @todo remove just error tags or error + additional ? currently additional also
        """
        begin = "%s linestart" % SEL_FIRST
        end = "%s lineend" % SEL_LAST

        self.text.remove_error_tags(begin, end)
        self.text.remove_additional_tags(begin, end)

    def on_closing(self):
        """
        Behavior to apply when the application closes : closes the action handler.
        """
        self.action_handler.close()
