"""This module contains definitions of classes for make different travels through the AST of a cool program. All
classes defined here follows the visitor pattern using the module visitor, with this we can get a more decoupled
inspection. """
from typing import List, Optional, Dict

import astnodes as ast
import visitor
from scope import (Context, SemanticError, Type, Scope, Method, AutoType, IntType, BoolType, StringType, ErrorType,
                   SelfType, ObjectType, IOType)

WRONG_SIGNATURE = 'Method "%s" already defined in "%s" with a different signature.'
SELF_IS_READONLY = 'Variable "self" is read-only.'
SELF_INVALID_ATTRIBUTE_ID = 'Cannot set "self" as attribute of a class.'
SELF_INVALID_PARAM_ID = 'Cannot set "self" as parameter of a method.'
INVALID_INHERIT_CLASS = 'Can not inherits from "Int", "String", "Bool".'
OVERRIDE_ATTRIBUTE_ID = 'Attributes cannot be override in derived class'
LOCAL_ALREADY_DEFINED = 'Variable "%s" is already defined in method "%s".'
INCOMPATIBLE_TYPES = 'Cannot convert "%s" into "%s".'
VARIABLE_NOT_DEFINED = 'Variable "%s" is not defined in "%s".'
INVALID_BINARY_OPERATION = 'Operation "%s" is not defined between "%s" and "%s".'
INVALID_UNARY_OPERATION = 'Operation "%s" is not defined for "%s".'
INVALID_ANCESTOR = 'Class "%s" has no an ancestor class "%s".'


