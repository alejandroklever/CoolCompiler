import re

PARSER_TEMPLATE = """from abc import ABC
from cmp.parsing import ShiftReduceParser
from %s import %s


class %s(ShiftReduceParser, ABC):
    def __init__(self, verbose=False):
        self.G = G
        self.verbose = verbose
        self.action = self.__action_table()
        self.goto = self.__goto_table()

    @staticmethod
    def __action_table():
        return %s

    @staticmethod
    def __goto_table():
        return %s
"""

LEXER_TEMPLATE = """import re

from cmp.lexing import Token, Lexer
from %s import %s


class %s(Lexer):
    def __init__(self):
        self.lineno = 1
        self.column = 1
        self.position = 0
        self.token = Token('', '', 0, 0)
        self.pattern = re.compile(r'%s')
        self.token_rules = %s
        self.error_handler = %s
        self.contain_errors = False
        self.eof = '%s'
    
    def __call__(self, text):
        return %s
"""


class LRParserSerializer:
    @staticmethod
    def build(parser, parser_class_name, grammar_module_name, grammar_variable_name):
        action, goto = LRParserSerializer._build_parsing_tables(parser, grammar_variable_name)
        content = PARSER_TEMPLATE % (grammar_module_name, grammar_variable_name, parser_class_name, action, goto)
        try:
            with open('parser.py', 'x') as f:
                f.write(content)
        except FileExistsError:
            with open('parser.py', 'w') as f:
                f.write(content)

    @staticmethod
    def _build_parsing_tables(parser, variable_name):
        s1 = '{\n'
        for (state, symbol), (act, tag) in parser.action.items():
            s1 += f'            ({state}, {variable_name}["{symbol}"]): '

            if act == 'SHIFT':
                s1 += f'("{act}", {tag}),\n'
            elif act == 'REDUCE':
                s1 += f'("{act}", {variable_name}["{repr(tag)}"]),\n'
            else:
                s1 += f'("{act}", None),\n'

        s1 += '        }'

        s2 = '{\n'
        for (state, symbol), dest in parser.goto.items():
            s2 += f'            ({state}, {variable_name}["{symbol}"]): {dest},\n'
        s2 += '        }'

        return s1, s2


class LexerSerializer:
    @staticmethod
    def build(grammar, lexer_class_name, grammar_module_name, grammar_variable_name):
        items = grammar.terminal_rules.items()
        values = grammar.terminal_rules.values()

        pattern = re.compile('|'.join(
            ['(?P<%s>%s)' % (name, regex) for name, (regex, _, rule) in items if rule is not None] +
            sorted(['(%s)' % regex for regex, literal, _ in values if literal], key=lambda x: len(x), reverse=True) +
            ['(?P<%s>%s)' % (name, regex) for name, (regex, literal, rule) in items if not literal and rule is None]
        )).pattern

        token_rules = f"{{key: rule for key, (_, _, rule) in {grammar_variable_name}.terminal_rules.items() if rule " \
            f"is not None}}"

        error_handler = f"{grammar_variable_name}.lexical_error_handler if "\
                        f"{grammar_variable_name}.lexical_error_handler is not None else self.error "

        call_return = f"[Token(t.lex, {grammar_variable_name}[t.token_type], t.line, t.column) for t in " \
            f"self.tokenize(text)] "

        content = LEXER_TEMPLATE % (
            grammar_module_name, grammar_variable_name, lexer_class_name, pattern, token_rules, error_handler,
            grammar.EOF.name, call_return,
        )

        try:
            with open('lexer.py', 'x') as f:
                f.write(content)
        except FileExistsError:
            with open('lexer.py', 'w') as f:
                f.write(content)
