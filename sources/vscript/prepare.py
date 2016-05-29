
import sys
import os
import ply.lex as lex
import ply.yacc as yacc
import settings
from . import lexemes, syntax


# tablepath = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), VDOM_CONFIG["TEMP-DIRECTORY"]))
# lexer_table_name = "vscript_%s_lexer_table" % os.path.splitext(os.path.basename(sys.argv[0]))[0]
# parser_table_name = "vscript_%s_parser_table" % os.path.splitext(os.path.basename(sys.argv[0]))[0]
lexer_table_name = "vscript.tables.lexer"
parser_table_name = "vscript.tables.parser"
optimize = settings.OPTIMIZE_VSCRIPT_PARSER


if VDOM_CONFIG["DISABLE-VSCRIPT"]:
    print "VScript are disabled through configuration"
    lexer = None
    parser = None
else:
    # print "Preparing VScript engine...",
    # lexer = lex.lex(module=lexemes, debug=False, optimize=optimize, outputdir=tablepath, lextab=lexer_table_name)
    # parser = yacc.yacc(module=syntax, debug=False, start="source", optimize=optimize, outputdir=tablepath, tabmodule=parser_table_name)
    lexer = lex.lex(module=lexemes, debug=False, optimize=optimize, lextab=lexer_table_name)
    parser = yacc.yacc(module=syntax, debug=False, start="source", optimize=optimize, tabmodule=parser_table_name) # write_tables=False
    # print "Done"
