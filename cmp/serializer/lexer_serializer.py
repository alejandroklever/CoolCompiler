LEXER_CONTENT = """from cmp.automata import State
from cmp.parsing import Lexer
from cmp.regex import NFA


class %s(Lexer):
    def __init__(self, G):
        self.G = G
        self.eof = G.EOF
        self.regexs = self._build_regexs(self.__table())
        self.automaton = self._build_automaton()

    def __table(self):
        G = self.G
        return %s

    def _build_regexs(self, table):
        regexs = []
        for n, (token_type, nfa) in enumerate(self.__table()):
            automaton, states = State.from_nfa(nfa, get_states=True)

            for state in states:
                if state.final:
                    state.tag = (n, token_type)

            regexs.append(automaton)

        return regexs
"""


class LexerSerializer:
    @staticmethod
    def build(**kwargs):
        lexer = kwargs['lexer']
        class_name = kwargs['class']
        file_name = kwargs['file']
        LexerSerializer.__meta(lexer, class_name, file_name)

    @staticmethod
    def __meta(table, class_name, file_name):
        table = LexerSerializer.__build_lexer_table(table)
        content = LEXER_CONTENT % (class_name, table)
        try:
            with open(file_name, 'x') as f:
                f.write(content)
        except FileExistsError:
            with open(file_name, 'w') as f:
                f.write(content)

    @staticmethod
    def __build_lexer_table(lexer):
        lexer = lexer
        formatting = '[\n'
        for regex in lexer.regexs:
            finals = []

            count = 0
            tag = None
            table = '{'
            for s in regex:
                symbols = s.transitions
                for symbol in symbols:
                    key_symbol = symbol

                    if symbol == "\"":
                        key_symbol = "\\\""

                    elif symbol == "\\":
                        key_symbol = "\\\\"

                    elif symbol == "\n":
                        key_symbol = "\\n"

                    elif symbol == "\t":
                        key_symbol = "\\t"

                    table += f'({s.state}, "{key_symbol}"): {[d.state for d in s.transitions[symbol]]}, '

                if s.final:
                    tag = s.tag[1]
                    finals.append(s.state)

                count += 1
            table += '}'
            formatting += f'            (G["{tag.Name}"], NFA({count}, {finals}, {table}, start={regex.state})),\n'
        formatting += '        ]'

        return formatting
