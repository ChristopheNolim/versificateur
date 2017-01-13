"""
@file src/parsers/syllabes_data.py
@version 1.0
@author CN
@author Gudule
@date jan 2017

Données utilisées pour la découpe en syllabes.

@see syllabes.py
"""

#=========================
# Voyelles reconnues par le versificateur
#=============================

VOYELLES = "aeiouyâàäéèêëùûüîïôöœÿ"

#============================
# Exceptions pour la diérèse : ne pas la compter
# dans les mots qui commencent ou se finissent par ces motifs
#=============================

EXCEPT_SYN = [
"amitié", "châtié", "inanitié", "inimitié", "initié", "moitié", "pitié",
"faon", "taon", "laon", "paon", "aaron", "août", "saoûl", "saoul",
"fiacre", "diacre", "diable", "piaf", "bréviaire", "aviaire", "ferroviaire",
"viande", "diantre",
"pied", "messied", "assied",
"bief", "relief", "briefing",
"ciel", "fiel", "miel",
"bielle", "nielle",
"deuxième", "troisième",
"tien", "mien", "sien", "chien", "bien", "rien", "vien",
"gardien", "paroissien",
"batelier", "collier", "fumier", "guerrier", "herbier",
"laurier", "palmier", "portier", "dernier", "familier", "premier",
"avant-hier", "concierge", "tiers", "vierge", "acquiert",
"lierre", "pierre", "miette", "assiette","pieu",
 "pieux", "essieu", "essieux", "mieux", "monsieur",
"vieux", "lieu", "lieux",
"aimiez", "seriez", "finissiez", "croiriez", "teniez",
"surlier", "perlier",
"parliez", "ferliez", "perliez", "hurliez", "ourliez",
"aimiez", "seriez", "finissiez", "croiriez", "teniez",
"fiole", "kiosque", "mioche", "pioche",
"aimions", "serions", "finissions", "croirions", "tenions",
"surlions", "ferlions", "perlions", "hurlions", "ourlions",
"moelle", "poêle",
"douan", "ouais", "ouest", "fouet",
"juan", "duègne", "écuelle", "suint", "croître",
"oui"
]


#============================
# Exceptions pour la diérèse : ne pas la compter
# dans ces mot (précisément)
#=============================

EXCEPT_SYN_2 = [ "fief", "fiefs", "fier", "dieux", "dieu", "cieux"]


def _is_in_list(w, l):
    for test in l:
        if w.startswith(test) or w.endswith(test):
            return True
    return False

def is_except_syn(word):
    return _is_in_list(word, EXCEPT_SYN) or word in EXCEPT_SYN_2

#============================
# Exceptions pour la diérèse : la compter dans ces mots (précisément)
#=============================

EXCEPT_DIE = [
"deum", "museum",
"grièche", "grief",
"client",
"inconvénience", "obédience", "patience",
"science", "conscience"
"meurtrière", "ouvrière", "prière", "sablière", "trière",
"inquiet",
"hardiesse", "liesse",
"druide", "fluide", "incongruité", "bruin", "bruir", "ruine", "jouis"
]

def is_except_die(word):
    return _is_in_list(word, EXCEPT_DIE)


#=========================
# Motifs de synérèses (sauf exceptions)
#=========================


SYNERESES = [
"ai", "aô", "au", "aî",
"eau", "ei", "eu",
"ou", "oû", "où",
"oi", "uu",
"uay", "œi", "œu", "oeu", "ui",
["g", "ue"], ["g", "uei"], ["g", "uai"], ["g", "ua"],
["g", "uè"], ["g", "uê"], ["g", "ué"],
["q", "ue"], ["q", "ua"], ["q", "uà"], ["q", "uê"], ["q", "ué"], ["q", "uai", ""],
["q", "uoi"], "ée",
"yeu",
["", "oui", "ll"], ["", "oue", None], ["", "ie", None],
["", "aye", None], ["", "ue", None], ["", "oie", None]
# ("iè"), ["ie", "l"],
# ["ie", "ll"], ["iè", "m"], ["ière", None],
]

E_MUET = ["e", "gue", "que"]

# E = [["q", "ue"], ["g", "ue"], "e"]

# toutes les terminaisons possibles par e

MUET = ["nt", "s"]

