import cmp.visitor as visitor
from astnodes import ProgramNode
from cmp.semantic import Scope


class SemanticChecker:
    def __init__(self):
        pass

    @visitor.on('node')
    def visit(self, node, scope):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode, scope: Scope = None):
        pass
