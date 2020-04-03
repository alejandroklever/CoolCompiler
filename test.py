import os
import inspect
import ast as ast

from cmp.serializer import LexerSerializer, LRParserSerializer
from definitions import cool_parser, cool_lexer


def open_or_create(file):
    try:
        return open(file, 'x')
    except FileExistsError:
        return open(file, 'w')


class LexerInfo:
    def __init__(self, lexer, class_name, file_name):
        self.lexer = lexer
        self.class_name = class_name
        self.file_name = file_name


class ParserInfo:
    def __init__(self, parser, ast_module, class_name, file_name):
        self.parser = parser
        self.ast_module = ast_module
        self.class_name = class_name
        self.file_name = file_name


class Modularizer:
    def __init__(self, module_name, parser_info=None, lexer_info=None):
        self.module_name = module_name
        self.parser_info = parser_info
        self.lexer_info = lexer_info

    def build(self):
        os.makedirs(self.module_name, exist_ok=True)
        open_or_create(self.module_name + '/__init__.py')
        self.build_module()
        self.build_ast()

    def build_ast(self):
        f = open_or_create(self.module_name + '/ast.py')
        f.write(inspect.getsource(self.parser_info.ast_module))
        f.close()

    def build_module(self):
        LRParserSerializer.build(self.parser_info.parser, self.parser_info.class_name,
                                 self.module_name + '/' + self.parser_info.file_name)

        LexerSerializer.build(self.lexer_info.lexer, self.lexer_info.class_name,
                              self.module_name + '/' + self.lexer_info.file_name)


if __name__ == '__main__':
    Modularizer(
        module_name='coolx',
        parser_info=ParserInfo(cool_parser(), ast, 'CoolParser', 'parser.py'),
        lexer_info=LexerInfo(cool_lexer(), 'CoolLexer', 'lexer.py')
    ).build()
