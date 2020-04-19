from enum import auto, Enum
from typing import List

from cmp.automata import State
from cmp.pycompiler import Item
from cmp.utils import ContainerSet
from cmp.parsing.lexing import Token


##############################
# Compute Firsts and Follows #
##############################
def compute_local_first(firsts, alpha):
    first_alpha = ContainerSet()

    try:
        alpha_is_epsilon = alpha.IsEpsilon
    except AttributeError:
        alpha_is_epsilon = False

    if alpha_is_epsilon:
        first_alpha.set_epsilon()
    else:
        for symbol in alpha:
            first_symbol = firsts[symbol]
            first_alpha.update(first_symbol)
            if not first_symbol.contains_epsilon:
                break
        else:
            first_alpha.set_epsilon()

    return first_alpha


def compute_firsts(G):
    firsts = {}
    change = True

    for terminal in G.terminals:
        firsts[terminal] = ContainerSet(terminal)

    for nonterminal in G.non_terminals:
        firsts[nonterminal] = ContainerSet()

    while change:
        change = False

        # P: X -> alpha
        for production in G.productions:
            X, alpha = production

            first_X = firsts[X]

            try:
                first_alpha = firsts[alpha]
            except KeyError:
                first_alpha = firsts[alpha] = ContainerSet()

            local_first = compute_local_first(firsts, alpha)

            change |= first_alpha.hard_update(local_first)
            change |= first_X.hard_update(local_first)

    return firsts


def compute_follows(G, firsts):
    follows = {}
    change = True

    local_firsts = {}

    # init Follow(Vn)
    for nonterminal in G.non_terminals:
        follows[nonterminal] = ContainerSet()
    follows[G.start_symbol] = ContainerSet(G.EOF)

    while change:
        change = False

        # P: X -> alpha
        for production in G.productions:
            X = production.Left
            alpha = production.Right

            follow_X = follows[X]

            for i, symbol_Y in enumerate(alpha):
                # X -> zeta Y beta
                if symbol_Y.IsNonTerminal:
                    follow_Y = follows[symbol_Y]
                    try:
                        first_beta = local_firsts[alpha, i]
                    except KeyError:
                        first_beta = local_firsts[alpha, i] = compute_local_first(firsts, alpha[i + 1:])
                    # First(beta) - { epsilon } subset of Follow(Y)
                    change |= follow_Y.update(first_beta)
                    # beta ->* epsilon or X -> zeta Y ? Follow(X) subset of Follow(Y)
                    if first_beta.contains_epsilon:
                        change |= follow_Y.update(follow_X)
    # Follow(Vn)
    return follows


########################
# LR1 & LALR1 AUTOMATA #
########################
def compress(items):
    centers = {}

    for item in items:
        center = item.Center()
        try:
            lookaheads = centers[center]
        except KeyError:
            centers[center] = lookaheads = set()
        lookaheads.update(item.lookaheads)

    return set(Item(x.production, x.pos, set(lookaheads)) for x, lookaheads in centers.items())


def expand(item, firsts):
    next_symbol = item.NextSymbol
    if next_symbol is None or not next_symbol.IsNonTerminal:
        return []

    lookaheads = ContainerSet()

    for preview in item.Preview():
        local_first = compute_local_first(firsts, preview)
        lookaheads.update(local_first)

    assert not lookaheads.contains_epsilon

    return [Item(p, 0, lookaheads) for p in next_symbol.productions]


def closure_lr1(items, firsts):
    closure = ContainerSet(*items)
    changed = True
    while changed:
        new_items = ContainerSet()
        for item in closure:
            new_items.extend(expand(item, firsts))
        changed = closure.update(new_items)
    return compress(closure)


def goto_lr1(items, symbol, firsts=None, just_kernel=False):
    assert just_kernel or firsts is not None, '`firsts` must be provided if `just_kernel=False`'
    items = frozenset(item.NextItem() for item in items if item.NextSymbol == symbol)
    return items if just_kernel else closure_lr1(items, firsts)


def build_lr1_automaton(G, firsts=None):
    assert len(G.startSymbol.productions) == 1, 'Grammar must be augmented'

    if not firsts:
        firsts = compute_firsts(G)
    firsts[G.EOF] = ContainerSet(G.EOF)

    start_production = G.startSymbol.productions[0]
    start_item = Item(start_production, 0, lookaheads=(G.EOF,))
    start = frozenset([start_item])

    closure = closure_lr1(start, firsts)
    automaton = State(frozenset(closure), True)

    pending = [start]
    visited = {start: automaton}

    symbols = G.terminals + G.non_terminals
    while pending:
        current = pending.pop()
        current_state = visited[current]

        current_closure = current_state.state
        for symbol in symbols:
            kernel = goto_lr1(current_closure, symbol, just_kernel=True)

            if kernel == frozenset():
                continue

            try:
                next_state = visited[kernel]
            except KeyError:
                goto = closure_lr1(kernel, firsts)
                visited[kernel] = next_state = State(frozenset(goto), True)
                pending.append(kernel)
            current_state.add_transition(symbol.Name, next_state)

    return automaton


