class Node:
    pass


class ProgramNode(Node):
    def __init__(self, declarations):
        self.declarations = declarations


class DeclarationNode(Node):
    pass


class ExprNode(Node):
    pass


class ClassDeclarationNode(DeclarationNode):
    def __init__(self, idx, features, parent=None):
        self.id = idx
        self.parent = parent
        self.features = features


class MethodDeclarationNode(DeclarationNode):
    def __init__(self, idx, params, return_type, body):
        self.id = idx
        self.params = params
        self.type = return_type
        self.body = body


class AttrDeclarationNode(DeclarationNode):
    def __init__(self, idx, typex, expr=None):
        self.id = idx
        self.type = typex
        self.expr = expr


class BlockNode(ExprNode):
    def __init__(self, expressions):
        self.expressions = expressions


class LetNode(ExprNode):
    def __init__(self, declarations, expr):
        self.expr = expr
        self.declarations = declarations


class SwitchCaseNode(ExprNode):
    def __init__(self, expr, cases):
        self.expr = expr
        self.cases = cases


class CaseNode(ExprNode):
    def __init__(self, idx, typex, expr):
        self.id = idx
        self.type = typex
        self.expr = expr


class VarDeclarationNode(ExprNode):
    def __init__(self, idx, typex, expr=None):
        self.id = idx
        self.type = typex
        self.expr = expr


class AssignNode(ExprNode):
    def __init__(self, idx, expr):
        self.id = idx
        self.expr = expr


class ConditionalNode(ExprNode):
    def __init__(self, ifx, then, elsex):
        self.if_expr = ifx
        self.then_expr = then
        self.else_expr = elsex


class WhileNode(ExprNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body


class MethodCallNode(ExprNode):
    def __init__(self, idx, args, obj=None, typex=None):
        self.obj = obj
        self.id = idx
        self.args = args
        self.type = typex


class AtomicNode(ExprNode):
    def __init__(self, lex):
        self.lex = lex


class UnaryNode(ExprNode):
    def __init__(self, obj):
        self.obj = obj


class BinaryNode(ExprNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right


class VariableNode(AtomicNode):
    pass


class InstantiateNode(AtomicNode):
    pass


class IntegerNode(AtomicNode):
    pass


class StringNode(AtomicNode):
    pass


class BooleanNode(AtomicNode):
    pass


class NegationNode(UnaryNode):
    pass


class ComplementNode(UnaryNode):
    pass


class IsVoidNode(UnaryNode):
    pass


class PlusNode(BinaryNode):
    pass


class MinusNode(BinaryNode):
    pass


class StarNode(BinaryNode):
    pass


class DivNode(BinaryNode):
    pass


class LessNode(BinaryNode):
    pass


class LessEqualNode(BinaryNode):
    pass


class EqualNode(BinaryNode):
    pass
