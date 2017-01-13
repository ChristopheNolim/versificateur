"""
@file src/parsers/tokenizer.py
@version 1.0
@author CN
@author Gudule
@date jan 2017

"""

# signe non-alphanumérique interne à un mot
_INTERNAL = "-%"

_EXCEPT_INTERNAL_SECOND_PART = ["il", "elle", "ils", "je", "tu", "toi", "moi", "nous", "vous", "le", "la", "les"]

def yield_current_word(pos, current):
    for p in _EXCEPT_INTERNAL_SECOND_PART:
        if current.endswith("-t-" + p):
            if len(current.split("-")) == 3:
                p1 = current.split("-")[0]
                p2 = current.split("-")[2]
                tok1 = dict()
                tok1["type"] = "W"
                tok1["token"] = p1
                tok1["pos"] = (pos, pos + len(p1))
                yield tok1
                tok = dict()
                tok["type"] = "P"
                tok["token"] = "-"
                tok["pos"] = (pos + len(p1), pos + len(p1) + 1)
                yield tok
                tok = dict()
                tok["type"] = "W"
                tok["token"] = "t"
                tok["pos"] = (pos + len(p1), pos + len(p1) + 1)
                yield tok
                tok = dict()
                tok["type"] = "P"
                tok["token"] = "-"
                tok["pos"] = (pos + len(p1), pos + len(p1) + 1)
                yield tok
                tok2 = dict()
                tok2["type"] = "W"
                tok2["token"] = p2
                tok2["pos"] = (pos + len(p1) + 1, pos + len(current))
                yield tok2
                return

        elif current.endswith("-" + p):
            if len(current.split("-")) == 2:
                p1 = current.split("-")[0]
                p2 = current.split("-")[1]
                tok1 = dict()
                tok1["type"] = "W"
                tok1["token"] = p1
                tok1["pos"] = (pos, pos + len(p1))
                yield tok1
                tok = dict()
                tok["type"] = "P"
                tok["token"] = "-"
                tok["pos"] = (pos + len(p1), pos + len(p1) + 1)
                yield tok
                tok2 = dict()
                tok2["type"] = "W"
                tok2["token"] = p2
                tok2["pos"] = (pos + len(p1) + 1, pos + len(current))
                yield tok2
                return
    tok1 = dict()
    tok1["type"] = "W"
    tok1["token"] = current
    tok1["pos"] = (pos, pos + len(current))
    yield tok1


def tokenize(text):
    """
    Découpe un texte français en tokens : mots ou ponctuations.
    Les ponctuations conservent les espaces.

    >>> list(tokenize("Gudule demanda-t-il.")) == [{'pos': (0, 6), 'type': 'W', 'token': 'Gudule'}, {'pos': (6, 7), 'type': 'P', 'token': ' '}, {'pos': (7, 14), 'type': 'W', 'token': 'demanda'}, {'pos': (14, 15), 'type': 'P', 'token': '-'}, {'pos': (14, 15), 'type': 'W', 'token': 't'}, {'pos': (14, 15), 'type': 'P', 'token': '-'}, {'pos': (15, 19), 'type': 'W', 'token': 'il'}, {'pos': (19, 19), 'type': 'P', 'token': '.'}]
    True
    """
    current = ""
    pos = 0
    posprec = 0
    if not text:
        return []
    currenttype = "W" if (text[0].isalpha() or text[0].isdigit()) else "P"
    if len(text) == 1:
        return [text]
    current = text[0]
    for c in text[1:]:
        pos += 1
        if c in _INTERNAL and currenttype == "W":
            newtype = "W"
        elif c.isalpha() or c.isdigit():
            newtype = "W"
        else:
            newtype = "P"
        if newtype != currenttype:
            if currenttype == "W":
                for t in yield_current_word(posprec , current ):
                    yield t
            else:
                tok = dict()
                tok["type"] = currenttype
                tok["token"] = current
                tok["pos"] = (posprec , pos )
                yield tok
            posprec = pos
            current = c
            currenttype = newtype
        else:
            current += c
    if current:
        if currenttype == "W":
            for t in yield_current_word(posprec , current ):
                yield t
        else:
            tok = dict()
            tok["type"] = currenttype
            tok["token"] = current
            tok["pos"] = (posprec , pos )
            yield tok

def get_words(text):
    """
    Attention : supprime toutes les apostrophes, par voie de conséquence.
    """
    res = list()
    for tok in tokenize(text):
        if tok["type"] == "W":
            res.append(tok)
        elif tok["token"] == "-t-":
            tok["token"] = t
            res.append(tok)
    return res

def get_non_maj_lines(text):
    res = list()
    lines = text.split("\n")
    line_count = 0
    current_line = []
    for l in lines:
        ltmp = l.rstrip().lstrip()
        if ltmp and not ltmp.isupper():
            current_line = []
            for tok in tokenize(l):
                if tok["type"] == "W":
                    tok["line"] = line_count
                    current_line.append(tok)
                elif tok["token"] == "-t-":
                    tok["line"] = line_count
                    tok["token"] = t
                    current_line.append(tok)
            if current_line:
                res.append(current_line)
        line_count += 1
    return res

if __name__ == "__main__":

    # print(list(tokenize("Gudule demanda-t-il.")))
    print(get_non_maj_lines("Jouons, alors, Akin. Jouons.\n\n   \n  AKIN\nQue veux-tu dire ?"))

    import doctest

    doctest.testmod()

    # print(list(tokenize("Gudule demanda-t-il.")))
