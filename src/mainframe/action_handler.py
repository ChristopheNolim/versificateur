from tkinter import YES, BOTH, SUNKEN, WORD, RIGHT, LEFT, Y, END, INSERT
from tkinter import SEL_FIRST, SEL_LAST, X, TOP, BOTTOM, W, E, N, S
from tkinter import Scrollbar, Text, Button, StringVar, Pack, Grid, Place
from tkinter import Frame, Label
import tkinter
import tkinter.filedialog as filedialog
import tkinter.simpledialog as simpledialog
import tkinter.messagebox as messagebox
import tkinter.scrolledtext as scrolledtext

import parsers
from parsers.verse_parser import HIATUS, CESURE, NBSYLL
from parsers.text_parser import NEEDS_MAJ, BAD_SENT_END, BAD_LINE_END, BAD_PUNC
import data.db_client as data




VERSE_ERROR_MESSAGES = {
HIATUS : "Hiatus entre ces deux mots",
CESURE : "Mauvaise césure",
NBSYLL : "Mauvais compte de pieds"
}


TEXT_ERROR_MESSAGES = {
NEEDS_MAJ : "Ce mot a besoin d'une majuscule",
BAD_SENT_END : "Mauvaise fin de phrase",
BAD_LINE_END : "Mauvaise fin de ligne",
BAD_PUNC : "Mauvaise ponctuation",
"Notindict" : "Pas dans le dictionnaire"
}

class FrenchActionProvider:

    def __init__(self):
        print("Connecting to DB.")
        self.connection = data.connection()

    def on_closing(self):
        self.connection.close()
        print("Connection to DB closed normally.")

    def get_syns(self, word):
        return sorted(data.syns(word, self.connection))

    def get_poor_rimes(self, word):
        return data.same_poor_rimes(word, self.connection)

    def get_rich_rimes(self, word):
        return data.same_rich_rimes(word, self.connection)

    def get_rimes(self, word):
        r1 = self.get_rich_rimes(word)
        if len(r1) < 10:
            return sorted(r1) + sorted(self.get_poor_rimes(word))
        else:
            return sorted(r1)

    def text_parse(self, text):
        return parsers.text_parser.text_parse(text)

    def verse_parse(self, text, nb):
        return parsers.verse_parser.verse_parse(text, nb)

    def register_errors(self, textw):

        for err in VERSE_ERROR_MESSAGES:
            textw.tag_configure(err, background='red')
            textw.tag_lower(err, "sel")
            textw.register_error_tag(err)
        #     self.text.tag_bind(err, "<ButtonRelease-1>",
        #         lambda e: self.text.show_tooltip_at_clicked_position(e, VERSE_ERROR_MESSAGES[err]))

        # self.text.tag_configure(NBSYLL, background="red")
        textw.tag_bind(NBSYLL, "<ButtonRelease-1>",
                lambda e: textw.show_tooltip_at_clicked_position(e, VERSE_ERROR_MESSAGES[NBSYLL]))
        textw.tag_bind(CESURE, "<ButtonRelease-1>",
                lambda e: textw.show_tooltip_at_clicked_position(e, VERSE_ERROR_MESSAGES[CESURE]))
        textw.tag_bind(HIATUS, "<ButtonRelease-1>",
                lambda e: textw.show_tooltip_at_clicked_position(e, VERSE_ERROR_MESSAGES[HIATUS]))

        for err in TEXT_ERROR_MESSAGES:
            textw.tag_configure(err, background='red')
            textw.tag_lower(err, "sel")
            textw.register_error_tag(err)
            # self.text.tag_bind(err, "<ButtonRelease-1>",
            #     lambda e, w=err: self.text.show_tooltip_at_clicked_position(e, TEXT_ERROR_MESSAGES[err]))

        textw.tag_bind(NEEDS_MAJ, "<ButtonRelease-1>",
                lambda e: textw.show_tooltip_at_clicked_position(e, TEXT_ERROR_MESSAGES[NEEDS_MAJ]))
        textw.tag_bind(BAD_SENT_END, "<ButtonRelease-1>",
                lambda e: textw.show_tooltip_at_clicked_position(e, TEXT_ERROR_MESSAGES[BAD_SENT_END]))
        textw.tag_bind(BAD_LINE_END, "<ButtonRelease-1>",
                lambda e: textw.show_tooltip_at_clicked_position(e, TEXT_ERROR_MESSAGES[BAD_LINE_END]))
        textw.tag_bind(BAD_PUNC, "<ButtonRelease-1>",
                lambda e: textw.show_tooltip_at_clicked_position(e, TEXT_ERROR_MESSAGES[BAD_PUNC]))
        textw.tag_bind("Notindict", "<ButtonRelease-1>",
                lambda e: textw.show_tooltip_at_clicked_position(e, TEXT_ERROR_MESSAGES["Notindict"]))





