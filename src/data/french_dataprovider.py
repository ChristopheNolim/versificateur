"""
@file src/data/french_dataprovider.py
@version 1.1
@author CN
@author Gudule
@date jan 2017


Contains a data provider for the French language. It relies on a database
produced using the Lexique data, and Libreoffice thesaurus.

The db dictionary.db contains two tables, created as follows :
- dictionary (word text, gram text, lemma text, genra text, nbr text, phon text, onephon text, twophon text, threephon text)
- synonymes (lemma text, syns text)

The methods only handle lowercase words.

he package sqlit3 is required to make this work.
"""

try:
    from dataprovider import DataProvider
except ImportError as e:
    from data.dataprovider import DataProvider

import sqlite3
import os


class FrenchDataProvider(DataProvider):
    """
    @class FrenchDataProvider

    A DataProvider subclass aimed at French.
    """

    def __init__(self):
        """
        Creates the objecs, but does not open the db connection.
        """
        self.connection = None

    def open(self):
        """
        Opens the DB connection and reads the lexique.
        """
        print("Connecting to database data/dictionary.db")
        currentdir = os.path.dirname(os.path.abspath(__file__))
        fpath = os.path.join(currentdir, "dictionary.db")
        self.connection = sqlite3.connect(fpath)

        self.lexique = set()
        currentdir = os.path.dirname(os.path.abspath(__file__))
        fpath = os.path.join(currentdir, "lexique.txt")
        print("Loading dictionary")
        with open(fpath, "r") as f:
            for l in f:
                self.lexique.add(l[:-1])
        print("Loaded dictionary : %i words." % len(list(self.lexique)))

    def close(self):
        """
        Closes the DB connection.
        """
        self.connection.close()

    def rimes(self, word):
        """
        Get the words that have the same phonetical termination as the input.
        If the input word is not in the dictionary database, this won't return
        any result (the software has not means to search by itself for the phonetic
        of a word).

        The method tries to give more than 20 results. It will give rich rimes
        if they exists, poorer if there aren't any rich rimes.
        """
        t = self.lookup(word)
        if t is None:
            return []
        else:
            res = list()
            (word, gram, lemma, genra, nbr, phon, onephon, twophon, threephon, fourphon) = t

            q = self.connection.execute(
            """SELECT * from dictionary WHERE fourphon=?""", (fourphon,))
            if q:
                res = sorted([r[0] for r in q])

            if len(res) > 20:
                return res

            q = self.connection.execute(
            """SELECT * from dictionary WHERE threephon=?""", (threephon,))
            if q:
                res = sorted([r[0] for r in q])

            if len(res) > 20:
                return res

            q = self.connection.execute(
            """SELECT * from dictionary WHERE twophon=?""", (twophon,))
            if q:
                res = sorted([r[0] for r in q])

            if len(res) > 20:
                return res

            q = self.connection.execute(
            """SELECT * from dictionary WHERE onephon=?""", (onephon,))
            if q:
                res = sorted([r[0] for r in q])

            return res

    def is_in_dict(self, word):
        """
        Checks if a word is in the lexique.

        @warning the lexique is not the same set of words as the dictionary table.
        To check if a word is in dictionary, use lookup (which is much slower).
        """
        return word in self.lexique

    def lookup(self, word):
        """
        Checks if a word is in the dictionary.

        @return the corresponding entry of the DB if the word is in, None otherwise.
        """
        q = self.connection.execute(
            """SELECT * from dictionary WHERE word=?""", (word,))
        # return the first result
        if q:
            for r in q:
                return r
        return None

    def _syns(self, lemma):
        """
        Returns the syns of a lemma.

        """
        q = self.connection.execute(
            """SELECT * from synonymes WHERE lemma=?""", (lemma,))
        if q:
            for r in q:
                s = r[1]
                return s.split("|")
        return []

    def syns(self, word):
        """
        Returns the synonyms of a word.

        The word will first be lemmatized using the dictionary table.
        Then, the synonymes table is queried.

        @todo this behavior could be improved
        """
        if self.connection is None:
            raise Exception("Connection to DB was not opened.")

        q = self.connection.execute(
            """SELECT * from dictionary WHERE word=? ORDER BY lemma""", (word,))
        if q:
            for r in q:
                lemma = r[2]
                return self._syns(lemma)
        return []


if __name__ == "__main__":
    d = FrenchDataProvider()
    d.open()
    print(d.lookup("brocoli"))
    print(d.is_in_dict("brocoli"))
    print(d.syns("brocoli"))
    print(d.rimes("brocoli"))
    d.close()
    # print(is_in_dict("brocoli"))
    # for i in range(10000):
    #     is_in_dict("brocoli")
    pass

