from lexer import CoolLexer
from parser import CoolParser
from semantics import (TypeCollector, TypeBuilder, OverriddenMethodChecker, TypeChecker, topological_ordering)
from semantics.scope import Context, Scope

program = r"""
class Main inherits IO {
    main(): IO {
        out_string("Hello, World.\n")
    };

    fibonacci(n: AUTO_TYPE): Int {
        if n <= 2 then 0 else fibonacci(n - 1) + fibonacci(n - 2) fi
    };
}
"""

lexer = CoolLexer()
parser = CoolParser()

if __name__ == '__main__':
    # tokens = lexer(program)
    # ast = parser(tokens)
    #
    # context = Context()
    # errors = []
    # scope = Scope()
    #
    # TypeCollector(context, errors).visit(ast)
    # TypeBuilder(context, errors).visit(ast)
    # topological_ordering(ast, context, errors)
    # OverriddenMethodChecker(context, errors).visit(ast)
    # TypeChecker(context, errors).visit(ast, scope)
    # # Executor(context, errors).visit(ast, scope)
    #
    # for error in errors:
    #     print(error)
    # print("Done!")

    class MyClass:
        def __init__(self, name):
            self.name = name

        def __hash__(self):
            return id(self)

        def __str__(self):
            return self.name

        def __repr__(self):
            return self.name

    a = MyClass('Item0')
    b = MyClass('Item1')
    c = MyClass('Item2')
    d = MyClass('Item3')
    e = MyClass('Item4')

    objects = {(0, a), (1, b), (2, c), (3, d), (4, e)}

    print((4, e) in objects)
    e.name = 'NewItem'
    print((4, e) in objects)
    print(objects)
