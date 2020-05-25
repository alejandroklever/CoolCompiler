<div style="text-align: center;">

# Segundo Proyecto de Programacion

## Inferencia de tipos en el lenguaje de programacion *COOL*, una aproximacion a traves de grafos

</div>

## Indice

- 0 Estructura del proyecto.
- 1 Analisis Lexicografico y Sintactico.
  - 1.1 Generador de lexers y parsers LR "PyJapt".
  - 1.2 Manejo de errores lexicograficos y sintacticos.
- 2 Inferencia de tipos.
  - 2.1 Grafo de dependencias.
  - 2.2 Casos factibles.
- 3 Ejecucion.

## 1 Analisis Lexicografico y Sintactico

### 1.1 Generador de lexers y parsers LR "PyJapt"

PyJapt es un generador de lexer y parser desarrolado por los autores del proyecto que pretende dar una solucion no solo a la creacion de estas piezas del proceso de compilacion, sino tambien permitir una interfaz de manejo de errores sintacticos y lexicograficos personalizados. Para su construccion nos hemos basado en las construcciones realizadas en las clases practicas y nos hemos inspirado en otros generadores de parser para las nuevas funcionalidades como yacc, bison, ply y antlr por ejemplo.

PyJapt gira alrededor del concepto de gramatica.

Para definir los no terminales de la gramatiga utilizamos el metodo `add_non_terminal()` de la clase `Grammar`.

```python
from pyjapt.grammar import Grammar

G = Grammar()

expr = G.add_non_terminal('expr', start_symbol=True)
term = G.add_non_terminal('term')
fact = G.add_non_terminal('fact')
```

Para definir los terminales de nuestra gramatica usaremos el metodo `add_terminal()` de la clase `Grammar`. Este metodo recibe como primer parametro el nombre del no terminal y como parametro opcional una expresion regular para el analizador lexicografico. En caso de el segundo parametro no se provea la expresion regular sera el nombre literal del terminal.

```python
plus = G.add_terminals('+')
minus = G.add_terminals('-')
star = G.add_terminals('*')
div = G.add_terminals('/')

num = G.add_terminal('int', regex=r'\d+')
```

Si tenemos un conjunto de terminales cuya expression regular coincide con su propio nombre podemos encapsularlos con las expression`add_terminals()` de la clase `Grammar`

```python
plus, minus, star, div = G.add_terminals('+ - * /')
num = G.add_terminal('int', regex=r'\d+')
```

Puede darse el caso tambien de que querramos aplicar una regla cuando un terminal especifico sea encontrado, para esto PyJapt nos brinda el decorador de funciones `terminal()` de la clase `Grammar` que recibe el nombre y la expresion regular del terminal. La funcion decorada debe recibir como parametro uan referencia al lexer para poder modificar parametros tales como la fila y la columna de los terminales o la posicion de lectura del parser y retornar un `Token`, en caso de no retornar este token sera ignorado.

```python
@G.terminal('int', r'\d+')
def id_terminal(lexer):
    lexer.column += len(lexer.token.lex)
    lexer.position += len(lexer.token.lex)
    lexer.token.lex = int(lexer.token.lex)
    return lexer.token
```

Tambien podemos usar esta forma de definicion de terminales para saltarnos ciertos caracteres o tokens.

```python
##################
# Ignored Tokens #
##################
@G.terminal('newline', r'\n+')
def newline(lexer):
    lexer.lineno += len(lexer.token.lex)
    lexer.position += len(lexer.token.lex)
    lexer.column = 1


@G.terminal('whitespace', r' +')
def whitespace(lexer):
    lexer.column += len(lexer.token.lex)
    lexer.position += len(lexer.token.lex)


@G.terminal('tabulation', r'\t+')
def tab(lexer):
    lexer.column += 4 * len(lexer.token.lex)
    lexer.position += len(lexer.token.lex)
```

Para definir las producciones de nuestra gramatica podemos usar una forma attributada o no atributada:

```python
# Esta es una gramatica no atributada usando las variable previamente declaradas
expr %= expr + plus + term
expr %= expr + minus + term
expr %= term

term %= term + star + fact
term %= term + div + fact
term %= fact

fact %= num

# Un poco mas sencillo...
# Cada simbolo del string de la produccion debe estar separado por un espacio en blanco
expr %= 'expr + term'
expr %= 'expr - term'
expr %= 'term'

term %= 'term * factor'
term %= 'term / factor'
term %= 'fact'

fact %= 'int'

# Esta es una gramatica atributada
expr %= 'expr + term', lambda s: s[1] + s[3]
expr %= 'expr - term', lambda s: s[1] + s[3]
expr %= 'term', lambda s: s[1]

term %= 'term * factor', lambda s: s[1] + s[3]
term %= 'term / factor', lambda s: s[1] + s[3]
term %= 'fact', lambda s: s[1]

fact %= 'int', lambda s: int(s[1])

# Tambien podemos atributar una funcion para definir una regla semantica
# Esta funcion debe recibir como parametro `s` que es una referencia a una
# lista con las reglas semanticas de cada simbolo de la produccion.
# Para separar el simbolo de la cabecera del cuerpo de la expresion
# usamos como segundo simbolo `->`
@G.production('expr -> expr + term')
def expr_prod(s):
    print('Estas sumando una expresion y un termino ;)')
    return s[1] + s[3]
```

