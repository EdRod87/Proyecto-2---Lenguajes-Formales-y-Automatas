# Proyecto 2 – Calculadora algebraica (Analizador Sintáctico, AST y Evaluación)

**Asignatura:** Lenguajes Formales y Autómatas
**Tema:** Autómatas de Pila, Gramáticas Libres de Contexto y Análisis Sintáctico

**Integrantes:**

- Elden Eduardo Gil Soto 164123
- Diego Alejandro Federico Afre Reyes 1594422
- Edgar Eduardo Rodas López 1629924
- Anthony Rafael Arriola Dominguez 1639523

## Descripción

Programa que recibe una expresión aritmética, valida su sintaxis y el balanceo de paréntesis con un **autómata de pila (PDA)**, construye su **Árbol de Sintaxis Abstracta (AST)**, lo muestra en formato ASCII y lo **evalúa con un recorrido en postorden**.

Operadores aceptados, de mayor a menor precedencia:

| Operador | Significado               | Asociatividad |
| -------- | ------------------------- | ------------- |
| `( )`    | Agrupación                | —             |
| `^`      | Potencia                  | Derecha       |
| `*` `/`  | Multiplicación y división | Izquierda     |
| `+` `-`  | Suma y resta              | Izquierda     |

Los operandos pueden ser enteros o decimales (`3`, `2.5`).

## Requisitos

- Python 3.8 o superior
- `tkinter` (viene incluido en Python para Windows y macOS; en Linux: `sudo apt install python3-tk`)

No se necesitan librerías externas.

## Cómo ejecutar

### Interfaz gráfica

```bash
python Interfaz.py
```

1. Escribe una expresión en el panel **SYSTEM.IN** o usa **Cargar .txt** para abrir un archivo de la carpeta `pruebas/`.
2. Presiona **PARTE 2: Calcular AST**.
3. Verás:
   - **DATA_STREAM:** la tabla de tokens.
   - **AST_VISUALIZER:** el árbol, el recorrido en postorden y la traza del autómata de pila.
   - **RESULTADO:** el valor final o el tipo de error.
   - **KERNEL_LOGS:** cada etapa ejecutada y los mensajes de error.

### Consola

```bash
python calculadora.py "3 + 5 * 2"   # evalúa una expresión
python calculadora.py               # corre los 7 casos de prueba del enunciado
```

## Estructura del proyecto

| Archivo / carpeta | Contenido                                                                                                                 |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `calculadora.py`  | Lógica de la Parte 2: `Pila`, `NodoAST` y `AnalizadorParte2` (tokenizador, PDA, Shunting-Yard, dibujo ASCII y evaluación) |
| `Interfaz.py`     | Interfaz gráfica (tkinter) que une la Parte 1 y la Parte 2                                                                |
| `programa.py`     | Analizador léxico de la Parte 1 (botón "Ejecutar Lexer")                                                                  |
| `pruebas/`        | Un archivo `.txt` por cada caso de prueba                                                                                 |
| `parte1_lexer/`   | Tablas y pruebas del analizador léxico (Proyecto 1)                                                                       |

## Gramática utilizada

```
E → E + T | E - T | T
T → T * F | T / F | F
F → P ^ F | P
P → ( E ) | num
```

## Casos de prueba

| Entrada                | Resultado esperado | Pila / Balanceo            | Estado           |
| ---------------------- | ------------------ | -------------------------- | ---------------- |
| `3 + 5 * 2`            | 13                 | Correcto                   | Válida           |
| `(3 + 5) * 2`          | 16                 | Correcto                   | Válida           |
| `2 ^ 3 ^ 2`            | 512                | Correcto                   | Válida           |
| `((4 + 2) * (10 - 5))` | 30                 | Correcto                   | Válida           |
| `(3 + 5 * 2`           | N/A                | Falta `)`                  | Error sintáctico |
| `3 + * 5`              | N/A                | Correcto                   | Error sintáctico |
| `)2 + 3(`              | N/A                | Tope inválido / desbalance | Error sintáctico |

Casos extra: `pruebas/extra_decimales.txt` (decimales) y `pruebas/extra_div_cero.txt` (división entre cero).
