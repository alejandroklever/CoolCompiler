# Interprete de Cool

# Manual de Desarrollo 

## Flujo de Trabajo:

- El archivo `astnodes.py` contiene los nodes del ast de cool, fue renombrado asi para no entrar en conflicto con la libreria `ast` de python
- Todo cambio realizado en la gramatica o al lexer se hara en el archivo `definitions.py`. Para probar si al hacer cambios en la gramatica esta sigue sin dar conflicto tansolo debemos correr el script de la siguiente forma `python3 definitions.py`
- Si ha ocurrido algun cambio significativo en la gramatica o el lexer, ya sea agragar una nueva produccion, terminal, o una nueva expresion regular, se debe recompilar este paquete. Para esta ultima accion tenemos el archivo `build.py`, para correrlo basta con hacer `python3 build.py` y este creara dos archivos nuevo `parser.py` y `lexer.py` que contendran el parser y el lexer de cool serializado con las modificaciones realizadas para no tener que construir el parser cada vez que probemos el programa.
- Al paquete `cmp` se le ha agregado un nuevo subpaquete `serializer`, que contiene tanto al serializador del parser como del lexer.
- Para probar programas tan solo escribalo en un archivo `.cool` en la carpeta `scripts/`  y ejecutar el comando en la terminal `python3 test.py <command> <file-name>`, por ejemplo `python3 test.py tokenize program.cool` o `python3 test.py parse program.cool`