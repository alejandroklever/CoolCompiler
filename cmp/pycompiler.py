import json
from typing import List, FrozenSet, Optional, Union, Tuple, Iterable, Callable

ProductionList = List[Union['Production', 'AttributeProduction']]
Rule = Optional[Callable[[List[object]], object]]


class Symbol:
    def __init__(self, name: str, grammar: 'Grammar'):
        self.name: str = name
        self.grammar: 'Grammar' = grammar

    @property
    def IsEpsilon(self):
        return False

    def __str__(self):
        return self.name

    def __repr__(self):
        return repr(self.name)

    def __add__(self, other):
        if isinstance(other, Symbol):
            return Sentence(self, other)

        raise TypeError(other)

    def __or__(self, other):
        if isinstance(other, Sentence):
            return SentenceList(Sentence(self), other)
        raise TypeError(other)

    def __len__(self):
        return 1


class NonTerminal(Symbol):
    def __init__(self, name, grammar):
        super().__init__(name, grammar)
        self.productions: ProductionList = []
        self.error_productions: ProductionList = []

    def __mod__(self, other):
        if isinstance(other, str):
            if other:
                p = Production(self, Sentence(*(self.grammar[s] for s in other.split())))
            else:
                p = Production(self, self.grammar.EPSILON)
            self.grammar.add_production(p)
            return self

        if isinstance(other, Symbol):
            p = Production(self, Sentence(other))
            self.grammar.add_production(p)
            return self

        if isinstance(other, Sentence):
            p = Production(self, other)
            self.grammar.add_production(p)
            return self

        if isinstance(other, tuple):
            assert len(other) > 1

            if isinstance(other[0], str):
                if other[0]:
                    other = (Sentence(*(self.grammar[s] for s in other[0].split())),) + other[1:]
                else:
                    other = (self.grammar.EPSILON,) + other[1:]

            if isinstance(other[0], Symbol) or isinstance(other[0], Sentence):
                p = AttributeProduction(self, other[0], other[1])
            else:
                raise Exception("")

            self.grammar.add_production(p)
            return self

        if isinstance(other, SentenceList):
            for s in other:
                p = Production(self, s)
                self.grammar.add_production(p)
            return self

        raise TypeError(other)

    @property
    def IsTerminal(self):
        return False

    @property
    def IsNonTerminal(self):
        return True

    @property
    def IsEpsilon(self):
        return False


class Terminal(Symbol):
    def __init__(self, name: str, grammar: 'Grammar'):
        super().__init__(name, grammar)

    @property
    def IsTerminal(self):
        return True

    @property
    def IsNonTerminal(self):
        return False

    @property
    def IsEpsilon(self):
        return False


class Error(Terminal):
    def __init__(self, G):
        super().__init__('error', G)

    def __eq__(self, other):
        return isinstance(other, Terminal)


class EOF(Terminal):
    def __init__(self, G):
        super().__init__('$', G)


class Sentence:
    def __init__(self, *args):
        self.symbols = tuple(x for x in args if not x.IsEpsilon)
        self.hash = hash(self.symbols)

    def __len__(self):
        return len(self.symbols)

    def __add__(self, other) -> 'Sentence':
        if isinstance(other, Symbol):
            return Sentence(*(self.symbols + (other,)))

        if isinstance(other, Sentence):
            return Sentence(*(self.symbols + other.symbols))

        raise TypeError(other)

    def __or__(self, other) -> 'SentenceList':
        if isinstance(other, Sentence):
            return SentenceList(self, other)

        if isinstance(other, Symbol):
            return SentenceList(self, Sentence(other))

        raise TypeError(other)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return ("%s " * len(self.symbols) % tuple(self.symbols)).strip()

    def __iter__(self):
        return iter(self.symbols)

    def __getitem__(self, index):
        return self.symbols[index]

    def __eq__(self, other) -> bool:
        return self.symbols == other.symbols

    def __hash__(self):
        return self.hash

    @property
    def IsEpsilon(self):
        return False


