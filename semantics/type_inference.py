from collections import deque
from typing import Dict, List, Tuple, Set

import semantics.astnodes as ast
import semantics.errors as err
import semantics.visitor as visitor
from semantics.scope import Type, Attribute, Method, Scope, Context, SemanticError, ErrorType, VariableInfo


class DependencyNode:
    def update(self, typex):
        raise NotImplementedError()

    def __repr__(self):
        return str(self)


class AtomNode(DependencyNode):
    def __init__(self, typex):
        self.type = typex

    def update(self, typex):
        pass

    def __str__(self):
        return f'Atom({self.type.name})'


class VariableInfoNode(DependencyNode):
    def __init__(self, var_type, variable_info):
        self.type: Type = var_type
        self.variable_info: VariableInfo = variable_info

    def update(self, typex):
        self.type = self.variable_info.type = typex

    def __str__(self):
        return f'VarInfo({self.variable_info.name}, {self.type.name})'


class AttributeNode(DependencyNode):
    def __init__(self, var_type, attribute):
        self.type: Type = var_type
        self.attribute: Attribute = attribute

    def update(self, typex):
        self.type = self.attribute.type = typex

    def __str__(self):
        return f'Attr({self.attribute.name}, {self.type.name})'


class ParameterNode(DependencyNode):
    def __init__(self, param_type, method, index):
        self.type: Type = param_type
        self.method: Method = method
        self.index: int = index

    def update(self, typex):
        self.type = self.method.param_types[self.index] = typex

    def __str__(self):
        return f'Param({self.method.name}, {self.index}, {self.type.name})'


class ReturnTypeNode(DependencyNode):
    def __init__(self, typex, method):
        self.type: Type = typex
        self.method: Method = method

    def update(self, typex):
        self.type = self.method.return_type = typex

    def __str__(self):
        return f'Return({self.method.name}, {self.type.name})'


class DependencyGraph:
    def __init__(self):
        self.dependencies: Dict[DependencyNode, List[DependencyNode]] = {}
        self.nodes: List[DependencyNode] = []

    def add_node(self, node: DependencyNode):
        if node not in self.dependencies:
            self.dependencies[node] = []
            self.nodes.append(node)

    def add_edge(self, node: DependencyNode, other: DependencyNode):
        try:
            self.dependencies[node].append(other)
        except KeyError:
            self.dependencies[node] = [other]
        self.nodes.append(node)
        self.add_node(other)

    def update_dependencies(self):
        queue = deque(key for key in self.nodes if isinstance(key, AtomNode))
        visited = set()

        while queue:
            current_node = queue.popleft()
            if current_node in visited:
                continue
            self.update_dependencies_of(current_node, current_node.type, visited)

    def update_dependencies_of(self, node: DependencyNode, typex: Type, visited: Set[DependencyNode]):
        queue = deque([node] + self.dependencies[node])
        while queue:
            current_node = queue.popleft()

            if current_node in visited:
                continue

            current_node.update(typex)
            visited.add(current_node)
            queue.extend(self.dependencies[current_node])

    def __str__(self):
        return '\n'.join(f'{key}: {value}' for key, value in self.dependencies.items())


