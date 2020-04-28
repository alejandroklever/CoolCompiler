# Interprete de Cool

# Manual de Desarrollo 

## Flujo de Trabajo:

- El archivo `astnodes.py` contiene los nodos del ast de cool, fue renombrado asi para no entrar en conflicto con la libreria `ast` de python

- Todo cambio realizado en la gramatica o al lexer se hara en el archivo `grammar.py`. Para probar si al hacer cambios en la gramatica esta sigue sin dar conflicto tansolo debemos correr el script de la siguiente forma `python3 grammar.py`

- Si ha ocurrido algun cambio significativo en la gramatica o el lexer, ya sea agragar una nueva produccion, terminal, o una nueva expresion regular, se debe ejecutar este modulo. Para esta ultima accion tenemos el archivo `grammar.py`, para correrlo basta con hacer `python3 grammar.py` y este creara dos archivos nuevo `parser.py` y `lexer.py` que contendran el parser y el lexer de cool serializado con las modificaciones realizadas para no tener que construir el parser cada vez que probemos el programa.

- Al paquete `cmp` se le han hecho varias modificaciones:

    - Se han eliminado todos los archivos y clases innecesarios para el proceso de parsing y lexing.
    
    - El archivo `lexing.py` contiene las clases `Token` y `Lexer`.
    
    - El archivo `parsing.py` contiene los metodos y funciones necesarios para el proceso de creacion de los parser SLR, LR(1), LALR(1). Se han hecho varias mejoras al proceso de de creacion de los parsers.
    
    - El archivo `pycompiler.py` se mantine con las definiciones de la gramatica, y se ha modificado para que casi todo sea manejado desde la clase `Grammar` (Tanto la creacion del lexer como el parser)
    
    - El archivo `serialization.py` contiene los serializers de las tablas de lexer y parsing.
    
    - El archivo `utils.py` contiene la clase `ContainerSet` (Posible eliminacion)
    
- Para probar programas tan solo escribalo en un archivo `.cl` en la carpeta `scripts/`  y ejecutar el comando en la terminal `python3 test.py <command> <file-name>`, por ejemplo `python3 test.py tokenize program.cl` o `python3 test.py parse program.cl`

- En el archivo `main.py` hay un pipeline de como es el proceso completo.
