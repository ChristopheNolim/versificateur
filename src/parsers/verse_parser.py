
"""
@file src/parsers/verse_parser.py
@version 1.1
@author CN
@author Gudule
@date jan 2017

Ce fichier contient un parser ainsi que les sous-fonctions traitant les mots
pour en extraire le nombre de syllabes.

"""

try:
    from syllabes_data import *
    from tokenizer import get_non_maj_lines
except ImportError:
    from parsers.syllabes_data import *
    from parsers.tokenizer import get_non_maj_lines

#====================
# Message correspondant à un hiatus
#==================

HIATUS = "Hiatus"

#====================
# Message correspondant à une mauvaise césure
#==================

CESURE = "Cesure"

#=======================
# Mauvais compte de syllabes
#=========================

NBSYLL = "Nbsyll"

#================================

def _cut_groups(word):
    """
    Coupe un mot en groupes de lettres qui sont soit des voyelles,
    soit des consonnes.
    Grosso modo, une syllabe par groupe de voyelles.
    """
    l = list()
    current = ""
    if word == "":
        return []
    isvow = word[0] in VOYELLES
    for c in word:
        if isvow == (c in VOYELLES):
            current += c
        else:
            isvow = not isvow
            l.append(current)
            current = c
    l.append(current)
    return l


def _analyze(w, verbose=False):
    """
    Analyse un mot et renvoie un dictionnaire avec les clés suivantes :
    word : le mot (état initial)
    syllmuette : le mot se termine-t-il par une syllabe muette ?
    endsvoy : se termine-t-il par une voyelle ?
    beginsvoy : le mot commence-t-il par une voyelle ?
    endse : se termine-t-il par e ou ue ?
    endslettere : se termine-t-il par e ? (pas forcément muet)
    hasdie : le mot a-t-il une diérèse ?
    diepos : les positions des diérèses possibles dans le mot

    Attention : le h non prononcé est automatiquement supprimé. Cela pourrait-il
    causer des erreurs ?
    """
    word = w
    # supprimer le h qu'on ne prononce pas
    if w.startswith("h") and not is_h_aspire(word):
        word = w[1:]

    # couper le mot en groupes de lettres
    l = _cut_groups(word)
    res = dict()
    res["word"] = w
    # res["pron"] = word

    # la dernière syllabe peut-elle se muettiser
    res["syllmuette"] = has_syll_muette(word, l)

    # le mot se finit-il par un e
    res["endsemuet"] = has_e_muet(word, l)

    # le mot commence par une voyelle ?
    res["beginsvoy"] = False
    if l[0][0] in VOYELLES:
        res["beginsvoy"] = True
    # le mot se finit par une voyelle ?
    res["endsvoy"] = False
    if l[-1][-1] in VOYELLES:
        res["endsvoy"] = True
    hasdie = False
    diepos = []
    count = 0
    # on compte maintenant les syllabes
    for i in range(len(l)):
        gr = l[i]
        # c'est un groupe de voyelles
        if gr[0] in VOYELLES:
            if len(gr) > 1:
                if verbose:
                    print(gr)
                syn = False
                # peut-être une diérèse
                for pat in SYNERESES:
                    if type(pat) == list:
                        if len(pat) == 2:
                            if i > 0:
                                if pat[1] == gr and pat[0] in l[i-1]:
                                    if verbose:
                                        print("Synerese")
                                    syn = True
                        elif len(pat) == 3:
                            if pat[2] is None:
                                if i == len(l) - 1:
                                    if pat[1] == gr and l[i-1].endswith(pat[0]):
                                        if verbose:
                                            print("Synerese")
                                        syn = True
                            elif i < len(l) - 1:
                                if (pat[1] == gr
                                    and l[i-1].endswith(pat[0])
                                    and l[i+1].startswith(pat[2]) ):
                                    if verbose:
                                        print("Synerese")
                                    syn = True
                    else:
                        if pat == gr:
                            if verbose:
                                print("Synerese")
                            # print(pat)
                            syn = True
                if is_except_syn(word):
                    # c'est une exception de synérèse
                    if verbose:
                        print("Synerese (exception connue)")
                    syn = True
                if not syn:
                    # on a trouvé une diérèse à cette position
                    diepos.append((len(''.join(l[:i])), len(''.join(l[:i+1]))))
                    hasdie = True
            count = count + 1
    res["diepos"] = diepos
    res["hasdie"] = hasdie
    res["count"] = count
    return res


