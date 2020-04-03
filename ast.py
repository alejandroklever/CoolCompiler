class Node:
    pass


class ProgramNode(Node):
    def __init__(self, declarations):
        self.declarations = declarations


class DeclarationNode(Node):
    pass


class ExpressionNode(Node):
    pass


class ClassDeclarationNode(DeclarationNode):
    def __init__(self, idx, features, parent=None):
        self.id = idx
        self.parent = parent
        self.features = features


class FuncDeclarationNode(DeclarationNode):
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


class CallNode(ExpressionNode):
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


class TernaryNode(ExpressionNode):
    def __init__(self, left, center, right):
        self.left = left
        self.right = right
        self.center = center


class ConditionalNode(TernaryNode):
    pass


class ConstantNumNode(AtomicNode):
    pass


class VariableNode(AtomicNode):
    pass


class InstantiateNode(AtomicNode):
    pass


class StringNode(AtomicNode):
    pass


class TrueNode(AtomicNode):
    pass


class FalseNode(AtomicNode):
    pass


class NegationNode(AtomicNode):
    pass


class IntegerComplementNode(AtomicNode):
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
