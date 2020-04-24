import time
from typing import List

import fire

from cmp.parsing.lexing import Token
from lexer import CoolLexer
from parser import CoolParser
from semantic import Formatter

lexer = CoolLexer()
parser = CoolParser()

formatter = Formatter()


def pprint_tokens(text: str, tokens: List[Token]) -> str:
    formatting = ''

    cursor = 0
    while cursor < len(tokens) - 1:
        token = tokens[cursor]

        if text.startswith(token.lex):
            formatting += token.token_type.name
            text = text[len(token.lex):]
            cursor += 1
        else:
            formatting += text[0]
            text = text[1:]

    return formatting


class Tester:
    @staticmethod
    def tokenize(script: str) -> str:
        """
        Method for tokenize a cool program
        :param script: string with the name of the program
        """
        file = f'scripts/{script}'
        program = open(file, 'r').read()

        return pprint_tokens(program, lexer(program))

    @staticmethod
    def parse(script: str) -> str:
        """
        Method for parse a cool program and return an ast
        :param script: string with the name of the program
        """
        file = f'scripts/{script}'
        program = open(file, 'r').read()

        tokens = [t for t in lexer(program)]

        ast = parser(tokens)
        return str(ast)

    def timeit(self, command: str, *args):
        if hasattr(self, command):
            attr = getattr(self, command)
            t = time.time()
            out = attr(*args)
            t = time.time() - t
            print(out)
            return f'Time : {t}'


if __name__ == '__main__':
    fire.Fire(Tester())
