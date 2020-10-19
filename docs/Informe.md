<div style="text-align: center;">

# Segundo Proyecto de Programacion

## Inferencia de tipos en el lenguaje de programacion *COOL*, una aproximacion a traves de grafos

</div>

## Indice

- 1 Inferencia de tipos.
  - 1.1 Algoritmo y Grafo de Dependecias.
  - 1.2 Nodos de Dependencia.
  - 1.3 Casos factibles.
    - 1.3.1 Ejemplos de casos Factibles para la Inferencia.
  - 1.4 Casos No factibles.
    - 1.4.1 Casos Generales.
    - 1.4.2 Casos Particulares.
  - 1.5 Expresiones atomicas.

## 1 Inferencia de Tipos

COOL es un lenguaje de programacion estaticamente tipado, y aunque el lenguaje no presenta inferencia de tipos esta es una caracteristica muy util que incorporaremos en un nuestro interprete.

Nuestro algoritmo de inferencia de tipos se apoya en el uso basico de la teoria de grafos y en el uso del patron de diseno visitor.

La inferencia de tipos de nuestro proyecto detecta para cada atributo, variable, parametro de funcion o retorno de funcion el primer tipo que le puede ser asignado, modificando en el arbol de sintaxis abstracta el string `AUTO_TYPE` por el nombre del tipo correspondiente y asignando los tipos correspondientes en el contexto y el ambito en que seon declarados.

### 1.1 Algoritmo y Grafo de Dependecias

***Entrada :*** Un arbol de sintaxis abstracta, un contexto con todos los tipos declarados en el programa de COOL.

***Salida :*** Un Arbol de Sintaxis Abstracta, Un Contexto y un Scope con tipos bien tagueados.

***Algoritmo :*** Durante el recorrido del AST sera construido un grafo dirigido cuyos nodos encerraran el concepto de las expresiones marcadas como `AUTO_TYPE` y las aristas representan las dependencias entre las expresiones de estos nodos para inferir su tipo. Sea `E1` una expresion cuyo tipo estatico es marcado como `AUTO_TYPE`, y sea `E2` una expresion a partir de a cual se puede inferir el tipo de estatico de E1 entonces en el grafo existira la arista `<E2, E1>`. Una vez construido el arbol se comenzara una cadena de expansion de tipos estaticos de la forma `E1, E2, ..., En` donde `Ej` se infiere de `Ei` con `1 < j = i + 1 <= n` y `E1` es una expresion con tipo estatico definido, al cual llamaremos atomo. Cuando todos los atomos se hayan propagado a traves del grafo los nodos que no hayan podido ser resueltos seran marcados como tipos `Object` al ser esta la clase mas general del lenguaje.

### 1.2 Nodos de Dependencia

Cada nodo del grafo sera una abstraccion de un concepto en el que se use un tagueo explicito de `AUTO_TYPE` y tendra las referencias a las partes del proceso de semantica del programa, ademas de que cada nodo contara con un metodo `update(type)` el cual actualiza el tipo estatico de estos conceptos.

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

### 1.3 Casos factibles

Funcionando de manera analoga para atributos, variables, parametros y retorno de funciones. Explicado de forma recursiva puede ser visto como:

- Un `AUTO_TYPE` sera sustituido por su tipo correspodiente si este forma parte de una operacion que permita saber su tipo, o es asignado a una expresion de la cual es posible determinar su tipo.

- Es importante senalar en que contexto estas dependencias son tomadas en cuenta:

  - Para los atributos marcados como autotype su tipo podra ser determinado dentro del cuerpo de cualquiera de las funciones de la clase o si es detectable el tipo de la expresion de inicializacion.

  - Para las variables su tipo sera determinado dentro del scope donde estas son validas.

- Para los parametros su tipo sera determinado dentro del cuerpo de la funcion o cuando esta sea funcion sea llamada a traves de una operacion de dispatch.

- Para los retornos de funciones, su tipo sera determinado con su expresion y los llamados a dicha funcion a traves de una operacion de dispatch.

- En las expresiones if-then-else o case-of asignan automaticamente el tipo `Object` por el momento debido a la complejidad que supone la operacion `join` en el los case y en las clausulas then-else.

### 1.3.1 Ejemplos de casos Factibles para la Inferencia

En este caso la expresion `d + 1` desambigua a `d` en un `Int` y luego `c` se infiere de `d`, `b` se infiere de `c`, `a` se infiere de `b` y el retorno de la funcion de infiere de `a`. Quedando todos los parametros y el retorno de la funcion marcados como `Int`.

```typescript
class Main {
    function(a: AUTO_TYPE, b: AUTO_TYPE, c: AUTO_TYPE, d: AUTO_TYPE): AUTO_TYPE {
        {
            a <- b;
            b <- c;
            c <- d;
            d <- a;
            d + 1;
            a;
        }
    };
}
```

