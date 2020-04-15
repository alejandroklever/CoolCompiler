from definitions import cool_parser
from cmp.parsing.serializer import LRParserSerializer

PARSER_SETTINGS = {
    'parser': cool_parser(),
    'class': 'CoolParser',
    'file': 'parser.py',
}

if __name__ == '__main__':
    LRParserSerializer.build(**PARSER_SETTINGS)
