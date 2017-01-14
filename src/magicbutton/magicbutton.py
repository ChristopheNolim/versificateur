"""
@file src/magicbutton/magicbutton.py
@version 1.1
@author CN
@author Gudule
@date jan 2017

Some magical operations, provided by Gudule.

Pygame is required for these operations.
"""

try:
    from pygame import mixer
except Exception as e:
    print("The magic button will not function correctly !")

import random
import os

_FILES = ["data/1.mp3", "data/2.mp3", "data/3.mp3", "data/4.mp3", "data/5.mp3"]


def do_magic():
    """
    Does some magic. This is good for health.
    """
    currentdir = os.path.dirname(os.path.abspath(__file__))
    f = os.path.join(currentdir, _FILES[random.randrange(len(_FILES))])
    try:
        mixer.init()
        mixer.music.load(f)
        mixer.music.play()
        # mixer.music.play(-1,0,0)
        # mixer.music.load(f)
    except Exception as e:
        print(e)
        print("I'm sorry, the magic button will not function !")

