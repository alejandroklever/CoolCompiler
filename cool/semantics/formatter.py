import cool.semantics.utils.astnodes as ast
import cool.semantics.visitor as visitor


class CodeBuilder:
    @visitor.on('node')
    def visit(self, node, tabs):
        pass

    @visitor.when(ast.ProgramNode)
    def visit(self, node: ast.ProgramNode, tabs: int = 0):
        return '\n\n'.join(self.visit(child, tabs) for child in node.declarations)

    @visitor.when(ast.ClassDeclarationNode)
    def visit(self, node: ast.ClassDeclarationNode, tabs: int = 0):
        parent = '' if node.parent is None else f"inherits {node.parent} "
        return (f'class {node.id} {parent}{{\n' +
                '\n\n'.join(self.visit(child, tabs + 1) for child in node.features) +
                '\n}')

    @visitor.when(ast.AttrDeclarationNode)
    def visit(self, node: ast.AttrDeclarationNode, tabs: int = 0):
        expr = f' <- {self.visit(node.expr, 0)}' if node.expr is not None else ''
        return '    ' * tabs + f'{node.id}: {node.type}{expr};'

    @visitor.when(ast.MethodDeclarationNode)
    def visit(self, node: ast.MethodDeclarationNode, tabs: int = 0):
        params = ', '.join(': '.join(param) for param in node.params)
        ans = '    ' * tabs + f'{node.id} ({params}): {node.return_type}'
        body = self.visit(node.body, tabs + 1)
        return f'{ans} {{\n{body}\n    }};'

    @visitor.when(ast.LetNode)
    def visit(self, node: ast.LetNode, tabs: int = 0):
        declarations = []
        for _id, _type, _expr in node.declarations:
            if _expr is not None:
                declarations.append(f'{_id}: {_type} <- {self.visit(_expr)}')
            else:
                declarations.append(f'{_id} : {_type}')
        declarations = (',\n' + '    ' * (tabs + 1)).join(declarations)
        return '    ' * tabs + f'let {declarations} in\n{self.visit(node.expr, tabs + 1)}'

    @visitor.when(ast.AssignNode)
    def visit(self, node: ast.AssignNode, tabs: int = 0):
        return '    ' * tabs + f'{node.id} <- {self.visit(node.expr)}'

    @visitor.when(ast.BlockNode)
    def visit(self, node: ast.BlockNode, tabs: int = 0):
        body = ';\n'.join(self.visit(child, tabs + 1) for child in node.expressions)
        return '    ' * tabs + f'{{\n{body};\n' + '    ' * tabs + '}'

    @visitor.when(ast.ConditionalNode)
    def visit(self, node: ast.ConditionalNode, tabs: int = 0):
        ifx = self.visit(node.if_expr)
        then = self.visit(node.then_expr, tabs + 1)
        elsex = self.visit(node.else_expr, tabs + 1)

        return ('    ' * tabs + f'if {ifx}\n' +
                '    ' * tabs + f'then\n{then}\n' +
                '    ' * tabs + f'else\n{elsex}\n' +
                '    ' * tabs + 'fi')

    @visitor.when(ast.WhileNode)
    def visit(self, node: ast.WhileNode, tabs: int = 0):
        condition = self.visit(node.condition, 0)
        body = self.visit(node.body, tabs + 1)

        return '    ' * tabs + f'while {condition} loop\n {body}\n' + '    ' * tabs + 'pool'

    @visitor.when(ast.SwitchCaseNode)
    def visit(self, node: ast.SwitchCaseNode, tabs: int = 0):
        cases = []
        for _id, _type, _expr in node.cases:
            expr = self.visit(_expr, tabs + 2)
            cases.append('    ' * (tabs + 1) + f'{_id} : {_type} =>\n{expr};')
        expr = self.visit(node.expr)
        cases = '\n'.join(cases)

        return '    ' * tabs + f'case {expr} of\n{cases}\n' + '    ' * tabs + 'esac'

    @visitor.when(ast.MethodCallNode)
    def visit(self, node: ast.MethodCallNode, tabs: int = 0):
        obj = f'{self.visit(node.obj, 0)}.' if node.obj is not None else ''
        return '    ' * tabs + f'{obj}{node.id}({", ".join(self.visit(arg, 0) for arg in node.args)})'

    @visitor.when(ast.BinaryNode)
    def visit(self, node: ast.BinaryNode, tabs: int = 0):
        left = self.visit(node.left) if isinstance(node.left, ast.BinaryNode) else self.visit(node.left, tabs)
        right = self.visit(node.right)
        return f'{left} {node.operation} {right}'

    @visitor.when(ast.AtomicNode)
    def visit(self, node: ast.AtomicNode, tabs: int = 0):
        lex = node.lex
        return '    ' * tabs + f'{lex}'

    @visitor.when(ast.InstantiateNode)
    def visit(self, node: ast.InstantiateNode, tabs: int = 0):
        return '    ' * tabs + f'(new {node.lex})'


