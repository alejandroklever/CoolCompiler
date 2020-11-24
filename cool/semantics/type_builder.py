from typing import List, Optional

import cool.semantics.utils.astnodes as ast
import cool.semantics.utils.errors as err
import cool.semantics.visitor as visitor
from cool.semantics.utils.scope import Context, SemanticError, Type, ErrorType


class TypeBuilder:
    """This visitor collect all the attributes and methods in classes and set the parent to the current class

    Params
    ------
    - syntactic_and_semantic_errors: List[str] is a list of syntactic_and_semantic_errors detected in the ast travel
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

        if node.parent is not None:
            if node.parent in ("Int", "String", "Bool", "SELF_TYPE"):
                self.errors.append(err.INVALID_PARENT_TYPE % (node.id, node.parent))

            try:
                self.current_type.set_parent(self.context.get_type(node.parent))
            except SemanticError as e:
                self.errors.append(e.text)
        else:
            self.current_type.set_parent(self.context.get_type('Object'))

        for feature in node.features:
            self.visit(feature)

    @visitor.when(ast.AttrDeclarationNode)
    def visit(self, node: ast.AttrDeclarationNode):
        try:
            self.current_type.define_attribute(node.id, self.context.get_type(node.type))
        except SemanticError as e:
            self.errors.append(e.text)
            self.current_type.define_attribute(node.id, ErrorType())

    @visitor.when(ast.MethodDeclarationNode)
    def visit(self, node: ast.MethodDeclarationNode):
        param_names = []
        param_types = []
        for name, typex in node.params:
            param_names.append(name)
            try:
                param_types.append(self.context.get_type(typex))
            except SemanticError as e:
                param_types.append(ErrorType())
                self.errors.append(e.text)

        try:
            return_type = self.context.get_type(node.return_type)
        except SemanticError as e:
            return_type = ErrorType()
            self.errors.append(e.text)

        self.current_type.define_method(node.id, param_names, param_types, return_type)
