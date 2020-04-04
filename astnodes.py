class Node:
    pass


class ProgramNode(Node):
    def __init__(self, class_list):
        self.class_list = class_list


class DeclarationNode(Node):
    pass


class ExpressionNode(Node):
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
    def __init__(self, idx, typex, expresion=None):
        self.id = idx
        self.type = typex
        self.expresion = expresion


class ParamNode(DeclarationNode):
    def __init__(self, idx, typex):
        self.id = idx
        self.type = typex


class BlockNode(ExpressionNode):
    def __init__(self, exprs):
        self.expressions = exprs


class LetNode(ExpressionNode):
    def __init__(self, declarations, expr):
        self.expr = expr
        self.declarations = declarations


class CasesNode(ExpressionNode):
    def __init__(self, expr, cases):
        self.expr = expr
        self.cases = cases


class SingleCaseNode(ExpressionNode):
    def __init__(self, idx, typex, expr):
        self.idx = idx
        self.typex = typex
        self.expr = expr


class VarDeclarationNode(ExpressionNode):
    def __init__(self, idx, typex, expr=None):
        self.id = idx
        self.type = typex
        self.expr = expr


class AssignNode(ExpressionNode):
    def __init__(self, idx, expr):
        self.id = idx
        self.expr = expr


class MethodCallNode(ExpressionNode):
    def __init__(self, idx, args, obj=None, typex=None):
        self.obj = obj
        self.id = idx
        self.args = args
        self.type = typex


class AtomicNode(ExpressionNode):
    def __init__(self, lex):
        self.lex = lex


class BinaryNode(ExpressionNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right


class ConditionalNode(ExpressionNode):
    def __init__(self, ifx, then, elsex):
        self.ifx = ifx
        self.then = then
        self.elsex = elsex


class ConstantNumNode(AtomicNode):
    pass


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


class NegationNode(AtomicNode):
    pass


class ComplementNode(AtomicNode):
    pass


class IsVoidNode(AtomicNode):
    pass


class WhileNode(BinaryNode):
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
