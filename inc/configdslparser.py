import pyparsing

def parse(str_to_parse):
    sym = dict()
    chains = list()
    def check_file_action(string, location, tokens):
        if not os.path.exists(tokens[0]):
            raise FileNotFoundError(tokens[0])
        return tokens
    
    def fill_sym_table_action(string, location, tokens):
        sym[tokens[0]] = tokens[1]
        return tokens
    
    def var_def_action(string, location, tokens):
        if not tokens[0] in sym:
            raise NameError("'{}' is not assigned to a path".format(tokens[0]))
        return tokens
    
    identifier = pyparsing.Word(pyparsing.alphas + '_', pyparsing.alphanums + '_')
    path = pyparsing.Word(pyparsing.alphas + '~-_/.', pyparsing.alphanums + '~-_/.').setParseAction(check_file_action)
    assign = identifier("id") + pyparsing.Suppress(':') + path("path")
    nxt = pyparsing.Suppress("->")
    subrule = ((pyparsing.Suppress("%") + path) | identifier.setParseAction(var_def_action))
    rule = subrule + pyparsing.ZeroOrMore(nxt + subrule)
    spec = pyparsing.Group(pyparsing.ZeroOrMore(assign.setParseAction(fill_sym_table_action)))\
        + pyparsing.OneOrMore(rule.setParseAction())
    

