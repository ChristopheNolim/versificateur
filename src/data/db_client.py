"""
@file src/data/db_client.py
@version 1.0
@author CN
@author Gudule
@date jan 2017


This file provides an interface to the database of french words stored
in dictionary.db.
The methods require a database connection.
"""

import sqlite3

import os

def connection():
    """
    Returns a datbase connection.
    It requires to be closed afterwards.
    """
    print("Connecting to database data/dictionary.db")
    currentdir = os.path.dirname(os.path.abspath(__file__))
    fpath = os.path.join(currentdir, "dictionary.db")
    conn = sqlite3.connect(fpath)
    return conn

def syns(word, conn):
    """
    Get synonyms of a word.
    """
    q = conn.execute(
        """SELECT * from dictionary WHERE word=? ORDER BY lemma""", (word,))
    if q:
        for r in q:
            lemma = r[2]
            return _syns(lemma, conn)
    return []

def _syns(lemma, conn):
    """
    Get the lemma of a word.
    """
    q = conn.execute(
        """SELECT * from synonymes WHERE lemma=?""", (lemma,))
    if q:
        for r in q:
            s = r[1]
            return s.split("|")
    return []

def lookup_in_dict(word, conn):
    """
    Look if a word is in the dictionary.
    """
    q = conn.execute(
        """SELECT * from dictionary WHERE word=?""", (word,))
    # return the first result
    if q:
        for r in q:
            return r
    return None


print("Loading dictionary")

LEXIQUE = set()
currentdir = os.path.dirname(os.path.abspath(__file__))
fpath = os.path.join(currentdir, "lexique.txt")

with open(fpath, "r") as f:
    for l in f:
        LEXIQUE.add(l[:-1])

print("Loaded dictionary : %i words." % len(list(LEXIQUE)))

def is_in_dict(word, conn=None):
    return word in LEXIQUE

# TODO enable even if the word is not in the dict
def same_poor_rimes(word, conn):
    """
    If this word is in the dictionary, find words with the same rimes.
    """
    t = lookup_in_dict(word, conn)
    if t is None:
        return []
    else:
        q = conn.execute(
        """SELECT * from dictionary WHERE rpoor=?""", (t[3],))
        if q:
            return [r[0] for r in q]
        else:
            return []


def same_rich_rimes(word, conn):
    t = lookup_in_dict(word, conn)
    if t is None:
        return []
    else:
        q = conn.execute(
        """SELECT * from dictionary WHERE rrich=?""", (t[4],))
        if q:
            return [r[0] for r in q]
        else:
            return []

if __name__ == "__main__":
    # print(is_in_dict("brocoli"))
    # for i in range(10000):
    #     is_in_dict("brocoli")
    pass
