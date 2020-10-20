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


def test_inference_programs():
    inference_testing_programs = []
    inference_testing_results = []

    cwd = Path.cwd()
    path = cwd / 'inference' if str(cwd).endswith('tests') else cwd / 'tests' / 'inference'
    for path in sorted(path.iterdir()):
        s = path.open('r').read()
        if 'program' in path.name:
            inference_testing_programs.append(s)
        else:
            inference_testing_results.append(s)

    for code, result in zip(inference_testing_programs, inference_testing_results):
        tokens, _ = tokenize(code)
        ast, _ = parse(tokens)
        ast, scope, context, errors = check_semantics(ast, Scope(), Context(), [])
        assert not errors and CodeBuilder().visit(ast, 0) == result


def test_errors_in_programs():
    errors_testing_programs = []
    errors_testing_results = []

    cwd = Path.cwd()
    path = cwd / 'syntactic_and_semantic_errors' if str(cwd).endswith('tests') else cwd / 'tests' / 'syntactic_and_semantic_errors'
    for path in sorted(path.iterdir()):
        s = path.open('r').read()
        if 'program' in path.name:
            errors_testing_programs.append(s)
        else:
            errors_testing_results.append(s)

    for code, result in zip(errors_testing_programs, errors_testing_results):
        tokens, _ = tokenize(code)
        ast, parser = parse(tokens)
        ast, _, _, errors = check_semantics(ast, Scope(), Context(), [])
        assert '\n'.join(parser.errors + errors) == result


if __name__ == '__main__':
    pass

    # if not syntactic_and_semantic_errors and not parser.contains_errors:
    #     try:
    #         Executor(context).visit(ast, Scope())
    #         print('Program finished...')
    #     except ExecutionError as e:
    #         sys.stderr.write(e.text + '\n')
    #
    # for error in syntactic_and_semantic_errors:
    #     sys.stderr.write(error + '\n')