class SentenceList:
    def __init__(self, *args):
        self._sentences = list(args)

    def Add(self, symbol):
        if not symbol and (symbol is None or not symbol.IsEpsilon):
            raise ValueError(symbol)

        self._sentences.append(symbol)

    def __iter__(self):
        return iter(self._sentences)

    def __or__(self, other):
        if isinstance(other, Sentence):
            self.Add(other)
            return self

        if isinstance(other, Symbol):
            return self | Sentence(other)


class Epsilon(Terminal, Sentence):
    def __init__(self, grammar: 'Grammar'):
        super().__init__('epsilon', grammar)

    def __str__(self):
        return "e"

    def __repr__(self):
        return 'epsilon'

    def __iter__(self):
        yield from ()

    def __len__(self):
        return 0

    def __add__(self, other):
        return other

    def __eq__(self, other):
        return isinstance(other, (Epsilon,))

    def __hash__(self):
        return hash("")

    @property
    def IsEpsilon(self):
        return True


class Production:
    def __init__(self, nonTerminal, sentence):
        self.Left: NonTerminal = nonTerminal
        self.Right: Sentence = sentence

    @property
    def IsEpsilon(self):
        return self.Right.IsEpsilon

    def __str__(self):
        return '%s := %s' % (self.Left, self.Right)

    def __repr__(self):
        return '%s -> %s' % (self.Left, self.Right)

    def __iter__(self):
        yield self.Left
        yield self.Right

    def __eq__(self, other):
        return isinstance(other, Production) and self.Left == other.Left and self.Right == other.Right

    def __hash__(self):
        return hash((self.Left, self.Right))


class AttributeProduction(Production):
    def __init__(self, nonTerminal, sentence, attribute):
        if not isinstance(sentence, Sentence) and isinstance(sentence, Symbol):
            sentence = Sentence(sentence)
        super().__init__(nonTerminal, sentence)

        self.attribute: Rule = attribute


