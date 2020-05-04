from typing import List

import semantics.astnodes as ast
import semantics.visitor as visitor
from semantics.scope import Context, SemanticError


class TypeCollector:
    """Visitor to collect the class in the program, and the basic classes as Object, Int, String, IO and Bool

    Params
    ----------
    - errors: List[str] is a list of errors detected in the ast travel
    - context: Context the context for keeping the classes"""

    def __init__(self, context: Context = Context(), errors: List[str] = []):
        self.errors: List[str] = errors
        self.context: Context = context

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(ast.ProgramNode)
    def visit(self, node):
        self.context.create_type('AUTO_TYPE')
        self_type = self.context.create_type('SELF_TYPE')
        object_type = self.context.create_type('Object')
        io_type = self.context.create_type('IO')
        string_type = self.context.create_type('String')
        int_type = self.context.create_type('Int')
        bool_type = self.context.create_type('Bool')

        io_type.set_parent(object_type)
        string_type.set_parent(object_type)
        int_type.set_parent(object_type)
        bool_type.set_parent(object_type)

        object_type.define_method('abort', ['self'], [self_type], object_type)
        object_type.define_method('get_type', ['self'], [self_type], string_type)
        object_type.define_method('copy', ['self'], [self_type], self_type)

        io_type.define_method('out_string', ['self', 'x'], [self_type, string_type], self_type)
        io_type.define_method('out_int', ['self', 'x'], [self_type, string_type], self_type)
        io_type.define_method('in_string', ['self'], [self_type], string_type)
        io_type.define_method('in_int', ['self'], [self_type], int_type)

        string_type.define_method('length', ['self'], [self_type], int_type)
        string_type.define_method('concat', ['self', 's'], [self_type, string_type], string_type)
        string_type.define_method('substr', ['self', 'i', 'l'], [self_type, int_type, int_type], string_type)

        for declaration in node.declarations:
            self.visit(declaration)

    @visitor.when(ast.ClassDeclarationNode)
    def visit(self, node):
        try:
            self.context.create_type(node.id)
        except SemanticError as e:
            self.errors.append(e.text)
