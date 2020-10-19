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


# execution_program_01 = r"""
# class A { }
#
# class B inherits A { }
#
# class C inherits A { }
#
# class Main inherits IO {
#     number: Int <- 5;
#
#     main () : Object {
#         0
#     };
#
#     testing_case() : IO {
#         let a: A <- new C in
#             case a of
#                 x: B => out_string("Is type B.\n");
#                 x: C => out_string("Is type C.\n");
#             esac
#     };
#
#     testing_fibonacci(n: Int) : IO {{
#         out_string("Iterative Fibonacci : ");
#         out_int(iterative_fibonacci(5));
#         out_string("\n");
#
#         out_string("Recursive Fibonacci : ");
#         out_int(recursive_fibonacci(5));
#         out_string("\n");
#     }};
#
#     recursive_fibonacci (n: AUTO_TYPE) : AUTO_TYPE {
#         if n <= 2 then 1 else recursive_fibonacci(n - 1) + recursive_fibonacci(n - 2) fi
#     };
#
#     iterative_fibonacci(n: AUTO_TYPE) : AUTO_TYPE {
#         let  i: Int <- 2, n1: Int <- 1, n2: Int <- 1, temp: Int in {
#             while i < n loop
#                 let temp: Int <- n2 in {
#                     n2 <- n2 + n1;
#                     n1 <- temp;
#                     i <- i + 1;
#                 }
#             pool;
#             n2;
#         }
#     };
# }
# """
#
# syntactic_errors = """
# class Main {
#     a: Int
#
#     b: String
#
#     main () : Object { let a: Int <- "" in 0 }
#
#     errors() : Object {
#         case a of
#             x: Int => (new IO).out_int(x)
#             y: String => (new IO).out_string(x)
#         esac
#     }
# }
# """

# lexer = CoolLexer()
# parser = CoolParser()

app = typer.Typer()


def check_semantics(ast, scope: Scope, context: Context, errors: List[str]):
    TypeCollector(context, errors).visit(ast)
    TypeBuilder(context, errors).visit(ast)
    topological_ordering(ast, context, errors)
    OverriddenMethodChecker(context, errors).visit(ast)
    InferenceChecker(context, errors).visit(ast, scope)
    TypeChecker(context, errors).visit(ast, scope)
    return ast, scope, context, errors


@app.command()
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

    return tokens


@app.command()
def parse(file: str, verbose: bool = False):
    tokens = tokenize(file, verbose)
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
                print('Program finished...')
            except ExecutionError as e:
                sys.stderr.write(e.text + '\n')

        for error in errors:
            sys.stderr.write(error + '\n')


if __name__ == '__main__':
    app()