class Grammar:
    def __init__(self):
        self.productions: ProductionList = []
        self.non_terminals: List[NonTerminal] = []
        self.terminals: List[Terminal] = []
        self.start_symbol: NonTerminal = None
        self.production_type: type = None
        self.ERROR: Error = Error(self)
        self.EPSILON: Epsilon = Epsilon(self)
        self.EOF: EOF = EOF(self)

        self.symbol_dict = {'$': self.EOF, 'error': self.ERROR}
        self.production_dict = {}

    def add_terminal(self, name: str) -> Terminal:
        name = name.strip()
        if not name:
            raise Exception("Empty name")

        term = Terminal(name, self)
        self.terminals.append(term)
        self.symbol_dict[name] = term
        return term

    def add_terminals(self, names: str) -> Tuple[Terminal, ...]:
        return tuple(self.add_terminal(x) for x in names.strip().split())

    def add_non_terminal(self, name: str, startSymbol: bool = False) -> NonTerminal:
        name = name.strip()
        if not name:
            raise Exception("Empty name")

        term = NonTerminal(name, self)

        if startSymbol:

            if self.start_symbol is None:
                self.start_symbol = term
            else:
                raise Exception("Cannot define more than one start symbol.")

        self.non_terminals.append(term)
        self.symbol_dict[name] = term
        return term

    def add_non_terminals(self, names: str) -> Tuple[NonTerminal, ...]:
        return tuple((self.add_non_terminal(x) for x in names.strip().split()))

    def add_production(self, production: Production):
        if len(self.productions) == 0:
            self.production_type = type(production)

        assert type(production) == self.production_type, "The Productions most be of only 1 type."

        production.Left.productions.append(production)
        self.productions.append(production)
        self.production_dict[repr(production)] = production

    def error(self, head, sentence, rule):
        pass

    def __str__(self):

        mul = '%s, '

        ans = 'Non-Terminals:\n\t'

        nonterminals = mul * (len(self.non_terminals) - 1) + '%s\n'

        ans += nonterminals % tuple(self.non_terminals)

        ans += 'Terminals:\n\t'

        terminals = mul * (len(self.terminals) - 1) + '%s\n'

        ans += terminals % tuple(self.terminals)

        ans += 'Productions:\n\t'

        ans += str(self.productions)

        return ans

    def __getitem__(self, item):
        try:
            try:
                return self.symbol_dict[item]
            except KeyError:
                return self.production_dict[item]
        except KeyError:
            return None

    @property
    def to_json(self):

        productions = []

        for p in self.productions:
            head = p.Left.name

            body = []

            for s in p.Right:
                body.append(s.Name)

            productions.append({'Head': head, 'Body': body})

        d = {'NonTerminals': [symb.name for symb in self.non_terminals],
             'Terminals': [symb.name for symb in self.terminals],
             'Productions': productions}

        # [{'Head':p.Left.Name, "Body": [s.Name for s in p.Right]} for p in self.Productions]
        return json.dumps(d)

    @staticmethod
    def from_json(data):
        data = json.loads(data)

        G = Grammar()
        dic = {'epsilon': G.EPSILON}

        for term in data['Terminals']:
            dic[term] = G.add_terminal(term)

        for noTerm in data['NonTerminals']:
            dic[noTerm] = G.add_non_terminal(noTerm)

        for p in data['Productions']:
            head = p['Head']
            dic[head] %= Sentence(*[dic[term] for term in p['Body']])

        return G

    def copy(self):
        G = Grammar()
        G.productions = self.productions.copy()
        G.non_terminals = self.non_terminals.copy()
        G.terminals = self.terminals.copy()
        G.production_type = self.production_type
        G.start_symbol = self.start_symbol
        G.EPSILON = self.EPSILON
        G.EOF = self.EOF
        G.symbol_dict = self.symbol_dict.copy()

        return G

    @property
    def IsAugmentedGrammar(self):
        augmented = 0
        for left, _ in self.productions:
            if self.start_symbol == left:
                augmented += 1
        if augmented <= 1:
            return True
        else:
            return False

    def AugmentedGrammar(self, force=False):
        if not self.IsAugmentedGrammar or force:

            G = self.copy()
            # S, self.startSymbol, SS = self.startSymbol, None, self.NonTerminal('S\'', True)
            S = G.start_symbol
            G.start_symbol = None
            SS = G.add_non_terminal('S\'', True)
            if G.production_type is AttributeProduction:
                SS %= S + G.EPSILON, lambda x: x
            else:
                SS %= S + G.EPSILON

            return G
        else:
            return self.copy()


class Item:
    def __init__(self, production: Production, pos: int, lookaheads: Iterable[Symbol] = None):
        if lookaheads is None:
            lookaheads = []
        self.production: Production = production
        self.pos: int = pos
        self.lookaheads: FrozenSet[Symbol] = frozenset(look for look in lookaheads)

    def __str__(self):
        s = str(self.production.Left) + " -> "
        if len(self.production.Right) > 0:
            for i, _ in enumerate(self.production.Right):
                if i == self.pos:
                    s += "."
                s += str(self.production.Right[i])
            if self.pos == len(self.production.Right):
                s += "."
        else:
            s += "."
        s += ", " + str(self.lookaheads)[10:-1]
        return s

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return (
                (self.pos == other.pos) and
                (self.production == other.production) and
                (set(self.lookaheads) == set(other.lookaheads))
        )

    def __hash__(self):
        return hash((self.production, self.pos, self.lookaheads))

    @property
    def IsReduceItem(self) -> bool:
        return len(self.production.Right) == self.pos

    @property
    def NextSymbol(self) -> Optional[Symbol]:
        if self.pos < len(self.production.Right):
            return self.production.Right[self.pos]
        else:
            return None

    def NextItem(self) -> Optional['Item']:
        if self.pos < len(self.production.Right):
            return Item(self.production, self.pos + 1, self.lookaheads)
        else:
            return None

    def Preview(self, skip=1) -> List[Symbol]:
        unseen = self.production.Right[self.pos + skip:]
        return [unseen + (lookahead,) for lookahead in self.lookaheads]

    def Center(self) -> 'Item':
        return Item(self.production, self.pos)