def _parse_a_verse(words, nbsyll=None, makecesure=True):
    """
    Parse un vers (un seul), à partir de la liste de ses mots.

    @param words Une liste de mots, et uniquement de mots. Pas forcément
    lowercase.
    """
    # words = tokens
    # each is still a token
    err = []
    analysis = []
    diepos = []

    current_word = _analyze(words[0]["token"].lower())
    current_word["line"] = words[0]["line"]
    current_word["pos"] = words[0]["pos"]
    analysis.append(current_word)
    newcount = current_word["count"], current_word["count"]

    if current_word["hasdie"]:
        newcount = newcount[0], newcount[1] + 1
    counts = [newcount]

    for w in words[1:]:
        # print(w)
        next_word = _analyze(w["token"].lower())
        next_word["pos"] = w["pos"]
        next_word["line"] = w["line"]
        newcount = counts[-1]
        # compter le nouveau mot
        newcount = newcount[0] + next_word["count"], newcount[1] + next_word["count"]

        if next_word["hasdie"]:
            # ajouter une possibilité de diérèse
            newcount = newcount[0], newcount[1] + 1
            for d in next_word["diepos"]:
                diepos.append(
                            (next_word["line"], d[0] + next_word["pos"][0], d[1] + next_word["pos"][0]))
        # règle du hiatus plutôt permissive
        # une règle plus stricte serait : not current_word["endsemuet"] (donc il faudrait forcément finir par un e muet)
        if next_word["beginsvoy"] and current_word["endsvoy"] and not current_word["word"].endswith("e"):
            # ici c'est quand même une élision
            # (oui, on a tué l'apostrophe...)
            if current_word["word"].endswith("qu"):
                newcount = newcount[0] - 1, newcount[1] - 1
            else:
                # on détecte un hiatus
                newerr = dict()
                newerr["pos"] = (current_word["line"], current_word["pos"][0], next_word["line"], next_word["pos"][1])
                newerr["message"] = HIATUS
                err.append(newerr)
        if next_word["beginsvoy"] and current_word["endsemuet"]:
            # retirer une syllabe par élision du e muet
            # la retirer aussi sur le vers précédent (!!!) sinon problèmes de césure
            counts[-1] = counts[-1][0] - 1, counts[-1][1] - 1
            newcount = newcount[0] - 1, newcount[1] - 1

        analysis.append(next_word)
        counts.append(newcount)
        current_word = next_word

    # la dernière syllabe est muette
    if current_word["syllmuette"]:
        counts[-1] = counts[-1][0] - 1, counts[-1][1] - 1

    if nbsyll is not None:
        if makecesure and nbsyll % 2 == 0:
            cesure = False
            for cmin, cmax in counts:
                if cmin <= nbsyll // 2 and nbsyll // 2 <= cmax:
                    cesure = True
            if not cesure:
                # erreur de césure
                newerr = dict()
                newerr["pos"] =  (words[0]["line"], words[0]["pos"][0], words[-1]["line"], words[-1]["pos"][1])
                newerr["message"] = CESURE
                err.append(newerr)
        if not (counts[-1][0] <= nbsyll and nbsyll <= counts[-1][1]):
            # erreur sur le nombre de syllabes
            newerr = dict()
            newerr["pos"] =  (words[0]["line"], words[0]["pos"][0], words[-1]["line"], words[-1]["pos"][1])
            newerr["message"] = NBSYLL
            err.append(newerr)

    return Verse(err, counts, analysis, diepos)


def verse_parse(s, nbsyll=None, makecesure=True):
    """
    Parse le texte en entrée et vérifie la versification.

    Afin de parser de la tragédie efficacement, les lignes qui ne contiennent
    que des uppercase (HIPPOLYTE.) sont oubliées. Les lignes vides sont oubliées.
    Le parser considère que les vers peuvent se poursuivre d'une ligne à l'autre,
    et recherche la "suite" du vers tant que le nombre de syllabes courant
    est inférieur à ce qu'il cherche.

    @return Renvoie une liste d'objets Verse.
    """
    tmp_lines = s.split("\n")
    lines = get_non_maj_lines(s) # the tokens contain line number
    # at "line"
    res = []
    if not lines:
        return []
    current_verse = lines[0]
    for l in lines[1:]:
        if nbsyll is None:
            res.append(_parse_a_verse(l, nbsyll, makecesure))
        elif _parse_a_verse(current_verse, nbsyll, makecesure).counts[-1][1] >= nbsyll:
            # aller plus loin pour voir si le vers ne se complète pas
            res.append(_parse_a_verse(current_verse, nbsyll, makecesure))
            current_verse = l
        else:
            current_verse += l

    if current_verse:
        res.append(_parse_a_verse(current_verse, nbsyll, makecesure))
    return res

#================================

class Verse:
    """
    @class Verse

    Container pour un vers parsé.

    Contient les messages d'erreur et les positions des diérèses. Toutes sont
    relatives au numéro de ligne du vers, lui-même relatif à la position
    dans le texte initial des vers qui sont parsés.
    """

    def __init__(self, err, counts, analysis, diepos):
        self.err = err
        self.counts = counts
        self.analysis = analysis
        self.diepos = diepos
        self.line_nbr = self.analysis[0]["line"]


if __name__ == "__main__":

    print("Analyzing test suite")
    with open("verse_parser_test_suite.txt", "r") as f:
        for v in verse_parse(f.read(), nbsyll=12):

            if v.err:
                print("=====================")
                print("ERROR !!")
                print(v.line_nbr)
                print(v.err)
                print(v.analysis)
    pass