class Formatter:
    @visitor.on('node')
    def visit(self, node, tabs):
        pass

    @visitor.when(ast.ProgramNode)
    def visit(self, node: ast.ProgramNode, tabs: int = 0):
        ans = '\t' * tabs + f'\\__ProgramNode [<class> ... <class>]'
        statements = '\n'.join(self.visit(child, tabs + 1) for child in node.declarations)
        return f'{ans}\n{statements}'

    @visitor.when(ast.ClassDeclarationNode)
    def visit(self, node: ast.ClassDeclarationNode, tabs: int = 0):
        parent = '' if node.parent is None else f": {node.parent}"
        ans = '\t' * tabs + f'\\__ClassDeclarationNode: class {node.id} {parent} {{ <feature> ... <feature> }}'
        features = '\n'.join(self.visit(child, tabs + 1) for child in node.features)
        return f'{ans}\n{features}'

    @visitor.when(ast.AttrDeclarationNode)
    def visit(self, node: ast.AttrDeclarationNode, tabs: int = 0):
        ans = '\t' * tabs + f'\\__AttrDeclarationNode: {node.id} : {node.type}'
        return f'{ans}'

    @visitor.when(ast.MethodDeclarationNode)
    def visit(self, node: ast.MethodDeclarationNode, tabs: int = 0):
        params = ', '.join(':'.join(param) for param in node.params)
        ans = '\t' * tabs + f'\\__FuncDeclarationNode: {node.id}({params}) : {node.return_type} -> <body>'
        body = self.visit(node.body, tabs + 1)
        return f'{ans}\n{body}'

    @visitor.when(ast.LetNode)
    def visit(self, node: ast.LetNode, tabs: int = 0):
        declarations = '\n'.join(self.visit(declaration, tabs + 1) for declaration in node.declarations)
        ans = '\t' * tabs + f'\\__LetNode:  let'
        expr = self.visit(node.expr, tabs + 2)
        return f'{ans}\n {declarations}\n' + '\t' * (tabs + 1) + 'in\n' + f'{expr}'

    @visitor.when(ast.VarDeclarationNode)
    def visit(self, node: ast.VarDeclarationNode, tabs: int = 0):
        if node.expr is not None:
            return '\t' * tabs + f'\\__VarDeclarationNode: {node.id}: {node.type} <-\n{self.visit(node.expr, tabs + 1)}'
        else:
            return '\t' * tabs + f'\\__VarDeclarationNode: {node.id} : {node.type}'

    @visitor.when(ast.AssignNode)
    def visit(self, node: ast.AssignNode, tabs: int = 0):
        ans = '\t' * tabs + f'\\__AssignNode: {node.id} <- <expr>'
        expr = self.visit(node.expr, tabs + 1)
        return f'{ans}\n{expr}'

    @visitor.when(ast.BlockNode)
    def visit(self, node: ast.BlockNode, tabs: int = 0):
        ans = '\t' * tabs + f'\\__BlockNode:'
        body = '\n'.join(self.visit(child, tabs + 1) for child in node.expressions)
        return f'{ans}\n{body}'

    @visitor.when(ast.ConditionalNode)
    def visit(self, node: ast.ConditionalNode, tabs: int = 0):
        ifx = self.visit(node.if_expr, tabs + 2)
        then = self.visit(node.then_expr, tabs + 2)
        elsex = self.visit(node.else_expr, tabs + 2)

        return '\n'.join([
            '\t' * tabs + f'\\__IfThenElseNode: if <expr> then <expr> else <expr> fi',
            '\t' * (tabs + 1) + f'\\__if \n{ifx}',
            '\t' * (tabs + 1) + f'\\__then \n{then}',
            '\t' * (tabs + 1) + f'\\__else \n{elsex}',
        ])

    @visitor.when(ast.WhileNode)
    def visit(self, node: ast.WhileNode, tabs: int = 0):
        condition = self.visit(node.condition, tabs + 2)
        body = self.visit(node.body, tabs + 2)

        return '\n'.join([
            '\t' * tabs + f'\\__WhileNode: while <expr> loop <expr> pool',
            '\t' * (tabs + 1) + f'\\__while \n{condition}',
            '\t' * (tabs + 1) + f'\\__loop \n{body}',
        ])

    @visitor.when(ast.SwitchCaseNode)
    def visit(self, node: ast.SwitchCaseNode, tabs: int = 0):
        expr = self.visit(node.expr, tabs + 2)
        cases = '\n'.join(self.visit(case, tabs + 3) for case in node.cases)

        return '\n'.join([
            '\t' * tabs + f'\\__SwitchCaseNode: case <expr> of [<case> ... <case>] esac',
            '\t' * (tabs + 1) + f'\\__case \n{expr} of',
        ]) + '\n' + cases

    @visitor.when(ast.CaseNode)
    def visit(self, node: ast.CaseNode, tabs: int = 0):
        expr = self.visit(node.expr, tabs + 1)
        return '\t' * tabs + f'\\__CaseNode: {node.id} : {node.type} =>\n{expr}'

    @visitor.when(ast.MethodCallNode)
    def visit(self, node: ast.MethodCallNode, tabs: int = 0):
        obj = self.visit(node.obj, tabs + 1)
        ans = '\t' * tabs + f'\\__CallNode: <obj>.{node.id}(<expr>, ..., <expr>)'
        args = '\n'.join(self.visit(arg, tabs + 1) for arg in node.args)
        return f'{ans}\n{obj}\n{args}'

    @visitor.when(ast.BinaryNode)
    def visit(self, node: ast.BinaryNode, tabs: int = 0):
        ans = '\t' * tabs + f'\\__<expr> {node.__class__.__name__} <expr>'
        left = self.visit(node.left, tabs + 1)
        right = self.visit(node.right, tabs + 1)
        return f'{ans}\n{left}\n{right}'

    @visitor.when(ast.AtomicNode)
    def visit(self, node: ast.AtomicNode, tabs: int = 0):
        return '\t' * tabs + f'\\__ {node.__class__.__name__}: {node.lex}'

    @visitor.when(ast.InstantiateNode)
    def visit(self, node: ast.InstantiateNode, tabs: int = 0):
        return '\t' * tabs + f'\\__ InstantiateNode: new {node.lex}()'


