
"""
@file src/tex_editor/tex_parser.py
@version 1.0
@author CN
@author Gudule
@date jan 2017

Parser for a small subset of the Tex / LateX language.


The parsing recognizes some TeX commands and returns a list of tuples
(text, tags applied to the text).

"""


MAPPING_IN = {
"textbf" : "BOLD",
"textit" : "ITAL",
"textsc" : "SMALLCAPS",
"chapter" : "CHAPTER",
"section" : "SECTION",
"flushleft" : "FLUSHLEFT",
"flushright" : "FLUSHRIGHT",
"center" : "CENTER",
"footnote" : "FOOTNOTE",
"underline" : "UNDERLINE"
}

MAPPING_IN_LONE = {
"oe" : "œ",
"OE" : "Œ",
"og" : "«",
"fg" : "»",
"dots" : "…",
"'e" : "é"
# ("’", "'"),
# ("«", "\""),
# ("»", "\""),
# ("…", "..."),
# ("[", "("),
# ("]", ")"),
# ("œ", "oe")
# "oe" : "œ"
}

MAPPING_OUT_LONE = {
# "é" : "'e",
"œ" : "oe",
"Œ" : "OE",
"«" : "og",
"»" : "fg",
"…" : "dots"
}

MAPPING_OUT_NORMAL = {
"BOLD" : ["textbf"],
"ITAL" : ["textit"],
"CHAPTER" : ["chapter"],
"SECTION" : ["section"],
"FOOTNOTE" : ["footnote"],
"UNDERLINE" : ["underline"],
"SMALLCAPS" : ["textsc"]
}

MAPPING_OUT_ENV = {
"FLUSHLEFT" : ["flushleft"],
"FLUSHRIGHT" : ["flushright"],
"CENTER" : ["center"]
}

_REPLACE ={
"^" : " ",
"\u00A0" : " ", # le dernier : espace insécable de LibreOffice
"’" : "'"
}


def pre_refactor(inpt):
    res = inpt.rstrip().replace("\n\n", "\n")
    for key in _REPLACE:
        res = res.replace(key, _REPLACE[key])
    return res.replace("~\n", "\n")

def post_refactor(outpt):
    # i = 1
    # m = "\n"
    # while m in outpt:
    #     i += 1
    #     m += "\n"
    # res = outpt
    # m = m[:-1]
    # while m in res and len(m) > 1:
    #     res = res.replace(m, "\n" + m[:-1].replace("\n", "~\n"))
    #     m = m[:-1]
    res = outpt.rstrip().replace("\n", "~\n")
    for key in _REPLACE:
        res = res.replace(key, _REPLACE[key])
    return res.replace("\n", "\n\n")


def _parse(inpt):
    formatted = []
    processing_command = False
    current_commands = []
    command = ""
    commands_have_changed = False
    current_envs = set()
    prevcoms = []
    currenttext = ""
    isbegin = False
    isend = False
    for c in inpt:
        try:
            prevcoms = [MAPPING_IN[com] for com in current_commands
            if com in MAPPING_IN] + [MAPPING_IN[com] for com in current_envs
            if com in MAPPING_IN]
            if c == "\\":
                command = ""
                processing_command = True
                commands_have_changed = False
            elif c == "{" and command == "begin":
                processing_command = True
                isend = False
                isbegin = True
                command = ""
                commands_have_changed = False
            elif c == "}" and isbegin:
                isbegin = False
                isend = False
                processing_command = False
                current_envs.add(command)
                commands_have_changed = True
            elif c == "{" and command == "end":
                processing_command = True
                isend = True
                isbegin = False
                command = ""
                commands_have_changed = False
            elif c == "}" and isend:
                processing_command = False
                isend = False
                isbegin = False
                if command in current_envs:
                    current_envs.discard(command)
                    commands_have_changed = True
            elif c == "{" and command in MAPPING_IN_LONE:
                processing_command = False

            elif c == "{" and command not in ["begin", "end"]:
                processing_command = False
                current_commands.append(command)
                commands_have_changed = True

            elif c == "}" and command in MAPPING_IN_LONE:
                currenttext += MAPPING_IN_LONE[command] + " "
                command = ""

            elif c == "}" and command not in ["begin", "end"]:
                current_commands = current_commands[:-1]
                commands_have_changed = True
            elif processing_command and c == " ":
                if command in MAPPING_IN_LONE:
                    currenttext += MAPPING_IN_LONE[command]
                command = ""
                processing_command = False
            elif processing_command:
                command += c
            else:
                currenttext += c

            if commands_have_changed:
                if currenttext:
                    if "SMALLCAPS" in prevcoms:
                        formatted.append((currenttext.upper(), prevcoms))
                    else:
                        formatted.append((currenttext, prevcoms))
                    # currenttext = c
                    commands_have_changed = False
                    currenttext = ""
                else:
                    # currenttext += c
                    commands_have_changed = False
            # else:
            #     currenttext += c

        except Exception as e:
            pass
    if currenttext:
        coms = [MAPPING_IN[com] for com in current_commands
        if com in MAPPING_IN] + [MAPPING_IN[com] for com in current_envs
        if com in MAPPING_IN]
        formatted.append((currenttext, coms))
        currenttext = c

    return formatted






