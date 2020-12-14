from pathlib import Path
from typing import List, Tuple

from cool import check_semantics, CoolLexer, CoolParser
from cool.semantics import CodeBuilder
from cool.semantics.utils.scope import Context, Scope


def tokenize(code):
    lexer = CoolLexer()
    tokens = lexer(code)
    return tokens, lexer


def parse(tokens):
    parser = CoolParser()
    ast = parser(tokens)
    return ast, parser


def get_programs(folder_name: str) -> Tuple[List[str], List[str]]:
    programs = []
    results = []

    cwd = Path.cwd()
    path = cwd / folder_name if str(cwd).endswith('tests') else cwd / 'tests' / folder_name
    for path in sorted(path.iterdir()):
        s = path.open('r').read()
        if path.name.endswith('.cl'):
            programs.append(s)
        else:
            results.append(s)

    return programs, results


def test_lexer():
    programs, results = get_programs('lexer')

    for program, result in zip(programs, results):
        tokens, lexer = tokenize(program)
        assert lexer.contain_errors and '\n'.join(lexer.errors) == result.strip()


def test_parser():
    programs, results = get_programs('parser')

    for code, result in zip(programs, results):
        tokens, _ = tokenize(code)
        ast, parser = parse(tokens)
        assert parser.contains_errors and '\n'.join(parser.errors) == result


def test_inference():
    programs, results = get_programs('inference')

    for program, result in zip(programs, results):
        tokens, _ = tokenize(program)
        ast, _ = parse(tokens)
        ast, _, _, errors = check_semantics(ast, Scope(), Context(), [])
        assert not errors and CodeBuilder().visit(ast, 0) == result


def test_semantic():
    programs, results = get_programs('semantic')

    for code, result in zip(programs, results):
        tokens, _ = tokenize(code)
        ast, parser = parse(tokens)
        ast, _, _, errors = check_semantics(ast, Scope(), Context(), [])
        assert (parser.contains_errors or errors) and '\n'.join(parser.errors + errors) == result


test_inference()
