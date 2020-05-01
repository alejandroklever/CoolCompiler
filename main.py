from lexer import CoolLexer
from parser import CoolParser
from scope import Context
from semantic import TypeCollector, TypeBuilder, TypeChecker, InferenceTypeChecker, Executor, topological_order

program = r"""
class Main inherits IO {
    main(): IO {
        out_string("Hello, World.\n")
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

    topological_order(ast, context)

    scope = TypeChecker(context, errors).visit(ast)

    InferenceTypeChecker(context, errors).visit(ast, scope)

    Executor(context, errors).visit(ast, scope)

    for error in errors:
        print(error)
    print("Done!")
