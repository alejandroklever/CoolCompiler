from cmp.pycompiler import Grammar, AttributeProduction, Sentence
from cmp.utils import Token
from cmp.parsing import ShiftReduceParser

from .ast import (ClosureNode, ConcatNode, EpsilonNode, PlusNode, QuestionNode,
                  RangeNode, SymbolNode, UnionNode)
from .automata import DFA


class Regex:
    def __init__(self, regex, skip_whitespaces=False):
        self.regex = regex
        self.automaton = self.build_automaton(regex, skip_whitespaces)

    def __call__(self, text):
        return self.automaton.recognize(text)

    @staticmethod
    def build_automaton(regex, skip_whitespaces=False):
        parser = RegexParser(verbose=False)
        tokens = regex_tokenizer(regex, parser.G, skip_whitespaces)
        _, ast = parser(tokens, get_ast=True)
        nfa = ast.evaluate()
        dfa = DFA.from_nfa(nfa)
        dfa = DFA.minimize(dfa)
        return dfa

    @staticmethod
    def Grammar():
        G = Grammar()

        E = G.NonTerminal('E', True)
        T, F, A, L = G.NonTerminals('T F A L')
        pipe, star, opar, cpar, symbol, epsilon, osquare, csquare, minus, plus, question = G.Terminals(
            '| * ( ) symbol ε [ ] - + ?')

        E %= E + pipe + T, lambda s: UnionNode(s[1], s[3])
        E %= T, lambda s: s[1]
        T %= T + F, lambda s: ConcatNode(s[1], s[2])
        T %= F, lambda s: s[1]
        F %= A + star, lambda s: ClosureNode(s[1])
        F %= A + plus, lambda s: PlusNode(s[1])
        F %= A + question, lambda s: QuestionNode(s[1])
        F %= A, lambda s: s[1]
        A %= symbol, lambda s: SymbolNode(s[1])
        A %= epsilon, lambda s: EpsilonNode(s[1])
        A %= opar + E + cpar, lambda s: s[2]
        A %= osquare + L + csquare, lambda s: s[2]
        L %= symbol, lambda s: SymbolNode(s[1])
        L %= symbol + minus + symbol, lambda s: RangeNode(SymbolNode(s[1]), SymbolNode(s[3]))
        L %= symbol + L, lambda s: UnionNode(SymbolNode(s[1]), s[2])
        L %= symbol + minus + symbol + L, lambda s: UnionNode(RangeNode(SymbolNode(s[1]), SymbolNode(s[3])), s[4])

        return G


