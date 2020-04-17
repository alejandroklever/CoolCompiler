import re

from cmp.utils import Token


class Lexer:
    def __init__(self, table, eof, special_symbols):
        self.lineno = 0
        self.column = 0
        self.table = {**table, **{'$': (eof, '$')}}
        self.pattern = self._build_regex(table)
        self.eof = eof
        self.special_symbols = special_symbols

    @staticmethod
    def _build_regex(table):
        r = '|'.join([f'(?P<{alias}>{regex})' for alias, (_, regex) in table.items()])
        return re.compile(r)

    def _tokenize(self, text):
        pos = 0
        while pos < len(text):
            if text[pos] in self.special_symbols:
                self.special_symbols[text[pos]](self)
                pos += 1
            else:
                match = self.pattern.match(text, pos=pos)
                yield match.group(), match.lastgroup, self.lineno, self.column
                pos = match.end()
                self.column += len(match.group())
        yield '$', '$', self.lineno, self.column

    def __call__(self, text):
        return [Token(lex, self.table[alias][0], row, col) for lex, alias, row, col in self._tokenize(text)]

