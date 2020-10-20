from pathlib import Path
from typing import List

from lexertab import CoolLexer
from parsertab import CoolParser
from semantics import TypeCollector, TypeBuilder, OverriddenMethodChecker, TypeChecker, topological_ordering
from semantics.formatter import CodeBuilder
from semantics.type_inference import InferenceChecker
from semantics.utils.scope import Context, Scope


def tokenize(code):
    lexer = CoolLexer()
    tokens = lexer(code)
    return tokens, lexer


def parse(tokens):
    parser = CoolParser()
    ast = parser(tokens)
    return ast, parser


def check_semantics(ast, scope: Scope, context: Context, errors: List[str]):
    TypeCollector(context, errors).visit(ast)
    TypeBuilder(context, errors).visit(ast)
    declarations = ast.declarations
    topological_ordering(ast, context, errors)
    ast.declarations = declarations
    OverriddenMethodChecker(context, errors).visit(ast)
    InferenceChecker(context, errors).visit(ast, scope)
    TypeChecker(context, errors).visit(ast, scope)
    return ast, scope, context, errors


def test_inference():
    paths = []
    programs = []
    results = []

    cwd = Path.cwd()
    folder_name = 'inference'
    path = cwd / folder_name if str(cwd).endswith('tests') else cwd / 'tests' / folder_name
    for path in sorted(path.iterdir()):
        s = path.open('r').read()
        if 'program' in path.name:
            programs.append(s)
            paths.append(path.name)
        else:
            results.append(s)

    for path, code, result in zip(paths, programs, results):
        tokens, _ = tokenize(code)
        ast, _ = parse(tokens)
        ast, scope, context, errors = check_semantics(ast, Scope(), Context(), [])
        assert not errors and CodeBuilder().visit(ast, 0) == result


def test_syntactic_and_semantic_errors():
    paths = []
    programs = []
    results = []

    cwd = Path.cwd()
    folder_name = 'syntactic_and_semantic_errors'
    path = cwd / folder_name if str(cwd).endswith('tests') else cwd / 'tests' / folder_name
    for path in sorted(path.iterdir()):
        s = path.open('r').read()
        if path.name.endswith('.cl'):
            programs.append(s)
            paths.append(path.name)
        else:
            results.append(s)

    for path, code, result in zip(paths, programs, results):
        tokens, _ = tokenize(code)
        ast, parser = parse(tokens)
        ast, _, _, errors = check_semantics(ast, Scope(), Context(), [])
        assert '\n'.join(parser.errors + errors) == result, path


def test_lexicographic_errors():
    paths = []
    programs = []
    results = []

    cwd = Path.cwd()
    folder_name = 'lexicographic_errors'
    path = cwd / folder_name if str(cwd).endswith('tests') else cwd / 'tests' / folder_name
    for path in sorted(path.iterdir())[:2 * 2]:
        s = path.open('r').read()
        if path.name.endswith('.cl'):
            programs.append(s)
            paths.append(path.name)
        else:
            results.append(s)

    for path, code, result in zip(paths, programs, results):
        tokens, lexer = tokenize(code)
        assert lexer.contain_errors and '\n'.join(lexer.errors) == result.strip(), path
