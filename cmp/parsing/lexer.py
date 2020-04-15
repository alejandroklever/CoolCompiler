import re

from cmp.utils import Token


class Lexer:
    def __init__(self, table, eof, skip_chars=None):
        if skip_chars is None:
            skip_chars = set()
        self.skip_chars = skip_chars
        self.table = {**table, **{'$': (eof, '$')}}
        self.pattern = self.__build_regex(table)
        self.eof = eof

    @staticmethod
    def __build_regex(table):
        r = '|'.join([f'(?P<{alias}>{regex})' for alias, (_, regex) in table.items()])
        return re.compile(r)

    def __tokenize(self, text):
        row = 0
        col = 0
        pos = 0
        while pos < len(text):
            if text[pos] == ' ':
                pos += 1
                col += 1
            elif text[pos] == '\t':
                pos += 1
                col += 4
            elif text[pos] == '\n':
                pos += 1
                row += 1
                col = 0
            else:
                match = self.pattern.match(text, pos=pos)
                yield match.group(), match.lastgroup, row, col
                pos = match.end()
                col += len(match.group())
        yield '$', '$'

    def __call__(self, text):
        return [Token(lex, self.table[alias][0], row, col) for lex, alias, row, col in self.__tokenize(text)]
