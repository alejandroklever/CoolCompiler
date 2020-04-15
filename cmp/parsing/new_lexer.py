import re

from cmp.utils import Token


class Lexer:
    def __init__(self, table, eof):
        self.table = table
        self.pattern = self.__build_regex(self.table)
        self.eof = eof

    @staticmethod
    def __build_regex(table):
        r = '|'.join([f'(?P<{alias}>{regex})' for alias, (_, regex) in table.items()])
        return re.compile(r)

    def __tokenize(self, text):
        pos = 0
        while pos < len(text):
            if text[pos] in (' ', '\n', '\t'):
                pos += 1
            else:
                match = self.pattern.match(text, pos=pos)
                yield match.group(), match.lastgroup
                pos = match.end()
        yield '$', self.eof

    def __call__(self, text):
        return [Token(lex, self.table[alias][0]) for lex, alias in self.__tokenize(text)]


if __name__ == '__main__':
    def get_lexer(G):
        return Lexer({
            'add': (G['+'], '\+'),
            'sub': (G['-'], '-'),
            'mul': (G['*'], '\*'),
            'div': (G['/'], '/'),
            'le': (G['<='], '<='),
            'lt': (G['<'], '<'),
            'eq': (G['='], '='),
            'comp': (G['~'], '~'),
            'not': (G['not'], 'not'),
            'ocur': (G['{'], '{'),
            'ccur': (G['}'], '}'),
            'opar': (G['('], '\('),
            'cpar': (G[')'], '\)'),
            'coma': (G[','], ','),
            'dot': (G['.'], '.'),
            'arroba': (G['@'], '@'),
            'colon': (G[':'], ':'),
            'semicolon': (G[';'], ';'),
            'assign': (G['<-'], '<-'),
            'arrow': (G['=>'], '=>'),
            'class': (G['class'], 'class'),
            'inherits': (G['inherits'], 'inherits'),
            'if': (G['if'], 'if'),
            'then': (G['then'], 'then'),
            'else': (G['else'], 'else'),
            'fi': (G['fi'], 'fi'),
            'while': (G['while'], 'while'),
            'loop': (G['loop'], 'loop'),
            'pool': (G['pool'], 'pool'),
            'let': (G['let'], 'let'),
            'in': (G['in'], 'in'),
            'case': (G['case'], 'case'),
            'esac': (G['esac'], 'esac'),
            'of': (G['of'], 'of'),
            'new': (G['new'], 'new'),
            'isvoid': (G['isvoid'], 'isvoid'),
            'true': (G['true'], 'true'),
            'false': (G['false'], 'false'),
            'end': (G['end'], 'end'),
            'int': (G['integer'], '-?[1-9][0-9]*'),
            'type': (G['type'], '[A-Z][a-zA-Z0-9]*'),
            'id': (G['id'], '[a-z][a-zA-Z0-9]*'),
            'string': (G['string'], '"[ -~]*"'),
        }, G.EOF)
