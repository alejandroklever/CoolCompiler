from lexer import CoolLexer
from parser import CoolParser
from semantics import (TypeCollector, TypeBuilder, OverriddenMethodChecker, TypeChecker, topological_ordering)
from semantics.scope import Context, Scope

program = r"""
class Main inherits IO {
    main(): IO {
        out_string("Hello, World.\n")
    };

    fibonacci(n: Int): Int {
        if n <= 2 then 0 else fibonacci(n - 1) + fibonacci(n - 2) fi
    };
}
"""

lexer = CoolLexer()
parser = CoolParser()

if __name__ == '__main__':
    tokens = lexer(program)
    ast = parser(tokens)

    # for t in tokens:
    #     print(t)

    context = Context()
    errors = []
    scope = Scope()

    TypeCollector(context, errors).visit(ast)
    TypeBuilder(context, errors).visit(ast)
    topological_ordering(ast, context, errors)
    OverriddenMethodChecker(context, errors).visit(ast)
    TypeChecker(context, errors).visit(ast, scope)
    # Executor(context, errors).visit(ast, scope)

    for error in errors:
        print(error)
    print("Done!")
