"""The type inference algorithm consist in a dependency di-graph with special nodes to handle the behavior of the
updates of components in the code and solve it in the `context`. For that we crate an structure called
DependencyGraph where we can create nodes as an structure called DependencyNode and arcs between them, an arc e =
<x,y> where x and y are dependency nodes means that the type of node y is inferred by the type of node x,
so for solve the type of y we need first to infer the type of x. For this operation we need some basic nodes that
only contains the type of the node called AtomNode and in the digraph formation an AtomNode is never inferred from
another node. The DependencyGraph consist in a dictionary[node, adjacency list] this adjacency has a declaration
order and this is fundamental for the inference solution algorithm. If we have a case {x : [y, z]} where x, y,
z are nodes then the algorithm will determinate the type of y and all it dependencies before to start with z (a
simple DFS). The order in the adjacency list is the same appearance order in the program. At the end of the algorithm
all nodes that cannot solve it type will be tagged as `Object`.

DependencyNode hierarchy
    AtomNode
        - type : Node type

    VariableInfoNode
        - type: Node type
        - variable_type : Reference to the variable info of the scope

    AttributeNode
        - type : Node type
        - attribute : Reference to the attribute of the class

    ParameterNode
        - type : Node type
        - method : Reference to the method of the class
        - index : Index of the parameter of the method

    ReturnTypeNode
        - type : Node type
        - method : Reference to the method of the class

All nodes has an implementation of the method update that handle how to update the type by it's dependencies
"""
from abc import ABC
from collections import OrderedDict, deque
from typing import Dict, List, Optional, Set, Tuple, Deque

import cool.semantics.utils.astnodes as ast
import cool.semantics.utils.errors as err
import cool.semantics.visitor as visitor
from cool.semantics.utils.scope import (Attribute, Context, ErrorType, Method,
                                        Scope, SemanticError, Type, VariableInfo)


class DependencyNode:
    type: Type

    def update(self, _type: Type) -> None:
        raise NotImplementedError()

    def __repr__(self):
        return str(self)

    @property
    def is_ready(self):
        return True


class AtomNode(DependencyNode):
    def __init__(self, atom_type: Type):
        self.type: Type = atom_type

    def update(self, _type: Type) -> None:
        pass

    def __str__(self):
        return f'Atom({self.type.name})'


class VariableInfoNode(DependencyNode):
    def __init__(self, var_type: Type, variable_info: VariableInfo):
        self.type: Type = var_type
        self.variable_info: VariableInfo = variable_info

    def update(self, _type):
        self.type = self.variable_info.type = _type

    def __str__(self):
        return f'VarInfo({self.variable_info.name}, {self.type.name})'


class AttributeNode(DependencyNode):
    def __init__(self, attr_type: Type, attribute: Attribute):
        self.type: Type = attr_type
        self.attribute: Attribute = attribute

    def update(self, _type: Type) -> None:
        self.type = self.attribute.type = _type

    def __str__(self):
        return f'Attr({self.attribute.name}, {self.type.name})'


class ParameterNode(DependencyNode):
    def __init__(self, param_type: Type, method: Method, index: int):
        self.type: Type = param_type
        self.method: Method = method
        self.index: int = index

    def update(self, _type):
        self.type = self.method.param_types[self.index] = _type

    def __str__(self):
        return f'Param({self.method.name}, {self.index}, {self.type.name})'


class ReturnTypeNode(DependencyNode):
    def __init__(self, ret_type: Type, method: Method):
        self.type: Type = ret_type
        self.method: Method = method

    def update(self, _type):
        self.type = self.method.return_type = _type

    def __str__(self):
        return f'Return({self.method.name}, {self.type.name})'


class BranchedNode(DependencyNode, ABC):
    branches: List[DependencyNode] = []

    @property
    def is_ready(self) -> bool:
        return all(x.type.name != 'AUTO_TYPE' for x in self.branches)


class ConditionalNode(BranchedNode):
    def __init__(self, conditional_type, then_branch, else_branch):
        self.type = conditional_type
        self.branches = [then_branch, else_branch]

    def update(self, _type: Type) -> None:
        self.type = _type

    def __str__(self):
        return f'ConditionalNode({self.type.name})'


class CaseOfNode(BranchedNode):
    def __init__(self, _type, branches):
        self.type = _type
        self.branches = branches

    def update(self, _type: Type) -> None:
        self.type = _type

    def __str__(self):
        return f'CaseOfNode({self.type.name})'


