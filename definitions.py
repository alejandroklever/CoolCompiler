import time

from astnodes import *
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
atom = G.NonTerminal('atom')

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
G.Terminal('tab')
G.Terminal('space')
G.Terminal('newline')

###############
# Productions #
###############
program %= 'class-set', lambda s: ProgramNode(s[1])

class_set %= 'class-def', lambda s: [s[1]]
class_set %= 'class-def class-set', lambda s: [s[1]] + s[2]

class_def %= 'class type { feature-list }', lambda s: ClassDeclarationNode(s[2], s[4])
class_def %= 'class type inherits type { feature-list }', lambda s: ClassDeclarationNode(s[2], s[6], s[4])

feature_list %= '', lambda s: []
feature_list %= 'attribute ; feature-list', lambda s: [s[1]] + s[3]
feature_list %= 'method ; feature-list', lambda s: [s[1]] + s[3]

attribute %= 'id : type', lambda s: AttrDeclarationNode(s[1], s[3])
attribute %= 'id : type <- expr', lambda s: AttrDeclarationNode(s[1], s[3], s[5])

method %= 'id ( ) : type { expr }', lambda s: MethodDeclarationNode(s[1], [], s[5], s[7])
method %= 'id ( param-list ) : type { expr }', lambda s: MethodDeclarationNode(s[1], s[3], s[6], s[8])

param_list %= 'id : type', lambda s: [ParamNode(s[1], s[3])]
param_list %= 'id : type , param-list', lambda s: [ParamNode(s[1], s[3])] + s[5]

expr %= 'id <- expr', lambda s: AssignNode(s[1], s[3])
expr %= '{ block }', lambda s: BlockNode(s[2])
expr %= 'if expr then expr else expr fi', lambda s: ConditionalNode(s[2], s[4], s[6])
expr %= 'while expr loop expr pool', lambda s: WhileNode(s[2], s[4])
expr %= 'let declaration-list in expr', lambda s: LetNode(s[2], s[4])
expr %= 'case expr of case-list esac', lambda s: CasesNode(s[2], s[4])
expr %= 'not expr', lambda s: NegationNode(s[2])
expr %= 'comp', lambda s: s[1]

comp %= 'comp < arith', lambda s: LessNode(s[1], s[3])
comp %= 'comp <= arith', lambda s: LessEqualNode(s[1], s[3])
comp %= 'comp = arith', lambda s: EqualNode(s[1], s[3])
comp %= 'arith', lambda s: s[1]

arith %= 'arith + term', lambda s: PlusNode(s[1], s[3])
arith %= 'arith - term', lambda s: MinusNode(s[1], s[3])
arith %= 'term', lambda s: s[1]

term %= 'term * factor', lambda s: StarNode(s[1], s[3])
term %= 'term / factor', lambda s: DivNode(s[1], s[3])
term %= 'factor', lambda s: s[1]

factor %= 'isvoid factor', lambda s: IsVoidNode(s[2])
factor %= '~ factor', lambda s: ComplementNode(s[2])
factor %= 'atom', lambda s: s[1]

atom %= 'id', lambda s: VariableNode(s[1])
atom %= 'true', lambda s: BooleanNode(s[1])
atom %= 'false', lambda s: BooleanNode(s[1])
atom %= 'integer', lambda s: IntegerNode(s[1])
atom %= 'string', lambda s: StringNode(s[1])
atom %= 'function-call', lambda s: s[1]
atom %= 'new type', lambda s: InstantiateNode(s[2])
atom %= '( expr )', lambda s: s[2]

block %= 'expr ;', lambda s: [s[1]]
block %= 'expr ; block', lambda s: [s[1]] + s[3]

declaration_list %= 'id : type', lambda s: [VarDeclarationNode(s[1], s[3])]
declaration_list %= 'id : type <- expr', lambda s: [VarDeclarationNode(s[1], s[3], s[5])]
declaration_list %= 'id : type , declaration-list', lambda s: [VarDeclarationNode(s[1], s[3])] + s[5]
declaration_list %= 'id : type <- expr , declaration-list', lambda s: [VarDeclarationNode(s[1], s[3], s[5])] + s[7]

case_list %= 'id : type => expr ;', lambda s: [SingleCaseNode(s[1], s[3], s[5])]
case_list %= 'id : type => expr ; case-list', lambda s: [SingleCaseNode(s[1], s[3], s[5])] + s[7]

function_call %= 'id ( expr-list )', lambda s: MethodCallNode(s[1], s[3])
function_call %= 'atom . id ( expr-list )', lambda s: MethodCallNode(s[3], s[5], s[1])
function_call %= 'atom @ type . id ( expr-list )', lambda s: MethodCallNode(s[3], s[5], s[1])

expr_list %= 'expr', lambda s: [s[1]]
expr_list %= 'expr , expr-list', lambda s: [s[1]] + s[3]


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
        (G['tab'], '\t+'),
        (G['integer'], '-?[1-9][0-9]*'),
        (G['type'], '[A-Z][a-zA-Z0-9]*'),
        (G['id'], '[a-z][a-zA-Z0-9]*'),
        (G['string'], '"[ -~]*"'),
    ], G.EOF)


if __name__ == '__main__':
    t = time.time()
    parser = cool_parser()
    print('Building Time        :', time.time() - t, 'sec')
    print('Action Table Entries :', len(parser.action))
    print('Got Table Entries    :', len(parser.goto))
    print('Presents Conflicts   :', parser.conflict is not None)
