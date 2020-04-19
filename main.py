from grammar import cool_grammar
from parser import CoolParser

if __name__ == '__main__':
    import time
    G = cool_grammar()

    t = time.time()
    CoolParser(G)
    print(time.time() - t)
