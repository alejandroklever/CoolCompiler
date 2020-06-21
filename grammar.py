import inspect
import time

from semantics.utils import astnodes as ast
from pyjapt.parsing import LALR1Parser
from pyjapt.grammar import Grammar

G = Grammar()

#################
# Non-Terminals #
#################
program = G.add_non_terminal('program', start_symbol=True)
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
not_empty_expr_list = G.add_non_terminal('not-empty-expr-list')
expr = G.add_non_terminal('expr')
comp = G.add_non_terminal('comp')
arith = G.add_non_terminal('arith')
term = G.add_non_terminal('term')
factor = G.add_non_terminal('factor')
atom = G.add_non_terminal('atom')

###########
# Symbols #
###########
G.add_terminals('{ } ( ) . , : ; @ <- =>')

############
# Keywords #
############
keywords = G.add_terminals(
    'class inherits if then else fi while loop pool let in case of esac new isvoid true false not')
keywords_names = {x.name for x in keywords}

#############
# Symbols #
#############
G.add_terminals('+ - * / < <= = ~')


###############
# Identifiers #
###############
@G.terminal('id', r'[a-z][a-zA-Z0-9_]*')
def id_terminal(lexer):
    lexer.column += len(lexer.token.lex)
    lexer.position += len(lexer.token.lex)
    lexer.token.token_type = lexer.token.lex if lexer.token.lex in keywords_names else lexer.token.token_type
    return lexer.token


G.add_terminal('type', regex=r'[A-Z][a-zA-Z0-9_]*')

###############
# Basic Types #
###############
G.add_terminal('string', regex=r'\"[^\"]*\"')
G.add_terminal('int', regex=r'\d+')


############
# Comments #
############
@G.terminal('comment', r'(\(\*[^$]*\*\))|--.*')
def comment(lexer):
    lex = lexer.token.lex
    for s in lex:
        if s == '\n':
            lexer.lineno += 1
            lexer.column = 0
        lexer.column += 1
    lexer.position += len(lex)


@G.terminal('comment_error', r'\(\*(.|\n)*$')
def comment_eof_error(lexer):
    lexer.contain_errors = True
    lex = lexer.token.lex
    for s in lex:
        if s == '\n':
            lexer.lineno += 1
            lexer.column = 0
        lexer.column += 1
    lexer.position += len(lex)
    lexer.print_error(f'{lexer.lineno, lexer.column} -LexicographicError: EOF in comment')


##################
# Ignored Tokens #
##################
@G.terminal('newline', r'\n+')
def newline(lexer):
    lexer.lineno += len(lexer.token.lex)
    lexer.position += len(lexer.token.lex)
    lexer.column = 1


@G.terminal('whitespace', r' +')
def whitespace(lexer):
    lexer.column += len(lexer.token.lex)
    lexer.position += len(lexer.token.lex)


@G.terminal('tabulation', r'\t+')
def tab(lexer):
    lexer.column += 4 * len(lexer.token.lex)
    lexer.position += len(lexer.token.lex)


@G.lexical_error
def lexical_error(lexer):
    lexer.print_error(f'{lexer.lineno, lexer.column} -LexicographicError: ERROR "{lexer.token.lex}"')
    lexer.column += 1
    lexer.position += 1


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

comp %= 'arith < arith', lambda s: ast.LessThanNode(s[1], s[2], s[3])
comp %= 'arith <= arith', lambda s: ast.LessEqualNode(s[1], s[2], s[3])
comp %= 'arith = arith', lambda s: ast.EqualNode(s[1], s[2], s[3])
comp %= 'arith', lambda s: s[1]

arith %= 'arith + term', lambda s: ast.PlusNode(s[1], s[2], s[3])
arith %= 'arith - term', lambda s: ast.MinusNode(s[1], s[2], s[3])
arith %= 'term', lambda s: s[1]

term %= 'term * factor', lambda s: ast.StarNode(s[1], s[2], s[3])
term %= 'term / factor', lambda s: ast.DivNode(s[1], s[2], s[3])
term %= 'factor', lambda s: s[1]

factor %= 'isvoid factor', lambda s: ast.IsVoidNode(s[2])
factor %= '~ factor', lambda s: ast.ComplementNode(s[2])
factor %= 'atom', lambda s: s[1]

atom %= 'id', lambda s: ast.VariableNode(s[1])
atom %= 'true', lambda s: ast.BooleanNode(s[1])
atom %= 'false', lambda s: ast.BooleanNode(s[1])
atom %= 'int', lambda s: ast.IntegerNode(s[1])
atom %= 'string', lambda s: ast.StringNode(s[1])
atom %= 'function-call', lambda s: s[1]
atom %= 'new type', lambda s: ast.InstantiateNode(s[2])
atom %= '( expr )', lambda s: s[2]

block %= 'expr ;', lambda s: [s[1]]
block %= 'expr ; block', lambda s: [s[1]] + s[3]

declaration_list %= 'id : type', lambda s: [(s[1], s[3], None)]
declaration_list %= 'id : type <- expr', lambda s: [(s[1], s[3], s[5])]
declaration_list %= 'id : type , declaration-list', lambda s: [(s[1], s[3], None)] + s[5]
declaration_list %= 'id : type <- expr , declaration-list', lambda s: [(s[1], s[3], s[5])] + s[7]

case_list %= 'id : type => expr ;', lambda s: [(s[1], s[3], s[5])]
case_list %= 'id : type => expr ; case-list', lambda s: [(s[1], s[3], s[5])] + s[7]

function_call %= 'id ( expr-list )', lambda s: ast.MethodCallNode(s[1], s[3])
function_call %= 'atom . id ( expr-list )', lambda s: ast.MethodCallNode(s[3], s[5], s[1])
function_call %= 'atom @ type . id ( expr-list )', lambda s: ast.MethodCallNode(s[5], s[7], s[1], s[3])

expr_list %= '', lambda s: []
expr_list %= 'not-empty-expr-list', lambda s: s[1]
not_empty_expr_list %= 'expr', lambda s: [s[1]]
not_empty_expr_list %= 'expr , not-empty-expr-list', lambda s: [s[1]] + s[3]

#####################
# Error Productions #
#####################
G.add_terminal_error()


@G.production("feature-list -> attribute error feature-list")
def feature_attribute_error(s):
    s.error(f"{s[2].line, s[2].column} - SyntacticError: Expected ';' instead of '{s[2].lex}'")
    return [s[1]] + s[3]


@G.production("feature-list -> method error feature-list")
def feature_method_error(s):
    s.error(f"{s[2].line, s[2].column} - SyntacticError: Expected ';' instead of '{s[2].lex}'")
    return [s[1]] + s[3]


@G.production("case-list -> id : type => expr error")
def case_list_error(s):
    s.error(f"{s[5].line, s[5].column} - SyntacticError: Expected ';' instead of '{s[5].lex}'")
    return [(s[1], s[3], s[5])]


@G.production("block -> expr error")
def block_single_error(s):
    s.error(f"{s[2].line, s[2].column} - SyntacticError: Expected ';' instead of '{s[2].lex}'")
    return [s[1]]


if __name__ == '__main__':
    t = time.time()
    G.serialize_lexer('CoolLexer', inspect.getmodulename(__file__))
    G.serialize_parser(LALR1Parser(G), 'CoolParser', inspect.getmodulename(__file__))
    print('Serialization Time :', time.time() - t, 'seconds')
