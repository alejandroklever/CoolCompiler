import time

from cmp.grammalyzer.parsing import LALR1Parser
from terminals import *

Program %= 'class-set'

ClassSet %= 'class-def'
ClassSet %= 'class-set class-def'

ClassDef %= 'class type { feature-list }'
ClassDef %= 'class type inherits type { feature-list }'

FeatureList %= 'attribute ;'
FeatureList %= 'method ;'
FeatureList %= 'feature-list attribute ;'
FeatureList %= 'feature-list method ;'

Attribute %= 'id : type'
Attribute %= 'id : type <- expr'

Method %= 'id ( ) : type { body-expr }'
Method %= 'id ( param-vector ) : type { body-expr }'

ParamVector %= 'id : type'
ParamVector %= 'param-vector , id : type'

####################
# Body-Expressions #
####################
BodyExpr %= 'id <- expr'
BodyExpr %= '{ block }'
BodyExpr %= 'if expr then body-expr else body-expr fi'
BodyExpr %= 'while expr loop body-expr pool'
BodyExpr %= 'declaration in body-expr'
BodyExpr %= 'case expr of case-list esac'
BodyExpr %= 'expr'
###################
#       end       #
###################

####################
# Body-Expressions #
####################
Expr %= 'not expr'
Expr %= 'comp-expr'
###################
#       end       #
###################

#######################
# Compose-Expressions #
#######################
CompExpr %= 'comp-expr < sub-expr'
CompExpr %= 'comp-expr <= sub-expr'
CompExpr %= 'comp-expr = sub-expr'
CompExpr %= 'sub-expr'
###################
#       end       #
###################

###################
# Sub-Expressions #
###################
SubExpr %= 'sub-expr + term'
SubExpr %= 'sub-expr - term'
SubExpr %= 'term'
###################
#       end       #
###################

########
# Term #
########
Term %= 'term * fact'
Term %= 'term / fact'
Term %= 'fact'
#######
# end #
#######

##########
# Factor #
##########
Fact %= 'isvoid fact'
Fact %= 'atom'
##########
#  end   #
##########

########
# Atom #
########
Atom %= '~ atom'
Atom %= 'particle'
###################
#       end       #
###################


############
# Particle #
############
Particle %= 'id'
Particle %= 'true'
Particle %= 'false'
Particle %= 'integer'
Particle %= 'string'
Particle %= 'function-call'
Particle %= 'new type'
Particle %= '( expr )'
###################
#       end       #
###################


#########
# Block #
#########
Block %= 'body-expr ;'
Block %= 'block body-expr ;'
#########
#  end  #
#########

###############
# Declaration #
###############
Declaration %= 'let id : type'
Declaration %= 'let id : type <- expr'
Declaration %= 'declaration , id : type'
Declaration %= 'declaration , id : type <- expr'
###############
#     end     #
###############

#############
# Case-List #
#############
CaseList %= 'id : type => expr ;'
CaseList %= 'case-list id : type => expr ;'
#############
#    end    #
#############

#################
# Function-Call #
#################
FunctionCall %= 'id ( expr-vector )'
FunctionCall %= 'particle . id ( expr-vector )'
FunctionCall %= 'particle @ type . id ( expr-vector )'
#################
#      end      #
#################


#####################
# Expression-Vector #
#####################
ExprVector %= 'expr'
ExprVector %= 'expr-vector , expr'
#####################
#        end        #
#####################


if __name__ == "__main__":
    print(len(G.Productions))
    for p in G.Productions:
        print(repr(p))
    print()

    t = time.time()
    parser = LALR1Parser(G)
    print('Build Parsing Time :', time.time() - t)
    print('Action Entries     :', len(parser.action))
    print('Parsing Conflicts  :', parser.conflict is not None)
