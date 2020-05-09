from typing import List

import semantics.astnodes as ast
import semantics.errors as err
import semantics.visitor as visitor
from semantics.scope import Context, Attribute, Method, Type, ErrorType, VariableInfo, Scope, SemanticError


class InferenceTypeChecker:
    def __init__(self, context: Context, errors: List[str] = []):
        self.context: Context = context
        self.errors: List[str] = errors
        self.current_type: Type = None
        self.current_method: Method = None
        self.dependencies = {}

    @visitor.on('node')
    def visit(self, node, tabs):
        pass

    @visitor.when(ast.ProgramNode)
    def visit(self, node: ast.ProgramNode, scope: Scope = None):
        if scope is None:
            scope = Scope()
        for elem in node.declarations:
            self.visit(elem, scope.create_child())
        return InferenceTypeSubstitute(self.context, self.errors).visit(node, scope)

    @visitor.when(ast.ClassDeclarationNode)
    def visit(self, node: ast.ClassDeclarationNode, scope: Scope):
        self.current_type = self.context.get_type(node.id)

        attrs = [feature for feature in node.features if isinstance(feature, ast.AttrDeclarationNode)]
        methods = [feature for feature in node.features if isinstance(feature, ast.MethodDeclarationNode)]

        for attr in attrs:
            self.visit(attr, scope)

        for i, method in enumerate(methods):
            self.visit(method, scope.create_child())

    @visitor.when(ast.AttrDeclarationNode)
    def visit(self, node: ast.AttrDeclarationNode, scope: Scope):
        attr_type = self.context.get_type(node.type)
        var = scope.define_variable(node.id, attr_type)
        if node.expr is not None:
            expr_type = self.visit(node.expr, scope.create_child())
            if attr_type == self.context.get_type('AUTO_TYPE'):
                if isinstance(expr_type, VariableInfo) or isinstance(expr_type, Method):
                    try:
                        self.dependencies[expr_type].append(var)
                    except KeyError:
                        self.dependencies[expr_type] = [var]
                else:
                    self._update_dependencies(var, expr_type)

    @visitor.when(ast.MethodDeclarationNode)
    def visit(self, node: ast.MethodDeclarationNode, scope: Scope):
        self.current_method = self.current_type.get_method(node.id)
        return_type = self.context.get_type(node.return_type)

        scope.define_variable('self', self.current_type)
        for i, (name, expr_body_type) in enumerate(node.params):
            if not scope.is_local(name):
                scope.define_variable(name, self.context.get_type(expr_body_type))

        expr_body_type = self.visit(node.body, scope)
        if return_type == self.context.get_type('AUTO_TYPE'):
            if isinstance(expr_body_type, VariableInfo) or isinstance(expr_body_type, Method):
                try:
                    self.dependencies[expr_body_type].append(self.current_method)
                except KeyError:
                    self.dependencies[expr_body_type] = [self.current_method]
            else:
                self._update_dependencies(self.current_method, expr_body_type)

    @visitor.when(ast.LetNode)
    def visit(self, node: ast.LetNode, scope: Scope):
        for elem in node.declarations:
            self.visit(elem, scope)
        return self.visit(node.expr, scope.create_child())

    @visitor.when(ast.VarDeclarationNode)
    def visit(self, node: ast.VarDeclarationNode, scope: Scope):
        var = scope.define_variable(node.id, self.context.get_type(node.type))

        if node.expr is not None:
            expr_type = self.visit(node.expr, scope)
            if node.type == 'AUTO_TYPE':
                if isinstance(expr_type, VariableInfo) or isinstance(expr_type, Method):
                    try:
                        self.dependencies[expr_type].append(var)
                    except KeyError:
                        self.dependencies[expr_type] = [var]
                else:
                    var.type = expr_type

    @visitor.when(ast.AssignNode)
    def visit(self, node: ast.AssignNode, scope: Scope):
        expr_type = self.visit(node.expr, scope)
        var_info = scope.find_variable(node.id)

        if var_info is not None:
            if var_info.type == self.context.get_type('AUTO_TYPE'):
                if isinstance(expr_type, VariableInfo) or isinstance(expr_type, Method):
                    try:
                        self.dependencies[expr_type].append(var_info)
                    except KeyError:
                        self.dependencies[expr_type] = [var_info]
                else:
                    self._update_dependencies(var_info, expr_type)
            else:
                if isinstance(expr_type, VariableInfo) or isinstance(expr_type, Method):
                    self._update_dependencies(expr_type, var_info.type)

    @visitor.when(ast.BlockNode)
    def visit(self, node: ast.BlockNode, scope: Scope):
        return_type = ErrorType()

        for expr in node.expressions:
            return_type = self.visit(expr, scope.create_child())

        return return_type

    @visitor.when(ast.ConditionalNode)
    def visit(self, node: ast.ConditionalNode, scope: Scope):
        if_type = self.visit(node.if_expr, scope)
        then_type = self.visit(node.then_expr, scope)
        else_type = self.visit(node.else_expr, scope)

        if isinstance(if_type, VariableInfo):
            if_type.type = self.context.get_type('BOOL_TYPE')

        if isinstance(if_type, Method):
            if_type.return_type = self.context.get_type('BOOL_TYPE')

        if isinstance(then_type, VariableInfo) or isinstance(then_type, Method):
            return then_type

        if isinstance(else_type, VariableInfo) or isinstance(else_type, Method):
            return else_type

        return then_type.join(else_type)

    @visitor.when(ast.WhileNode)
    def visit(self, node: ast.WhileNode, scope: Scope):
        condition = self.visit(node.condition, scope)
        if isinstance(condition, VariableInfo) or isinstance(condition, Method):
            self._update_dependencies(condition, self.context.get_type('Bool'))

        self.visit(node.body, scope)
        return self.context.get_type('Object')

    @visitor.when(ast.SwitchCaseNode)
    def visit(self, node: ast.SwitchCaseNode, scope: Scope):
        # TODO: Esta mal la inferencia de tipo, no se esta aplicando el join de los tipos en lo branch del case
        self.visit(node.expr, scope)

        for case in node.cases:
            self.visit(case, scope.create_child())

        return self.context.get_type('Object')

    @visitor.when(ast.CaseNode)
    def visit(self, node: ast.CaseNode, scope: Scope):
        try:
            var = scope.define_variable(node.id, self.context.get_type(node.type))
        except SemanticError:
            var = scope.find_variable('ERROR_TYPE')

        self.visit(node.expr, scope)
        return var.type

    @visitor.when(ast.MethodCallNode)
    def visit(self, node: ast.MethodCallNode, scope: Scope):
        obj_type = self.visit(node.obj, scope)
        if isinstance(obj_type, VariableInfo) or isinstance(obj_type, Method):
            obj_type = self.context.get_type('AUTO_TYPE')

        if node.type is not None:
            try:
                ancestor_type = self.context.get_type(node.type)
            except SemanticError:
                ancestor_type = ErrorType()
        else:
            ancestor_type = obj_type

        try:
            method = ancestor_type.get_method(node.id)
        except SemanticError:
            for arg in node.args:
                self.visit(arg, scope)
            return ErrorType()

        for i, arg in enumerate(node.args, 1):
            arg_type = self.visit(arg, scope)
            if isinstance(arg_type, VariableInfo) or isinstance(arg_type, VariableInfo):
                if method.param_types[i].name != 'AUTO_TYPE':
                    self._update_dependencies(arg_type, method.param_types[i])

        if method.return_type != self.context.get_type('AUTO_TYPE'):
            return method.return_type
        return method

    @visitor.when(ast.IntegerNode)
    def visit(self, node: ast.IntegerNode, scope: Scope):
        return self.context.get_type('Int')

    @visitor.when(ast.StringNode)
    def visit(self, node: ast.StringNode, scope: Scope):
        return self.context.get_type('String')

    @visitor.when(ast.BooleanNode)
    def visit(self, node: ast.BooleanNode, scope: Scope):
        return self.context.get_type('Bool')

    @visitor.when(ast.VariableNode)
    def visit(self, node: ast.VariableNode, scope: Scope):
        try:
            var = scope.find_variable(node.lex)
            if var.type == self.context.get_type('AUTO_TYPE'):
                return var
            return var.type
        except SemanticError:
            return self.context.get_type('ERROR_TYPE')

    @visitor.when(ast.InstantiateNode)
    def visit(self, node: ast.InstantiateNode, scope: Scope):
        try:
            return self.context.get_type(node.lex)
        except SemanticError:
            return self.context.get_type('Object')

    @visitor.when(ast.NegationNode)
    def visit(self, node: ast.NegationNode, scope: Scope):
        a = self.visit(node.expr, scope)
        if isinstance(a, VariableInfo) or isinstance(a, Method):
            self._update_dependencies(a, self.context.get_type('Bool'))

    @visitor.when(ast.ComplementNode)
    def visit(self, node: ast.ComplementNode, scope: Scope):
        a = self.visit(node.expr, scope)
        if isinstance(a, VariableInfo) or isinstance(a, Method):
            self._update_dependencies(a, self.context.get_type('Int'))

    @visitor.when(ast.IsVoidNode)
    def visit(self, node: ast.IsVoidNode, scope: Scope):
        a = self.visit(node.expr, scope)
        return self.context.get_type('BOOL_TYPE')

    @visitor.when(ast.PlusNode)
    def visit(self, node: ast.PlusNode, scope: Scope):
        return self._visit_binary_operation(node, scope, self.context.get_type('Int'))

    @visitor.when(ast.MinusNode)
    def visit(self, node: ast.MinusNode, scope: Scope):
        return self._visit_binary_operation(node, scope, self.context.get_type('Int'))

    @visitor.when(ast.StarNode)
    def visit(self, node: ast.StarNode, scope: Scope):
        return self._visit_binary_operation(node, scope, self.context.get_type('Int'))

    @visitor.when(ast.DivNode)
    def visit(self, node: ast.DivNode, scope: Scope):
        return self._visit_binary_operation(node, scope, self.context.get_type('Int'))

    @visitor.when(ast.LessEqualNode)
    def visit(self, node: ast.LessEqualNode, scope: Scope):
        return self._visit_binary_operation(node, scope, self.context.get_type('Bool'))

    @visitor.when(ast.LessThanNode)
    def visit(self, node: ast.LessThanNode, scope: Scope):
        return self._visit_binary_operation(node, scope, self.context.get_type('Bool'))

    @visitor.when(ast.EqualNode)
    def visit(self, node: ast.EqualNode, scope: Scope):
        self.visit(node.left, scope)
        self.visit(node.right, scope)
        return self.context.get_type('Bool')

    def _visit_binary_operation(self, node: ast.BinaryNode, scope: Scope, return_type: Type):
        left_type = self.visit(node.left, scope)
        right_type = self.visit(node.right, scope)
        if isinstance(left_type, VariableInfo) or isinstance(left_type, VariableInfo):
            self._update_dependencies(left_type, self.context.get_type('Int'))
        if isinstance(right_type, VariableInfo) or isinstance(right_type, VariableInfo):
            self._update_dependencies(right_type, self.context.get_type('Int'))
        return return_type

    def _update_dependencies(self, info, typex):
        try:
            stack = self.dependencies[info] + [info]
            self.dependencies[info] = []
        except KeyError:
            stack = [info]

        visited = set(stack)
        while stack:
            item = stack.pop()
            if isinstance(item, VariableInfo):
                item.type = typex if item.type.name == 'AUTO_TYPE' else item.type.join(typex)
            else:
                item.return_type = typex if item.return_type.name == 'AUTO_TYPE' else item.return_type.join(typex)

            try:
                Q2 = self.dependencies[item]
                self.dependencies[item] = []
                for item2 in Q2:
                    if item2 not in visited:
                        stack.append(item2)
                        visited.add(item2)
            except KeyError:
                continue