class DependencyGraph:
    def __init__(self):
        self.dependencies: Dict[DependencyNode, List[DependencyNode]] = OrderedDict()

    def add_node(self, node: DependencyNode):
        if node not in self.dependencies:
            self.dependencies[node] = []

    def add_edge(self, node: DependencyNode, other: DependencyNode):
        try:
            self.dependencies[node].append(other)
        except KeyError:
            self.dependencies[node] = [other]
        self.add_node(other)

    def update_dependencies(self, default_type: Type = None):
        queue: Deque[DependencyNode] = deque(node for node in self.dependencies if isinstance(node, AtomNode))
        visited: Set[DependencyNode] = set(queue)

        while queue:
            node = queue.popleft()

            if not node.is_ready:
                continue

            for adj in self.dependencies[node]:
                if adj not in visited:
                    adj.update(node.type)
                    visited.add(adj)
                    if not isinstance(adj, BranchedNode):
                        queue.append(adj)

        for node in self.dependencies:
            if isinstance(node, BranchedNode) and node.is_ready:
                node.update(Type.multi_join([x.type for x in node.branches]))

        queue = deque(node for node in self.dependencies
                      if isinstance(node, BranchedNode) and node.type.name != 'AUTO_TYPE')
        visited.update(queue)
        while queue:
            node = queue.popleft()
            for adj in self.dependencies[node]:
                if adj not in visited:
                    adj.update(node.type)
                    visited.add(adj)
                    queue.append(adj)

        if default_type is not None:
            for node in self.dependencies:
                if node not in visited:
                    node.update(default_type)

    def __str__(self):
        return '{\n\t' + '\n\t'.join(f'{key}: {value}' for key, value in self.dependencies.items()) + '\n}'


