"""
@file src/verse2.py
@version 1.0
@author CN
@author Gudule
@date jan 2017


Main file of the versificator : contains the main frame.
"""

from mainframe.mainframe import MainFrame
from tkinter import Tk

#==================================================

if __name__ == "__main__":

    # print("toto !")
    # print(str(__file__))
    # with open("~/Documents/V/versificateur/src/vtest.txt", "w") as f:
    #     f.write(str(__file__))

    print("Hello :D !")
    root = Tk()
    root.title("Versificateur 1.0")
    f = MainFrame(root)
    root.mainloop()
    print("Goodbye ;) !")
