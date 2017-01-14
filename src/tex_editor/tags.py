"""
@file src/tex_editor/tags.py
@version 1.1
@author CN
@author Gudule
@date jan 2017

Support for serializing tag information into TeX comments.

@todo add more tests !!
"""

import json


class Tag:

    def __init__(self, name=None):
        self.d = dict()
        self.name = name
        self.d["name"] = name

    @staticmethod
    def from_pos(name, l1, p1, l2, p2, line_offset=0):
        res = Tag(name)
        res.d["lbegin"] = l1 + line_offset
        res.d["lend"] = l2 + line_offset
        res.d["pbegin"] = p1
        res.d["pend"] = p2
        return res

    def dumps(self):
        return "%%-TAG-%% " +  json.dumps(self.d)

    @staticmethod
    def from_str(arg):
        dtmp = json.loads(arg[10:])
        res = Tag(dtmp["name"])
        res.d = dtmp
        return res

    @staticmethod
    def from_tkinter_pos(name, begin, end):
        res = Tag(name)
        t1 = str(begin).split(".")
        t2 = str(end).split(".")
        res.d["lbegin"] = int(t1[0])
        res.d["lend"] = int(t2[0])
        res.d["pbegin"] = int(t1[1])
        res.d["pend"] = int(t2[1])
        return res

    def to_tkinter_pos(self, line_offset=0):
        return (str(self.d["lbegin"] + line_offset) + "." + str(self.d["pbegin"]),
                str(self.d["lend"] + line_offset) + "." + str(self.d["pend"]) )

if __name__ == "__main__":

    t = Tag.from_pos("toto", 1, 2, 3, 4)
    t2 = Tag.from_str(t.dumps())
    assert t.d == t2.d

    # print(t.to_tkinter_pos())

    assert Tag.from_tkinter_pos(t.name, t.to_tkinter_pos()[0], t.to_tkinter_pos()[1]).d == t.d
