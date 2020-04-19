import re


class Token:
    """
    A Token class.

    Parameters
    ----------
    lex: str
        Token's lexeme.
    token_type: Enum
        Token's type.
    """

    def __init__(self, lex, token_type, line=0, column=0):
        """
        :param lex: str
        :param token_type: Enum
        :param line: int
        :param column: int
        """
        self.lex = lex
        self.token_type = token_type
        self.line = line
        self.column = column

    def __str__(self):
        return f'{self.token_type}: {self.lex}'

    def __repr__(self):
        return str(self)

    @property
    def is_valid(self):
        return True


class UnknownToken(Token):
    """
    Special class to detect lexical errors. Is derived from cmp.utils.Token
    """

    def __init__(self, lex):
        super().__init__(self, lex, None)

    def transform_to(self, token_type):
        return Token(self.lex, token_type)

    @property
    def is_valid(self):
        return False


class Lexer:
    def __init__(self, table, eof, special_symbols):
        self.lineno = 0
        self.column = 0
        self.pos = 0
        self.table = {**table, **{'$': (eof, '$')}}
        self.pattern = self._build_regex(table)
        self.eof = eof
        self.special_symbols = special_symbols

    @staticmethod
    def _build_regex(table):
        r = '|'.join([f'(?P<{alias}>{regex})' for alias, (_, regex) in table.items()])
        return re.compile(r)

    def _tokenize(self, text):
        pos = self.pos
        while pos < len(text):
            if text[pos] in self.special_symbols:
                self.special_symbols[text[pos]](self)
                pos += 1
            else:
                match = self.pattern.match(text, pos=pos)

                if match is None:
                    # TODO: Handle bad parsing error
                    pass

                yield match.group(), match.lastgroup, self.lineno, self.column
                pos = match.end()
                self.column += len(match.group())
        yield '$', '$', self.lineno, self.column

    def __call__(self, text):
        return [Token(lex, self.table[alias][0], row, col) for lex, alias, row, col in self._tokenize(text)]
