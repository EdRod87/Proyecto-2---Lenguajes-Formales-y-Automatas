"""
calculadora.py
Proyecto 2 - Lenguajes Formales y Automatas
Analizador sintactico, construccion de AST y evaluacion de expresiones aritmeticas.

Etapas (en el orden que pide el enunciado):
    A. Tokenizacion y validacion sintactica con un Automata de Pila (PDA).
    B. Construccion del Arbol de Sintaxis Abstracta (AST) con Shunting-Yard.
    C. Visualizacion del AST en formato ASCII.
    D. Evaluacion del AST con un recorrido en postorden.

Gramatica Libre de Contexto (GLC) en la que se basa la implementacion:
    E -> E + T | E - T | T
    T -> T * F | T / F | F
    F -> P ^ F | P
    P -> ( E ) | num

Uso por consola:
    python calculadora.py "3 + 5 * 2"
    python calculadora.py            (corre los 7 casos de prueba del enunciado)
"""

import sys


class Pila:
    """Estructura de Pila (LIFO) explicita, usada por el PDA y por Shunting-Yard."""

    def __init__(self):
        self._items = []

    def apilar(self, item):
        """Coloca un elemento en el tope de la pila (push)."""
        self._items.append(item)

    def desapilar(self):
        """Quita y devuelve el elemento del tope (pop). Falla si la pila esta vacia."""
        if self.esta_vacia():
            raise IndexError("Pila vacía")
        return self._items.pop()

    def cima(self):
        """Devuelve el elemento del tope sin quitarlo, o None si esta vacia."""
        return None if self.esta_vacia() else self._items[-1]

    def esta_vacia(self) -> bool:
        """Indica si la pila no tiene elementos."""
        return len(self._items) == 0

    def contenido(self) -> str:
        """Representacion de la pila (fondo -> tope) para mostrar la traza del PDA."""
        return "Z0 " + " ".join(str(x) for x in self._items)


class NodoAST:
    """Nodo del AST. Los nodos internos guardan un operador; las hojas, un numero."""

    def __init__(self, valor, izquierdo=None, derecho=None):
        self.valor = valor
        self.izquierdo = izquierdo
        self.derecho = derecho

    def es_hoja(self) -> bool:
        """Un nodo es hoja cuando no tiene hijos (representa un operando)."""
        return self.izquierdo is None and self.derecho is None


