"""Mini DSL for the experimentation of incremental compilation of the
Linux kernel.

See the following grammar:

           GRAMMAR
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    spec    ::= (assign)*(rule)+
    assign  ::= id : path
    path    ::= [aA0-zZ9_/-.]+
    subrule ::= ("%"path | id)
    rule    ::= id (nxt id)*
    nxt     ::= "->"
    id      ::= [aA0-zZ9_/.]+
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

Identifier:
-----------

You can assign a path to an identifier like so:
``id : path/to/.config``

Path:
-----

If you do not want to assign a path to an identifier, you can write it
in the chain by adding a ``%`` before the path, like so:
``%path/to/config1 -> %path/to/config2``

Chain Rule
----------

Example:
  c : linux-4.14.152/.config
  config1 : exp0/.config
  config1 -> %linux-4.14.152/.config -> c

"""


import os
import pyparsing

def parse_file(filename):
    """Parse the content of a file

    """
    file_content = []
    with open(filename, 'r') as f:
        file_content = f.readlines()
    return parse(''.join(file_content))


def parse(str_to_parse):
    """Parser of the following grammar:

    """

    sym = dict()
    chains = list()

    def check_file_action(string, location, tokens):
        if not os.path.exists(tokens[0]):
            raise FileNotFoundError("Line {}, col {}: {}"\
                                    .format(pyparsing.lineno(location, string),
                                        pyparsing.col(location, string),
                                        tokens[0]))
        return tokens


    def fill_sym_table_action(string, location, tokens):
        sym[tokens[0]] = tokens[1]
        return tokens

    def var_def_action(string, location, tokens):
        if not tokens[0] in sym:
            raise NameError("Line {}, col {}: '{}' is not assigned to a path"\
                            .format(pyparsing.lineno(location, string),
                                    pyparsing.col(location, string), tokens[0]))
        return tokens

    def fill_chain_list_action(string, location, tokens):
        tokens_list = tokens.asList()
        if tokens_list not in chains:
            chains.append(tokens.asList())
        return tokens

    identifier = pyparsing.Word(pyparsing.alphas + '_',
                                pyparsing.alphanums + '_')
    path = pyparsing.Word(pyparsing.alphas + '~-_/.',
                          pyparsing.alphanums + '~-_/.')\
                    .setParseAction(check_file_action)
    assign = identifier("id") + pyparsing.Suppress(':') + path("path")
    nxt = pyparsing.Suppress("->")
    subrule = (
        (pyparsing.Suppress("%") + path)
        | identifier.setParseAction(var_def_action))
    rule = subrule + pyparsing.ZeroOrMore(nxt + subrule)
    spec = pyparsing.Group(pyparsing.ZeroOrMore(
        assign.setParseAction(fill_sym_table_action)))\
        + pyparsing.OneOrMore(rule.setParseAction(fill_chain_list_action))
    spec.parseString(str_to_parse)
    return sym, chains
