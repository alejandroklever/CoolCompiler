from typing import List, Dict, Optional

import semantics.astnodes as ast
import semantics.semantic_errors as err
import semantics.visitor as visitor
from semantics.scope import Context, Type, SemanticError


def topological_ordering(program_node: ast.ProgramNode,
                         context: Context,
                         errors: List[str]) -> ast.ProgramNode:
    """Set an order in the program node of de ast such that for all class A with parent B, class B is before A in the
    list, if in the process is detected a cycle an error is added to the `error` parameter

    :param program_node: Root of the first AST of the program

    :param context: Context With all collected and building types

    :param errors: The error list

    :return: a new AST where all declared class are in topological order"""

    types = context.types

    graph: Dict[str, List[str]] = {name: [] for name in types}

    for name, typex in types.items():
        if name in ('Object', 'SELF_TYPE', 'AUTO_TYPE'):
            continue
        graph[typex.parent.name].append(name)

    order = []
    visited = {name: False for name in graph}
    stack = ['Object']

    while stack:
        current_name = stack.pop()

        if visited[current_name]:
            errors.append(f'Cyclic class hierarchy in class {current_name}.')

        visited[current_name] = True
        stack += graph[current_name]
        order.append(current_name)

    declarations = {d.id: d for d in program_node.declarations}
    program_node.declarations = [declarations[name] for name in order if
                                 name not in ('Object', 'Int', 'IO', 'String', 'Bool')]

    return program_node


class OverriddenMethodChecker:
    """This visitor for validate the signature of the overridden methods

        Params
        ------
        - errors: List[str] is a list of errors detected in the ast travel
        - context: Context the context for keeping the classes
        - current_type: Optional[Type] is the current type in the building process"""

    def __init__(self, context: Context, errors: List[str]):
        self.context: Context = context
        self.current_type: Optional[Type] = None
        self.errors: List[str] = errors

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(ast.ProgramNode)
    def visit(self, node: ast.ProgramNode):
        for declaration in node.declarations:
            self.visit(declaration)

    @visitor.when(ast.ClassDeclarationNode)
    def visit(self, node: ast.ClassDeclarationNode):
        self.current_type = self.context.get_type(node.id)

        for feature in node.features:
            if isinstance(feature, ast.MethodDeclarationNode):
                self.visit(feature)

    @visitor.when(ast.AttrDeclarationNode)
    def visit(self, node: ast.AttrDeclarationNode):
        try:
            attribute, owner = self.current_type.parent.get_attribute(node.id)
            self.errors.append(err.ATTRIBUTE_OVERRIDE_ERROR % (attribute.name, owner.name))
        except SemanticError:
            pass

    @visitor.when(ast.MethodDeclarationNode)
    def visit(self, node: ast.MethodDeclarationNode):
        try:
            method, owner = self.current_type.parent.get_method(node.id, get_owner=True)

            if len(method.param_types) != len(node.params) + 1:
                self.errors.append(err.METHOD_OVERRIDE_ERROR % (method.name, owner.name))

            for parent_param_type, (_, current_param_type_name) in zip(method.param_types[1:], node.params):
                if parent_param_type != self.context.get_type(current_param_type_name):
                    self.errors.append(err.METHOD_OVERRIDE_ERROR % (method.name, owner.name))
                    break

            if method.return_type != self.context.get_type(node.return_type):
                self.errors.append(err.METHOD_OVERRIDE_ERROR % (method.name, owner.name))
        except SemanticError:
            pass
