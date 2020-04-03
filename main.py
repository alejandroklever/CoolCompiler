import time
from parser import CoolParser
from definitions import cool_grammar

if __name__ == '__main__':
    G = cool_grammar()
    t = time.time()
    parser = CoolParser(G)
    print(time.time() - t)