class TypeCollector:
    """Visitor to collect the class in the program, and the basic classes as Object, Int, String, IO and Bool

    Params
    ----------
    - errors: List[str] is a list of errors detected in the ast travel
    - context: Context the context for keeping the classes"""

    def __init__(self, context: Context = Context(), errors: List[str] = []):
        self.errors: List[str] = errors
        self.context: Context = context

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(ast.ProgramNode)
    def visit(self, node):
        self.context.types['AUTO_TYPE'] = AutoType()
        self_type = self.context.types['SELF_TYPE'] = SelfType()
        object_type = self.context.types['Object'] = ObjectType()
        io_type = self.context.types['IO'] = IOType()
        string_type = self.context.types['String'] = StringType()
        int_type = self.context.types['Int'] = IntType()
        bool_type = self.context.types['Bool'] = BoolType()

        io_type.set_parent(object_type)
        string_type.set_parent(object_type)
        int_type.set_parent(object_type)
        bool_type.set_parent(object_type)

        object_type.define_method('abort', ['self'], [self_type], object_type)
        object_type.define_method('get_type', ['self'], [self_type], string_type)
        object_type.define_method('copy', ['self'], [self_type], self_type)

        io_type.define_method('out_string', ['self', 'x'], [self_type, string_type], self_type)
        io_type.define_method('out_int', ['self', 'x'], [self_type, string_type], self_type)
        io_type.define_method('in_string', ['self'], [self_type], string_type)
        io_type.define_method('in_int', ['self'], [self_type], int_type)

        string_type.define_method('length', ['self'], [self_type], int_type)
        string_type.define_method('concat', ['self', 's'], [self_type, string_type], string_type)
        string_type.define_method('substr', ['self', 'i', 'l'], [self_type, int_type, int_type], string_type)

        for declaration in node.declarations:
            self.visit(declaration)

    @visitor.when(ast.ClassDeclarationNode)
    def visit(self, node):
        try:
            self.context.create_type(node.id)
        except SemanticError as e:
            self.errors.append(e.text)


class TypeBuilder:
    """This visitor collect all the attributes and methods in classes and set the parent to the current class

    Params
    ------
    - errors: List[str] is a list of errors detected in the ast travel
    - context: Context the context for keeping the classes
    - current_type: Optional[Type] is the current type in the building process"""

    def __init__(self, context: Context, errors: List[str]):
        self.context: Context = context
        self.current_type: Optional[Type] = None
        self.errors: List[str] = errors

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(ast.ProgramNode)
    def visit(self, node: ast.ProgramNode):
        for declaration in node.declarations:
            self.visit(declaration)

    @visitor.when(ast.ClassDeclarationNode)
    def visit(self, node: ast.ClassDeclarationNode):
        self.current_type = self.context.get_type(node.id)

        if node.parent is not None:
            if node.parent in ("Int", "String", "Bool", "SELF_TYPE"):
                self.errors.append('Can not inherits from "Int", "String" or "Bool".')

            try:
                self.current_type.set_parent(node.parent)
            except SemanticError as e:
                self.errors.append(e.text)
        else:
            self.current_type.set_parent(ObjectType())

        for feature in node.features:
            self.visit(feature)

    @visitor.when(ast.AttrDeclarationNode)
    def visit(self, node: ast.AttrDeclarationNode):
        try:
            name = node.id
            typex = self.context.get_type(node.type)
            self.current_type.define_attribute(name, typex)
        except SemanticError as e:
            self.errors.append(e.text)

    @visitor.when(ast.MethodDeclarationNode)
    def visit(self, node: ast.MethodDeclarationNode):
        name = node.id
        param_names = ['self']
        param_types = [SelfType()]
        for name, typex in node.params:
            param_names.append(name)
            try:
                param_types.append(self.context.get_type(name))
            except SemanticError as e:
                param_types.append(ErrorType())
                self.errors.append(e.text)

        try:
            return_type = self.context.get_type(node.return_type)
        except SemanticError as e:
            return_type = ErrorType()
            self.errors.append(e.text)

        self.current_type.define_method(name, param_names, param_types, return_type)


def topological_ordering(program_node: ast.ProgramNode,
                         context: Context,
                         errors: List[str]) -> ast.ProgramNode:
    """Set an order in the program node of de ast such that for all class A with parent B, class B is before A in the
    list, if in the process is detected a cycle an error is added to the `error` parameter

    :param program_node: Root of the first AST of the program

    :param context: Context With all collected and building types

    :param errors: The error list

    :return: a new AST where all declared class are in topological order"""

    types = context.types

    graph: Dict[str, List[str]] = {name: [] for name in types}

    for name, typex in types.items():
        if name == 'Object':
            continue
        graph[typex.parent.name].append(name)

    order = []
    visited = {name: False for name in graph}
    stack = ['Object']

    while stack:
        current_name = stack.pop()

        if visited[current_name]:
            errors.append(f'Cyclic class hierarchy in class {current_name}.')

        visited[current_name] = True
        stack += graph[current_name]
        order.append(current_name)

    declarations = {d.id: d for d in program_node.declarations}
    program_node.declarations = [declarations[name] for name in order if
                                 name not in ('Object', 'Int', 'IO', 'String', 'Bool')]

    return program_node


