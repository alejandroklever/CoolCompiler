# Cool Interpreter for compiling class Type Inference

La inferencia de tipos de nuestro proyecto detecta para cada atributo variable 
o retorno de funcion el primer tipo que le puede ser asignado,
cambiando en el arbol de sintaxis abstracta el string AUTO_TYPE por
el nombre del tipo correspondiente.

## Casos factibles:


Funcionamdo de manera analoga, tanto para atributos, varibales, parametros 
y retorno de funciones. Explicado de forma recursiva puede ser visto como:

Un AUTO_TYPE sera sustituido por su tipo correspodiente si este forma 
parte de una operacion que permita saber su tipo; o es asignado a 
una expresion de la cual es posible determinar su tipo.
 
Es importante senalar en que contexto estas dependencias son tomadas en cuenta:
 
 - Para los atributos marcados como autotype su tipo podra ser determinado dentro del cuerpo de cualquiera de las funciones de la clase o si es detectable el tipo de la expresion de inicializacion.
 
 - Para las variables su tipo sera determinado dentro del scope donde estas
 son validas.
 
 . Para los parametros, su tipo sera determinado solo dentro del cuerpo de la funcion.
 
 . Para los retornos de funciones, su tipo sera determinado con su expresion y los llamados a dicha 
 funcion.
 
 Ejemplos de casos Factibles para la Inferencia:
 -
 
 ```text
class Main inherits IO {
    function(a: AUTO_TYPE, b: AUTO_TYPE, c: AUTO_TYPE, d: AUTO_TYPE): AUTO_TYPE {
        { 
            a<-b;
            b<-c;
            c<-d;
            d<-a;
            d+1;
            if a< 10 then a else b fi;
        } 
    };
}
```
 
 ```text
class Main inherits IO {   
    function(a: AUTO_TYPE): AUTO_TYPE {
        { 
            if a< 10 then f(a) else f(b) fi;
        } 
    };
    
    f(a :AUTO_TYPE): AUTO_TYPE{
    if a<3 then 1 else f(a-1) + f(a-2) fi 
    };
}
```

```text
class Main inherits IO {

    b: AUTO_TYPE; 
    c: AUTO_TYPE <-"1"; 
    d: AUTO_TYPE;
    function(a: AUTO_TYPE): AUTO_TYPE {
        { 
            b<-a;
            d+1;
            if a< 10 then f(a) else f(b) fi;
        } 
    };
    
    f(a: AUTO_TYPE): AUTO_TYPE{
    if a<3 then 1 else f(a-1) + f(a-2) fi 
    };
}
```
 Casos No factibles:
 -
 No es posible determinar el tipo de una variable, atributo, parametro,
 o retorno de funcion si para este se cumple el Caso general y su caso 
 especifico correspondiente.
 
 Caso general:
 -
 
 El tipo es utilizado en expresiones que no permiten determinar su tipo,
 o solo se logra determinar que poseen el mismo tipo que otras variables, 
 atributos, parametros o retorno de funciones de las cuales tampoco se 
 puede determinar el mismo.
 
 ```text
class Main inherits IO {

    b: AUTO_TYPE; 
    c: AUTO_TYPE; 
    function(a: AUTO_TYPE, d: AUTO_TYPE): AUTO_TYPE {
        { 
            b<-a;
            d<-c;
            f(a);
        } 
    };
    
    f(a: AUTO_TYPE): AUTO_TYPE{
    if a<3 then 1 else f(a-1) fi 
    };
}
```
En este ejemplo solo es posible inferir el typo del parametro 'a' de la 
funcion f.

 Casos Particulares:
 -
 . Para variables: si estas no son utilizadas en el ambito en que son validas.
 ```text
class Main inherits IO {
    function(): int {
        let a:AUTOTYPE, b:AUTO_TYPE in {
            1;
        } 
    };
}
```
 
 . Para argumentos: si dentro del cuerpo de la funcion estas no son utilizadas. 
 ```text
class Main inherits IO {
    function(a: Int): Int {
        f(a)
    };
    
    f(a: AUTO_TYPE): Int{
    1 
    };
}
```
 
 . Para atributos: si no es posible determinar el tipo de la expresion de 
 inicializacion o si dentro del cuerpo de todas las funciones de su clase
 correspondiente este no son utilizadas.
 ```text
class Main inherits IO {

    b: AUTO_TYPE <- c; 
    c: AUTO_TYPE <- b; 
    
    f(a: AUTO_TYPE): AUTO_TYPE{
    if a<3 then 1 else f(a-1) + f(a-2) fi 
    };
}
```
 
 . Para el retorno de funciones: si no es posible determinar el tipo de su expresion.
 ```text
class Main inherits IO {
    f(a: Int): AUTO_TYPE{
    if a<3 then a else f(a-3) fi 
    };
}
```
 
 Expresiones de las cuales es posible determinar su tipo:
 -
 
 .Valores Constantes.
 
 .Operaciones aritmeticas.
 
 .Operaciones logicas.
 
 .Llamdos a funciones con valor de retorno conocido.
 
 .Instancias de clases.
 
 .Variables de las cuales se conoce su tipo.
 
 .Bloques donde se puede determinar el tipo de la ultima expresion.
 