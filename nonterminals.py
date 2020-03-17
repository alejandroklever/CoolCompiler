from cmp.pycompiler import Grammar, Production, Sentence, NonTerminal


class ImprovedGrammar(Grammar):
    def NonTerminal(self, name, startSymbol=False):
        name = name.strip()
        if not name:
            raise Exception("Empty name")

        term = ImprovedNonTerminal(name, self)

        if startSymbol:

            if self.startSymbol is None:
                self.startSymbol = term
            else:
                raise Exception("Cannot define more than one start symbol.")

        self.nonTerminals.append(term)
        self.symbDict[name] = term
        return term


class ImprovedNonTerminal(NonTerminal):
    def __imod__(self, other):
        try:
            return super().__imod__(other)
        except TypeError:

            if isinstance(other, str):
                sentence = Sentence(*(self.Grammar[s] for s in other.split()))
                p = Production(self, sentence)
                self.Grammar.Add_Production(p)
                return self

            raise TypeError()


G = ImprovedGrammar()

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