class InferenceTypeSubstitute:
    def __init__(self, context: Context, errors: List[str] = []):
        self.context: Context = context
        self.errors: List[str] = errors
        self.current_type: Type = None
        self.current_method: Method = None
        self.dependencies = {}

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
            var = scope.find_variable(name)
            if var.type == self.context.get_type('AUTO_TYPE'):
                self.errors.append(err.INFERENCE_ERROR_ATTRIBUTE % name)
            node.params[i] = (name, var.type.name)
            self.current_method.param_types[i + 1] = var.type

        self.visit(node.body, scope)

        if return_type == self.context.get_type('AUTO_TYPE'):
            if self.current_method.return_type == self.context.get_type('AUTO_TYPE'):
                self.errors.append(err.INFERENCE_ERROR_ATTRIBUTE % node.id)
            node.return_type = self.current_method.return_type.name

    @visitor.when(ast.LetNode)
    def visit(self, node: ast.LetNode, scope: Scope):
        scope_child = scope.children[0]

        for elem in node.declarations:
            self.visit(elem, scope)

        self.visit(node.expr, scope_child)

    @visitor.when(ast.VarDeclarationNode)
    def visit(self, node: ast.VarDeclarationNode, scope: Scope):
        var = scope.find_variable(node.id)

        if node.expr is not None:
            self.visit(node.expr, scope)

        if node.type == 'AUTO_TYPE':
            if var.type == self.context.get_type('AUTO_TYPE'):
                self.errors.append(err.INFERENCE_ERROR_ATTRIBUTE % node.id)
            node.type = var.type.name

    @visitor.when(ast.AssignNode)
    def visit(self, node: ast.AssignNode, scope: Scope):
        self.visit(node.expr, scope)

    @visitor.when(ast.BlockNode)
    def visit(self, node: ast.BlockNode, scope: Scope):
        for i, expr in enumerate(node.expressions):
            self.visit(expr, scope.children[i])

    @visitor.when(ast.ConditionalNode)
    def visit(self, node: ast.ConditionalNode, scope: Scope):
        self.visit(node.if_expr, scope)
        self.visit(node.then_expr, scope)
        self.visit(node.else_expr, scope)

    @visitor.when(ast.WhileNode)
    def visit(self, node: ast.WhileNode, scope: Scope):
        self.visit(node.condition, scope)
        self.visit(node.body, scope)

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