### 1.2 Manejo de errores lexicograficos y sintacticos

Una parte importante del proceso de parsing es manejar los errores. Para esto podemos hacer el parser a mano e insertar el reporte de errores, ya que los las tecnicas como `Panic Recovery Mode` la cual implementa `PyJapt` solo permiten que no se detenga la ejecucion de nuestro parser, para dar reportes de errores especificos `PyJapt` ofrece la creacion de producciones erroneas y para reportar errores comunes en un lenguaje de programacion como la falta de un `;` un operador desconocido etc. para esto nuestra gramatica debe activar el flag de terminal de error.

```python
G.add_terminal_error() # Agrega el terminal de error a la gramatica.

# Ejemplo de una posible produccion de error
@G.production("instruction -> let id = expr error")
def attribute_error(s):
    # Con esta linea reportamos el mensaje del error
    # Como la regla semantica de s[5] es el propio token (por ser un terminal) entonces tenemos acceso
    # a su lexema, tipo de token, line y columna.
    s.error(f"{s[5].line, s[5].column} - SyntacticError: Expected ';' instead of '{s[5].lex}'")

    # Con esta linea permitimos que se siga creando una nodo del ast para
    # poder detectar errores semanticos a pesar de haber errores sintacticos
    return LetInstruction(s[2], s[4])
```

## 2 Inferencia de Tipos

COOL es un lenguaje de programacion estaticamente tipado, y aunque el lenguaje no presenta inferencia de tipos esta es una caracteristica muy util que incorporaremos en un nuestro interprete.

Nuestro algoritmo de inferencia de tipos se apoya en el uso basico de la teoria de grafos y en el uso del patron de diseno visitor.

La inferencia de tipos de nuestro proyecto detecta para cada atributo, variable, parametro de funcion o retorno de funcion el primer tipo que le puede ser asignado, modificando en el arbol de sintaxis abstracta el string `AUTO_TYPE` por el nombre del tipo correspondiente y asignando los tipos correspondientes en el contexto y el ambito en que seon declarados.

### El algoritmo

***Entrada :*** Un arbol de sintaxis abstracta, un contexto con todos los tipos declarados en el programa de COOL.

***Salida :*** Un Arbol de Sintaxis Abstracta, Un Contexto y un Scope con tipos bien tagueados.

***Algoritmo :*** Durante el recorrido del AST sera construido un grafo dirigido cuyos nodos encerraran el concepto de las expresiones marcadas como `AUTO_TYPE` y las aristas representan las dependencias entre las expresiones de estos nodos para inferir su tipo. Sea `E1` una expresion cuyo tipo estatico es marcado como `AUTO_TYPE`, y sea `E2` una expresion a partir de a cual se puede inferir el tipo de estatico de E1 entonces en el grafo existira la arista `<E2, E1>`. Una vez construido el arbol se comenzara una cadena de expansion de tipos estaticos de la forma `E1, E2, ..., En` donde `Ej` se infiere de `Ei` con `1 < j = i + 1 <= n` y `E1` es una expresion con tipo estatico definido, al cual llamaremos atomo. Cuando todos los atomos se hayan propagado a traves del grafo los nodos que no hayan podido ser resueltos seran marcados como tipos `Object` al ser esta la clase mas general del lenguaje.

### Sistemas de nodos

Cada nodo del grafo sera una abstraccion de un concepto en el que se use un tagueo explicito de `AUTO_TYPE` y tendra las referencias a las partes del proceso de semantica del programa, ademas de que cada nodo contara con un metodo `update(type)` el cual actualiza el tipo estatico de estos conceptos.

### Jerarquia de nodos

```python
class DependencyNode:
    pass

class AtomNode(DependencyNode):
    """Nodo base el cual es creado a partir de expresiones que
    contienen tipo estatico u operaciones aritmeticas"""
    pass

class AttributeNode(DependencyNode):
    """Atributo de una clase"""
    pass

class ParameterNode(DependencyNode):
    """Parametro de una funcion"""
    pass

class ReturnTypeNode(DependencyNode):
    """Tipo de retorno de una funcion"""
    pass

class VariableInfoNode(DependencyNode):
    """Variables declaradas en el scope."""
    pass
```

### Casos factibles

Funcionando de manera analoga para atributos, variables, parametros y retorno de funciones. Explicado de forma recursiva puede ser visto como:

- Un `AUTO_TYPE` sera sustituido por su tipo correspodiente si este forma parte de una operacion que permita saber su tipo, o es asignado a una expresion de la cual es posible determinar su tipo.

