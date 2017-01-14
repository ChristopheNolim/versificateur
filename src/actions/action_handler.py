"""
@file src/actions/action_handler.py
@version 1.1
@author CN
@author Gudule
@date jan 2017

This package contains the layer over all "actions" that will be provided
on a text zone. The class ActionHandler defines all these actions.

The class FrenchActionHandler is a working implementation, aimed at the
french language. It relies on other packages.

@see parsers.verse_parser
@see parsers.text_parser
@see data.french_dataprovider
@see tex_editor.tags
"""

from tex_editor.tags import Tag
from data.french_dataprovider import FrenchDataProvider

from parsers.text_parser import text_parse
from parsers.verse_parser import verse_parse
from parsers.verse_parser import HIATUS, CESURE, NBSYLL
from parsers.text_parser import NEEDS_MAJ, BAD_SENT_END, BAD_LINE_END, BAD_PUNC


class ActionHandler:
    """
    @class ActionHandler

    Provides all the "actions" that may be needed in the software, for a
    specific language.
    """

    def __init__(self, data_provider):
        """
        Initializes the handler.

        @param data_provider  A DataProvider object that provides some dictionary-
                              related methods (such as looking for a word).
        """
        self.data_provider = data_provider
        self.data_provider.open()

    def error_tags(self):
        """
        Returns all the error tags that this handler's actions may return.
        """
        raise Exception("Not implemented")

    def additional_tags(self):
        """
        Returns all the additional tags that this handler's actions may return.
        """
        raise Exception("Not implemented")

    def error_message(self, tag):
        """
        Get the specific error message raised by this handler for some error tag.
        """
        raise Exception("Not implemented")

    def syns(self, word):
        """
        Queries the underlying data provider for the synonyms of a word. Handles only
        lowercase words.
        """
        return self.data_provider.syns(word)

    def rimes(self, word):
        """
        Queries the underlying data provider for the rimes of a word. Handles only
        lowercase words.
        """
        return self.data_provider.rimes(word)

    def read(self, text, line_offset=0):
        """
        Reads some text (multi-line).

        @param line_offset  The line at which this text begins in the text zone.

        @return A triple out, tags_out, errors where out is a string (typically an
        output message), tags_out is a list of tags (Tag objects) to add to the text zone
        (typically error tags), errors is the list of possible errors raised
        by this method.
        """
        raise Exception("Not implemented")

    def verse(self, text, nb, ces=True, line_offset=0):
        """
        Reads some verses (multi-line) and check syllable counts.

        @param line_offset  The line at which this text begins in the text zone.

        @return A triple out, tags_out, errors where out is a string (typically an
        output message), tags_out is a list of tags (Tag objects) to add to the text zone
        (typically error tags), errors is the list of possible errors raised
        by this method.
        """
        raise Exception("Not implemented")

    def open(self):
        """
        Opens the ActionHandler object : opens the underlying data provider
        and all its database connections.
        """
        self.data_provider.open()

    def close(self):
        """
        Closes the ActionHandler object : closes the underlying data provider
        and all its databse connections.
        """
        self.data_provider.close()



_ERROR_MESSAGES = {
    "verse" : {
    HIATUS : "Hiatus entre ces deux mots",
    CESURE : "Mauvaise césure",
    NBSYLL : "Mauvais compte de pieds"
    },
    "read" : {
    NEEDS_MAJ : "Ce mot a besoin d'une majuscule",
    BAD_SENT_END : "Mauvaise fin de phrase",
    BAD_LINE_END : "Mauvaise fin de ligne",
    BAD_PUNC : "Mauvaise ponctuation",
    "Notindict" : "Pas dans le dictionnaire"
    }
}


class FrenchActionHandler(ActionHandler):
    """
    @class FrenchActionHandler

    An ActionHandler subclass aimed at French.
    """

    def __init__(self):
        """
        Initializes the handler with a FrenchDataProvider object.
        """
        super().__init__(FrenchDataProvider())
        self._err_tags = []
        for t in _ERROR_MESSAGES:
            self._err_tags += [d for d in _ERROR_MESSAGES[t]]

    def error_tags(self):
        return self._err_tags

    def additional_tags(self):
        return ["Die"]

    def error_message(self, tag):
        for t in _ERROR_MESSAGES:
            if tag in _ERROR_MESSAGES[t]:
                return _ERROR_MESSAGES[t][tag]
        raise Exception("Did not find the error message")

    def read(self, text, line_offset=0):
        build_out = "Résultat de la relecture :\n"
        tags_out = list()
        parsed = text_parse(text)

        for s in parsed:
            line_nbr = s.line_nbr
            for token in s.tokens:
                # vérifier que c'est dans le dico
                if token["type"] == "W" and not token["token"].isdigit() and not token["token"][0].isupper():
                    if not self.data_provider.is_in_dict(token["token"]) and len(token["token"]) > 1:

                        build_out += self.error_message("Notindict") + "\n"
                        a,b = token["pos"]
                        tags_out.append(Tag.from_pos("Notindict", line_nbr, a, line_nbr, b, line_offset))
                if s.err:
                    build_out += "Ligne " + str(line_offset + line_nbr) + " : \n"
                for error in s.err:
                    build_out += self.error_message(error["message"]) + " " + str(error["pos"]) + "\n"
                    a,b = error["pos"]
                    tags_out.append(Tag.from_pos(error["message"], line_nbr, a, line_nbr, b, line_offset))

        return build_out, tags_out, _ERROR_MESSAGES["read"]

    def verse(self, text, nb, ces=True, line_offset=0):
        build_out = "Résultat du décompte :\n"
        tags_out = list()
        t = verse_parse(text, nb, makecesure=ces)

        for verse in t:
            # s'il y a des erreurs
            if verse.err:
                build_out += "Ligne " + str(line_offset + verse.line_nbr) + " : \n"
                for error in verse.err:
                    build_out += self.error_message(error["message"]) + "\n"
                    a,b,c,d = error["pos"]
                    # print(error["pos"])
                    tags_out.append(Tag.from_pos(error["message"], a, b, c, d, line_offset))

            for a,b,c in verse.diepos: # positions des diérèses
                tags_out.append(Tag.from_pos("Die", a, b, a, c, line_offset))

        return build_out, tags_out, _ERROR_MESSAGES["verse"]
