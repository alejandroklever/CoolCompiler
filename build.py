from definitions import cool_parser, cool_lexer
from cmp.serializer import LexerSerializer, LRParserSerializer

PARSER_SETTINGS = {
    'parser': cool_parser(),
    'class': 'CoolParser',
    'file': 'parser.py',
}

LEXER_SETTINGS = {
    'lexer': cool_lexer(),
    'class': 'CoolLexer',
    'file': 'lexer.py',
}

if __name__ == '__main__':
    LRParserSerializer.build(**PARSER_SETTINGS)
    LexerSerializer.build(**LEXER_SETTINGS)