class OverriddenMethodChecker:
    """This visitor for validate the signature of the overridden methods

        Params
        ------
        - errors: List[str] is a list of errors detected in the ast travel
        - context: Context the context for keeping the classes
        - current_type: Optional[Type] is the current type in the building process"""

    def __init__(self, context: Context, errors: List[str]):
        self.context: Context = context
        self.current_type: Optional[Type] = None
        self.errors: List[str] = errors

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(ast.ProgramNode)
    def visit(self, node: ast.ProgramNode):
        for declaration in node.declarations:
            self.visit(declaration)

    @visitor.when(ast.ClassDeclarationNode)
    def visit(self, node: ast.ClassDeclarationNode):
        self.current_type = self.context.get_type(node.id)

        for feature in node.features:
            if isinstance(feature, ast.MethodDeclarationNode):
                self.visit(feature)

    @visitor.when(ast.MethodDeclarationNode)
    def visit(self, node: ast.MethodDeclarationNode):
        # At this point all class has defined a parent and they are visited in topological order
        method, owner = self.current_type.parent.get_method(node.id, get_owner=True)

        if len(method.param_types) != len(node.params):
            self.errors.append(WRONG_SIGNATURE % (method.name, owner.name))

        for parent_param_type, (_, current_param_type_name) in zip(method.param_types, node.params):
            if parent_param_type != self.context.get_type(current_param_type_name):
                self.errors.append(WRONG_SIGNATURE % (method.name, owner.name))
                break

        if method.return_type != self.context.get_type(node.return_type):
            self.errors.append(WRONG_SIGNATURE % (method.name, owner.name))


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


