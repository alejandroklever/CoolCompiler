from typing import Tuple, List, Any

from cmp.automata import State
from cmp.regex import Regex
from cmp.utils import Token


class Lexer:
    def __init__(self, table, eof):
        self.eof = eof
        self.regexs = self._build_regexs(table)
        self.automaton = self._build_automaton()

    def _build_regexs(self, table: List[Tuple[Any, str]]) -> List[State]:
        regexs = []
        for n, (token_type, regex) in enumerate(table):
            automaton = Regex.build_automaton(regex)
            automaton, states = State.from_nfa(automaton, get_states=True)

            for state in states:
                if state.final:
                    state.tag: Tuple[int, Any] = (n, token_type)

            regexs.append(automaton)

        return regexs

    def _build_automaton(self) -> State:
        start: State = State('start')
        regexs = self.regexs

        for regex in regexs:
            start.add_epsilon_transition(regex)

        return start.to_deterministic()

    def _walk(self, string: str):
        state = self.automaton
        final = state if state.final else None
        final_lex = lex = ''

        for symbol in string:
            try:
                state = state[symbol][0]
                lex += symbol
                final, final_lex = (state, lex) if state.final else (final, final_lex)
            except TypeError:
                break

        return final, final_lex

    def _tokenize(self, text: str):
        while text != '':
            state, lex = self._walk(text)

            if state is not None:
                text = text[len(lex):]
                token_type = min((s for s in state.state if s.final), key=lambda x: x.tag).tag[1]
                yield lex, token_type

            else:
                return None

        yield '$', self.eof

    def __call__(self, text: str):
        return [Token(lex, token_type) for lex, token_type in self._tokenize(text)]