class ActionHandler(FrenchActionProvider):
    """
    @class ActionHandler

    """

    def __init__(self, textzone=None, textoutput=None):
        super().__init__()
        if textzone is None:
            raise Exception("Expected a Text element here, not None")
        if textoutput is None:
            raise Exception("Expected a Text element here, not None")

        self.sw = StringVar()
        self.sw.set("ACTION :       ")

        self.text = textzone
        self.text.tag_configure("Die", background='blue')
        self.text.register_additional_tag("Die")

        self.register_errors(self.text)

        self.output = textoutput

        self.text.bind("<KeyRelease-Return>", lambda e: self.on_hit_return_in_text(e))


    def get_stringvar(self):
        return self.sw


    def on_hit_return_in_text(self, event=None):
        begin = self.text.index("insert-1line linestart")
        end = self.text.index("insert-1line lineend")
        self.read(begin, end)

    def on_syn(self):
        try:
            s = self.text.get("insert wordstart", "insert wordend").rstrip().lstrip().lower()
        except Exception as e:
            # no selection
            pass
        self.sw.set("ACTION : SYNONYMES")
        self.output.delete(1.0, END)
        syns = self.get_syns(s)
        out = "\n".join(syns)
        self.output.insert(1.0, out)

    def on_ri(self):
        try:
            s = self.text.get("insert wordstart", "insert wordend").rstrip().lstrip().lower()
            self.sw.set("ACTION : RIMES")
            self.output.delete(1.0, END)
            syns = self.get_rimes(s)
            out = "\n".join(syns)
            self.output.insert(1.0, out)
        except Exception as e:
            # no selection
            pass

    def on_ct(self, nb):
        begin = "%s linestart" % SEL_FIRST
        end = "%s lineend" % SEL_LAST

        try:
            s = self.text.get(begin, end)
        except Exception as e:
            s = ""

        if len(s) > 1:
            self.sw.set("ACTION : COMPTAGE")
            self.output.delete(1.0, END)

            for e in VERSE_ERROR_MESSAGES:
                self.text.tag_remove(e, begin, end)

            self.text.tag_remove("Die", begin, end)

            # TODO le paramètre de recherche de la césure ???
            t = self.verse_parse(s, nb)
            # a,b = t.get_syll_count()
            # build_out = "Nombre de syllabes potentiel : entre " + str(a) + " et " + str(b) + "\n"
            ind = self.text.index(begin)
            linenb = int(str(ind).split(".")[0])

            build_out = "Résultat du décompte :\n"
            for verse in t:

                # s'il y a des erreurs
                if verse.err:
                    build_out += "Ligne " + str(linenb + verse.line_nbr) + " : \n"
                    for error in verse.err:
                        build_out += VERSE_ERROR_MESSAGES[error["message"]] + "\n"
                        a,b,c,d = error["pos"]
                        self.text.tag_add(error["message"], '{}+{}l+{}c'.format(ind, a,b), '{}+{}l+{}c'.format(ind, c, d) )
                        # self.text.tag_add(d["message"], '{}+{}'.format(ind, a), '{}+{}'.format(ind, b))
                        # self.text.tag_add(d["message"], '{}+{}l'.format(a, linenb), '{}+{}l'.format(b, linenb))
                        # self.text.tag_add(d["message"], '{}+{}l+{}c'.format(ind, verse.line_nbr, a), '{}+{}l+{}c'.format(ind, verse.line_nbr, b))


                for a,b,c in verse.diepos: # positions des diérèses
                    self.text.tag_add("Die", '{}+{}l+{}c'.format(ind, a, b), '{}+{}l+{}c'.format(ind, a, c))
                    # self.text.tag_add("Die", '{}+{}l'.format(a, linenb), '{}+{}l'.format(b, linenb))
                    # self.text.tag_add("Die", '{}+{}l+{}c'.format(ind, verse.line_nbr, a), '{}+{}l+{}c'.format(ind, verse.line_nbr, b))

            self.output.insert(1.0, build_out)


    def on_read(self, event=None):
        begin = "%s linestart" % SEL_FIRST
        end = "%s lineend" % SEL_LAST

        self.read(begin, end)

    def read(self, begin, end):
        """
        Calls the text parser (reading and verifying) on the selection begin-end.
        """
        try:
            s = self.text.get(begin, end)
        except Exception as e:
            return

        parsed = self.text_parse(s)

        if parsed:
            for e in TEXT_ERROR_MESSAGES:
                self.text.tag_remove(e, begin, end)
            self.output.delete(1.0, END)
            build_out = ""
            ind = self.text.index(begin)
            for s in parsed:
                line_nbr = s.line_nbr
                for token in s.tokens:
                    # vérifier que c'est dans le dico
                    if token["type"] == "W" and not token["token"].isdigit() and not token["token"][0].isupper():
                        if not data.is_in_dict(token["token"]) and len(token["token"]) > 1:
                            # print(token["token"])
                            # if not build_out:
                            #     build_out += "Ligne " + str(line_nbr) + " : \n"
                            build_out += TEXT_ERROR_MESSAGES["Notindict"] + "\n"
                            a,b = token["pos"]
                            self.text.tag_add("Notindict", '{}+{}l+{}c'.format(ind, line_nbr, a), '{}+{}l+{}c'.format(ind, line_nbr, b))
                if s.err:
                    build_out += "Ligne " + str(line_nbr) + " : \n"
                for error in s.err:
                    build_out += TEXT_ERROR_MESSAGES[error["message"]] + str(error["pos"]) + "\n"
                    a,b = error["pos"]
                    # print('{}+{}l+{}c'.format(ind, line_nbr, a))
                    # print('{}+{}l+{}c'.format(ind, line_nbr, b))
                    self.text.tag_add(error["message"], '{}+{}l+{}c'.format(ind, line_nbr, a), '{}+{}l+{}c'.format(ind, line_nbr, b))
            self.output.insert(1.0, build_out)

    def on_remove_error_tags(self, event=None):
        begin = "%s linestart" % SEL_FIRST
        end = "%s lineend" % SEL_LAST

        self.text.remove_error_tags(begin, end)
        self.text.remove_additional_tags(begin, end)

    # def on_remove_additional_tags(self, event=None):
    #     begin = "%s linestart" % SEL_FIRST
    #     end = "%s lineend" % SEL_LAST
    #
    #     self.remove_additional_tags(begin, end)

    def on_closing(self):
        self.connection.close()
        print("Connection to DB closing normally !")
