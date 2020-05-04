from lexer import CoolLexer
from parser import CoolParser
from semantics.scope import Context
from semantics import (TypeCollector, TypeBuilder, OverriddenMethodChecker, SelfTypeReplacement, TypeChecker,
                       topological_ordering, Formatter)

program = r"""
class Main inherits IO {
    main(): IO {
        out_string("Hello, World.\n")
    };
    
    function(): SELF_TYPE { 0 };
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
    ast = topological_ordering(ast, context, errors)
    OverriddenMethodChecker(context, errors).visit(ast)
    ast = SelfTypeReplacement(context, errors).visit(ast)
    scope = TypeChecker(context, errors).visit(ast)
    print(Formatter().visit(ast))
    # InferenceTypeChecker(context, errors).visit(ast, scope)
    # Executor(context, errors).visit(ast, scope)

    for error in errors:
        print(error)
    print("Done!")
