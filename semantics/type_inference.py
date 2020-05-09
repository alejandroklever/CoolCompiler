from typing import Dict, List, Tuple

import semantics.astnodes as ast
import semantics.visitor as visitor
from semantics.scope import Type, Attribute, Method, Scope, Context


class DependencyNode:
    def update(self, typex):
        raise NotImplementedError()


class AtomNode(DependencyNode):
    def __init__(self, typex):
        self.type = typex

    def update(self, typex):
        pass


class VariableInfoNode(DependencyNode):
    def __init__(self, var_type, variable_info):
        self.type: Type = var_type
        self.variable_info: str = variable_info

    def update(self, typex):
        self.type = self.variable_info.type = typex


class AttributeNode(DependencyNode):
    def __init__(self, var_type, attribute):
        self.type: Type = var_type
        self.attribute: Attribute = attribute

    def update(self, typex):
        self.type = self.attribute.type = typex


class ParameterNode(DependencyNode):
    def __init__(self, param_type, method, index):
        self.type: Type = param_type
        self.method: Method = method
        self.index: int = index

    def update(self, typex):
        self.type = self.method.param_types[self.index] = typex


class ReturnTypeNode(DependencyNode):
    def __init__(self, typex, method):
        self.type: Type = typex
        self.method: Method = method

    def update(self, typex):
        self.type = self.method.return_type = typex


class DependencyGraph:
    def __init__(self):
        self.dependencies: Dict[DependencyNode, List[DependencyNode]] = {}

    def add_node(self, node: DependencyNode):
        if node not in self.dependencies:
            self.dependencies[node] = []

    def add_edge(self, node: DependencyNode, other: DependencyNode):
        try:
            self.dependencies[node].append(other)
        except KeyError:
            self.dependencies[node] = [other]

        if other not in self.dependencies:
            self.dependencies[other] = []

    def update_dependencies(self, node: DependencyNode, typex: Type):
        visited = set()
        stack = self.dependencies[node] + [node]
        while stack:
            current_node = stack.pop()

            if current_node in visited:
                continue

            current_node.update(typex)
            visited.add(current_node)
            stack += self.dependencies[current_node]


