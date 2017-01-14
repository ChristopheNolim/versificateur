"""
@package tex_editor
@version 1.1
@author CN
@author Gudule
@date jan 2017

This package provides a simple editor to recognize and parse a simple subset of LateX.

It is intended for use within the software, to export documents as tex files.
Upon reading a file, Tex commands will be recognized accordingly.
Tex comments may contain additional information such as error tags, and they
will be read as well.

The commands recognized form a very small subset.
The software ensures the compatibility software -> lateX, but will never
ensure the compatibility lateX -> software.


"""

