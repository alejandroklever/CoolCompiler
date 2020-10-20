import sys
from typing import List

import typer
from pathlib import Path

from lexertab import CoolLexer
from parsertab import CoolParser
from semantics import TypeCollector, TypeBuilder, OverriddenMethodChecker, TypeChecker, topological_ordering
from semantics.formatter import CodeBuilder
from semantics.execution import Executor, ExecutionError
from semantics.type_inference import InferenceChecker
from semantics.utils.scope import Context, Scope

app = typer.Typer()


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


def tokenize(file: str, verbose: bool = False):
    path = Path.cwd() / file
    s = path.open('r').read()
    lexer = CoolLexer()
    tokens = lexer(s)

    if lexer.contain_errors:
        for e in lexer.errors:
            typer.echo(e, err=True)

    if verbose:
        for t in tokens:
            typer.echo(t)

    return tokens, lexer


def parse(file: str, verbose: bool = False):
    tokens, lexer = tokenize(file, verbose)

    if lexer.contain_errors:
        return None, None

    parser = CoolParser(verbose)
    ast = parser(tokens)

    if parser.contains_errors:
        for e in parser.errors:
            typer.echo(e, err=True)

    return ast, parser


@app.command()
def infer(file: str, verbose: bool = False):
    ast, _ = parse(file, verbose)

    if ast is not None:
        ast, scope, context, errors = check_semantics(ast, Scope(), Context(), [])
        if errors:
            for e in errors:
                typer.echo(e, err=True)
        typer.echo(CodeBuilder().visit(ast, 0))


@app.command()
def run(file: str, verbose: bool = False):
    ast, parser = parse(file, verbose)

    if ast is not None:
        ast, scope, context, errors = check_semantics(ast, Scope(), Context(), [])

        if not errors and not parser.contains_errors:
            try:
                Executor(context).visit(ast, Scope())
                typer.echo('Program finished...')
            except ExecutionError as e:
                typer.echo(e.text, err=True)

        for error in errors:
            typer.echo(error, err=True)


if __name__ == '__main__':
    app()
