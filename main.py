import time

from lexer import CoolLexer
from parser import CoolParser


if __name__ == '__main__':
    t = time.time()
    CoolLexer()
    CoolParser()
    print('Create  :', time.time() - t)
