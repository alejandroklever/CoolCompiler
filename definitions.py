import time

from cmp.parsing import LALR1Parser, Lexer
from cmp.pycompiler import Grammar

G = Grammar()

#################
# Non-Terminals #
#################
program = G.NonTerminal('program', startSymbol=True)
class_set = G.NonTerminal('class-set')
class_def = G.NonTerminal('class-def')
feature_list = G.NonTerminal('feature-list')
attribute = G.NonTerminal('attribute')
method = G.NonTerminal('method')
param_list = G.NonTerminal('param-list')
block = G.NonTerminal('block')
declaration_list = G.NonTerminal('declaration-list')
case_list = G.NonTerminal('case-list')
function_call = G.NonTerminal('function-call')
expr_list = G.NonTerminal('expr-list')
expr = G.NonTerminal('expr')
comp = G.NonTerminal('comp')
arith = G.NonTerminal('arith')
term = G.NonTerminal('term')
factor = G.NonTerminal('factor')

###############
# identifiers #
###############
G.Terminal('id')
G.Terminal('type')

###############
# Basic Types #
###############
G.Terminal('string')
G.Terminal('integer')
G.Terminal('boolean')

###########
# Symbols #
###########
G.Terminal('{')
G.Terminal('}')
G.Terminal('(')
G.Terminal(')')
G.Terminal(',')
G.Terminal('.')
G.Terminal('@')
G.Terminal(':')
G.Terminal(';')
G.Terminal('<-')
G.Terminal('=>')

############
# Keywords #
############
G.Terminal('class')
G.Terminal('inherits')
G.Terminal('if')
G.Terminal('then')
G.Terminal('else')
G.Terminal('fi')
G.Terminal('while')
G.Terminal('loop')
G.Terminal('pool')
G.Terminal('let')
G.Terminal('in')
G.Terminal('case')
G.Terminal('esac')
G.Terminal('of')
G.Terminal('new')
G.Terminal('isvoid')
G.Terminal('true')
G.Terminal('false')
G.Terminal('end')

#############
# Operators #
#############
G.Terminal('+')
G.Terminal('-')
G.Terminal('*')
G.Terminal('/')
G.Terminal('<')
G.Terminal('<=')
G.Terminal('=')
G.Terminal('~')
G.Terminal('not')

############
# Specials #
############
G.Terminal('space')
G.Terminal('newline')

###############
# Productions #
###############
program %= 'class-set', lambda s: None

class_set %= 'class-def', lambda s: None
class_set %= 'class-def class-set', lambda s: None

class_def %= 'class type { feature-list }', lambda s: None
class_def %= 'class type inherits type { feature-list }', lambda s: None

feature_list %= 'attribute ;', lambda s: None
feature_list %= 'method ;', lambda s: None
feature_list %= 'attribute ; feature-list', lambda s: None
feature_list %= 'method ; feature-list', lambda s: None

attribute %= 'id : type', lambda s: None
attribute %= 'id : type <- expr', lambda s: None

method %= 'id ( ) : type { expr }', lambda s: None
method %= 'id ( param-list ) : type { expr }', lambda s: None

param_list %= 'id : type', lambda s: None
param_list %= 'id : type , param-list', lambda s: None

# TODO: Fix operators precedence
expr %= 'id <- expr', lambda s: None
expr %= '{ block }', lambda s: None
expr %= 'if expr then expr else expr fi', lambda s: None
expr %= 'while expr loop expr pool', lambda s: None
expr %= 'let declaration-list in expr', lambda s: None
expr %= 'case expr of case-list esac', lambda s: None
expr %= 'not expr', lambda s: None
expr %= 'isvoid expr', lambda s: None
expr %= '~ expr', lambda s: None
expr %= 'comp', lambda s: None

comp %= 'comp < arith', lambda s: None
comp %= 'comp <= arith', lambda s: None
comp %= 'comp = arith', lambda s: None
comp %= 'arith', lambda s: None

arith %= 'arith + term', lambda s: None
arith %= 'arith - term', lambda s: None
arith %= 'term', lambda s: None

term %= 'term * factor', lambda s: None
term %= 'term / factor', lambda s: None
term %= 'factor', lambda s: None

factor %= 'id', lambda s: None
factor %= 'true', lambda s: None
factor %= 'false', lambda s: None
factor %= 'integer', lambda s: None
factor %= 'string', lambda s: None
factor %= 'function-call', lambda s: None
factor %= 'new type', lambda s: None

block %= 'expr ;', lambda s: None
block %= 'expr ; block', lambda s: None

declaration_list %= 'id : type', lambda s: None
declaration_list %= 'id : type <- expr', lambda s: None
declaration_list %= 'id : type , declaration-list', lambda s: None
declaration_list %= 'id : type , declaration-list', lambda s: None

case_list %= 'id : type => expr ;', lambda s: None
case_list %= 'case-list id : type => expr ;', lambda s: None

function_call %= 'id ( expr-list )', lambda s: None
function_call %= 'factor . id ( expr-list )', lambda s: None
function_call %= 'factor @ type . id ( expr-list )', lambda s: None

expr_list %= 'expr', lambda s: None
expr_list %= 'expr , expr-list', lambda s: None


def cool_grammar():
    return G


def cool_parser():
    return LALR1Parser(G)


def cool_lexer():
    return Lexer([
        (G['+'], '\+'),
        (G['-'], '-'),
        (G['*'], '\*'),
        (G['/'], '/'),
        (G['<='], '<='),
        (G['<'], '<'),
        (G['='], '='),
        (G['~'], '~'),
        (G['not'], 'not'),
        (G['{'], '{'),
        (G['}'], '}'),
        (G['('], '\('),
        (G[')'], '\)'),
        (G[','], ','),
        (G['.'], '.'),
        (G['@'], '@'),
        (G[':'], ':'),
        (G[';'], ';'),
        (G['<-'], '<-'),
        (G['=>'], '=>'),
        (G['class'], 'class'),
        (G['inherits'], 'inherits'),
        (G['if'], 'if'),
        (G['then'], 'then'),
        (G['else'], 'else'),
        (G['fi'], 'fi'),
        (G['while'], 'while'),
        (G['loop'], 'loop'),
        (G['pool'], 'pool'),
        (G['let'], 'let'),
        (G['in'], 'in'),
        (G['case'], 'case'),
        (G['esac'], 'esac'),
        (G['of'], 'of'),
        (G['new'], 'new'),
        (G['isvoid'], 'isvoid'),
        (G['true'], 'true'),
        (G['false'], 'false'),
        (G['end'], 'end'),
        (G['space'], ' +'),
        (G['newline'], '\n+'),
        (G['integer'], '-?[1-9][0-9]+'),
        (G['type'], '[A-Z][a-zA-Z0-9]*'),
        (G['id'], '[a-z][a-zA-Z0-9]*'),
        (G['string'], '"[ -~]*"'),
    ], G.EOF)


if __name__ == '__main__':
    t = time.time()
    parser = cool_parser()
    print('Building Time        :', time.time() - t, 'sec')
    print('Action Table Entries :', len(parser.action))
    print('Presents Conflicts   :', parser.conflict is not None)