class InferenceChecker:
    def __init__(self, context, errors):
        self.context: Context = context
        self.errors: List[str] = errors
        self.current_type: Type = None
        self.current_method: Method = None

        self.variables = {}
        self.attributes = self.build_attributes_reference(context)
        self.methods = self.build_methods_reference(context)
        self.dependencies = DependencyGraph()

    @staticmethod
    def build_attributes_reference(context: Context) -> Dict[Tuple[str, str], AttributeNode]:
        attributes = {}

        for typex in context:
            for attr in typex.attributes:
                attributes[typex.name, attr.name] = AttributeNode(attr.type, attr)

        return attributes

    @staticmethod
    def build_methods_reference(context: Context) -> Dict[Tuple[str, str], Tuple[List[ParameterNode], ReturnTypeNode]]:
        methods = {}

        for typex in context:
            for method in typex.methods:
                methods[typex.name, method.name] = (
                    [ParameterNode(t, method, i) for i, t in enumerate(method.param_types)],
                    ReturnTypeNode(method.return_type, method))

        return methods

    @visitor.on('node')
    def visit(self, node, scope):
        pass

    @visitor.when(ast.ProgramNode)
    def visit(self, node: ast.ProgramNode, scope: Scope = None):
        if scope is None:
            scope = Scope()

        for item in node.declarations:
            self.visit(item, scope.create_child())

    @visitor.when(ast.ClassDeclarationNode)
    def visit(self, node: ast.ClassDeclarationNode, scope: Scope):
        self.current_type = self.context.get_type(node.id)

        for node in node.features:
            if isinstance(node, ast.AttrDeclarationNode):
                self.visit(node, scope)
            else:
                self.visit(node, scope.create_child())

    @visitor.when(ast.AttrDeclarationNode)
    def visit(self, node: ast.AttrDeclarationNode, scope: Scope):
        # Define attribute in the scope
        var_info = scope.define_variable(node.id, self.context.get_type(node.type))

        # Solve the expression of the attribute
        expr_node = self.visit(node.expr, scope) if node.expr is not None else None

        # Set and get the reference to the variable info node
        var_info_node = self.variables[var_info] = VariableInfoNode(self.context.get_type('AUTO_TYPE'), var_info)

        if node.type == 'AUTO_TYPE':
            # Get the reference to the attribute node
            attr_node = self.attributes[self.current_type.name, node.id]

            # If the expression node is not None then two edges are creates in the graph
            if expr_node is not None:
                self.dependencies.add_edge(expr_node, var_info_node)
                self.dependencies.add_edge(expr_node, attr_node)

            # Finally a cycle is of two nodes are created between var_info_node and attr_node
            self.dependencies.add_edge(var_info_node, attr_node)
            self.dependencies.add_edge(attr_node, var_info_node)

    @visitor.when(ast.MethodDeclarationNode)
    def visit(self, node: ast.MethodDeclarationNode, scope: Scope):
        self.current_method = self.current_type.get_method(node.id)

        self_var = scope.define_variable('self', self.current_type)
        self.variables[self_var] = VariableInfoNode(self.current_type, self_var)

        for param_name, param_type in zip(self.current_method.param_names, self.current_method.param_types):
            pass

        pass

    @visitor.when(ast.LetNode)
    def visit(self, node: ast.LetNode, scope: Scope):
        pass

    @visitor.when(ast.VarDeclarationNode)
    def visit(self, node: ast.VarDeclarationNode, scope: Scope):
        pass

    @visitor.when(ast.AssignNode)
    def visit(self, node: ast.AssignNode, scope: Scope):
        pass

    @visitor.when(ast.BlockNode)
    def visit(self, node: ast.BlockNode, scope: Scope):
        pass

    @visitor.when(ast.ConditionalNode)
    def visit(self, node: ast.ConditionalNode, scope: Scope):
        pass

    @visitor.when(ast.WhileNode)
    def visit(self, node: ast.WhileNode, scope: Scope):
        pass

    @visitor.when(ast.SwitchCaseNode)
    def visit(self, node: ast.SwitchCaseNode, scope: Scope):
        pass

    @visitor.when(ast.CaseNode)
    def visit(self, node: ast.CaseNode, scope: Scope):
        pass

    @visitor.when(ast.MethodCallNode)
    def visit(self, node: ast.MethodCallNode, scope: Scope):
        pass

    @visitor.when(ast.IntegerNode)
    def visit(self, node: ast.IntegerNode, scope: Scope):
        pass

    @visitor.when(ast.StringNode)
    def visit(self, node: ast.StringNode, scope: Scope):
        pass

    @visitor.when(ast.BooleanNode)
    def visit(self, node: ast.BooleanNode, scope: Scope):
        pass

    @visitor.when(ast.VariableNode)
    def visit(self, node: ast.VariableNode, scope: Scope):
        pass

    @visitor.when(ast.InstantiateNode)
    def visit(self, node: ast.InstantiateNode, scope: Scope):
        pass

    @visitor.when(ast.NegationNode)
    def visit(self, node: ast.NegationNode, scope: Scope):
        pass

    @visitor.when(ast.ComplementNode)
    def visit(self, node: ast.ComplementNode, scope: Scope):
        pass

    @visitor.when(ast.IsVoidNode)
    def visit(self, node: ast.IsVoidNode, scope: Scope):
        pass

    @visitor.when(ast.PlusNode)
    def visit(self, node: ast.PlusNode, scope: Scope):
        pass

    @visitor.when(ast.MinusNode)
    def visit(self, node: ast.MinusNode, scope: Scope):
        pass

    @visitor.when(ast.StarNode)
    def visit(self, node: ast.StarNode, scope: Scope):
        pass

    @visitor.when(ast.DivNode)
    def visit(self, node: ast.DivNode, scope: Scope):
        pass

    @visitor.when(ast.LessEqualNode)
    def visit(self, node: ast.LessEqualNode, scope: Scope):
        pass

    @visitor.when(ast.LessThanNode)
    def visit(self, node: ast.LessThanNode, scope: Scope):
        pass

    @visitor.when(ast.EqualNode)
    def visit(self, node: ast.EqualNode, scope: Scope):
        pass