# noinspection PyAbstractClass
class RegexParser(ShiftReduceParser):
    def __init__(self, verbose=False):
        G = Grammar()
        G.NonTerminal('E', True)
        G.NonTerminals('T F A L')
        G.Terminals('| * ( ) symbol ε [ ] - + ?')

        self.G = G
        self.verbose = verbose
        self.action = self.__action_table()
        self.goto = self.__goto_table()

    def __action_table(self):
        G = self.G
        return {
            (0, G["symbol"]): ("SHIFT", 2),
            (0, G["["]): ("SHIFT", 4),
            (0, G["ε"]): ("SHIFT", 3),
            (0, G["("]): ("SHIFT", 1),
            (1, G["["]): ("SHIFT", 4),
            (1, G["symbol"]): ("SHIFT", 2),
            (1, G["("]): ("SHIFT", 1),
            (1, G["ε"]): ("SHIFT", 3),
            (2, G["$"]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["symbol"]), [lambda s: SymbolNode(s[1])])),
            (2, G["+"]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["symbol"]), [lambda s: SymbolNode(s[1])])),
            (2, G[")"]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["symbol"]), [lambda s: SymbolNode(s[1])])),
            (2, G["|"]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["symbol"]), [lambda s: SymbolNode(s[1])])),
            (2, G["?"]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["symbol"]), [lambda s: SymbolNode(s[1])])),
            (2, G["symbol"]): (
                "REDUCE", AttributeProduction(G["A"], Sentence(G["symbol"]), [lambda s: SymbolNode(s[1])])),
            (2, G["ε"]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["symbol"]), [lambda s: SymbolNode(s[1])])),
            (2, G["("]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["symbol"]), [lambda s: SymbolNode(s[1])])),
            (2, G["["]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["symbol"]), [lambda s: SymbolNode(s[1])])),
            (2, G["*"]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["symbol"]), [lambda s: SymbolNode(s[1])])),
            (3, G["$"]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["ε"]), [lambda s: EpsilonNode(s[1])])),
            (3, G["+"]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["ε"]), [lambda s: EpsilonNode(s[1])])),
            (3, G[")"]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["ε"]), [lambda s: EpsilonNode(s[1])])),
            (3, G["|"]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["ε"]), [lambda s: EpsilonNode(s[1])])),
            (3, G["?"]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["ε"]), [lambda s: EpsilonNode(s[1])])),
            (3, G["symbol"]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["ε"]), [lambda s: EpsilonNode(s[1])])),
            (3, G["ε"]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["ε"]), [lambda s: EpsilonNode(s[1])])),
            (3, G["("]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["ε"]), [lambda s: EpsilonNode(s[1])])),
            (3, G["["]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["ε"]), [lambda s: EpsilonNode(s[1])])),
            (3, G["*"]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["ε"]), [lambda s: EpsilonNode(s[1])])),
            (4, G["symbol"]): ("SHIFT", 5),
            (5, G["symbol"]): ("SHIFT", 5),
            (5, G["-"]): ("SHIFT", 6),
            (5, G["]"]): ("REDUCE", AttributeProduction(G["L"], Sentence(G["symbol"]), [lambda s: SymbolNode(s[1])])),
            (6, G["symbol"]): ("SHIFT", 7),
            (7, G["symbol"]): ("SHIFT", 5),
            (7, G["]"]): ("REDUCE", AttributeProduction(G["L"], Sentence(G["symbol"], G["-"], G["symbol"]),
                                                        [lambda s: RangeNode(SymbolNode(s[1]), SymbolNode(s[3]))])),
            (8, G["]"]): ("REDUCE", AttributeProduction(G["L"], Sentence(G["symbol"], G["-"], G["symbol"], G["L"]), [
                lambda s: UnionNode(RangeNode(SymbolNode(s[1]), SymbolNode(s[3])), s[4])])),
            (9, G["]"]): ("REDUCE", AttributeProduction(G["L"], Sentence(G["symbol"], G["L"]),
                                                        [lambda s: UnionNode(SymbolNode(s[1]), s[2])])),
            (10, G["]"]): ("SHIFT", 11),
            (11, G["$"]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["["], G["L"], G["]"]), [lambda s: s[2]])),
            (11, G["+"]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["["], G["L"], G["]"]), [lambda s: s[2]])),
            (11, G[")"]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["["], G["L"], G["]"]), [lambda s: s[2]])),
            (11, G["|"]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["["], G["L"], G["]"]), [lambda s: s[2]])),
            (11, G["?"]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["["], G["L"], G["]"]), [lambda s: s[2]])),
            (11, G["symbol"]): (
                "REDUCE", AttributeProduction(G["A"], Sentence(G["["], G["L"], G["]"]), [lambda s: s[2]])),
            (11, G["ε"]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["["], G["L"], G["]"]), [lambda s: s[2]])),
            (11, G["("]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["["], G["L"], G["]"]), [lambda s: s[2]])),
            (11, G["["]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["["], G["L"], G["]"]), [lambda s: s[2]])),
            (11, G["*"]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["["], G["L"], G["]"]), [lambda s: s[2]])),
            (12, G["|"]): ("SHIFT", 13),
            (12, G[")"]): ("SHIFT", 21),
            (13, G["symbol"]): ("SHIFT", 2),
            (13, G["("]): ("SHIFT", 1),
            (13, G["["]): ("SHIFT", 4),
            (13, G["ε"]): ("SHIFT", 3),
            (14, G["$"]): (
                "REDUCE",
                AttributeProduction(G["E"], Sentence(G["E"], G["|"], G["T"]), [lambda s: UnionNode(s[1], s[3])])),
            (14, G[")"]): (
                "REDUCE",
                AttributeProduction(G["E"], Sentence(G["E"], G["|"], G["T"]), [lambda s: UnionNode(s[1], s[3])])),
            (14, G["|"]): (
                "REDUCE",
                AttributeProduction(G["E"], Sentence(G["E"], G["|"], G["T"]), [lambda s: UnionNode(s[1], s[3])])),
            (14, G["symbol"]): ("SHIFT", 2),
            (14, G["("]): ("SHIFT", 1),
            (14, G["["]): ("SHIFT", 4),
            (14, G["ε"]): ("SHIFT", 3),
            (15, G["$"]): (
                "REDUCE", AttributeProduction(G["T"], Sentence(G["T"], G["F"]), [lambda s: ConcatNode(s[1], s[2])])),
            (15, G["|"]): (
                "REDUCE", AttributeProduction(G["T"], Sentence(G["T"], G["F"]), [lambda s: ConcatNode(s[1], s[2])])),
            (15, G[")"]): (
                "REDUCE", AttributeProduction(G["T"], Sentence(G["T"], G["F"]), [lambda s: ConcatNode(s[1], s[2])])),
            (15, G["symbol"]): (
                "REDUCE", AttributeProduction(G["T"], Sentence(G["T"], G["F"]), [lambda s: ConcatNode(s[1], s[2])])),
            (15, G["["]): (
                "REDUCE", AttributeProduction(G["T"], Sentence(G["T"], G["F"]), [lambda s: ConcatNode(s[1], s[2])])),
            (15, G["("]): (
                "REDUCE", AttributeProduction(G["T"], Sentence(G["T"], G["F"]), [lambda s: ConcatNode(s[1], s[2])])),
            (15, G["ε"]): (
                "REDUCE", AttributeProduction(G["T"], Sentence(G["T"], G["F"]), [lambda s: ConcatNode(s[1], s[2])])),
            (16, G["+"]): ("SHIFT", 18),
            (16, G["$"]): ("REDUCE", AttributeProduction(G["F"], Sentence(G["A"]), [lambda s: s[1]])),
            (16, G["|"]): ("REDUCE", AttributeProduction(G["F"], Sentence(G["A"]), [lambda s: s[1]])),
            (16, G[")"]): ("REDUCE", AttributeProduction(G["F"], Sentence(G["A"]), [lambda s: s[1]])),
            (16, G["symbol"]): ("REDUCE", AttributeProduction(G["F"], Sentence(G["A"]), [lambda s: s[1]])),
            (16, G["["]): ("REDUCE", AttributeProduction(G["F"], Sentence(G["A"]), [lambda s: s[1]])),
            (16, G["("]): ("REDUCE", AttributeProduction(G["F"], Sentence(G["A"]), [lambda s: s[1]])),
            (16, G["ε"]): ("REDUCE", AttributeProduction(G["F"], Sentence(G["A"]), [lambda s: s[1]])),
            (16, G["?"]): ("SHIFT", 19),
            (16, G["*"]): ("SHIFT", 17),
            (17, G["$"]): (
                "REDUCE", AttributeProduction(G["F"], Sentence(G["A"], G["*"]), [lambda s: ClosureNode(s[1])])),
            (17, G["|"]): (
                "REDUCE", AttributeProduction(G["F"], Sentence(G["A"], G["*"]), [lambda s: ClosureNode(s[1])])),
            (17, G[")"]): (
                "REDUCE", AttributeProduction(G["F"], Sentence(G["A"], G["*"]), [lambda s: ClosureNode(s[1])])),
            (17, G["symbol"]): (
                "REDUCE", AttributeProduction(G["F"], Sentence(G["A"], G["*"]), [lambda s: ClosureNode(s[1])])),
            (17, G["["]): (
                "REDUCE", AttributeProduction(G["F"], Sentence(G["A"], G["*"]), [lambda s: ClosureNode(s[1])])),
            (17, G["("]): (
                "REDUCE", AttributeProduction(G["F"], Sentence(G["A"], G["*"]), [lambda s: ClosureNode(s[1])])),
            (17, G["ε"]): (
                "REDUCE", AttributeProduction(G["F"], Sentence(G["A"], G["*"]), [lambda s: ClosureNode(s[1])])),
            (18, G["$"]): ("REDUCE", AttributeProduction(G["F"], Sentence(G["A"], G["+"]), [lambda s: PlusNode(s[1])])),
            (18, G["|"]): ("REDUCE", AttributeProduction(G["F"], Sentence(G["A"], G["+"]), [lambda s: PlusNode(s[1])])),
            (18, G[")"]): ("REDUCE", AttributeProduction(G["F"], Sentence(G["A"], G["+"]), [lambda s: PlusNode(s[1])])),
            (18, G["symbol"]): (
                "REDUCE", AttributeProduction(G["F"], Sentence(G["A"], G["+"]), [lambda s: PlusNode(s[1])])),
            (18, G["["]): ("REDUCE", AttributeProduction(G["F"], Sentence(G["A"], G["+"]), [lambda s: PlusNode(s[1])])),
            (18, G["("]): ("REDUCE", AttributeProduction(G["F"], Sentence(G["A"], G["+"]), [lambda s: PlusNode(s[1])])),
            (18, G["ε"]): ("REDUCE", AttributeProduction(G["F"], Sentence(G["A"], G["+"]), [lambda s: PlusNode(s[1])])),
            (19, G["$"]): (
                "REDUCE", AttributeProduction(G["F"], Sentence(G["A"], G["?"]), [lambda s: QuestionNode(s[1])])),
            (19, G["|"]): (
                "REDUCE", AttributeProduction(G["F"], Sentence(G["A"], G["?"]), [lambda s: QuestionNode(s[1])])),
            (19, G[")"]): (
                "REDUCE", AttributeProduction(G["F"], Sentence(G["A"], G["?"]), [lambda s: QuestionNode(s[1])])),
            (19, G["symbol"]): (
                "REDUCE", AttributeProduction(G["F"], Sentence(G["A"], G["?"]), [lambda s: QuestionNode(s[1])])),
            (19, G["["]): (
                "REDUCE", AttributeProduction(G["F"], Sentence(G["A"], G["?"]), [lambda s: QuestionNode(s[1])])),
            (19, G["("]): (
                "REDUCE", AttributeProduction(G["F"], Sentence(G["A"], G["?"]), [lambda s: QuestionNode(s[1])])),
            (19, G["ε"]): (
                "REDUCE", AttributeProduction(G["F"], Sentence(G["A"], G["?"]), [lambda s: QuestionNode(s[1])])),
            (20, G["$"]): ("REDUCE", AttributeProduction(G["T"], Sentence(G["F"]), [lambda s: s[1]])),
            (20, G["|"]): ("REDUCE", AttributeProduction(G["T"], Sentence(G["F"]), [lambda s: s[1]])),
            (20, G[")"]): ("REDUCE", AttributeProduction(G["T"], Sentence(G["F"]), [lambda s: s[1]])),
            (20, G["symbol"]): ("REDUCE", AttributeProduction(G["T"], Sentence(G["F"]), [lambda s: s[1]])),
            (20, G["["]): ("REDUCE", AttributeProduction(G["T"], Sentence(G["F"]), [lambda s: s[1]])),
            (20, G["("]): ("REDUCE", AttributeProduction(G["T"], Sentence(G["F"]), [lambda s: s[1]])),
            (20, G["ε"]): ("REDUCE", AttributeProduction(G["T"], Sentence(G["F"]), [lambda s: s[1]])),
            (21, G["$"]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["("], G["E"], G[")"]), [lambda s: s[2]])),
            (21, G["+"]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["("], G["E"], G[")"]), [lambda s: s[2]])),
            (21, G[")"]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["("], G["E"], G[")"]), [lambda s: s[2]])),
            (21, G["|"]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["("], G["E"], G[")"]), [lambda s: s[2]])),
            (21, G["?"]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["("], G["E"], G[")"]), [lambda s: s[2]])),
            (21, G["symbol"]): (
                "REDUCE", AttributeProduction(G["A"], Sentence(G["("], G["E"], G[")"]), [lambda s: s[2]])),
            (21, G["ε"]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["("], G["E"], G[")"]), [lambda s: s[2]])),
            (21, G["("]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["("], G["E"], G[")"]), [lambda s: s[2]])),
            (21, G["["]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["("], G["E"], G[")"]), [lambda s: s[2]])),
            (21, G["*"]): ("REDUCE", AttributeProduction(G["A"], Sentence(G["("], G["E"], G[")"]), [lambda s: s[2]])),
            (22, G["symbol"]): ("SHIFT", 2),
            (22, G["("]): ("SHIFT", 1),
            (22, G["["]): ("SHIFT", 4),
            (22, G["$"]): ("REDUCE", AttributeProduction(G["E"], Sentence(G["T"]), [lambda s: s[1]])),
            (22, G[")"]): ("REDUCE", AttributeProduction(G["E"], Sentence(G["T"]), [lambda s: s[1]])),
            (22, G["|"]): ("REDUCE", AttributeProduction(G["E"], Sentence(G["T"]), [lambda s: s[1]])),
            (22, G["ε"]): ("SHIFT", 3),
            (23, G["|"]): ("SHIFT", 13),
            (23, G["$"]): ("OK", None),
        }

    def __goto_table(self):
        G = self.G
        return {
            (0, G["E"]): 23,
            (0, G["T"]): 22,
            (0, G["A"]): 16,
            (0, G["F"]): 20,
            (1, G["A"]): 16,
            (1, G["T"]): 22,
            (1, G["E"]): 12,
            (1, G["F"]): 20,
            (4, G["L"]): 10,
            (5, G["L"]): 9,
            (7, G["L"]): 8,
            (13, G["T"]): 14,
            (13, G["A"]): 16,
            (13, G["F"]): 20,
            (14, G["A"]): 16,
            (14, G["F"]): 15,
            (22, G["A"]): 16,
            (22, G["F"]): 15,
        }


