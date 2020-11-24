import re

from pyjapt import Token, Lexer
from cool.grammar import G


class CoolLexer(Lexer):
    def __init__(self):
        self.lineno = 1
        self.column = 1
        self.position = 0
        self.token = Token('', '', 0, 0)
        self.pattern = re.compile(r'(?P<id>[a-z][a-zA-Z0-9_]*)|(?P<string>\")|(?P<single_line_comment>--.*)|(?P<multi_line_comment>\(\*)|(?P<newline>\n+)|(?P<whitespace> +)|(?P<tabulation>\t+)|(?P<type>[A-Z][a-zA-Z0-9_]*)|(?P<int>\d+)|(inherits)|(isvoid)|(class)|(while)|(false)|(then)|(else)|(loop)|(pool)|(case)|(esac)|(true)|(<\-)|(let)|(new)|(not)|(\{)|(\})|(\()|(\))|(\.)|(=>)|(if)|(fi)|(in)|(of)|(\+)|(\-)|(\*)|(<=)|(\~)|(,)|(:)|(;)|(@)|(/)|(<)|(=)')
        self.token_rules = {key: rule for key, (_, _, rule) in G.terminal_rules.items() if rule is not None}
        self.error_handler = G.lexical_error_handler if G.lexical_error_handler is not None else self.error 
        self._errors = []
        self.contain_errors = False
        self.eof = '$'
    
    def __call__(self, text):
        return [Token(t.lex, G[t.token_type], t.line, t.column) for t in self.tokenize(text)] 
