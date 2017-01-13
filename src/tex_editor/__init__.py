"""
@package tex_editor
@version 1.0
@author CN
@author Gudule
@date jan 2017

This package provides a simple editor
 to recognize and parse a simple subset of LateX.
It is intended for use within the software, to export documents as tex files.
Upon reading a file, Tex commands will be recognized accordingly, as well
as Tex comments.
Those commands form currently a very small subset.

This package relies on ply, which uses lex / yacc. However, the user shouldn't
need to recompile the LAR tables included in the software.
"""