- Es importante senalar en que contexto estas dependencias son tomadas en cuenta:

  - Para los atributos marcados como autotype su tipo podra ser determinado dentro del cuerpo de cualquiera de las funciones de la clase o si es detectable el tipo de la expresion de inicializacion.

  - Para las variables su tipo sera determinado dentro del scope donde estas son validas.

- Para los parametros su tipo sera determinado dentro del cuerpo de la funcion o cuando esta sea funcion sea llamada a traves de una operacion de dispatch.

- Para los retornos de funciones, su tipo sera determinado con su expresion y los llamados a dicha funcion a traves de una operacion de dispatch.

### Ejemplos de casos Factibles para la Inferencia

```typescript
class Main inherits IO {
    function(a: AUTO_TYPE, b: AUTO_TYPE, c: AUTO_TYPE, d: AUTO_TYPE): AUTO_TYPE {
        {
            a <- b;
            b <- c;
            c <- d;
            d <- a;
            d + 1;
            if a < 10 then a else b fi;
        }
    };
}
```

```typescript
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
```

```typescript
class Main inherits IO {
    g(a: AUTO_TYPE): AUTO_TYPE {
        if a < 10 then f(a) else f(b) fi;
    };

    f(a :AUTO_TYPE): AUTO_TYPE{
        if a < 3 then 1 else f(a - 1) + f(a - 2) fi
    };
}
```

```typescript
class Main inherits IO {

    b: AUTO_TYPE;
    c: AUTO_TYPE <- "1";
    d: AUTO_TYPE;

    g(a: AUTO_TYPE): AUTO_TYPE {
        {
            b <- a;
            d + 1;
            if a < 10 then f(a) else f(b) fi;
        }
    };

    f(a: AUTO_TYPE): AUTO_TYPE {
        if a < 3 then 1 else f(a - 1) + f(a - 2) fi
    };
}
```

```typescript
class Ackermann {
    ackermann(m: AUTO_TYPE, n: AUTO_TYPE): AUTO_TYPE {
        if m = 0 then n + 1 else
            if n = 0 then ackermann(m - 1, 1) else
                ackermann(m - 1, ackermann(m, n - 1))
            fi
        fi
    };
}
```

### Casos No factibles

No es posible determinar el tipo de una variable, atributo, parametro, o retorno de funcion si para este se cumple el caso general y su caso especifico correspondiente.

### Caso general

El tipo es utilizado en expresiones que no permiten determinar su tipo, o solo se logra determinar que poseen el mismo tipo que otras variables, atributos, parametros o retorno de funciones de las cuales tampoco se puede determinar el mismo.

```csharp
class Main inherits IO {
    b: AUTO_TYPE;
    c: AUTO_TYPE;

    function(a: AUTO_TYPE, d: AUTO_TYPE): AUTO_TYPE {
        {
            b <- a;
            d <- c;
            f(a);
        }
    };

    f(a: AUTO_TYPE): AUTO_TYPE {
        if a < 3 then 1 else f(a - 1) fi
    };
}
```

En este ejemplo solo es posible inferir el typo del parametro `a` de la funcion `f` y el atributo `b`, el resto sera marcado como `Object`.

### Casos Particulares

***Para variables:*** si estas no son utilizadas en el ambito en que son marcadas como `Object`.

```csharp
class Main inherits IO {
    function(): Int {
        let a:AUTOTYPE, b:AUTO_TYPE in {
            1;
        }
    };
}
```

***Para parametros:*** si dentro del cuerpo de la funcion estas no son utilizadas y no existe otra funcion que llame a esta con argumetnos con tipado estatico definidos seran marcadas como `Object`:

```csharp
class Main inherits IO {
    f(a: AUTO_TYPE): Int{
        1
    };
}
```

***Para atributos:*** si no es posible determinar el tipo de la expresion de inicializacion o si dentro del cuerpo de todas las funciones de su clase correspondiente este no son utilizadas, seran marcadas como `Objects`.

```csharp
class Main inherits IO {

    b: AUTO_TYPE <- c;
    c: AUTO_TYPE <- b;

    f(a: AUTO_TYPE): AUTO_TYPE{
        if a < 3 then 1 else f(a - 1) + f(a - 2) fi
    };
}
```

***Para el retorno de funciones:*** si no es posible determinar el tipo de su expresion.

```csharp
class Main inherits IO {
    f(a: Int): AUTO_TYPE{
        if a<3 then a else f(a-3) fi
    };
}
```

#### Expresiones atomicas

- Valores Constantes.

- Operaciones aritmeticas.

- Operaciones logicas.

- Llamdos a funciones con valor de retorno conocido.

- Instancias de clases.

- Variables de las cuales se conoce su tipo.

- Bloques donde se puede determinar el tipo de la ultima expresion.

## 3 Ejecucion
