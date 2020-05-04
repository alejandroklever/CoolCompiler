from typing import List, Optional

import semantics.astnodes as ast
import semantics.visitor as visitor
from semantics.scope import Context, Type, Method, ErrorType


class SelfTypeReplacement:
    """Check that `SELF_TYPE` is used correctly and replace every match with the correspondent class type.

        The principal method visit return a new AST with all the SELF_TYPE replaced by it's correspondent class name,
        all the definitions of SELF_TYPE in the Type definition where be overridden.
        Params
        ------
        - errors: List[str] is a list of errors detected in the ast travel
        - context: Context the context for keeping the classes
        - current_type: Optional[Type] is the current type in the building process"""

    def __init__(self, context: Context, errors: List[str]):
        self.context: Context = context
        self.errors: List[str] = errors
        self.current_type: Optional[Type] = None
        self.current_method: Optional[Method] = None

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(ast.ProgramNode)
    def visit(self, node: ast.ProgramNode):
        return ast.ProgramNode([self.visit(declaration) for declaration in node.declarations])

    @visitor.when(ast.ClassDeclarationNode)
    def visit(self, node: ast.ClassDeclarationNode):
        self.current_type = self.context.get_type(node.id)

        if node.parent is not None and node.parent == 'SELF_TYPE':
            self.errors.append(f'Invalid use of "SELF_TYPE" as parent of class "{node.id}"')

        features = [self.visit(feature) for feature in node.features]

        return ast.ClassDeclarationNode(node.id, features, node.parent)

    @visitor.when(ast.AttrDeclarationNode)
    def visit(self, node: ast.AttrDeclarationNode):
        typex = node.type
        if typex == 'SELF_TYPE':
            typex = self.current_type.name
            self.current_type.get_attribute(node.id).type = self.current_type

        expr = self.visit(node.expr) if node.expr is not None else None

        return ast.AttrDeclarationNode(node.id, typex, expr)

    @visitor.when(ast.MethodDeclarationNode)
    def visit(self, node: ast.MethodDeclarationNode):
        self.current_method = self.current_type.get_method(node.id)

        self.current_method.param_types[0] = self.current_type

        for i, (_, param_type) in enumerate(node.params, 1):
            if param_type == 'SELF_TYPE':
                self.errors.append('The static type of a param cannot be "SELF_TYPE"')
                self.current_method.param_types[i] = ErrorType()  # Change the static type to "ErrorType"

        if node.return_type == 'SELF_TYPE':
            self.current_method.return_type = self.current_type

        expr = self.visit(node.body)

        return ast.MethodDeclarationNode(node.id, node.params, self.current_method.return_type.name, expr)

    @visitor.when(ast.LetNode)
    def visit(self, node: ast.LetNode):
        return ast.LetNode([self.visit(declaration) for declaration in node.declarations], self.visit(node.expr))

    @visitor.when(ast.VarDeclarationNode)
    def visit(self, node: ast.VarDeclarationNode):
        typex = self.current_type.name if node.type == 'SELF_TYPE' else node.type
        expr = self.visit(node.expr) if node.expr is not None else None
        return ast.VarDeclarationNode(node.id, typex, expr)

    @visitor.when(ast.AssignNode)
    def visit(self, node: ast.AssignNode):
        return ast.AssignNode(node.id, self.visit(node.expr))

    @visitor.when(ast.BlockNode)
    def visit(self, node: ast.BlockNode):
        return ast.BlockNode([self.visit(expr) for expr in node.expressions])

    @visitor.when(ast.ConditionalNode)
    def visit(self, node: ast.ConditionalNode):
        return ast.ConditionalNode(self.visit(node.if_expr), self.visit(node.then_expr), self.visit(node.else_expr))

    @visitor.when(ast.WhileNode)
    def visit(self, node: ast.WhileNode):
        return ast.WhileNode(self.visit(node.condition), self.visit(node.body))

    @visitor.when(ast.SwitchCaseNode)
    def visit(self, node: ast.SwitchCaseNode):
        expr = self.visit(node.expr)
        cases = [self.visit(case) for case in node.cases]
        return ast.SwitchCaseNode(expr, cases)

    @visitor.when(ast.CaseNode)
    def visit(self, node: ast.CaseNode):
        if node.type == 'SELF_TYPE':
            self.errors.append('SELF_TYPE cannot be used as branch type in a case expression')
        return ast.CaseNode(node.id, node.type, self.visit(node.expr))

    @visitor.when(ast.MethodCallNode)
    def visit(self, node: ast.MethodCallNode):
        obj = self.visit(node.obj) if node.obj is not None else ast.VariableNode('self')
        args = [self.visit(arg) for arg in node.args]
        return ast.MethodCallNode(node.id, args, obj, node.type)

    @visitor.when(ast.IntegerNode)
    def visit(self, node: ast.IntegerNode):
        return node

    @visitor.when(ast.StringNode)
    def visit(self, node: ast.StringNode):
        return node

    @visitor.when(ast.BooleanNode)
    def visit(self, node: ast.BooleanNode):
        return node

    @visitor.when(ast.VariableNode)
    def visit(self, node: ast.VariableNode):
        return node

    @visitor.when(ast.InstantiateNode)
    def visit(self, node: ast.InstantiateNode):
        node.lex = node.lex if node.lex != 'SELF_TYPE' else self.current_type.name
        return node

    @visitor.when(ast.UnaryNode)
    def visit(self, node: ast.UnaryNode):
        return type(node)(self.visit(node.expr))

    @visitor.when(ast.BinaryNode)
    def visit(self, node: ast.BinaryNode):
        return type(node)(self.visit(node.left), self.visit(node.right))
