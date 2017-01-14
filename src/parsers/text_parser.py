"""
@file src/parsers/text_parser.py
@version 1.1
@author CN
@author Gudule
@date jan 2017

Parse du texte :  découpe en tokens et vérifie que la ponctuation est correcte.

@todo La vérification de ponctuation n'est pas optimale

"""

try:
    from tokenizer import tokenize
except ImportError as e:
    from parsers.tokenizer import tokenize

# signe de fin de phrase
_SEND = [".", "!", "?"]

# ponctuation acceptée en fin de phrase, en milieu de paragraphe
_ACCEPT_SEND_1 = [". ", " ! ", " ? ", "… ", " ».", ". » ", ". « ",
" » ! ", " ! » ", " ? » ", " » ? "]

# ponctuation acceptée en fin de phrase, en fin de paragraphe
_ACCEPT_SEND_2 = [".\n", " !\n", " ?\n", " :\n", ",\n", " ;\n", "…\n",
". »\n", " ».\n", " »\n", "\n", " » !\n", " » ?\n", " ! »\n", " ? »\n", ")\n"
]

# ponctuation acceptée si la phrase coupe sur un saut de ligne
# _ACCEPT_PUNC_2 = [",", " ;", " :", ""]

# ponctuation acceptée en cours de phrase
# TODO séparer avec début de phrase
_ACCEPT_PUNC = ["« ", "(",
 ", ", " ; ", " : ",
" - ", "- ", " ", "'", " (", ") ", " « ", " » ", "-", ", « ", " »,",
" : « ", "[…]", ". » – ", " – ", " ? » – "
]

# message d'erreur : besoin d'une majuscule au mot indiqué
NEEDS_MAJ = "Needsmaj"

# message d'erreur : mauvaise fin de phrase
BAD_SENT_END = "Badsentend"

# mauvaise fin de ligne (typiquement espace en fin de ligne)
BAD_LINE_END = "Badlineend"

# mauvaise ponctuation
BAD_PUNC = "Badpunc"

#======================================================


def _parse(tokens):
    """
    Parse la liste des tokens obtenus à partir d'une ligne de texte. JUSTE une
    ligne.
    """
    current_errs = []
    current_sent = []

    i = 0
    needsmaj = True
    for t in tokens:
        current_sent = current_sent + [t]
        if t["type"] == "W":
            if needsmaj:
                if t["token"][0].islower():
                    newerr = dict()
                    newerr["message"] = NEEDS_MAJ
                    newerr["pos"] = t["pos"]
                    current_errs = current_errs + [newerr]
            needsmaj = False
        elif "\n" in t["token"]:
            ok = False
            for test in _ACCEPT_SEND_2:
                if t["token"].startswith(test):
                    ok = True
            if ok:
                yield current_errs, current_sent
                current_errs, current_sent = [], []
            else:
                newerr = dict()
                newerr["message"] = BAD_LINE_END
                newerr["pos"] = t["pos"]
                yield current_errs + [newerr], current_sent
                current_errs, current_sent = [], []
        else:
            # punctuation
            ok = False
            is_send = False
            for c in _SEND:
                if c in t["token"]:
                    is_send = True
                    needsmaj = True
                    ok = t["token"] in _ACCEPT_SEND_1
                        # for test in _ACCEPT_SEND_1:
                        #     if t["token"].startswith(test):
                        #         ok = True
            if is_send:
                # mustmaj = True
                if ok:
                    yield current_errs, current_sent
                    current_errs, current_sent = [], []
                else:
                    newerr = dict()
                    newerr["message"] = BAD_SENT_END
                    newerr["pos"] = t["pos"]
                    yield current_errs + [newerr], current_sent
                    current_errs, current_sent = [], []

            elif t["token"] in _ACCEPT_PUNC:
                pass
                mustmaj = False
            else:
                mustmaj = False
                newerr = dict()
                newerr["message"] = BAD_PUNC
                newerr["pos"] = t["pos"]
                current_errs += [newerr]
    if current_sent:
        yield current_errs, current_sent


class Sent:

    def __init__(self, err, tokens, line_nbr):
        self.err = err
        self.tokens = tokens
        self.line_nbr = line_nbr


def text_parse(text):
    """
    Parse le texte. Découpe d'abord en lignes, puis parse chaque ligne
    et renvoie la liste complète des phrases (objets Sent).
    """
    res = []
    spl = text.split("\n")
    line_nbr = 0
    for par in spl:
        for errs, toks in _parse(tokenize(par + "\n")):
            res.append(Sent(errs, toks, line_nbr))
        line_nbr += 1

    return res


if __name__ == "__main__":
    # TODO écrire des tests
    test = """Toi qui connais mon cœur depuis que je respire.\nDes sentiments d’un cœur si fier, si dédaigneux,\n
Peux-tu me demander le désaveu honteux ?\n
C’est peu qu’avec son lait une mère amazone \n
M’a fait sucer encor cet orgueil qui t’étonne;
    """

    for s in text_parse("Toi qui connais mon cœur depuis que je respire\n\nDes sentiments d'un cœur si fier, si dédaigneux,\n\n\n\n"):
        # print(s.tokens)
        print(s.line_nbr)
        print(s.err)

