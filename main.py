import time

from lexer import CoolLexer
from parser import CoolParser
from definitions import cool_grammar

if __name__ == '__main__':
    t = time.time()
    G = cool_grammar()
    parser = CoolParser(G)
    lexer = CoolLexer(G)
    print(time.time() - t)
