from nonterminals import *

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