class AnalizadorParte2:
    """Motor de la calculadora: tokenizador, PDA, constructor del AST y evaluador."""

    # Nivel de precedencia de cada operador (mayor numero = se agrupa primero).
    # Corresponde a los niveles de la GLC: E (+,-) < T (*,/) < F (^).
    PRECEDENCIA = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3}
    # La potencia es asociativa a la derecha (F -> P ^ F); el resto, a la izquierda.
    ASOCIATIVIDAD_DER = {'^'}
    NOMBRES_TOKENS = {
        '+': 'TK_SUMA',
        '-': 'TK_RESTA',
        '*': 'TK_MULT',
        '/': 'TK_DIV',
        '^': 'TK_POTENCIA',
        '(': 'TK_PAR_IZQ',
        ')': 'TK_PAR_DER',
    }

    # ------------------------------------------------------------------
    # ETAPA A.1: TOKENIZACION
    # ------------------------------------------------------------------
    @classmethod
    def tokenizar(cls, cadena: str) -> list:
        """
        Recorre la cadena caracter por caracter y devuelve la lista de tokens.
        Cada token es un diccionario con linea, columna, tipo de token y lexema.
        Lanza ValueError si encuentra un caracter que no pertenece al lenguaje.
        """
        tokens = []
        i = 0
        n = len(cadena)
        linea = 1
        col_inicio_linea = 0

        while i < n:
            char = cadena[i]
            if char == '\n':
                linea += 1
                col_inicio_linea = i + 1
                i += 1
                continue
            if char.isspace():
                i += 1
                continue

            columna = (i - col_inicio_linea) + 1

            if char in cls.NOMBRES_TOKENS:
                tokens.append({'linea': linea, 'columna': columna,
                               'token': cls.NOMBRES_TOKENS[char], 'lexema': char})
                i += 1
            elif char.isdigit() or char == '.':
                # Numero entero o decimal: digitos con a lo mas un punto
                inicio = i
                puntos = 0
                while i < n and (cadena[i].isdigit() or cadena[i] == '.'):
                    if cadena[i] == '.':
                        puntos += 1
                        if puntos > 1:
                            raise ValueError(
                                f"Linea {linea}:{columna} -> Número decimal inválido '{cadena[inicio:i+1]}'")
                    i += 1
                lexema = cadena[inicio:i]
                if lexema == '.':
                    raise ValueError(f"Linea {linea}:{columna} -> Punto decimal aislado '.'")
                tokens.append({'linea': linea, 'columna': columna,
                               'token': 'TK_NUMERO', 'lexema': lexema})
            else:
                raise ValueError(f"Linea {linea}:{columna} -> Carácter no válido '{char}'")

        return tokens

    # ------------------------------------------------------------------
    # ETAPA A.2: VALIDACION CON AUTOMATA DE PILA (PDA)
    # ------------------------------------------------------------------
    @classmethod
    def validar_pda(cls, tokens: list) -> list:
        """
        Simula el Automata de Pila que valida la expresion.

        Estados de control:
            q0 = ESPERA_OPERANDO  (al inicio, despues de '(' o de un operador)
            q1 = ESPERA_OPERADOR  (despues de un numero o de ')')
        Pila: inicia con el simbolo de fondo Z0.
            '('  -> apila '('
            ')'  -> desapila '(' (si el tope es Z0 la pila esta desbalanceada)
        Acepta si al terminar la entrada el estado es q1 y la pila solo tiene Z0.

        Devuelve la traza de pasos (estado, simbolo leido, contenido de la pila)
        y lanza SyntaxError con un mensaje claro si la expresion no es valida.
        """
        if not tokens:
            raise SyntaxError("La expresión aritmética está vacía.")

        pila = Pila()
        estado = "q0"  # ESPERA_OPERANDO
        traza = [("q0", "-", pila.contenido())]

        for t in tokens:
            lex = t['lexema']
            pos = f"{t['linea']}:{t['columna']}"

            if lex == '(':
                if estado != "q0":
                    raise SyntaxError(f"Pos {pos} -> Falta un operador antes de '('.")
                pila.apilar('(')
                estado = "q0"
            elif lex == ')':
                # Primero se revisa el tope: si es Z0 no hay '(' que cerrar
                if pila.esta_vacia():
                    raise SyntaxError(
                        f"Pos {pos} -> Tope inválido / desbalance: se leyó ')' "
                        f"pero la pila no tiene '(' (tope = Z0).")
                if estado == "q0":
                    raise SyntaxError(f"Pos {pos} -> Paréntesis vacíos o ')' después de un operador.")
                pila.desapilar()
                estado = "q1"
            elif lex in cls.PRECEDENCIA:
                if estado != "q1":
                    raise SyntaxError(f"Pos {pos} -> Operador mal ubicado '{lex}': se esperaba un número o '('.")
                estado = "q0"
            else:  # numero
                if estado != "q0":
                    raise SyntaxError(f"Pos {pos} -> Falta un operador antes del número '{lex}'.")
                estado = "q1"

            traza.append((estado, lex, pila.contenido()))

        if not pila.esta_vacia():
            raise SyntaxError(
                f"Fin de la entrada -> Paréntesis desbalanceados: falta ')' "
                f"(quedan {len(pila._items)} '(' en la pila).")

        if estado == "q0":
            ultimo = tokens[-1]
            raise SyntaxError(
                f"Pos {ultimo['linea']}:{ultimo['columna']} -> "
                f"La expresión no puede terminar en '{ultimo['lexema']}'.")

        return traza

    # ------------------------------------------------------------------
    # ETAPA B: CONSTRUCCION DEL AST (SHUNTING-YARD)
    # ------------------------------------------------------------------
    @classmethod
    def construir_ast(cls, tokens: list) -> NodoAST:
        """
        Construye el AST con el algoritmo Shunting-Yard de Dijkstra usando dos pilas:
            pila_ops   -> operadores y parentesis pendientes
            pila_nodos -> subarboles ya construidos
        "Reducir" = sacar un operador y dos subarboles y formar un nodo nuevo.
        Antes de apilar un operador se reducen los del tope que tengan mayor
        precedencia, o igual precedencia si el operador es asociativo a la izquierda.
        """
        pila_ops = Pila()
        pila_nodos = Pila()

        def reducir():
            op = pila_ops.desapilar()
            der = pila_nodos.desapilar()
            izq = pila_nodos.desapilar()
            pila_nodos.apilar(NodoAST(op, izq, der))

        for t in tokens:
            lex = t['lexema']
            if t['token'] == 'TK_NUMERO':
                valor = float(lex) if '.' in lex else int(lex)
                pila_nodos.apilar(NodoAST(valor))
            elif lex == '(':
                pila_ops.apilar(lex)
            elif lex == ')':
                while not pila_ops.esta_vacia() and pila_ops.cima() != '(':
                    reducir()
                pila_ops.desapilar()  # quita el '(' correspondiente
            elif lex in cls.PRECEDENCIA:
                while (not pila_ops.esta_vacia() and pila_ops.cima() != '(' and
                       (cls.PRECEDENCIA[pila_ops.cima()] > cls.PRECEDENCIA[lex] or
                        (cls.PRECEDENCIA[pila_ops.cima()] == cls.PRECEDENCIA[lex] and
                         lex not in cls.ASOCIATIVIDAD_DER))):
                    reducir()
                pila_ops.apilar(lex)

        while not pila_ops.esta_vacia():
            reducir()

        return pila_nodos.desapilar()

    # ------------------------------------------------------------------
    # ETAPA C: VISUALIZACION DEL AST
    # ------------------------------------------------------------------
    @classmethod
    def dibujar_ast(cls, nodo: NodoAST, prefijo: str = "", es_ultimo: bool = True,
                    es_raiz: bool = True) -> str:
        """Devuelve el arbol en formato ASCII jerarquico (hijo izquierdo arriba)."""
        if nodo is None:
            return ""
        if es_raiz:
            linea = f" [RAÍZ] --> {nodo.valor}\n"
            nuevo_prefijo = "   "
        else:
            conector = "└── " if es_ultimo else "├── "
            linea = f"{prefijo}{conector}{nodo.valor}\n"
            nuevo_prefijo = prefijo + ("    " if es_ultimo else "│   ")

        if not nodo.es_hoja():
            linea += cls.dibujar_ast(nodo.izquierdo, nuevo_prefijo, False, False)
            linea += cls.dibujar_ast(nodo.derecho, nuevo_prefijo, True, False)
        return linea

    @classmethod
    def recorrido_postorden(cls, nodo: NodoAST, lista=None) -> list:
        """Lista de nodos en postorden (izquierda, derecha, raiz) = notacion polaca inversa."""
        if lista is None:
            lista = []
        if nodo is not None:
            cls.recorrido_postorden(nodo.izquierdo, lista)
            cls.recorrido_postorden(nodo.derecho, lista)
            lista.append(str(nodo.valor))
        return lista

    # ------------------------------------------------------------------
    # ETAPA D: EVALUACION EN POSTORDEN
    # ------------------------------------------------------------------
    @classmethod
    def evaluar_ast(cls, nodo: NodoAST):
        """
        Evalua el AST de abajo hacia arriba: primero ambos hijos, luego el operador.
        Lanza ZeroDivisionError si se intenta dividir entre cero.
        """
        if nodo.es_hoja():
            return nodo.valor

        izq = cls.evaluar_ast(nodo.izquierdo)
        der = cls.evaluar_ast(nodo.derecho)

        op = nodo.valor
        if op == '+':
            return izq + der
        if op == '-':
            return izq - der
        if op == '*':
            return izq * der
        if op == '/':
            if der == 0:
                raise ZeroDivisionError("División entre cero detectada durante la evaluación.")
            return izq / der
        if op == '^':
            return izq ** der
        raise ValueError(f"Operador desconocido: {op}")


