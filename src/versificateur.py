"""
@file src/versificateur.py
@version 1.1
@author CN
@author Gudule
@date jan 2017


Main file.

"""

from mainframe.mainframe import MainFrame
from tkinter import Tk

import os

#==================================================

if __name__ == "__main__":

    print("Hello :D !")
    root = Tk()

    root.title("Versificateur 1.0")
    try:
        currentdir = os.path.dirname(os.path.abspath(__file__))
        ipath = os.path.join(currentdir, "betterave.xbm")
        root.iconbitmap("@" + ipath)
    except Exception as e:
        print(e)

    f = MainFrame(root)
    root.mainloop()
    print("Goodbye ;) !")
