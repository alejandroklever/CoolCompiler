from cmp.parsing import Lexer


class CoolLexer(Lexer):
    """
    Specialized lexer for COOL programing language.

    This derived from cmp.parsing.lexer.Lexer
    """
    def __init__(self, G):
        """
        Receive a Grammar to take it terminals as token types

        :param G: cmp.pycompiler.Grammar
        """
        self.G = G
        super().__init__(self.__table, G.EOF, self.__skip_characters)

    @property
    def __skip_characters(self):
        return {' ', '\n', '\t'}

    @property
    def __table(self):
        G = self.G
        return {
            'int': (G['integer'], '-?[1-9][0-9]*'),
            'add': (G['+'], '\+'),
            'sub': (G['-'], '-'),
            'mul': (G['*'], '\*'),
            'div': (G['/'], '/'),
            'le': (G['<='], '<='),
            'assign': (G['<-'], '<-'),
            'lt': (G['<'], '<'),
            'eq': (G['='], '='),
            'comp': (G['~'], '~'),
            'not': (G['not'], 'not'),
            'ocur': (G['{'], '{'),
            'ccur': (G['}'], '}'),
            'opar': (G['('], '\('),
            'cpar': (G[')'], '\)'),
            'coma': (G[','], ','),
            'dot': (G['.'], '\.'),
            'arroba': (G['@'], '@'),
            'colon': (G[':'], ':'),
            'semicolon': (G[';'], ';'),
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
            'type': (G['type'], '[A-Z][a-zA-Z0-9]*'),
            'id': (G['id'], '[a-z][a-zA-Z0-9]*'),
            'string': (G['string'], '".*"'),
        }
