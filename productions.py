from terminals import *
from cmp.grammalyzer.parsing import LR1Parser, LALR1Parser

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

CompExpr %= 'comp-expr < sub-expr'
CompExpr %= 'comp-expr <= sub-expr'
CompExpr %= 'comp-expr = sub-expr'
CompExpr %= 'sub-expr'

SubExpr %= 'sub-expr + term'
SubExpr %= 'sub-expr - term'
SubExpr %= 'term'

Term %= 'term * fact'
Term %= 'term / fact'
Term %= 'fact'

Fact %= 'isvoid fact'
Fact %= 'atom'

Atom %= '~ atom'
Atom %= 'particle'

Particle %= 'id'
Particle %= 'true'
Particle %= 'false'
Particle %= 'integer'
Particle %= 'string'
Particle %= 'function-call'
Particle %= 'new type'
Particle %= '( expr )'

Block %= 'body-expr ;'
Block %= 'block body-expr ;'

Declaration %= 'let id : type'
Declaration %= 'let id : type <- expr'
Declaration %= 'declaration , id : type'
Declaration %= 'declaration , id : type <- expr'

CaseList %= 'id : type => expr ;'
CaseList %= 'case-list id : type => expr ;'

FunctionCall %= 'id ( expr-vector )'
FunctionCall %= 'particle . id ( expr-vector )'
FunctionCall %= 'particle @ type . id ( expr-vector )'

ExprVector %= 'expr'
ExprVector %= 'expr-vector , expr'


if __name__ == "__main__":
    print(len(G.Productions))
    for p in G.Productions:
        print(repr(p))
    print()

    parser = LALR1Parser(G)
    print(len(parser.action))
    if parser.conflict is not None:
        print(parser.conflict.cType)
        for item in parser.state_dict[parser.conflict.state].state:
            print(item)
