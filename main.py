import time

from cmp.grammalyzer import LALR1Parser, Lexer

from cmp.pycompiler import AttributeProduction, Sentence, Grammar


def attribute(production: str):
    def decorator(attr):
        head, body = production.split('->')
        head = G[head[:-1]]
        body = Sentence(*(G[symbol] for symbol in body[1:].split()))
        G.Add_Production(AttributeProduction(head, body, attr))

    return decorator


G = Grammar()

#################
# Non-Terminals #
#################
Program = G.NonTerminal('program', startSymbol=True)
ClassSet = G.NonTerminal('class-set')
ClassDef = G.NonTerminal('class-def')
FeatureList = G.NonTerminal('feature-list')
Attribute = G.NonTerminal('attribute')
Method = G.NonTerminal('method')
ParamVector = G.NonTerminal('param-vector')
Block = G.NonTerminal('block')
Declaration = G.NonTerminal('declaration')
CaseList = G.NonTerminal('case-list')
FunctionCall = G.NonTerminal('function-call')
ExprVector = G.NonTerminal('expr-vector')
BodyExpr = G.NonTerminal('body-expr')
Expr = G.NonTerminal('expr')
CompExpr = G.NonTerminal('comp-expr')
SubExpr = G.NonTerminal('sub-expr')
Term = G.NonTerminal('term')
Fact = G.NonTerminal('fact')
Atom = G.NonTerminal('atom')
Particle = G.NonTerminal('particle')

###############
# identifiers #
###############
identifier = G.Terminals('id')
type_name = G.Terminals('type')

###############
# Basic Types #
###############
string = G.Terminal('string')
integer = G.Terminal('integer')
boolean = G.Terminal('boolean')

###########
# Symbols #
###########
open_bracket = G.Terminal('{')
close_bracket = G.Terminal('}')
opar = G.Terminal('(')
cpar = G.Terminal(')')
comma = G.Terminal(',')
dot = G.Terminal('.')
arroba = G.Terminal('@')
two_points = G.Terminal(':')
semi_colon = G.Terminal(';')
left_arrow = G.Terminal('<-')
right_arrow = G.Terminal('=>')

############
# KeyWords #
############
keyword_class = G.Terminal('class')
keyword_inherits = G.Terminal('inherits')
keyword_if = G.Terminal('if')
keyword_then = G.Terminal('then')
keyword_else = G.Terminal('else')
keyword_fi = G.Terminal('fi')
keyword_while = G.Terminal('while')
keyword_loop = G.Terminal('loop')
keyword_pool = G.Terminal('pool')
keyword_let = G.Terminal('let')
keyword_in = G.Terminal('in')
keyword_case = G.Terminal('case')
keyword_esac = G.Terminal('esac')
keyword_of = G.Terminal('of')
keyword_new = G.Terminal('new')
keyword_isvoid = G.Terminal('isvoid')
keyword_true = G.Terminal('true')
keyword_false = G.Terminal('false')
keyword_end = G.Terminal('end')

#############
# Operators #
#############
plus = G.Terminal('+')
minus = G.Terminal('-')
star = G.Terminal('*')
div = G.Terminal('/')
less = G.Terminal('<')
lesse = G.Terminal('<=')
equal = G.Terminal('=')
complement = G.Terminal('~')
not_op = G.Terminal('not')


class CoolGrammar:

    @staticmethod
    @attribute('program -> class-set')
    def program(rule):
        pass

    @staticmethod
    @attribute('class-set -> class-def')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('class-set -> class-set class-def')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('class-def -> class type { feature-list }')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('class-def -> class type inherits type { feature-list }')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('feature-list -> attribute ;')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('feature-list -> method ;')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('feature-list -> feature-list attribute ;')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('feature-list -> feature-list method ;')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('attribute -> id : type')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('attribute -> id : type <- expr')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('method -> id ( ) : type { body-expr }')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('method -> id ( param-vector ) : type { body-expr }')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('param-vector -> id : type')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('param-vector -> param-vector , id : type')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('body-expr -> id <- expr')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('body-expr -> { block }')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('body-expr -> if expr then body-expr else body-expr fi')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('body-expr -> while expr loop body-expr pool')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('body-expr -> declaration in body-expr')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('body-expr -> case expr of case-list esac')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('body-expr -> expr')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('expr -> not expr')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('expr -> comp-expr')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('comp-expr -> comp-expr < sub-expr')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('comp-expr -> comp-expr <= sub-expr')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('comp-expr -> comp-expr = sub-expr')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('comp-expr -> sub-expr')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('sub-expr -> sub-expr + term')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('sub-expr -> sub-expr - term')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('sub-expr -> term')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('term -> term * fact')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('term -> term / fact')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('term -> fact')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('fact -> isvoid fact')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('fact -> atom')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('atom -> ~ atom')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('atom -> particle')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('particle -> id')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('particle -> true')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('particle -> false')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('particle -> integer')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('particle -> string')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('particle -> function-call')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('particle -> new type')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('particle -> ( expr )')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('block -> body-expr ;')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('block -> block body-expr ;')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('declaration -> let id : type')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('declaration -> let id : type <- expr')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('declaration -> declaration , id : type')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('declaration -> declaration , id : type <- expr')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('case-list -> id : type => expr ;')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('case-list -> case-list id : type => expr ;')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('function-call -> id ( expr-vector )')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('function-call -> particle . id ( expr-vector )')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('function-call -> particle @ type . id ( expr-vector )')
    def assignment(rule):
        pass

    @staticmethod
    @attribute('expr-vector -> expr')
    def assignment(rule):
        pass

    @attribute('expr-vector -> expr-vector , expr')
    def expr_vector(rule):
        pass


if __name__ == '__main__':
    print('Productions :', len(G.Productions))
    for p in G.Productions:
        print(repr(p))
    print()

    t = time.time()
    parser = LALR1Parser(G)
    print('Build Parsing Time :', time.time() - t)
    print('Action Entries     :', len(parser.action))
    print('Parsing Conflicts  :', parser.conflict is not None)
