<center>

# Segundo Proyecto de Programacion

## Inferencia de tipos en el lenguaje de programacion *COOL*, una aproximacion a traves de grafos

</center>

El lenguaje de programacion COOL es un lenguaje de programacion estaticamente tipado, y aunque el lenguaje no presenta inferencia de tipos esta es una caracteristica muy util que incorporaremos en un nuestro interprete.

Nuestro algoritmo de inferencia de tipos se apoya en el uso basico de la teoria de grafos y en el uso del patron de diseno visitor.

La inferencia de tipos de nuestro proyecto detecta para cada atributo, variable, parametro de funcion o retorno de funcion el primer tipo que le puede ser asignado, modificando en el arbol de sintaxis abstracta el string `AUTO_TYPE` por el nombre del tipo correspondiente y asignando los tipos correspondientes en el contexto y el ambito en que seon declarados.

### El algoritmo

***Entrada :*** Un arbol de sintaxis abstracta, un contexto con todos los tipos declarados en el programa de COOL.

***Salida :*** Un Arbol de Sintaxis Abstracta, Un Contexto y un Scope con tipos bien tagueados.

***Algoritmo :*** Durante el recorrido del AST sera construido un grafo dirigido cuyos nodo encerraran el concepto de las expresiones marcadas com `AUTO_TYPE` y las aristas representan las dependencias entre las expresiones de estos nodos para inferir su tipo. Sea E1 una expresion cuyo tipo estatico es marcado como AUTO_TYPE, y sea E2 una expresion a partir de a cual se puede inferir el tipo de estatico de E1 entonces en el grafo existira la arista <E1, E2>. Una vez construido el arbol Se comenzara una cadena de expansion de tipos estaticos de la forma E1, E2, ..., En donde Ej se infiere de Ei con `1 < j = i + 1 <= n` y E1 es una expresion con tipo estatico definido, al cual llamaremos atomo. Cuando todos los atomos se hayan propagado a traves del grafo los nodos que no hayan podido ser resueltos seran marcados como tipos `Object` al ser esta la clase mas general del lenguaje.

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

```csharp
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

```csharp
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

```csharp
class Main inherits IO {
    function(a: AUTO_TYPE): AUTO_TYPE {
        if a < 10 then f(a) else f(b) fi;
    };

    f(a :AUTO_TYPE): AUTO_TYPE{
        if a < 3 then 1 else f(a - 1) + f(a - 2) fi
    };
}
```

```csharp
class Main inherits IO {

    b: AUTO_TYPE;
    c: AUTO_TYPE <- "1";
    d: AUTO_TYPE;

    function(a: AUTO_TYPE): AUTO_TYPE {
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

```csharp
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

No es posible determinar el tipo de una variable, atributo, parametro, o retorno de funcion si para este se cumple el Caso general y su caso especifico correspondiente. En caso de no poderse determinar el tipo por defecto sera tagueado como `AUTO_TYPE`.

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

En este ejemplo solo es posible inferir el typo del parametro `a` de la funcion `f`, el resto sera marcado como `Object`.

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

#### Expresiones de las cuales es posible determinar su tipo

- Valores Constantes.

- Operaciones aritmeticas.

- Operaciones logicas.

- Llamdos a funciones con valor de retorno conocido.

- Instancias de clases.

- Variables de las cuales se conoce su tipo.

- Bloques donde se puede determinar el tipo de la ultima expresion.
