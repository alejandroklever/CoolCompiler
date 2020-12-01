from typing import Any, Dict

import cool.semantics.utils.astnodes as ast
import cool.semantics.utils.errors as err
import cool.semantics.visitor as visitor
from cool.semantics.utils.scope import Context, Method, Scope, Type, SemanticError


class ExecutionError(Exception):
    @property
    def text(self):
        return self.args[0]


def abort(obj, context):
    print('Aborting Program')
    exit()


def copy(obj, context):
    x_copy = Instance(obj.type, obj.value if obj.type.name in ('Int', 'String', 'Bool') else None)
    x_copy.attribute_values = obj.attribute_values
    return x_copy


def type_name(obj, context):
    return Instance(context.get_type('String'), obj.type.name)


def out_string(obj, s, context):
    print(s.value, end='')
    return obj


def out_int(obj, s, context):
    print(s.value, end='')
    return obj


def in_string(obj, context):
    return Instance(context.get_type('Int'), input())


def in_int(obj, context):
    try:
        return Instance(context.get_type('Int'), int(input()))
    except ValueError:
        raise ExecutionError(err.INPUT_INT_ERROR)


def length(obj, context):
    return Instance(context.get_type('Int'), len(obj.value))


def concat(obj, s, context):
    return Instance(context.get_type('String'), obj.value + s.value)


def substr(obj, i, l, context):
    return Instance(context.get_type('String'), obj.value[i: i + l])


defaults = {
    ('Object', 'abort'): abort,
    ('Object', 'copy'): copy,
    ('Object', 'type_name'): type_name,
    ('IO', 'out_string'): out_string,
    ('IO', 'out_int'): out_int,
    ('IO', 'in_string'): in_string,
    ('IO', 'in_int'): in_int,
    ('String', 'length'): length,
    ('String', 'concat'): concat,
    ('String', 'substr'): substr,
}


class Instance:
    def __init__(self, typex: Type, value: Any = None):
        if value is None:
            value = id(self)

        self.type: Type = typex
        self.value: Any = value
        self.attribute_values: Dict[str, Instance] = {}

    def set_attribute_instance(self, name: str, value: 'Instance') -> None:
        self.attribute_values[name] = value

    def get_attribute_instance(self, name: str) -> 'Instance':
        return self.attribute_values[name]

    def get_method(self, name: str) -> Method:
        return self.type.get_method(name)

    def __str__(self):
        return f'{self.type.name} {self.value}'


class VoidInstance(Instance):
    def __init__(self):
        super(VoidInstance, self).__init__(None, None)

    def __eq__(self, other):
        return isinstance(other, VoidInstance)


