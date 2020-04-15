import cmp.visitor as visitor
from astnodes import ProgramNode


class SemanticChecker:
    def __init__(self):
        pass

    @visitor.on('node')
    def visit(self, node, scope):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode, scope=None):
        pass