# the toplevel function
# TODO
# handle lone commands in a tex-compliant way
#    >>> print(tex_parse("\\\\oe{}uf ou bien \\\\oe uf"))
#    [('œ', []), ('uf', []), (' ', []), ('ou', []), (' ', []), ('bien', []), (' ', []), ('œ', []), (' ', []), ('uf', [])]
def tex_parse(inpt):
    """
    Parses the input.
    Warning :  to write tests, need to double the backslash symbol (that has to be doubled already)

    >>> print(tex_parse("\\\\begin{center} Toto\\\\textbf{plage}Bloup \\\\end{center}"))
    [(' Toto', ['CENTER']), ('plage', ['BOLD', 'CENTER']), ('Bloup ', ['CENTER'])]
    >>> print(tex_parse("\\\\textbf{argument} Tandis que cependant \\\\textbf{} suite"))
    [('argument', ['BOLD']), (' Tandis que cependant ', []), (' suite', [])]
    >>> print(tex_parse("\\\\textbf{./;,?!§─}_"))
    [('./;,?!§─', ['BOLD']), ('_', [])]
    >>> print(tex_parse("\\\\textbf{./;,?!§─}"))
    [('./;,?!§─', ['BOLD'])]
    >>> print(tex_parse("\\\\textbf{blou()\\"blou}blo\\""))
    [('blou()"blou', ['BOLD']), ('blo"', [])]
    """
    return _parse(pre_refactor(inpt))


def tex_to_tags(inpt):
    """
    Used only for debugging / testing purposes, since the interface
    between parsed tex and tags is normally made by the tkinter
    text zone itself...
    """
    tmp = tex_parse(inpt)
    if not tmp:
        return []

    res = []
    current_tags = tmp[0][1]
    for t in current_tags:
        res.append(('tagon', t, ''))
    current_text = tmp[0][0]

    for text, tags in tmp[1:]:
        if tags == current_tags:
            current_text += text
        else:
            # tags have changed
            res.append(('text', current_text, ''))
            current_text = text
            add_tags = set(tags) - set(current_tags)
            remove_tags = set(current_tags) - set(tags)

            for t in add_tags:
                res.append(('tagon', t, ''))
            for t in remove_tags:
                res.append(('tagoff', t, ''))
            current_tags = tags
    if current_text:
        res.append(('text', current_text, ''))
    if current_tags:
        for t in current_tags:
            res.append(('tagoff', t, ''))

    return res


def tags_to_tex(formatted):
    """
    Takes in input a list of triples from the description of a Tex-compliant
    text zone (from tkinter).
    Translates it in TeX.
    The third part of the triple is not interesting, it represents a position
    in the text zone.

    >>> print(tags_to_tex([('tagon', 'BOLD', '1.0'), ('text', 'toto', '1.0'), ('tagoff', 'BOLD', '1.4'), ('text', 'bloup', '1.4')]))
    \\textbf{toto}bloup
    """
    res = ""
    to_tag_off = set()
    to_tag_on = set()
    # current_normal_tags = set()
    is_small_caps = False
    for a,b,c in formatted:
        if a == 'tagon':
            to_tag_on.add(b)

        elif a == 'text':

            for tag in to_tag_off:
                if tag in MAPPING_OUT_NORMAL:
                    for t in MAPPING_OUT_NORMAL[tag]:
                        res += "}"
                if tag == "SMALLCAPS":
                    is_small_caps = False

            for tag in to_tag_off:
                if tag in MAPPING_OUT_ENV:
                    for t in MAPPING_OUT_ENV[tag]:
                        res += "\\end{" + t + "}"

            for tag in to_tag_on:
                if tag in MAPPING_OUT_ENV:
                    for t in MAPPING_OUT_ENV[tag]:
                        res += "\\begin{" + t + "}"

            for tag in to_tag_on:
                if tag == "SMALLCAPS":
                    is_small_caps = True
                if tag in MAPPING_OUT_NORMAL:
                    for t in MAPPING_OUT_NORMAL[tag]:
                        res += "\\" + t + "{"

            if is_small_caps:
                res += b.lower()
            else:
                res += b
            to_tag_on = set()
            to_tag_off = set()

        elif a == 'tagoff':
            to_tag_off.add(b)

    for tag in to_tag_off:
        if tag in MAPPING_OUT_NORMAL:
            for t in MAPPING_OUT_NORMAL[tag]:
                res += "}"
    for tag in to_tag_off:
        if tag in MAPPING_OUT_ENV:
            for t in MAPPING_OUT_ENV[tag]:
                res += "\\end{" + t + "}"

    # the last refactoring to do
    for c in MAPPING_OUT_LONE:
        res = res.replace(c + " ", "\\" + MAPPING_OUT_LONE[c] + "{}")
        res = res.replace(c, "\\" + MAPPING_OUT_LONE[c] + " ")
    while "  " in res:
        res = res.replace("  ", " ")

    return post_refactor(res)
    # if verbose:
    #     print(res)
    # return res


if __name__ == "__main__":

    import doctest

    test_suite_1 = [
        "\\textbf{toto} re \\oe blo\\oe up. \\fg{}",
        "\\begin{center}\\textbf{Toto}\\end{center}",
        "\\og{} Toto floufi \\fg{}."
        # "Ceci est un test h\\'e h\\'e h\\'e{}grandeur nature."
    ]
    for test in test_suite_1:
        if tags_to_tex(tex_to_tags(test)) != test:
            print("Failure :")
            print(test)
            print(tex_to_tags(test))
            print(tags_to_tex(tex_to_tags(test)))

    test_suite_2 = [
        [('text', "Héhéhé bouh Moche.", '')],
        [('text', "Et de sa voix puissante, il tempêta : « encore » floufi !", '')]
    ]
    for test in test_suite_2    :
        # print(tags_to_tex(test))
        if tex_to_tags(tags_to_tex(test)) != test:
            print("Failure :")
            print(test)
            print(tags_to_tex(test))
            print(tex_to_tags(tags_to_tex(test)))
