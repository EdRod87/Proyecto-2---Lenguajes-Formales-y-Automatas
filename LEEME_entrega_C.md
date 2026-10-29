# Entrega de B a C: autómatas para el lexer

## Contenido

| Archivo | Para qué sirve |
|---|---|
| `tabla_transicion_completo.csv` | Tabla del AFD combinado (18 estados, q0 inicial). `-` = sin transición. Columnas `acepta` y `token` para los estados finales |
| `clases_caracteres.csv` | Qué caracteres pertenecen a cada columna de la tabla |
| `palabras_reservadas.csv` | Tabla de búsqueda para `int`, `if`, `while` |
| `casos_por_afd.csv` | Cadenas que cada AFD acepta o rechaza, con el resultado esperado |
| `pruebas/*.txt` y `*.esperado` | Programas de entrada y la salida exacta que debe producir el lexer |
| `../afd/*.jff` | Diseño de cada AFD (referencia) |

## Reglas de ejecución

1. **Estado inicial:** q0. Para cada carácter se calcula su clase (ver `clases_caracteres.csv`) y se consulta la tabla.
2. **Longest match:** seguir leyendo mientras haya transición. Cada vez que se llega a un estado con `acepta = si`, guardar (posición, token). Al quedarse sin transición, volver a la última posición guardada y emitir ese token.
3. **Estados que no aceptan:** q3 (`3.` sin dígito después) y q15 (`/` sola). Si el lexer termina ahí, retrocede al último estado de aceptación. Ejemplo: `3.` produce `3` (entero) y luego error en `.`.
4. **Sin ningún estado de aceptación:** desde q0 no hay transición para el carácter. Es un error léxico: reportarlo con línea y columna, avanzar un carácter y continuar.
5. **Palabras reservadas:** si el token es `TK_IDENTIFICADOR`, buscar el lexema completo en `palabras_reservadas.csv`. Si está, cambiar el token. `intx`, `integer`, `If` siguen siendo identificadores (distingue mayúsculas).
6. **Tokens que se reconocen pero no se emiten:** `TK_ESPACIO` y `TK_COMENTARIO`. Sí deben actualizar línea y columna.
7. **Salto de línea:** clase propia `SALTO_LINEA`. Dentro de un comentario no tiene transición (termina el comentario) y en `TK_ESPACIO` sí. Después de un salto, línea += 1 y columna = 1.
8. **Mayúsculas y minúsculas:** `While` no es palabra reservada.

## Formato de salida esperado

Una línea por token, separada por tabuladores: `linea:columna  TOKEN  lexema`. Líneas y columnas empiezan en 1. Los errores usan el token `ERROR_LEXICO` y el lexema entre comillas simples.

```
1:1	TK_RES_INT	int
1:5	TK_IDENTIFICADOR	a
1:11	ERROR_LEXICO	'@'
```

## Aclaraciones

- En los `.jff`, el símbolo `#` representa espacio o tabulador. Es solo una convención de JFLAP. En el código real son la clase `ESPACIO`, y un `#` literal debe tratarse como `OTRO` (error fuera de comentarios).
- No existen en el lenguaje: `<=`, `>`, `*`, `/`, `!`. Un `<=` se lee como `<` seguido de `=`.
- Si agregan un token nuevo, hay que actualizar el AFD, una columna o fila de la tabla, y `casos_por_afd.csv`.
