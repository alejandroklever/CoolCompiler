from productions import *

def attribute(nonTerminal, sentence):
    from cmp.pycompiler import AttributeProduction, Sentence
    def decorator(attribute):
        G.Add_Production(
            AttributeProduction(
                G[nonTerminal], 
                Sentence(*(G[s] for s in sentence.split())), 
                attribute)
                )
    return decorator

class CoolGrammar:
    @attribute('program', 'class-set')
    def assignment(s):
        pass

    @attribute('assignment', 'id <- expr')
    def assignment(s):
        pass