class InferenceChecker:
    def __init__(self, context, errors):
        self.context: Context = context
        self.errors: List[str] = errors
        self.current_type: Optional[Type] = None
        self.current_method: Optional[Method] = None

        self.variables: Dict[VariableInfo, VariableInfoNode] = {}
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

        # print(self.graph, '\n')
        self.graph.update_dependencies(default_type=self.context.get_type('Object'))
        # print(self.graph, '\n')
        InferenceTypeSubstitute(self.context, self.errors).visit(node, scope)

    @visitor.when(ast.ClassDeclarationNode)
    def visit(self, node: ast.ClassDeclarationNode, scope: Scope):
        self.current_type = self.context.get_type(node.id)

        attrs = [feature for feature in node.features if isinstance(feature, ast.AttrDeclarationNode)]
        methods = [feature for feature in node.features if isinstance(feature, ast.MethodDeclarationNode)]

        for attr in attrs:
            self.visit(attr, scope)

        for method in methods:
            self.visit(method, scope.create_child())

    @visitor.when(ast.AttrDeclarationNode)
    def visit(self, node: ast.AttrDeclarationNode, scope: Scope):
        # Solve the expression of the attribute
        expr_node = self.visit(node.expr, scope.create_child()) if node.expr is not None else None

        # Define attribute in the scope
        var_info = scope.define_variable(node.id, self.context.get_type(node.type))

        # Set and get the reference to the variable info node
        var_info_node = self.variables[var_info] = VariableInfoNode(self.context.get_type(node.type), var_info)

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
        for _id, _type, _expr in node.declarations:
            try:
                # Define and get the var_info
                var_info = scope.define_variable(_id, self.context.get_type(_type))
            except SemanticError:
                var_info = scope.define_variable(_id, ErrorType())
            var_info_node = self.variables[var_info] = VariableInfoNode(var_info.type, var_info)

            expr_node = self.visit(_expr, scope.create_child()) if _expr is not None else None

            if var_info.type.name == 'AUTO_TYPE':
                # Create an edge or add an new node only if it is AutoType
                if expr_node is not None:
                    self.graph.add_edge(expr_node, var_info_node)
                    if expr_node.type.name == 'AUTO_TYPE':
                        self.graph.add_edge(var_info_node, expr_node)
                else:
                    self.graph.add_node(var_info_node)
            elif expr_node is not None and expr_node.type.name == 'AUTO_TYPE':
                self.graph.add_edge(var_info_node, expr_node)

        return self.visit(node.expr, scope.create_child())

    @visitor.when(ast.AssignNode)
    def visit(self, node: ast.AssignNode, scope: Scope):
        var_info = scope.find_variable(node.id)

        expr_node = self.visit(node.expr, scope.create_child())

        if var_info is not None:
            if expr_node.type.name != 'AUTO_TYPE' and var_info.type.name == 'AUTO_TYPE':
                self.graph.add_edge(expr_node, self.variables[var_info])
            elif var_info.type.name != 'AUTO_TYPE' and expr_node.type.name == 'AUTO_TYPE':
                self.graph.add_edge(AtomNode(self.context.get_type(var_info.type.name)), expr_node)
            elif var_info.type.name == 'AUTO_TYPE' and expr_node.type.name == 'AUTO_TYPE':
                # Create a cycle
                self.graph.add_edge(expr_node, self.variables[var_info])
                self.graph.add_edge(self.variables[var_info], expr_node)
        else:
            pass

        return expr_node

    @visitor.when(ast.BlockNode)
    def visit(self, node: ast.BlockNode, scope: Scope):
        child_scope = scope.create_child()
        result_node = None
        for expr in node.expressions:
            result_node = self.visit(expr, child_scope)
        return result_node

    @visitor.when(ast.ConditionalNode)
    def visit(self, node: ast.ConditionalNode, scope: Scope):
        if_node = self.visit(node.if_expr, scope)

        if not isinstance(if_node, AtomNode):
            self.graph.add_edge(AtomNode(self.context.get_type('Bool')), if_node)

        then_node = self.visit(node.then_expr, scope.create_child())
        else_node = self.visit(node.else_expr, scope.create_child())

        if isinstance(then_node, AtomNode) and isinstance(else_node, AtomNode):
            return AtomNode(then_node.type.join(else_node.type))

        conditional_node = ConditionalNode(self.context.get_type('AUTO_TYPE'), then_node, else_node)
        if isinstance(then_node, AtomNode) and not isinstance(else_node, AtomNode):
            self.graph.add_edge(then_node, else_node)
        elif not isinstance(then_node, AtomNode) and isinstance(else_node, AtomNode):
            self.graph.add_edge(else_node, then_node)
        else:
            self.graph.add_edge(then_node, else_node)
            self.graph.add_edge(else_node, then_node)
            self.graph.add_edge(conditional_node, then_node)
            self.graph.add_edge(conditional_node, else_node)

        return conditional_node

    @visitor.when(ast.WhileNode)
    def visit(self, node: ast.WhileNode, scope: Scope):
        self.visit(node.condition, scope)
        self.visit(node.body, scope.create_child())
        return AtomNode(self.context.get_type('Object'))

    @visitor.when(ast.SwitchCaseNode)
    def visit(self, node: ast.SwitchCaseNode, scope: Scope):
        self.visit(node.expr, scope)

        defined_nodes = []
        not_defined_nodes = []
        case_nodes = []
        for _id, _type, _expr in node.cases:
            new_scope = scope.create_child()
            var_info = new_scope.define_variable(_id, self.context.get_type(_type))
            self.variables[var_info] = VariableInfoNode(var_info.type, var_info)

            case_node = self.visit(_expr, new_scope)
            if isinstance(case_node, AtomNode):
                defined_nodes.append(case_node)
            else:
                not_defined_nodes.append(case_node)
            case_nodes.append(case_node)

        if any(e.type.name == 'AUTO_TYPE' for e in case_nodes):
            if defined_nodes:
                t = Type.multi_join([x.type for x in defined_nodes])
                for x in not_defined_nodes:
                    self.graph.add_edge(AtomNode(t), x)
            case_of_node = CaseOfNode(self.context.get_type('AUTO_TYPE'), case_nodes)
            self.graph.add_node(case_of_node)
            return case_of_node
        return AtomNode(Type.multi_join([e.type for e in case_nodes]))

    @visitor.when(ast.MethodCallNode)
    def visit(self, node: ast.MethodCallNode, scope: Scope):
        if node.obj is None:
            node.obj = ast.VariableNode('self')
        obj_node = self.visit(node.obj, scope)

        if isinstance(obj_node, AtomNode) and obj_node.type.contains_method(node.id):
            method, owner = obj_node.type.get_method(node.id, get_owner=True)
            param_nodes, return_node = self.methods[owner.name, method.name]
            for i, arg in enumerate(node.args):
                arg_node = self.visit(arg, scope)

                if arg_node is None:
                    # Possible error
                    continue

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

            if return_node.type.name == 'AUTO_TYPE':
                return return_node
            return AtomNode(return_node.type if return_node.type.name != 'SELF_TYPE' else obj_node.type)

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
            return None

    @visitor.when(ast.InstantiateNode)
    def visit(self, node: ast.InstantiateNode, scope: Scope):
        if node.lex in self.context.types:
            return AtomNode(self.context.get_type(node.lex))
        return AtomNode(self.context.get_type('Object'))

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
    def __init__(self, context: Context, errors: List[str]):
        self.context: Context = context
        self.errors: List[str] = errors
        self.current_type: Optional[Type] = None
        self.current_method: Optional[Method] = None

    @visitor.on('node')
    def visit(self, node, tabs):
        pass

    @visitor.when(ast.ProgramNode)
    def visit(self, node: ast.ProgramNode, scope: Scope):
        for i, elem in enumerate(node.declarations):
            self.visit(elem, scope.children[i])
        return scope

    @visitor.when(ast.ClassDeclarationNode)
    def visit(self, node: ast.ClassDeclarationNode, scope: Scope):
        self.current_type = self.context.get_type(node.id)

        attrs = [feature for feature in node.features if isinstance(feature, ast.AttrDeclarationNode)]
        methods = [feature for feature in node.features if isinstance(feature, ast.MethodDeclarationNode)]

        i = 0
        for attr in attrs:
            if attr.expr is not None:
                attr.index = i
                i += 1
            self.visit(attr, scope)

        for i, method in enumerate(methods, i):
            self.visit(method, scope.children[i])

    @visitor.when(ast.AttrDeclarationNode)
    def visit(self, node: ast.AttrDeclarationNode, scope: Scope):
        attr_type = self.context.get_type(node.type)
        var_info = scope.find_variable(node.id)

        if node.expr is not None:
            self.visit(node.expr, scope.children[node.index])

        if attr_type == self.context.get_type('AUTO_TYPE'):
            if var_info.type == self.context.get_type('AUTO_TYPE'):
                self.errors.append(err.INFERENCE_ERROR_ATTRIBUTE % node.id)
            node.type = var_info.type.name

    @visitor.when(ast.MethodDeclarationNode)
    def visit(self, node: ast.MethodDeclarationNode, scope: Scope):
        self.current_method = self.current_type.get_method(node.id)
        return_type = self.context.get_type(node.return_type)

        for i, (name, expr_body_type) in enumerate(node.params):
            variable_info = scope.find_variable(name)
            if variable_info.type == self.context.get_type('AUTO_TYPE'):
                self.errors.append(err.INFERENCE_ERROR_ATTRIBUTE % name)
            node.params[i] = (name, variable_info.type.name)

        self.visit(node.body, scope)

        if return_type == self.context.get_type('AUTO_TYPE'):
            if self.current_method.return_type == self.context.get_type('AUTO_TYPE'):
                self.errors.append(err.INFERENCE_ERROR_ATTRIBUTE % node.id)
            node.return_type = self.current_method.return_type.name

    @visitor.when(ast.LetNode)
    def visit(self, node: ast.LetNode, scope: Scope):
        child_index = 0
        for i, (_id, _type, _expr) in enumerate(node.declarations):
            variable_info = scope.find_variable(_id)

            if _expr is not None:
                self.visit(_expr, scope.children[child_index])
                child_index += 1

            if _type == 'AUTO_TYPE':
                if variable_info.type == self.context.get_type('AUTO_TYPE'):
                    self.errors.append(err.INFERENCE_ERROR_ATTRIBUTE % _id)
                node.declarations[i] = (_id, variable_info.type.name, _expr)

        self.visit(node.expr, scope.children[child_index])

    @visitor.when(ast.AssignNode)
    def visit(self, node: ast.AssignNode, scope: Scope):
        self.visit(node.expr, scope.children[0])

    @visitor.when(ast.BlockNode)
    def visit(self, node: ast.BlockNode, scope: Scope):
        child_scope = scope.children[0]
        for i, expr in enumerate(node.expressions):
            self.visit(expr, child_scope)

    @visitor.when(ast.ConditionalNode)
    def visit(self, node: ast.ConditionalNode, scope: Scope):
        self.visit(node.if_expr, scope)
        self.visit(node.then_expr, scope.children[0])
        self.visit(node.else_expr, scope.children[1])

    @visitor.when(ast.WhileNode)
    def visit(self, node: ast.WhileNode, scope: Scope):
        self.visit(node.condition, scope)
        self.visit(node.body, scope.children[0])

    @visitor.when(ast.SwitchCaseNode)
    def visit(self, node: ast.SwitchCaseNode, scope: Scope):
        self.visit(node.expr, scope)
        for i, (_id, _type, _expr) in enumerate(node.cases):
            self.visit(_expr, scope.children[i])

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
