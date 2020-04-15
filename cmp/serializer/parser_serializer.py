import inspect

from cmp.pycompiler import Epsilon

TEMPLATE = """from abc import ABC
from cmp.parsing import ShiftReduceParser
from cmp.pycompiler import AttributeProduction, Sentence
from astnodes import *


class %s(ShiftReduceParser, ABC):
    def __init__(self, G, verbose=False):
        self.G = G
        self.verbose = verbose
        self.action = self.__action_table()
        self.goto = self.__goto_table()

    def __action_table(self):
        G = self.G
        return %s

    def __goto_table(self):
        G = self.G
        return %s
"""


class LRParserSerializer:
    @staticmethod
    def build(**kwargs):
        parser = kwargs['parser']
        class_name = kwargs['class']
        file_name = kwargs['file']
        LRParserSerializer.__meta(parser, class_name, file_name)

    @staticmethod
    def __meta(parser, class_name, file_name):
        action, goto = LRParserSerializer.__build_parsing_tables(parser)
        content = TEMPLATE % (class_name, action, goto)
        try:
            with open(file_name, 'x') as f:
                f.write(content)
        except FileExistsError:
            with open(file_name, 'w') as f:
                f.write(content)

    @staticmethod
    def __build_parsing_tables(parser):
        parser = parser
        G = parser.G

        lambdas = {}
        for p in G.Productions:
            attr = p.attributes[0]
            code: str = 'lambda' + inspect.getsource(attr).replace('\n', '').split('lambda')[1]
            repr_p: str = repr(p)
            lambdas[repr_p] = code

        s1 = '{\n'
        for (state, symbol), (act, tag) in parser.action.items():
            s1 += f'            ({state}, G["{symbol}"]): '

            if act == 'SHIFT':
                s1 += f'("{act}", {tag}),\n'
            elif act == 'REDUCE':
                head, body = tag
                if isinstance(body, Epsilon):
                    s1 += f'("{act}", AttributeProduction(G["{head}"], G.Epsilon, [{lambdas[repr(tag)]}])),\n'
                else:
                    body = ', '.join(f'G["{s}"]' for s in body)
                    s1 += f'("{act}", AttributeProduction(G["{head}"], Sentence({body}), [{lambdas[repr(tag)]}])),\n'
            else:
                s1 += f'("{act}", None),\n'

        s1 += '        }'

        s2 = '{\n'
        for (state, symbol), dest in parser.goto.items():
            s2 += f'            ({state}, G["{symbol}"]): {dest},\n'
        s2 += '        }'

        return s1, s2