class Formatter:
    @visitor.on('node')
    def visit(self, node, tabs):
        pass

    @visitor.when(ast.ProgramNode)
    def visit(self, node: ast.ProgramNode, tabs: int = 0):
        ans = '    ' * tabs + f'\\__ProgramNode [<class> ... <class>]'
        statements = '\n'.join(self.visit(child, tabs + 1) for child in node.declarations)
        return f'{ans}\n{statements}'

    @visitor.when(ast.ClassDeclarationNode)
    def visit(self, node: ast.ClassDeclarationNode, tabs: int = 0):
        parent = '' if node.parent is None else f": {node.parent}"
        ans = '    ' * tabs + f'\\__ClassDeclarationNode: class {node.id} {parent} {{ <feature> ... <feature> }}'
        features = '\n'.join(self.visit(child, tabs + 1) for child in node.features)
        return f'{ans}\n{features}'

    @visitor.when(ast.AttrDeclarationNode)
    def visit(self, node: ast.AttrDeclarationNode, tabs: int = 0):
        ans = '    ' * tabs + f'\\__AttrDeclarationNode: {node.id} : {node.type}'
        return f'{ans}'

    @visitor.when(ast.MethodDeclarationNode)
    def visit(self, node: ast.MethodDeclarationNode, tabs: int = 0):
        params = ', '.join(':'.join(param) for param in node.params)
        ans = '    ' * tabs + f'\\__FuncDeclarationNode: {node.id}({params}) : {node.return_type} -> <body>'
        body = self.visit(node.body, tabs + 1)
        return f'{ans}\n{body}'

    @visitor.when(ast.LetNode)
    def visit(self, node: ast.LetNode, tabs: int = 0):
        declarations = []
        for _id, _type, _expr in node.declarations:
            if _expr is not None:
                declarations.append('    ' * tabs + f'\\__VarDeclarationNode: {_id}: {_type} <-\n{self.visit(_expr, tabs + 1)}')
            else:
                declarations.append('    ' * tabs + f'\\__VarDeclarationNode: {_id} : {_type}')

        declarations = '\n'.join(declarations)
        ans = '    ' * tabs + f'\\__LetNode:  let'
        expr = self.visit(node.expr, tabs + 2)
        return f'{ans}\n {declarations}\n' + '    ' * (tabs + 1) + 'in\n' + f'{expr}'

    @visitor.when(ast.AssignNode)
    def visit(self, node: ast.AssignNode, tabs: int = 0):
        ans = '    ' * tabs + f'\\__AssignNode: {node.id} <- <expr>'
        expr = self.visit(node.expr, tabs + 1)
        return f'{ans}\n{expr}'

    @visitor.when(ast.BlockNode)
    def visit(self, node: ast.BlockNode, tabs: int = 0):
        ans = '    ' * tabs + f'\\__BlockNode:'
        body = '\n'.join(self.visit(child, tabs + 1) for child in node.expressions)
        return f'{ans}\n{body}'

    @visitor.when(ast.ConditionalNode)
    def visit(self, node: ast.ConditionalNode, tabs: int = 0):
        ifx = self.visit(node.if_expr, tabs + 2)
        then = self.visit(node.then_expr, tabs + 2)
        elsex = self.visit(node.else_expr, tabs + 2)

        return '\n'.join([
            '    ' * tabs + f'\\__IfThenElseNode: if <expr> then <expr> else <expr> fi',
            '    ' * (tabs + 1) + f'\\__if \n{ifx}',
            '    ' * (tabs + 1) + f'\\__then \n{then}',
            '    ' * (tabs + 1) + f'\\__else \n{elsex}',
        ])

    @visitor.when(ast.WhileNode)
    def visit(self, node: ast.WhileNode, tabs: int = 0):
        condition = self.visit(node.condition, tabs + 2)
        body = self.visit(node.body, tabs + 2)

        return '\n'.join([
            '    ' * tabs + f'\\__WhileNode: while <expr> loop <expr> pool',
            '    ' * (tabs + 1) + f'\\__while \n{condition}',
            '    ' * (tabs + 1) + f'\\__loop \n{body}',
        ])

    @visitor.when(ast.SwitchCaseNode)
    def visit(self, node: ast.SwitchCaseNode, tabs: int = 0):
        cases = []
        for _id, _type, _expr in node.cases:
            expr = self.visit(_expr, tabs + 3)
            cases.append('    ' * tabs + f'\\__CaseNode: {_id} : {_type} =>\n{expr}')
        expr = self.visit(node.expr, tabs + 2)
        cases = '\n'.join(cases)

        return '\n'.join([
            '    ' * tabs + f'\\__SwitchCaseNode: case <expr> of [<case> ... <case>] esac',
            '    ' * (tabs + 1) + f'\\__case \n{expr} of',
        ]) + '\n' + cases

    @visitor.when(ast.MethodCallNode)
    def visit(self, node: ast.MethodCallNode, tabs: int = 0):
        obj = self.visit(node.obj, tabs + 1)
        ans = '    ' * tabs + f'\\__CallNode: <obj>.{node.id}(<expr>, ..., <expr>)'
        args = '\n'.join(self.visit(arg, tabs + 1) for arg in node.args)
        return f'{ans}\n{obj}\n{args}'

    @visitor.when(ast.BinaryNode)
    def visit(self, node: ast.BinaryNode, tabs: int = 0):
        ans = '    ' * tabs + f'\\__<expr> {node.__class__.__name__} <expr>'
        left = self.visit(node.left, tabs + 1)
        right = self.visit(node.right, tabs + 1)
        return f'{ans}\n{left}\n{right}'

    @visitor.when(ast.AtomicNode)
    def visit(self, node: ast.AtomicNode, tabs: int = 0):
        return '    ' * tabs + f'\\__ {node.__class__.__name__}: {node.lex}'

    @visitor.when(ast.InstantiateNode)
    def visit(self, node: ast.InstantiateNode, tabs: int = 0):
        return '    ' * tabs + f'\\__ InstantiateNode: new {node.lex}()'
