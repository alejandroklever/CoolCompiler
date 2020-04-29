from lexer import CoolLexer
from parser import CoolParser
from scope import Context
from semantic import TypeCollector, TypeBuilder, TypeChecker, InferenceTypeChecker, Executor
from Fixing_Self_Type import *

program = """
class Main {
    main ( msg : String ) : Object {
        let a: Int <- 25, b: Int <- 15 in {
            a <- a + 1;
        }
    };
    testing6(a: Int): IO {
        let count: Int <- 1, pow: Int <- 1 
        in {
            count <- 0;
            pow <- 1;
            while pow < a 
            loop 
                {
                    count <- count + 1;
                    pow <- pow * 2;
                } 
            pool;
            new IO.out_string("El logaritmo en base 2 de a es algo");
        }
    };
}
"""

lexer = CoolLexer()
parser = CoolParser()

if __name__ == '__main__':
    tokens = lexer(program)
    ast = parser(tokens)

    context = Context()
    errors = []

    TypeCollector(context, errors).visit(ast)
    TypeBuilder(context, errors).visit(ast)
    fix_self_type(context, errors)
    scope = TypeChecker(context, errors).visit(ast)
    InferenceTypeChecker(context, errors).visit(ast, scope)
    Executor(context, errors).visit(ast, scope)

    for error in errors:
        print(error)
    print("Done!")