Similar al caso anterior pero enesta ocacion incluyendo atributos, la expresion los `x + y` infiere a los parametros `x` y `y` como `Int` y tambien al atributo `b`, `a` se infiere de `b`. El tipo de retorno de `create_point()` se infiere de su porpia cuerpo con la expression `new Point` y esta a su vez infiere el tipo de retorno de `init()`.

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

Probando con funciones recursivas tenemos el caso de fibonacci tipo de `n` se infiere al ser usado en las expresiones `n <= 2`, `n - 1`, `n - 2`, las cuales lo marcan como `Int`, `fibonacci(n - 1) + fibonacci(n - 2)` marca al retorno de la funcion como `Int` y y la expresion if-then-else lo marca como `Object`. en este ultimo caso la expresion `fibonacci(n - 1) + fibonacci(n - 2)` termina de analizarse primero que la expresion if-then-else por lo cual el tipo de retorno sera `Int` el cual fue el primero que se definio, lo cual demuestra que el orden en el que se analizan las inferencias importan de las inferencias importan.

```typescript
class Main {
    fibonacci(n: AUTO_TYPE): AUTO_TYPE {
        if n <= 2 then 1 else fibonacci(n - 1) + fibonacci(n - 2) fi
    };
}
```

El caso de Ackerman es bastante interesante, en nuestro algoritmo importa el orden en el que fueron definidas las dependencias. `m` y `n` son inferibles como `Int` a partir de las expresiones `n + 1` y `m - 1` respectivamente, y el tipo de retorno de `ackermann` en inferible por `n` al ser usado como segundo parametro en un llamado de si mismo, por lo cual sera `Int`. La influencia de la expresion if-then-else se ve anulada por el orden de inferencia.

```typescript
class Main {
    ackermann(m: AUTO_TYPE, n: AUTO_TYPE): AUTO_TYPE {
        if m = 0 then n + 1 else
            if n = 0 then ackermann(m - 1, 1) else
                ackermann(m - 1, ackermann(m, n - 1))
            fi
        fi
    };
}
```

### 2.4 Casos No factibles

No es posible determinar el tipo de una variable, atributo, parametro, o retorno de funcion si para este se cumple el caso general y su caso especifico correspondiente.

### 2.4.1 Casos generales

El tipo es utilizado en expresiones que no permiten determinar su tipo, o solo se logra determinar que poseen el mismo tipo que otras variables, atributos, parametros o retorno de funciones de las cuales tampoco se puede determinar el mismo.

```typescript
class Main {
    b: AUTO_TYPE;
    c: AUTO_TYPE;

    function(a: AUTO_TYPE, d: AUTO_TYPE): AUTO_TYPE {
        {
            b <- a;
            d <- c;
            f(a);
        }
    };

    factorial(n: AUTO_TYPE): AUTO_TYPE {
        if n = 1 then 1 else n * factorial(n - 1) fi
    };
}
```

En este ejemplo solo es posible inferir el typo del parametro `n` de la funcion `factorial`, su tipo de retorno, el parametro `a` de la funcion `function`, su tipo de retorno y el atributo `b` de la clase `Main`, el resto sera marcado como `Object`.

### 2.4.2 Casos Particulares

***Para variables:*** si estas no son utilizadas en el ambito en que son marcadas como `Object`.

```typescript
class Main inherits IO {
    function(): Int {
        let a:AUTOTYPE, b:AUTO_TYPE in {
            1;
        }
    };
}
```

***Para parametros:*** si dentro del cuerpo de la funcion estas no son utilizadas y no existe otra funcion que llame a esta con argumentos con tipado estatico definidos seran marcadas como `Object`:

```typescript
class Main inherits IO {
    f(a: AUTO_TYPE): Int{
        1
    };
}
```

***Para atributos:*** si no es posible determinar el tipo de la expresion de inicializacion o si dentro del cuerpo de todas las funciones de su clase correspondiente este no son utilizadas, seran marcadas como `Objects`.

```typescript
class Main inherits IO {

    b: AUTO_TYPE <- c;
    c: AUTO_TYPE <- b;

    f(a: AUTO_TYPE): AUTO_TYPE{
        if a < 3 then 1 else f(a - 1) + f(a - 2) fi
    };
}
```

***Para el retorno de funciones:*** si no es posible determinar el tipo de su expresion.

```typescript
class Main inherits IO {
    f(a: Int): AUTO_TYPE{
        if a<3 then a else f(a-3) fi
    };
}
```

### 2.5 Expresiones atomicas

- Valores Constantes.

- Operaciones aritmeticas.

- Operaciones logicas.

- Llamdos a funciones con valor de retorno conocido.

- Instancias de clases.

- Variables de las cuales se conoce su tipo.

- Bloques donde se puede determinar el tipo de la ultima expresion.