class InferenceChecker:
    def __init__(self, context, errors):
        self.context: Context = context
        self.errors: List[str] = errors
        self.current_type: Type = None
        self.current_method: Method = None

        self.variables = {}
        self.attributes = self.build_attributes_reference(context)
        self.methods = self.build_methods_reference(context)
        self.graph = DependencyGraph()

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

        # print(self.graph)
        self.graph.update_dependencies()
        InferenceTypeSubstitute(self.context, self.errors).visit(node, scope)

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
                self.graph.add_edge(expr_node, var_info_node)
                self.graph.add_edge(expr_node, attr_node)

            # Finally a cycle of two nodes is created between var_info_node and attr_node
            self.graph.add_edge(var_info_node, attr_node)
            self.graph.add_edge(attr_node, var_info_node)

    @visitor.when(ast.MethodDeclarationNode)
    def visit(self, node: ast.MethodDeclarationNode, scope: Scope):
        self.current_method = self.current_type.get_method(node.id)

        # Define 'self' as a variable in the scope
        self_var = scope.define_variable('self', self.current_type)

        # Set the reference of 'self' variable info node
        self.variables[self_var] = VariableInfoNode(self.current_type, self_var)

        param_names = self.current_method.param_names
        param_types = self.current_method.param_types

        for i, (param_name, param_type) in enumerate(zip(param_names, param_types)):
            # Define parameter as local variable in current scope
            param_var_info = scope.define_variable(param_name, param_type)

            # Set the reference to the variable info node
            param_var_info_node = self.variables[param_var_info] = VariableInfoNode(param_type, param_var_info)

            if param_type.name == 'AUTO_TYPE':
                # Get the parameter node
                parameter_node = self.methods[self.current_type.name, self.current_method.name][0][i]

                # Create the cycle of two nodes between param_var_info_node and parameter_node
                self.graph.add_edge(param_var_info_node, parameter_node)
                self.graph.add_edge(parameter_node, param_var_info_node)

        # Solve the body of the method
        body_node = self.visit(node.body, scope)

        if self.current_method.return_type.name == 'AUTO_TYPE':
            # Get the return type node and add an edge body_node -> return_type_node
            return_type_node = self.methods[self.current_type.name, self.current_method.name][1]
            self.graph.add_edge(body_node, return_type_node)

    @visitor.when(ast.LetNode)
    def visit(self, node: ast.LetNode, scope: Scope):
        for item in node.declarations:
            self.visit(item, scope)

        return self.visit(node.expr, scope.create_child())

    @visitor.when(ast.VarDeclarationNode)
    def visit(self, node: ast.VarDeclarationNode, scope: Scope):
        try:
            var_info = scope.define_variable(node.id, self.context.get_type(node.type))
        except SemanticError:
            var_info = scope.define_variable(node.id, ErrorType())
        var_info_node = self.variables[var_info] = VariableInfoNode(var_info.name, var_info)

        expr_node = self.visit(node.expr, scope.create_child()) if node.expr is not None else None

        if var_info.type.name == 'AUTO_TYPE':
            self.graph.add_edge(expr_node, var_info_node)

    @visitor.when(ast.AssignNode)
    def visit(self, node: ast.AssignNode, scope: Scope):
        var_info = scope.find_variable(node.id)

        expr_node = self.visit(node.expr, scope.create_child())

        if var_info is not None:
            self.graph.add_edge(expr_node, self.variables[var_info])
        else:
            # Maybe some error
            pass

        return expr_node

    @visitor.when(ast.BlockNode)
    def visit(self, node: ast.BlockNode, scope: Scope):
        result_node = None
        for expr in node.expressions:
            result_node = self.visit(expr, scope)
        return result_node

    @visitor.when(ast.ConditionalNode)
    def visit(self, node: ast.ConditionalNode, scope: Scope):
        if_node = self.visit(node.if_expr, scope)

        if not isinstance(if_node, AtomNode):
            self.graph.add_edge(AtomNode(self.context.get_type('Bool')), if_node)

        then_node = self.visit(node.then_expr, scope)
        else_node = self.visit(node.else_expr, scope)

        if isinstance(then_node, AtomNode) and isinstance(else_node, AtomNode):
            return AtomNode(then_node.type.join(else_node.type))

        return AtomNode(self.context.get_type('Object'))  # For now

    @visitor.when(ast.WhileNode)
    def visit(self, node: ast.WhileNode, scope: Scope):
        self.visit(node.condition, scope)
        self.visit(node.body, scope.create_child())
        return AtomNode(self.context.get_type('Object'))

    @visitor.when(ast.SwitchCaseNode)
    def visit(self, node: ast.SwitchCaseNode, scope: Scope):
        self.visit(node.expr, scope)
        for case in node.cases:
            self.visit(case, scope.create_child())
        return AtomNode(self.context.get_type('Object'))  # For now

    @visitor.when(ast.CaseNode)
    def visit(self, node: ast.CaseNode, scope: Scope):
        var_info = scope.define_variable(node.id, self.context.get_type(node.type))
        self.variables[var_info] = VariableInfoNode(var_info.type, var_info)
        return self.visit(node.expr, scope)

    @visitor.when(ast.MethodCallNode)
    def visit(self, node: ast.MethodCallNode, scope: Scope):
        if node.obj is None:
            node.obj = ast.VariableNode('self')
        obj_node = self.visit(node.obj, scope)

        if isinstance(obj_node, AtomNode):
            method = obj_node.type.get_method(node.id)
            param_nodes, return_node = self.methods[obj_node.type.name, method.name]
            for i, arg in enumerate(node.args):
                arg_node = self.visit(arg, scope)
                if isinstance(arg_node, AtomNode):
                    if param_nodes[i].type.name == 'AUTO_TYPE':
                        self.graph.add_edge(arg_node, param_nodes[i])
                    else:
                        continue
                else:
                    if param_nodes[i].type.name != 'AUTO_TYPE':
                        self.graph.add_edge(param_nodes[i], arg_node)
                    else:
                        self.graph.add_edge(param_nodes[i], arg_node)
                        self.graph.add_edge(arg_node, param_nodes[i])
            return return_node if return_node.type.name == 'AUTO_TYPE' else AtomNode(return_node.type)

        for arg in node.args:
            self.visit(arg, scope)
        return AtomNode(self.context.get_type('Object'))

    @visitor.when(ast.IntegerNode)
    def visit(self, node: ast.IntegerNode, scope: Scope):
        return AtomNode(self.context.get_type('Int'))

    @visitor.when(ast.StringNode)
    def visit(self, node: ast.StringNode, scope: Scope):
        return AtomNode(self.context.get_type('String'))

    @visitor.when(ast.BooleanNode)
    def visit(self, node: ast.BooleanNode, scope: Scope):
        return AtomNode(self.context.get_type('Bool'))

    @visitor.when(ast.VariableNode)
    def visit(self, node: ast.VariableNode, scope: Scope):
        var_info = scope.find_variable(node.lex)

        if var_info is not None:
            if var_info.type.name == 'AUTO_TYPE':
                return self.variables[var_info]
            else:
                return AtomNode(var_info.type)
        else:
            pass

    @visitor.when(ast.InstantiateNode)
    def visit(self, node: ast.InstantiateNode, scope: Scope):
        return AtomNode(self.context.get_type(node.lex))

    @visitor.when(ast.NegationNode)
    def visit(self, node: ast.NegationNode, scope: Scope):
        self.visit(node.expr, scope)
        return AtomNode(self.context.get_type('Bool'))

    @visitor.when(ast.ComplementNode)
    def visit(self, node: ast.ComplementNode, scope: Scope):
        self.visit(node.expr, scope)
        return AtomNode(self.context.get_type('Int'))

    @visitor.when(ast.IsVoidNode)
    def visit(self, node: ast.IsVoidNode, scope: Scope):
        self.visit(node.expr, scope)
        return AtomNode(self.context.get_type('Bool'))

    @visitor.when(ast.PlusNode)
    def visit(self, node: ast.PlusNode, scope: Scope):
        return self._visit_arithmetic_node(node, scope, self.context.get_type('Int'), self.context.get_type('Int'))

    @visitor.when(ast.MinusNode)
    def visit(self, node: ast.MinusNode, scope: Scope):
        return self._visit_arithmetic_node(node, scope, self.context.get_type('Int'), self.context.get_type('Int'))

    @visitor.when(ast.StarNode)
    def visit(self, node: ast.StarNode, scope: Scope):
        return self._visit_arithmetic_node(node, scope, self.context.get_type('Int'), self.context.get_type('Int'))

    @visitor.when(ast.DivNode)
    def visit(self, node: ast.DivNode, scope: Scope):
        return self._visit_arithmetic_node(node, scope, self.context.get_type('Int'), self.context.get_type('Int'))

    @visitor.when(ast.LessEqualNode)
    def visit(self, node: ast.LessEqualNode, scope: Scope):
        return self._visit_arithmetic_node(node, scope, self.context.get_type('Int'), self.context.get_type('Bool'))

    @visitor.when(ast.LessThanNode)
    def visit(self, node: ast.LessThanNode, scope: Scope):
        return self._visit_arithmetic_node(node, scope, self.context.get_type('Int'), self.context.get_type('Bool'))

    @visitor.when(ast.EqualNode)
    def visit(self, node: ast.EqualNode, scope: Scope):
        self.visit(node.left, scope)
        self.visit(node.right, scope)
        return AtomNode(self.context.get_type('Bool'))

    def _visit_arithmetic_node(self, node: ast.BinaryNode, scope: Scope, member_types: Type, return_type: Type):
        left = self.visit(node.left, scope)
        right = self.visit(node.right, scope)

        if not isinstance(left, AtomNode):
            self.graph.add_edge(AtomNode(member_types), left)

        if not isinstance(right, AtomNode):
            self.graph.add_edge(AtomNode(member_types), right)

        return AtomNode(return_type)


