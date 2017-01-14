"""
@file src/data/dataprovider.py
@version 1.1
@author CN
@author Gudule
@date jan 2017

"""


class DataProvider:
    """
    @class DataProvider

    This abstract class provides the methods to open a set of data (e.g databases),
    query it and then close it.
    """

    def __init__(self):
        raise Exception("Not implemented")

    def open(self):
        raise Exception("Not implemented")

    def close(self):
        raise Exception("Not implemented")

    def rimes(self, word):
        raise Exception("Not implemented")

    def is_in_dict(self, word):
        raise Exception("Not implemented")

    def syns(self, word):
        raise Exception("Not implemented")

