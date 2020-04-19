import astnodes as ast
import time

from cmp.parsing import LALR1Parser
from cmp.pycompiler import Grammar

G = Grammar()

#################
# Non-Terminals #
#################
program = G.add_non_terminal('program', startSymbol=True)
class_list = G.add_non_terminal('class-list')
class_def = G.add_non_terminal('class-def')
feature_list = G.add_non_terminal('feature-list')
attribute = G.add_non_terminal('attribute')
method = G.add_non_terminal('method')
param_list = G.add_non_terminal('param-list')
block = G.add_non_terminal('block')
declaration_list = G.add_non_terminal('declaration-list')
case_list = G.add_non_terminal('case-list')
function_call = G.add_non_terminal('function-call')
expr_list = G.add_non_terminal('expr-list')
expr = G.add_non_terminal('expr')
comp = G.add_non_terminal('comp')
arith = G.add_non_terminal('arith')
term = G.add_non_terminal('term')
factor = G.add_non_terminal('factor')
atom = G.add_non_terminal('atom')

###############
# identifiers #
###############
G.add_terminal('id')
G.add_terminal('type')

###############
# Basic Types #
###############
G.add_terminal('string')
G.add_terminal('integer')
G.add_terminal('boolean')

###########
# Symbols #
###########
G.add_terminal('{')
G.add_terminal('}')
G.add_terminal('(')
G.add_terminal(')')
G.add_terminal(',')
G.add_terminal('.')
G.add_terminal('@')
G.add_terminal(':')
G.add_terminal(';')
G.add_terminal('<-')
G.add_terminal('=>')

############
# Keywords #
############
G.add_terminal('class')
G.add_terminal('inherits')
G.add_terminal('if')
G.add_terminal('then')
G.add_terminal('else')
G.add_terminal('fi')
G.add_terminal('while')
G.add_terminal('loop')
G.add_terminal('pool')
G.add_terminal('let')
G.add_terminal('in')
G.add_terminal('case')
G.add_terminal('esac')
G.add_terminal('of')
G.add_terminal('new')
G.add_terminal('isvoid')
G.add_terminal('true')
G.add_terminal('false')

#############
# Operators #
#############
G.add_terminal('+')
G.add_terminal('-')
G.add_terminal('*')
G.add_terminal('/')
G.add_terminal('<')
G.add_terminal('<=')
G.add_terminal('=')
G.add_terminal('~')
G.add_terminal('not')


###############
# Productions #
###############
program %= 'class-list', lambda s: ast.ProgramNode(s[1])

class_list %= 'class-def', lambda s: [s[1]]
class_list %= 'class-def class-list', lambda s: [s[1]] + s[2]

class_def %= 'class type { feature-list }', lambda s: ast.ClassDeclarationNode(s[2], s[4])
class_def %= 'class type inherits type { feature-list }', lambda s: ast.ClassDeclarationNode(s[2], s[6], s[4])

feature_list %= '', lambda s: []
feature_list %= 'attribute ; feature-list', lambda s: [s[1]] + s[3]
feature_list %= 'method ; feature-list', lambda s: [s[1]] + s[3]

attribute %= 'id : type', lambda s: ast.AttrDeclarationNode(s[1], s[3])
attribute %= 'id : type <- expr', lambda s: ast.AttrDeclarationNode(s[1], s[3], s[5])

method %= 'id ( ) : type { expr }', lambda s: ast.MethodDeclarationNode(s[1], [], s[5], s[7])
method %= 'id ( param-list ) : type { expr }', lambda s: ast.MethodDeclarationNode(s[1], s[3], s[6], s[8])

param_list %= 'id : type', lambda s: [(s[1], s[3])]
param_list %= 'id : type , param-list', lambda s: [(s[1], s[3])] + s[5]

expr %= 'id <- expr', lambda s: ast.AssignNode(s[1], s[3])
expr %= '{ block }', lambda s: ast.BlockNode(s[2])
expr %= 'if expr then expr else expr fi', lambda s: ast.ConditionalNode(s[2], s[4], s[6])
expr %= 'while expr loop expr pool', lambda s: ast.WhileNode(s[2], s[4])
expr %= 'let declaration-list in expr', lambda s: ast.LetNode(s[2], s[4])
expr %= 'case expr of case-list esac', lambda s: ast.SwitchCaseNode(s[2], s[4])
expr %= 'not expr', lambda s: ast.NegationNode(s[2])
expr %= 'comp', lambda s: s[1]

comp %= 'arith < arith', lambda s: ast.LessNode(s[1], s[3])
comp %= 'arith <= arith', lambda s: ast.LessEqualNode(s[1], s[3])
comp %= 'arith = arith', lambda s: ast.EqualNode(s[1], s[3])
comp %= 'arith', lambda s: s[1]

arith %= 'arith + term', lambda s: ast.PlusNode(s[1], s[3])
arith %= 'arith - term', lambda s: ast.MinusNode(s[1], s[3])
arith %= 'term', lambda s: s[1]

term %= 'term * factor', lambda s: ast.StarNode(s[1], s[3])
term %= 'term / factor', lambda s: ast.DivNode(s[1], s[3])
term %= 'factor', lambda s: s[1]

factor %= 'isvoid factor', lambda s: ast.IsVoidNode(s[2])
factor %= '~ factor', lambda s: ast.ComplementNode(s[2])
factor %= 'atom', lambda s: s[1]

atom %= 'id', lambda s: ast.VariableNode(s[1])
atom %= 'true', lambda s: ast.BooleanNode(s[1])
atom %= 'false', lambda s: ast.BooleanNode(s[1])
atom %= 'integer', lambda s: ast.IntegerNode(s[1])
atom %= 'string', lambda s: ast.StringNode(s[1])
atom %= 'function-call', lambda s: s[1]
atom %= 'new type', lambda s: ast.InstantiateNode(s[2])
atom %= '( expr )', lambda s: s[2]

block %= 'expr ;', lambda s: [s[1]]
block %= 'expr ; block', lambda s: [s[1]] + s[3]

declaration_list %= 'id : type', lambda s: [ast.VarDeclarationNode(s[1], s[3])]
declaration_list %= 'id : type <- expr', lambda s: [ast.VarDeclarationNode(s[1], s[3], s[5])]
declaration_list %= 'id : type , declaration-list', lambda s: [ast.VarDeclarationNode(s[1], s[3])] + s[5]
declaration_list %= 'id : type <- expr , declaration-list', lambda s: [ast.VarDeclarationNode(s[1], s[3], s[5])] + s[7]

case_list %= 'id : type => expr ;', lambda s: [ast.CaseNode(s[1], s[3], s[5])]
case_list %= 'id : type => expr ; case-list', lambda s: [ast.CaseNode(s[1], s[3], s[5])] + s[7]

function_call %= 'id ( expr-list )', lambda s: ast.MethodCallNode(s[1], s[3])
function_call %= 'atom . id ( expr-list )', lambda s: ast.MethodCallNode(s[3], s[5], s[1])
function_call %= 'atom @ type . id ( expr-list )', lambda s: ast.MethodCallNode(s[3], s[5], s[1])

expr_list %= 'expr', lambda s: [s[1]]
expr_list %= 'expr , expr-list', lambda s: [s[1]] + s[3]


def cool_parser():
    return LALR1Parser(G)


if __name__ == '__main__':
    t = time.time()
    parser = cool_parser()
    print('Building Time        :', time.time() - t, 'seconds')
    print('Action Table Entries :', len(parser.action))
    print('Got Table Entries    :', len(parser.goto))
    print('Presents Conflicts   :', parser.conflicts is not None)
