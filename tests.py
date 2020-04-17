from typing import List

import fire

from cmp.utils import Token
from definitions import cool_grammar
from lexer import CoolLexer
from parser import CoolParser

G = cool_grammar()
lexer = CoolLexer(G)
parser = CoolParser(G)


class Tester:
    @staticmethod
    def tokenize(script: str) -> List[Token]:
        """
        Method for tokenize a cool program
        :param script: string with the name of the program
        """
        file = f'scripts/{script}'
        program = open(file, 'r').read()

        return [t for t in lexer(program)]

    @staticmethod
    def parse(script: str):
        """
        Method for parse a cool program and return an ast
        :param script: string with the name of the program
        """
        tokens = Tester.tokenize(script)
        ast = parser(tokens)
        print(ast)


if __name__ == '__main__':
    fire.Fire(Tester())