def regex_tokenizer(text, G, skip_whitespaces=True):
    tokens = []
    fixed_tokens = {lex: Token(lex, G[lex]) for lex in '| * ( ) ε [ ] ? + -'.split()}
    open_pos = 0
    inside_squares = False
    set_literal = False
    for i, char in enumerate(text):
        if skip_whitespaces and char.isspace():
            continue

        if not set_literal and char == '\\':
            set_literal = True
            continue

        if set_literal:
            tokens.append(Token(char, G['symbol']))
            set_literal = False
            continue

        ################
        # Squares flow #
        ################
        if not inside_squares:
            if char in (']', '-') or char not in fixed_tokens:
                tokens.append(Token(char, G['symbol']))
            else:
                tokens.append(fixed_tokens[char])

            open_pos = i
            inside_squares = char == '['

        else:
            if char == ']':
                if i - open_pos == 1:
                    tokens.append(Token(char, G['symbol']))
                else:
                    inside_squares = False
                    tokens.append(fixed_tokens[char])
            elif char == '-':
                if is_minus_a_symbol(G, text, tokens, i, open_pos):
                    tokens.append(Token(char, G['symbol']))
                else:
                    tokens.append(fixed_tokens[char])
            else:
                tokens.append(Token(char, G['symbol']))

    if inside_squares:
        raise Exception(f'Unterminated character set at position {open_pos}')

    tokens.append(Token('$', G.EOF))
    return tokens


def is_minus_a_symbol(G, text, tokens, i, open_pos):
    return (i + 1 < len(text) and text[i + 1] == ']') or (text[i - 1] == '[') or \
           (i - 2 > open_pos and tokens[-2].token_type == G['-']) or \
           (i - 1 > open_pos and text[i - 1] == '-') or (i + 1 < len(text) and text[i + 1] == '-')