class InferenceTypeSubstitute:
    def __init__(self, context: Context, errors: List[str] = []):
        self.context: Context = context
        self.errors: List[str] = errors
        self.current_type: Type = None
        self.current_method: Method = None

    @visitor.on('node')
    def visit(self, node, tabs):
        pass

    @visitor.when(ast.ProgramNode)
    def visit(self, node: ast.ProgramNode, scope: Scope = None):
        if scope is not None:
            for elem in node.declarations:
                self.visit(elem, scope.children[0])
        return scope

    @visitor.when(ast.ClassDeclarationNode)
    def visit(self, node: ast.ClassDeclarationNode, scope: Scope):
        self.current_type = self.context.get_type(node.id)

        attrs = [feature for feature in node.features if isinstance(feature, ast.AttrDeclarationNode)]
        methods = [feature for feature in node.features if isinstance(feature, ast.MethodDeclarationNode)]

        for attr in attrs:
            self.visit(attr, scope)

        for i, method in enumerate(methods):
            self.visit(method, scope.children[i])

    @visitor.when(ast.AttrDeclarationNode)
    def visit(self, node: ast.AttrDeclarationNode, scope: Scope):
        attr_type = self.context.get_type(node.type)
        var_info = scope.find_variable(node.id)

        if node.expr is not None:
            self.visit(node.expr, scope.create_child())

        if attr_type == self.context.get_type('AUTO_TYPE'):
            if var_info.type == self.context.get_type('AUTO_TYPE'):
                self.errors.append(err.INFERENCE_ERROR_ATTRIBUTE % node.id)
            node.type = var_info.type.name
            self.current_type.get_attribute(node.id).type = var_info.type

    @visitor.when(ast.MethodDeclarationNode)
    def visit(self, node: ast.MethodDeclarationNode, scope: Scope):
        self.current_method = self.current_type.get_method(node.id)
        return_type = self.context.get_type(node.return_type)

        for i, (name, expr_body_type) in enumerate(node.params):
            variable_info = scope.find_variable(name)
            if variable_info.type == self.context.get_type('AUTO_TYPE'):
                self.errors.append(err.INFERENCE_ERROR_ATTRIBUTE % name)
            node.params[i] = (name, variable_info.type.name)
            self.current_method.param_types[i] = variable_info.type

        self.visit(node.body, scope)

        if return_type == self.context.get_type('AUTO_TYPE'):
            if self.current_method.return_type == self.context.get_type('AUTO_TYPE'):
                self.errors.append(err.INFERENCE_ERROR_ATTRIBUTE % node.id)
            node.return_type = self.current_method.return_type.name

    @visitor.when(ast.LetNode)
    def visit(self, node: ast.LetNode, scope: Scope):
        for elem in node.declarations:
            self.visit(elem, scope)

        self.visit(node.expr, scope.children[0])

    @visitor.when(ast.VarDeclarationNode)
    def visit(self, node: ast.VarDeclarationNode, scope: Scope):
        variable_info = scope.find_variable(node.id)

        if node.expr is not None:
            self.visit(node.expr, scope)

        if node.type == 'AUTO_TYPE':
            if variable_info.type == self.context.get_type('AUTO_TYPE'):
                self.errors.append(err.INFERENCE_ERROR_ATTRIBUTE % node.id)
            node.type = variable_info.type.name

    @visitor.when(ast.AssignNode)
    def visit(self, node: ast.AssignNode, scope: Scope):
        self.visit(node.expr, scope)

    @visitor.when(ast.BlockNode)
    def visit(self, node: ast.BlockNode, scope: Scope):
        for i, expr in enumerate(node.expressions):
            self.visit(expr, scope)

    @visitor.when(ast.ConditionalNode)
    def visit(self, node: ast.ConditionalNode, scope: Scope):
        self.visit(node.if_expr, scope)
        self.visit(node.then_expr, scope)
        self.visit(node.else_expr, scope)

    @visitor.when(ast.WhileNode)
    def visit(self, node: ast.WhileNode, scope: Scope):
        self.visit(node.condition, scope)
        self.visit(node.body, scope.children[0])

    @visitor.when(ast.SwitchCaseNode)
    def visit(self, node: ast.SwitchCaseNode, scope: Scope):
        self.visit(node.expr, scope)
        for i, case in enumerate(node.cases):
            self.visit(case, scope.children[i])

    @visitor.when(ast.CaseNode)
    def visit(self, node: ast.CaseNode, scope: Scope):
        var_info = scope.find_variable(node.id)
        if node.type == 'AUTO_TYPE':
            if var_info.type == self.context.get_type('AUTO_TYPE'):
                self.errors.append(err.INFERENCE_ERROR_VARIABLE % node.id)
            node.type = var_info.type.name
        self.visit(node.expr, scope)

    @visitor.when(ast.MethodCallNode)
    def visit(self, node: ast.MethodCallNode, scope: Scope):
        self.visit(node.obj, scope)

        for arg in node.args:
            self.visit(arg, scope)

    @visitor.when(ast.AtomicNode)
    def visit(self, node: ast.AtomicNode, scope: Scope):
        pass

    @visitor.when(ast.UnaryNode)
    def visit(self, node: ast.UnaryNode, scope: Scope):
        self.visit(node.expr, scope)

    @visitor.when(ast.BinaryNode)
    def visit(self, node: ast.BinaryNode, scope: Scope):
        self.visit(node.left, scope)
        self.visit(node.right, scope)
