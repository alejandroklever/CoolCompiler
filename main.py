from lexer import CoolLexer
from parser import CoolParser
from semantics import (TypeCollector, TypeBuilder, OverriddenMethodChecker, TypeChecker, topological_ordering)
from semantics.formatter import CodeBuilder
from semantics.progam_executor import Executor
from semantics.utils.scope import Context, Scope
from semantics.type_inference import InferenceChecker

program = r"""
class Main inherits IO {
    a: Int;

    main(): IO {{
        let a: Int <- 2 in a;
        
        a <- 2;
        
        new IO;
        
        while true loop
            0
        pool;
        
        case a of
            x: Int => 
                x + 2;n 
            x: String => 
                x.concat(" is a String\n");
        esac;
        
        out_string("Hello, World.\n");
    }};

    fibonacci(n: AUTO_TYPE): Int {
        if n <= 2 
        then 
            0 
        else 
            fibonacci(n - 1) + fibonacci(n - 2) fi
    };
}
"""

inference_program_01 = r"""
class Point {
    a: AUTO_TYPE;
    b: AUTO_TYPE;

    init(x: AUTO_TYPE, y: AUTO_TYPE): AUTO_TYPE {{
        a <- b;
        b <- x + y;
        create_point();
    }};
    
    create_point(): AUTO_TYPE { new Point };
}
"""

inference_program_02 = r"""
class Ackermann {
    ackermann(m: AUTO_TYPE, n: AUTO_TYPE): AUTO_TYPE {
        if m = 0 then n + 1 else
            if n = 0 then ackermann(m - 1, 1) else
                ackermann(m - 1, ackermann(m, n - 1))
            fi
        fi
    };
}
"""

inference_program_03 = r"""
class Main {
    f(a: AUTO_TYPE, b: AUTO_TYPE): AUTO_TYPE {
        if a = 1 then b else
            g(a + 1, b / 1) 
        fi
    };
    
    g(a: AUTO_TYPE, b: AUTO_TYPE): AUTO_TYPE {
        if b = 1 then a else
            f(a / 2, b + 1) 
        fi
    };
}
"""

inference_program_04 = r"""
class Main inherits IO {
    f(a: Int): Int {
        g(a)
    };

    g(a: AUTO_TYPE): Int{
        1
    };
}
"""

hello_world = r"""
class Main inherits IO {
    x : AUTO_TYPE <- 5 + 5;

    main () : IO {{
        out_int(x);
        out_string("\n");
    }};
    
    get_x () : AUTO_TYPE {
        x 
    };
}
"""

lexer = CoolLexer()
parser = CoolParser()

if __name__ == '__main__':
    tokens = lexer(hello_world)
    ast = parser(tokens)

    context = Context()
    errors = []
    scope = Scope()

    TypeCollector(context, errors).visit(ast)
    TypeBuilder(context, errors).visit(ast)
    topological_ordering(ast, context, errors)
    OverriddenMethodChecker(context, errors).visit(ast)
    InferenceChecker(context, errors).visit(ast, scope)
    TypeChecker(context, errors).visit(ast, scope)

    print(CodeBuilder().visit(ast))

    if not errors:
        print()
        Executor(context, errors).visit(ast, Scope())
        print('Program finished...')

    for error in errors:
        print(error)