class Executor:
    def __init__(self, context: Context):
        self.context: Context = context
        self.current_type: Type = None
        self.current_instance: Instance = None
        self.call_stack: list = []

    @visitor.on('node')
    def visit(self, node, tabs):
        pass

    @visitor.when(ast.ProgramNode)
    def visit(self, node: ast.ProgramNode, scope: Scope = None):
        for declaration in node.declarations:
            self.visit(declaration, None)

        try:
            main_class = self.context.get_type('Main')
        except SemanticError:
            raise ExecutionError(err.MAIN_CLASS_NOT_FOUND)

        try:
            main_class.get_method('main')
        except SemanticError:
            raise ExecutionError(err.MAIN_METHOD_NOT_FOUND)

        execution_node = ast.MethodCallNode('main', [], ast.InstantiateNode('Main'))
        self.visit(execution_node, scope)

    @visitor.when(ast.ClassDeclarationNode)
    def visit(self, node: ast.ClassDeclarationNode, scope: Scope):
        self.current_type = self.context.get_type(node.id)

        attrs = [f for f in node.features if isinstance(f, ast.AttrDeclarationNode)]
        methods = [f for f in node.features if isinstance(f, ast.MethodDeclarationNode)]

        for attr in attrs:
            self.visit(attr, None)

        for method in methods:
            self.visit(method, None)

    @visitor.when(ast.AttrDeclarationNode)
    def visit(self, node: ast.AttrDeclarationNode, scope: Scope):
        self.current_type.get_attribute(node.id).expr = node.expr

    @visitor.when(ast.MethodDeclarationNode)
    def visit(self, node: ast.MethodDeclarationNode, scope: Scope):
        self.current_type.get_method(node.id).expr = node.body

    @visitor.when(ast.LetNode)
    def visit(self, node: ast.LetNode, scope: Scope):
        default = {'String': '', 'Int': 0, 'Bool': False}
        for _id, _type, _expr in node.declarations:

            instance = self.visit(_expr, scope.create_child()) if _expr is not None else VoidInstance()

            if _expr is None and _type in default:
                instance = Instance(self.context.get_type(_type), default[_type])

            scope.define_variable(_id, instance.type).instance = instance

        return self.visit(node.expr, scope.create_child())

    @visitor.when(ast.AssignNode)
    def visit(self, node: ast.AssignNode, scope: Scope):
        variable_info = scope.find_variable(node.id)

        if variable_info is None:
            self.current_instance.set_attribute_instance(node.id, self.visit(node.expr, scope))
            return self.current_instance.get_attribute_instance(node.id)

        variable_info.instance = self.visit(node.expr, scope)
        return variable_info.instance

    @visitor.when(ast.BlockNode)
    def visit(self, node: ast.BlockNode, scope: Scope):
        child_scope = scope.create_child()
        instance = None
        for expr in node.expressions:
            instance = self.visit(expr, child_scope)
        return instance

    @visitor.when(ast.ConditionalNode)
    def visit(self, node: ast.ConditionalNode, scope: Scope):
        if_instance = self.visit(node.if_expr, scope)

        if if_instance.value:
            return self.visit(node.then_expr, scope.create_child())
        return self.visit(node.else_expr, scope.create_child())

    @visitor.when(ast.WhileNode)
    def visit(self, node: ast.WhileNode, scope: Scope):
        while self.visit(node.condition, scope).value:
            self.visit(node.body, scope.create_child())
        return VoidInstance()

    @visitor.when(ast.SwitchCaseNode)
    def visit(self, node: ast.SwitchCaseNode, scope: Scope):
        instance = self.visit(node.expr, scope)

        if isinstance(instance, VoidInstance):
            raise ExecutionError(err.VOID_EXPRESSION)

        types = [(i, self.context.get_type(t)) for i, (_, t, _) in enumerate(node.cases)
                 if instance.type.conforms_to(self.context.get_type(t))]

        if not types:
            raise ExecutionError(err.CASE_OF_ERROR)

        (index, most_conformable_type), *types = types
        for i, t in types:
            if t.conforms_to(most_conformable_type):
                index, most_conformable_type = i, t

        child_scope = scope.create_child()
        name, typex, expr = node.cases[index]
        child_scope.define_variable(name, self.context.get_type(typex)).instance = instance
        return self.visit(expr, child_scope)

    @visitor.when(ast.MethodCallNode)
    def visit(self, node: ast.MethodCallNode, scope: Scope):
        obj_instance = self.visit(node.obj, scope)

        if isinstance(obj_instance, VoidInstance):
            raise ExecutionError(err.VOID_EXPRESSION)

        if obj_instance.type.conforms_to(self.context.get_type('Object')) and ('Object', node.id) in defaults:
            args = (obj_instance,) + tuple(self.visit(arg, scope) for arg in node.args) + (self.context,)
            return defaults['Object', node.id](*args)

        if obj_instance.type.conforms_to(self.context.get_type('IO')) and ('IO', node.id) in defaults:
            args = (obj_instance,) + tuple(self.visit(arg, scope) for arg in node.args) + (self.context,)
            return defaults['IO', node.id](*args)

        if obj_instance.type.conforms_to(self.context.get_type('String')) and ('String', node.id) in defaults:
            args = (obj_instance,) + tuple(self.visit(arg, scope) for arg in node.args) + (self.context,)
            return defaults['String', node.id](*args)

        new_scope = Scope()

        method = obj_instance.get_method(node.id)
        new_scope.define_variable('self', obj_instance.type).instance = obj_instance
        for name, typex, arg in zip(method.param_names, method.param_types, node.args):
            new_scope.define_variable(name, typex).instance = self.visit(arg, scope)

        self.call_stack.append(self.current_instance)
        self.current_instance = obj_instance
        output = self.visit(method.expr, new_scope)
        self.current_instance = self.call_stack.pop()
        return output

    @visitor.when(ast.IntegerNode)
    def visit(self, node: ast.IntegerNode, scope: Scope):
        return Instance(self.context.get_type('Int'), int(node.lex))

    @visitor.when(ast.StringNode)
    def visit(self, node: ast.StringNode, scope: Scope):
        return Instance(self.context.get_type('String'), str(node.lex[1:-1].replace('\\n', '\n')))

    @visitor.when(ast.BooleanNode)
    def visit(self, node: ast.BooleanNode, scope: Scope):
        return Instance(self.context.get_type('Bool'), True if node.lex == 'true' else False)

    @visitor.when(ast.VariableNode)
    def visit(self, node: ast.VariableNode, scope: Scope):
        variable_info = scope.find_variable(node.lex)
        if variable_info is not None:
            return variable_info.instance
        else:
            return self.current_instance.get_attribute_instance(node.lex)

    @visitor.when(ast.InstantiateNode)
    def visit(self, node: ast.InstantiateNode, scope: Scope):
        default = None
        if node.lex == 'String':
            default = ''
        elif node.lex == 'Int':
            default = 0
        elif node.lex == 'Bool':
            default = False

        instance = Instance(self.context.get_type(node.lex), default)
        self.call_stack.append(self.current_instance)
        self.current_instance = instance
        fake_scope = Scope()
        for attr, _ in instance.type.all_attributes():
            attr_instance = self.visit(attr.expr, fake_scope) if attr.expr is not None else VoidInstance()
            fake_scope.define_variable(attr.name, attr.type).instance = attr_instance
            self.current_instance.set_attribute_instance(attr.name, attr_instance)
        self.current_instance = self.call_stack.pop()
        return instance

    @visitor.when(ast.NegationNode)
    def visit(self, node: ast.NegationNode, scope: Scope):
        value = not self.visit(node.expr, scope).value
        return Instance(self.context.get_type('Bool'), value)

    @visitor.when(ast.ComplementNode)
    def visit(self, node: ast.ComplementNode, scope: Scope):
        value = ~ self.visit(node.expr, scope).value
        return Instance(self.context.get_type('Int'), value)

    @visitor.when(ast.IsVoidNode)
    def visit(self, node: ast.IsVoidNode, scope: Scope):
        value = isinstance(self.visit(node.expr, scope), VoidInstance)
        return Instance(self.context.get_type('Bool'), value)

    @visitor.when(ast.PlusNode)
    def visit(self, node: ast.PlusNode, scope: Scope):
        value = self.visit(node.left, scope).value + self.visit(node.right, scope).value
        return Instance(self.context.get_type('Int'), value)

    @visitor.when(ast.MinusNode)
    def visit(self, node: ast.MinusNode, scope: Scope):
        value = self.visit(node.left, scope).value - self.visit(node.right, scope).value
        return Instance(self.context.get_type('Int'), value)

    @visitor.when(ast.StarNode)
    def visit(self, node: ast.StarNode, scope: Scope):
        value = self.visit(node.left, scope).value * self.visit(node.right, scope).value
        return Instance(self.context.get_type('Int'), value)

    @visitor.when(ast.DivNode)
    def visit(self, node: ast.DivNode, scope: Scope):
        try:
            value = self.visit(node.left, scope).value / self.visit(node.right, scope).value
            return Instance(self.context.get_type('Int'), value)
        except ZeroDivisionError:
            raise ExecutionError(err.DIVIDE_BY_ZERO)

    @visitor.when(ast.LessEqualNode)
    def visit(self, node: ast.LessEqualNode, scope: Scope):
        value = self.visit(node.left, scope).value <= self.visit(node.right, scope).value
        return Instance(self.context.get_type('Bool'), value)

    @visitor.when(ast.LessThanNode)
    def visit(self, node: ast.LessThanNode, scope: Scope):
        value = self.visit(node.left, scope).value < self.visit(node.right, scope).value
        return Instance(self.context.get_type('Bool'), value)

    @visitor.when(ast.EqualNode)
    def visit(self, node: ast.EqualNode, scope: Scope):
        value = self.visit(node.left, scope).value == self.visit(node.right, scope).value
        return Instance(self.context.get_type('Bool'), value)