# ----------------------------------------------------------------------
# MODO CONSOLA
# ----------------------------------------------------------------------
CASOS_PRUEBA = [
    "3 + 5 * 2",
    "(3 + 5) * 2",
    "2 ^ 3 ^ 2",
    "((4 + 2) * (10 - 5))",
    "(3 + 5 * 2",
    "3 + * 5",
    ")2 + 3(",
]


def formatear(resultado):
    """Muestra 8.0 como 8, y deja los decimales reales como estan."""
    if isinstance(resultado, float) and resultado.is_integer():
        return int(resultado)
    return resultado


def analizar(expresion: str) -> None:
    """Ejecuta las cuatro etapas sobre una expresion e imprime todo en consola."""
    print("=" * 50)
    print(f"Entrada: {expresion}")
    try:
        tokens = AnalizadorParte2.tokenizar(expresion)
        print("Tokens :", " ".join(f"{t['token']}({t['lexema']})" for t in tokens))
        AnalizadorParte2.validar_pda(tokens)
        print("PDA    : Pila balanceada -> expresión VÁLIDA")
        raiz = AnalizadorParte2.construir_ast(tokens)
        print("AST:")
        print(AnalizadorParte2.dibujar_ast(raiz), end="")
        print("Postorden:", " ".join(AnalizadorParte2.recorrido_postorden(raiz)))
        print("Resultado:", formatear(AnalizadorParte2.evaluar_ast(raiz)))
    except SyntaxError as e:
        print(f"ERROR SINTÁCTICO: {e}")
    except ValueError as e:
        print(f"ERROR LÉXICO: {e}")
    except ZeroDivisionError as e:
        print(f"ERROR MATEMÁTICO: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        analizar(" ".join(sys.argv[1:]))
    else:
        for caso in CASOS_PRUEBA:
            analizar(caso)
