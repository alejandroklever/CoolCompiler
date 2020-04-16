from .automatas import build_lr1_automaton, build_larl1_automaton
from .utils import compute_firsts, compute_follows


class ShiftReduceParser:
    SHIFT = 'SHIFT'
    REDUCE = 'REDUCE'
    OK = 'OK'

    def __init__(self, G):
        self.G = G
        self.augmented_G = G.AugmentedGrammar(True)
        self.firsts = compute_firsts(self.augmented_G)
        self.follows = compute_follows(self.augmented_G, self.firsts)
        self.automaton = self._build_automaton()
        self.state_dict = {}
        self.conflict = None

        self.action = {}
        self.goto = {}
        self._build_parsing_table()

        if self.conflict is None:
            self._clean_tables()

    def _build_parsing_table(self):
        G = self.augmented_G
        automaton = self.automaton

        for i, node in enumerate(automaton):
            node.idx = i
            self.state_dict[i] = node

        for node in automaton:
            idx = node.idx
            for item in node.state:
                if item.IsReduceItem:
                    if item.production.Left == G.startSymbol:
                        self._register(self.action, (idx, G.EOF), (self.OK, None))
                    else:
                        for lookahead in self._lookaheads(item):
                            self._register(self.action, (idx, lookahead), (self.REDUCE, item.production))
                else:
                    symbol = item.NextSymbol
                    idj = node.get(symbol.Name).idx
                    if symbol.IsTerminal:
                        self._register(self.action, (idx, symbol), (self.SHIFT, idj))
                    else:
                        self._register(self.goto, (idx, symbol), idj)

    def __call__(self, tokens):
        stack: list = [0]
        cursor = 0

        while True:
            state = stack[-1]
            lookahead = tokens[cursor]

            assert (state, lookahead.token_type) in self.action, f'Parsing Error in ' \
                f'{(state, lookahead.lex, lookahead.token_type)} '

            action, tag = self.action[state, lookahead.token_type]

            if action == self.SHIFT:
                stack += [lookahead, lookahead.lex, tag]
                cursor += 1
            elif action == self.REDUCE:
                head, body = tag

                try:
                    attribute = tag.attributes[0]  # It's an attributed grammar
                except AttributeError:
                    attribute = None  # it's not an attribute grammar

                syn = [None] * (len(body) + 1)
                for i, symbol in enumerate(reversed(body), 1):
                    state, node, token = stack.pop(), stack.pop(), stack.pop()
                    syn[-i] = node
                    assert symbol == token.token_type, 'Bad Reduce...'
                syn[0] = attribute(syn) if attribute is not None else None

                state = stack[-1]
                goto = self.goto[state, head]
                stack += [head, syn[0], goto]
            elif action == self.OK:
                return stack[2]
            else:
                raise Exception(f'Parsing error: invalid action {action}')

    def _register(self, table, key, value):
        # assert key not in table or table[key] == value, 'Shift-Reduce or Reduce-Reduce conflict!!!'
        try:
            n = len(table[key])
            table[key].add(value)
            if self.conflict is None and n != len(table[key]):
                if all(action == self.REDUCE for action, _ in list(table[key])[:2]):
                    cType = LRConflictType.ReduceReduce
                else:
                    cType = LRConflictType.ShiftReduce

                self.conflict = LRConflict(key[0], key[1], cType)
                self.conflict.value1 = list(table[key])[0]
                self.conflict.value2 = list(table[key])[1]

        except KeyError:
            table[key] = {value}

    def _clean_tables(self):
        for key in self.action:
            self.action[key] = self.action[key].pop()
        for key in self.goto:
            self.goto[key] = self.goto[key].pop()

    def _build_automaton(self):
        raise NotImplementedError()

    def _lookaheads(self, item):
        raise NotImplementedError()


class LR1Parser(ShiftReduceParser):
    def _build_automaton(self):
        return build_lr1_automaton(self.augmented_G, firsts=self.firsts)

    def _lookaheads(self, item):
        return item.lookaheads


class LALR1Parser(LR1Parser):
    def _build_automaton(self):
        return build_larl1_automaton(self.augmented_G, firsts=self.firsts)