def build_larl1_automaton(G, firsts=None):
    assert len(G.start_symbol.productions) == 1, 'Grammar must be augmented'

    if not firsts:
        firsts = compute_firsts(G)
    firsts[G.EOF] = ContainerSet(G.EOF)

    start_production = G.start_symbol.productions[0]
    start_item = Item(start_production, 0, lookaheads=ContainerSet(G.EOF))
    start = frozenset([start_item.Center()])

    closure = closure_lr1([start_item], firsts)
    automaton = State(frozenset(closure), True)

    pending = [start]
    visited = {start: automaton}

    symbols = G.terminals + G.non_terminals
    while pending:
        current = pending.pop()
        current_state = visited[current]

        current_closure = current_state.state
        for symbol in symbols:
            goto = goto_lr1(current_closure, symbol, just_kernel=True)
            closure = closure_lr1(goto, firsts)
            center = frozenset(item.Center() for item in goto)

            if center == frozenset():
                continue

            try:
                next_state = visited[center]

                centers = {item.Center(): item for item in next_state.state}
                centers = {item.Center(): (centers[item.Center()], item) for item in closure}

                updated_items = frozenset(
                    Item(c.production, c.pos, item_a.lookaheads | item_b.lookaheads) for c, (item_a, item_b) in
                    centers.items())
                if next_state.state != updated_items:
                    pending.append(center)
                next_state.state = updated_items
            except KeyError:
                visited[center] = next_state = State(frozenset(closure), True)
                pending.append(center)

            if current_state[symbol.name] is None:
                current_state.add_transition(symbol.name, next_state)
            else:
                assert current_state.get(symbol.name) is next_state, 'Bad build!!!'

    return automaton


#######################
# LR1 & LALR1 Parsers #
#######################
class LRConflictType(Enum):
    """
    Enum for mark the type of lr-family conflict parser
    """
    ReduceReduce = auto()
    ShiftReduce = auto()


class LRConflict:
    def __init__(self, state, symbol, ctype):
        self.state = state
        self.symbol = symbol
        self.cType = ctype

    def __iter__(self):
        yield self.state
        yield self.symbol


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
        self.conflicts = None

        self.action = {}
        self.goto = {}
        self._build_parsing_table()

        if self.conflicts is None:
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
                    if item.production.Left == G.start_symbol:
                        self._register(self.action, (idx, G.EOF), (self.OK, None))
                    else:
                        for lookahead in self._lookaheads(item):
                            self._register(self.action, (idx, lookahead), (self.REDUCE, item.production))
                else:
                    symbol = item.NextSymbol
                    idj = node.get(symbol.name).idx
                    if symbol.IsTerminal:
                        self._register(self.action, (idx, symbol), (self.SHIFT, idj))
                    else:
                        self._register(self.goto, (idx, symbol), idj)

    def __call__(self, tokens: List[Token]):
        stack: list = [0]  # The order in stack is [init state] + [symbol, rule, state, ...]
        cursor = 0

        while True:
            state = stack[-1]
            lookahead = tokens[cursor]

            assert (state, lookahead.token_type) in self.action, f'ParsingError: in ' \
                f'{(state, lookahead.lex, lookahead.token_type)} '

            action, tag = self.action[state, lookahead.token_type]

            if action == self.SHIFT:
                stack += [lookahead.token_type, lookahead.lex, tag]
                cursor += 1
            elif action == self.REDUCE:
                head, body = tag

                rules = [None] * (len(body) + 1)
                for i, s in enumerate(reversed(body), 1):
                    state, rules[-i], symbol = stack.pop(), stack.pop(), stack.pop()
                    assert s == symbol, f'ReduceError: in production "{repr(tag)}". Expected {s} instead of {s}'

                try:
                    rules[0] = tag.attribute(rules)  # It's an attributed grammar
                except AttributeError:
                    pass

                state = stack[-1]
                goto = self.goto[state, head]
                stack += [head, rules[0], goto]
            elif action == self.OK:
                return stack[2]
            else:
                raise Exception(f'Parsing error: invalid action {action}')

    def _register(self, table, key, value):
        # assert key not in table or table[key] == value, 'Shift-Reduce or Reduce-Reduce conflict!!!'
        try:
            n = len(table[key])
            table[key].add(value)
            if self.conflicts is None and n != len(table[key]):
                if all(action == self.REDUCE for action, _ in list(table[key])[:2]):
                    cType = LRConflictType.ReduceReduce
                else:
                    cType = LRConflictType.ShiftReduce

                self.conflicts = LRConflict(key[0], key[1], cType)
                self.conflicts.value1 = list(table[key])[0]
                self.conflicts.value2 = list(table[key])[1]

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