class TypeChecker:
    def __init__(self, context: Context, errors: List[str]):
        self.context: Context = context
        self.errors: List[str] = errors
        self.current_type: Type = None
        self.current_method: Method = None

    @visitor.on('node')
    def visit(self, node, scope):
        pass

    @visitor.when(ast.ProgramNode)
    def visit(self, node: ast.ProgramNode, scope: Scope = None):
        if scope is None:
            scope = Scope()

        for elem in node.declarations:
            self.visit(elem, scope.create_child())

        return scope

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
        if node.id == 'self':
            self.errors.append(SELF_INVALID_ATTRIBUTE_ID)

        attr_type = self.context.get_type(node.type)

        if node.expr is not None:
            expr_type = self.visit(node.expr, scope.create_child())
            if not expr_type.conforms_to(attr_type):
                self.errors.append(INCOMPATIBLE_TYPES % (expr_type.name, attr_type.name))

        scope.define_variable(node.id, attr_type)

    @visitor.when(ast.MethodDeclarationNode)
    def visit(self, node: ast.MethodDeclarationNode, scope: Scope):
        self.current_method = self.current_type.get_method(node.id)

        # Defining parameters in the scope. Parameters can hide the attribute declaration, that's why we are not
        # checking  if there is defined, instead we are checking for local declaration
        for i, (name, expr_body_type) in enumerate(node.params):
            if not scope.is_local(name):
                scope.define_variable(name, self.context.get_type(expr_body_type))
            else:
                self.errors.append(LOCAL_ALREADY_DEFINED % (name, self.current_method.name))

        return_type = self.context.get_type(node.return_type)

        expr_body_type = self.visit(node.body, scope)

        if not expr_body_type.conforms_to(return_type):
            self.errors.append(INCOMPATIBLE_TYPES % (expr_body_type.name, return_type.name))

    @visitor.when(ast.LetNode)
    def visit(self, node: ast.LetNode, scope: Scope):
        for elem in node.declarations:
            self.visit(elem, scope)
        return self.visit(node.expr, scope.create_child())

    @visitor.when(ast.VarDeclarationNode)
    def visit(self, node: ast.VarDeclarationNode, scope: Scope):
        try:
            var_static_type = self.context.get_type(node.type)
        except SemanticError as e:
            var_static_type = ErrorType()
            self.errors.append(e.text)

        if scope.is_local(node.id):
            self.errors.append(LOCAL_ALREADY_DEFINED % (node.id, self.current_method.name))
        else:
            scope.define_variable(node.id, var_static_type)

        if node.expr is not None:
            expr_type = self.visit(node.expr, scope)
            if not (expr_type.conforms_to(var_static_type)):
                self.errors.append(INCOMPATIBLE_TYPES % (expr_type.name, var_static_type.name))

        return var_static_type

    @visitor.when(ast.AssignNode)
    def visit(self, node: ast.AssignNode, scope: Scope):
        expr_type = self.visit(node.expr, scope)
        var_info = scope.find_variable(node.id)
        if var_info is None:
            self.errors.append(VARIABLE_NOT_DEFINED % (node.id, self.current_method.name))
            return ErrorType()
        else:
            if not expr_type.conforms_to(var_info.type):
                self.errors.append(INCOMPATIBLE_TYPES % (expr_type.name, var_info.type.name))
            return var_info.type

    @visitor.when(ast.BlockNode)
    def visit(self, node: ast.BlockNode, scope: Scope):
        return_type = ErrorType()
        for expr in node.expressions:
            return_type = self.visit(expr, scope)
        return return_type

    @visitor.when(ast.ConditionalNode)
    def visit(self, node: ast.ConditionalNode, scope: Scope):
        if_type = self.visit(node.if_expr, scope)
        then_type = self.visit(node.then_expr, scope)
        else_type = self.visit(node.else_expr, scope)
        if if_type != BoolType:
            self.errors.append(INCOMPATIBLE_TYPES % (if_type.name, 'Bool'))
        return then_type.join(else_type)

    @visitor.when(ast.WhileNode)
    def visit(self, node: ast.WhileNode, scope: Scope):
        condition = self.visit(node.condition, scope)
        if condition != BoolType():
            self.errors.append(INCOMPATIBLE_TYPES % (condition.name, 'Bool'))

        self.visit(node.body)
        return ObjectType()

    @visitor.when(ast.SwitchCaseNode)
    def visit(self, node: ast.SwitchCaseNode, scope: Scope):
        self.visit(node.expr, scope)
        return Type.multi_join([self.visit(case, scope.create_child()) for case in node.cases])

    @visitor.when(ast.CaseNode)
    def visit(self, node: ast.CaseNode, scope: Scope):
        try:
            scope.define_variable(node.id, self.context.get_type(node.type))
        except SemanticError as e:
            scope.define_variable(node.id, ErrorType())
            self.errors.append(e.text)

        return self.visit(node.expr, scope)

    @visitor.when(ast.MethodCallNode)
    def visit(self, node: ast.MethodCallNode, scope: Scope):
        obj_type = self.visit(node.obj, scope)

        if node.type is not None:
            try:
                ancestor_type = self.context.get_type(node.type)
            except SemanticError as e:
                ancestor_type = ErrorType()
                self.errors.append(e.text)

            if not obj_type.conforms_to(ancestor_type):
                self.errors.append(INVALID_ANCESTOR % (obj_type.name, ancestor_type.name))
        else:
            ancestor_type = obj_type

        try:
            method = ancestor_type.get_method(node.id)
        except SemanticError as e:
            self.errors.append(e.text)
            for arg in node.args:
                self.visit(arg, scope)
            return ErrorType()

        if len(node.args) + 1 != len(method.param_names):
            self.errors.append(WRONG_SIGNATURE % (method.name, obj_type.name))

        if not obj_type.conforms_to(method.param_types[0]):
            self.errors.append(INCOMPATIBLE_TYPES % (obj_type.name, method.param_types[0].name))

        for i, arg in enumerate(node.args, 1):
            arg_type = self.visit(arg, scope)
            if not arg_type.conforms_to(method.param_types[i]):
                self.errors.append(INCOMPATIBLE_TYPES % (arg_type.name, method.param_types[i].name))

        return method.return_type

    @visitor.when(ast.IntegerNode)
    def visit(self, node: ast.IntegerNode, scope: Scope):
        return IntType()

    @visitor.when(ast.StringNode)
    def visit(self, node: ast.StringNode, scope: Scope):
        return StringType()

    @visitor.when(ast.BooleanNode)
    def visit(self, node: ast.BooleanNode, scope: Scope):
        return BoolType()

    @visitor.when(ast.VariableNode)
    def visit(self, node: ast.VariableNode, scope: Scope):
        variable = scope.find_variable(node.lex)
        if variable is None:
            self.errors.append(VARIABLE_NOT_DEFINED % (node.lex, self.current_method.name))
            return ErrorType()
        return variable.type

    @visitor.when(ast.InstantiateNode)
    def visit(self, node: ast.InstantiateNode, scope: Scope):
        try:
            return self.context.get_type(node.lex)
        except SemanticError as e:
            self.errors.append(e.text)
            return ErrorType()

    @visitor.when(ast.NegationNode)
    def visit(self, node: ast.NegationNode, scope: Scope):
        return self._check_unary_operation(node, scope, 'not', BoolType())

    @visitor.when(ast.ComplementNode)
    def visit(self, node: ast.ComplementNode, scope: Scope):
        return self._check_unary_operation(node, scope, '~', IntType())

    @visitor.when(ast.IsVoidNode)
    def visit(self, node: ast.IsVoidNode, scope: Scope):
        self.visit(node.expr, scope)
        return BoolType()

    @visitor.when(ast.PlusNode)
    def visit(self, node: ast.PlusNode, scope: Scope):
        return self._check_int_binary_operation(node, scope, '+', IntType())

    @visitor.when(ast.MinusNode)
    def visit(self, node: ast.MinusNode, scope: Scope):
        return self._check_int_binary_operation(node, scope, '-', IntType())

    @visitor.when(ast.StarNode)
    def visit(self, node: ast.StarNode, scope: Scope):
        return self._check_int_binary_operation(node, scope, '*', IntType())

    @visitor.when(ast.DivNode)
    def visit(self, node: ast.DivNode, scope: Scope):
        return self._check_int_binary_operation(node, scope, '/', IntType())

    @visitor.when(ast.LessEqualNode)
    def visit(self, node: ast.LessEqualNode, scope: Scope):
        return self._check_int_binary_operation(node, scope, '<=', BoolType())

    @visitor.when(ast.LessThanNode)
    def visit(self, node: ast.LessThanNode, scope: Scope):
        return self._check_int_binary_operation(node, scope, '<', BoolType())

    @visitor.when(ast.EqualNode)
    def visit(self, node: ast.EqualNode, scope: Scope):
        self.visit(node.left, scope)
        self.visit(node.right, scope)
        return BoolType()

    def _check_int_binary_operation(self, node: ast.BinaryNode, scope: Scope, operation: str, return_type: Type):
        left_type = self.visit(node.left, scope)
        right_type = self.visit(node.right, scope)

        if left_type == right_type == IntType():
            return return_type
        self.errors.append(INVALID_BINARY_OPERATION % (operation, left_type.name, right_type.name))
        return ErrorType()

    def _check_unary_operation(self, node: ast.UnaryNode, scope: Scope, operation: str, expected_type: Type):
        typex = self.visit(node.expr, scope)
        if typex == expected_type:
            return typex
        self.errors.append(INVALID_UNARY_OPERATION % (operation, typex.name))
        return ErrorType()


class InferenceTypeChecker:
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
        pass

    @visitor.when(ast.ClassDeclarationNode)
    def visit(self, node: ast.ClassDeclarationNode, scope: Scope):
        pass

    @visitor.when(ast.AttrDeclarationNode)
    def visit(self, node: ast.AttrDeclarationNode, scope: Scope):
        pass

    @visitor.when(ast.MethodDeclarationNode)
    def visit(self, node: ast.MethodDeclarationNode, scope: Scope):
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


class Executor:
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
        pass

    @visitor.when(ast.ClassDeclarationNode)
    def visit(self, node: ast.ClassDeclarationNode, scope: Scope):
        pass

    @visitor.when(ast.AttrDeclarationNode)
    def visit(self, node: ast.AttrDeclarationNode, scope: Scope):
        pass

    @visitor.when(ast.MethodDeclarationNode)
    def visit(self, node: ast.MethodDeclarationNode, scope: Scope):
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