EXCEPTIONS_SYLLMUETTE = ["moment", "que", "ment", "éloquent", "souvent", "vent", "serpent",
"cent", "adjacent", "sous-jacent", "subjacent"
]

TERM_NON_MUETTES = ["ement", "amment", "emment", "ément", "aiement", "iment"]

def has_e_muet(word, groups):
    if word in ["que"]:
        return False
    if groups[-1] == "e":
        return True
    elif groups[-1] == "ue":
        for t in ["q", "g"]:
            if groups[-2].endswith(t):
                return True
    return False

def has_syll_muette(word, groups):
    if has_e_muet(word, groups):
        return True
    for test in TERM_NON_MUETTES:
        if word.endswith(test):
            return False
    if word in EXCEPTIONS_SYLLMUETTE:
        return False
    if len(groups) > 2:
        if groups[-1] in MUET:
            if groups[-2] == "e":
                return True
            elif groups[-2] == "ue":
                for t in ["q", "g"]:
                    if groups[-3].endswith(t):
                        return True
    return False

# def _is_except_syll(word):
#     for test in TERM_NON_MUETTES:
#         if word.endswith(test):
#             return True
#     return word in EXCEPTIONS_SYLLMUETTE

#=========================
# Liste de h aspirés : le compter dans le smots qui commencent par ces motifs
# TODO non complète
#==========================

H_ASPIRE = [
"hâble", "hache", "hachette", "hachis", "hachisch", "hashich",
"hachoir", "hachure","hagard",
"haie", "haillon", "haine", "haïr", "haï", "hais", "haïra", "haire",
"halage", "halbran", "halbrener", "hâle", "halener",
"haletant", "haleter", "haleur", "hall",
"hallali", "halle", "hallebarde", "hallier",
"halo", "hâloir", "halot", "halotechnie", "halte"
"hamadryade", "hameau", "hampe", "han", "hanche",
"hand-ball", "handicap", "handicaper", "hangar",
"hanneton", "hanse", "hante", "hantise", "happe",
"haquenée", "haquet", "hara-kiri", "harangue",
"haras", "harasser", "harceler", "harcèle",
"harde", "hardi", "harem", "hareng",
"harengère", "harengerie", "hargneux",
"hargner", "haricot", "harnacher", "harnais",
"haro", "harpagon", "harpe", "harpeau",
"harpie", "harpon", "hart", "hasard",
"hase", "hâte", "hâtier", "hâtille",
"hâtif", "hâtive",  "hauban", "haubert",
"hausse", "haut",
"hâve", "havane", "havir", "havre", "heaume",
"hennir", "henniss",
"henri", "héraut", "hère", "hériss", "hernie", "herniaire",
"héron", "héros", "herse", "hêtraie", "hêtre",
"heurter", "heurtoir", "hibou", "heurt",
"hic", "hideur", "hideux", "hideuse",
"hiérarchi", "hisser", "hobereau", "hoc",
"hoche", "hochement", "hochequeue", "hochepot",
"hochet", "hocher", "hold-up", "hola",
"hollande", "hollandais", "homard", "hongre",
"hongrois", "honte", "hoquet", "hoqueton",
"horde", "horion", "hors", "hors-bord",
"hors-d’œuvre", "hors-jeu",
"hors-la-loi", "hors-série",
"hotte", "hottentot", "houblon", "houille",
"houle", "houlette", "houppe", "houleux",
"houppelande", "hourdage",
"hourder", "hourra", "hourvari", "houseaux",
"houspille", "houssage", "houssaie", "housse",
"houssoir", "houx", "hoyau", "hublot", "huche", "hue",
"hué", "huer", "huguenot",
"huhau", "huit", "hulotte",
"humer", "hurl",
"hune", "hunier", "huppe", "hure",
"hurle", "hurle", "hurluberlu", "hussard",
"hutte", "hyacinthe", "hyalin"
]

#==========================
# H aspiré dans ces mots précis
#========================

H_ASPIRE_2 = [
"hume", "huma", "héler", "hèle"
]


def is_h_aspire(word):
    for test in H_ASPIRE:
        if word.startswith(test):
            return True
    return word in H_ASPIRE_2

if __name__ == "__main__":
    print(is_h_aspire("homme"))
    print(is_h_aspire("humain"))
