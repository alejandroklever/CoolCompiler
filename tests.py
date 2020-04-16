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
    def tokenize(script: str, print_tokens: bool = True) -> List[Token]:
        """
        Method for tokenize a cool program
        :param script: string with the name of the program
        :param print_tokens: if true tokens will be printing with the program format
        """
        file = f'scripts/{script}'
        program = ''.join(open(file, 'r').read())

        tokens = [t for t in lexer(program) if t.token_type not in (G['space'], G['newline'], G['tab'])]

        if print_tokens:
            for t in tokens:
                print(t)

        return tokens

    @staticmethod
    def parse(script: str):
        """
        Method for parse a cool program and return an ast
        :param script: string with the name of the program
        """
        tokens = Tester.tokenize(script, print_tokens=False)
        ast = parser(tokens)
        print(ast)


if __name__ == '__main__':
    fire.Fire(Tester())
