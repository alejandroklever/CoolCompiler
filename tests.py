import fire

from definitions import cool_grammar
from lexer import CoolLexer
from parser import CoolParser

G = cool_grammar()
lexer = CoolLexer(G)
parser = CoolParser(G)


class Tester:
    @staticmethod
    def tokenize(script, print_tokens=True):
        file = f'scripts/{script}'
        program = ''.join(open(file, 'r').read())

        tokens = [t for t in lexer(program) if t.token_type not in (G['space'], G['newline'], G['tab'])]

        if print_tokens:
            for t in tokens:
                print(t)

        return tokens

    @staticmethod
    def parse(script):
        tokens = Tester.tokenize(script, print_tokens=False)
        _, ast = parser(tokens, get_ast=True)
        print(ast)


if __name__ == '__main__':
    fire.Fire(Tester())
