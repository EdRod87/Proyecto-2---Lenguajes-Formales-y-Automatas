import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

# Intentamos importar programa.py (Parte 1)
try:
    import programa  # Analizador léxico de la Parte 1
except ImportError:
    programa = None


# Parte 2: Autómata de Pila (PDA), construcción del AST y evaluación
from calculadora import AnalizadorParte2


# ==============================================================================
# INTERFAZ GRÁFICA PRINCIPAL
# ==============================================================================

class LexerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ANALIZADOR LÉXICO Y SINTÁCTICO (AST / PDA) // v2.0")
        self.root.geometry("1200x700")
        self.root.configure(bg="#050505")

        # --- ESTILOS NEÓN ---
        self.color_bg = "#000000"
        self.color_borde = "#00FF00"
        self.color_texto_verde = "#00FF00"
        self.color_texto_cian = "#00FFFF"
        self.color_texto_amarillo = "#FFFF00"
        self.color_texto_rojo = "#FF0033"
        self.fuente_consola = ("Consolas", 10, "bold")

        self.setup_ui()
        self.log_kernel("SISTEMA INICIADO. MÓDULOS PARTE 1 (LEXER) Y PARTE 2 (CALCULADORA AST) LISTOS.")

    def setup_ui(self):
        # 1. PANEL SUPERIOR (Botones)
        frame_top = tk.Frame(self.root, bg=self.color_bg, highlightbackground=self.color_borde, highlightthickness=1)
        frame_top.pack(fill="x", padx=10, pady=10)

        btn_cargar = tk.Button(
            frame_top, text="[ 📁 Cargar .txt ]", bg=self.color_bg, fg=self.color_texto_cian,
            font=self.fuente_consola, activebackground="#222", activeforeground=self.color_texto_cian,
            bd=0, command=self.cargar_archivo
        )
        btn_cargar.pack(side="left", padx=10, pady=10)

        btn_ejecutar = tk.Button(
            frame_top, text="[ ▶ Ejecutar Lexer (Parte 1) ]", bg=self.color_bg, fg=self.color_texto_verde,
            font=self.fuente_consola, activebackground="#222", activeforeground=self.color_texto_verde,
            bd=0, command=self.ejecutar_lexer
        )
        btn_ejecutar.pack(side="left", padx=10)

        # NUEVO BOTÓN: PARTE 2 (Calculadora AST / PDA)
        btn_parte2 = tk.Button(
            frame_top, text="[ ⚡ PARTE 2: Calcular AST ]", bg=self.color_bg, fg=self.color_texto_amarillo,
            font=self.fuente_consola, activebackground="#222", activeforeground=self.color_texto_amarillo,
            bd=0, command=self.ejecutar_parte2
        )
        btn_parte2.pack(side="left", padx=10)

        btn_purgar = tk.Button(
            frame_top, text="[ 🗑 Purgar Memoria ]", bg=self.color_bg, fg=self.color_texto_rojo,
            font=self.fuente_consola, activebackground="#222", activeforeground=self.color_texto_rojo,
            bd=0, command=self.purgar_memoria
        )
        btn_purgar.pack(side="left", padx=10)

        # 2. PANEL CENTRAL (Dividido en 3 columnas: Entrada | Tokens | AST y Evaluación)
        frame_mid = tk.Frame(self.root, bg=self.color_bg)
        frame_mid.pack(fill="both", expand=True, padx=10)

        # 2.1 SYSTEM.IN (Izquierda)
        frame_in = tk.Frame(frame_mid, bg=self.color_bg)
        frame_in.pack(side="left", fill="both", expand=True, padx=(0, 5))

        lbl_in = tk.Label(
            frame_in, text="SYSTEM.IN (Source / Expresión)",
            bg=self.color_bg, fg=self.color_texto_cian, font=self.fuente_consola
        )
        lbl_in.pack(anchor="w")

        self.txt_in = tk.Text(
            frame_in, bg=self.color_bg, fg=self.color_texto_verde, font=self.fuente_consola,
            width=32, insertbackground=self.color_texto_verde,
            highlightbackground=self.color_texto_cian, highlightthickness=1
        )
        self.txt_in.pack(fill="both", expand=True)

        # Insertamos una expresión de ejemplo inicial para probar rápido
        self.txt_in.insert(tk.END, "3 + 4 * 2 / ( 1 - 5 ) ^ 2")

        # 2.2 DATA_STREAM (Centro - Treeview)
        frame_out = tk.Frame(frame_mid, bg=self.color_bg)
        frame_out.pack(side="left", fill="both", expand=True, padx=5)

        lbl_out = tk.Label(
            frame_out, text="DATA_STREAM (Tokens)",
            bg=self.color_bg, fg=self.color_texto_cian, font=self.fuente_consola
        )
        lbl_out.pack(anchor="w")

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview", background=self.color_bg, foreground=self.color_texto_verde,
            fieldbackground=self.color_bg, font=("Consolas", 10), rowheight=25, borderwidth=0
        )
        style.configure(
            "Treeview.Heading", background=self.color_bg, foreground=self.color_texto_cian,
            font=("Consolas", 10, "bold"), borderwidth=1
        )
        style.map("Treeview", background=[('selected', '#222222')])

        columnas = ("POS", "TOKEN_ID", "LEXEMA")
        self.tabla_tokens = ttk.Treeview(frame_out, columns=columnas, show="headings", style="Treeview")

        self.tabla_tokens.heading("POS", text="POS")
        self.tabla_tokens.heading("TOKEN_ID", text="TOKEN_ID")
        self.tabla_tokens.heading("LEXEMA", text="LEXEMA")

        self.tabla_tokens.column("POS", width=70, anchor="center")
        self.tabla_tokens.column("TOKEN_ID", width=150, anchor="w")
        self.tabla_tokens.column("LEXEMA", width=110, anchor="w")

        self.tabla_tokens.pack(fill="both", expand=True)

        # 2.3 PARTE 2: AST VISUALIZER & RESULTADO (Derecha)
        frame_ast = tk.Frame(frame_mid, bg=self.color_bg)
        frame_ast.pack(side="right", fill="both", expand=True, padx=(5, 0))

        lbl_ast = tk.Label(
            frame_ast, text="PARTE 2 // AST_VISUALIZER & PDA",
            bg=self.color_bg, fg=self.color_texto_amarillo, font=self.fuente_consola
        )
        lbl_ast.pack(anchor="w")

        self.txt_ast = tk.Text(
            frame_ast, bg=self.color_bg, fg=self.color_texto_verde, font=self.fuente_consola,
            width=38, wrap="word", highlightbackground=self.color_texto_amarillo, highlightthickness=1, state="disabled"
        )
        self.txt_ast.pack(fill="both", expand=True)

        # Panel de Estado PDA y Resultado Numérico
        frame_res = tk.Frame(
            frame_ast, bg=self.color_bg,
            highlightbackground=self.color_borde, highlightthickness=1
        )
        frame_res.pack(fill="x", pady=(5, 0))

        self.lbl_estado_pda = tk.Label(
            frame_res, text="PDA PILA: EN ESPERA",
            bg=self.color_bg, fg=self.color_texto_cian, font=self.fuente_consola
        )
        self.lbl_estado_pda.pack(anchor="w", padx=8, pady=(5, 2))

        self.lbl_resultado = tk.Label(
            frame_res, text="RESULTADO: ---",
            bg=self.color_bg, fg=self.color_texto_amarillo, font=("Consolas", 13, "bold")
        )
        self.lbl_resultado.pack(anchor="w", padx=8, pady=(2, 6))

        # 3. PANEL INFERIOR (Logs)
        frame_bot = tk.Frame(self.root, bg=self.color_bg)
        frame_bot.pack(fill="x", padx=10, pady=10)

        lbl_log = tk.Label(
            frame_bot, text="KERNEL_LOGS",
            bg=self.color_bg, fg=self.color_texto_cian, font=self.fuente_consola
        )
        lbl_log.pack(anchor="w")

        self.txt_log = tk.Text(
            frame_bot, bg=self.color_bg, fg=self.color_texto_verde, font=self.fuente_consola,
            height=6, highlightbackground=self.color_texto_cian, highlightthickness=1, state="disabled"
        )
        self.txt_log.pack(fill="x")

    # --- FUNCIONES DE LA INTERFAZ ---

    def log_kernel(self, mensaje, tipo="info"):
        self.txt_log.config(state="normal")
        prefijo = "> "
        if tipo == "error":
            prefijo = "[!] ERROR: "
        self.txt_log.insert(tk.END, f"{prefijo}{mensaje}\n")
        self.txt_log.see(tk.END)
        self.txt_log.config(state="disabled")

    def mostrar_en_visor_ast(self, texto):
        self.txt_ast.config(state="normal")
        self.txt_ast.delete("1.0", tk.END)
        self.txt_ast.insert(tk.END, texto)
        self.txt_ast.config(state="disabled")

    def cargar_archivo(self):
        ruta = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt")])
        if ruta:
            try:
                with open(ruta, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                self.txt_in.delete("1.0", tk.END)
                self.txt_in.insert(tk.END, contenido)
                self.log_kernel(f"ARCHIVO CARGADO: {ruta.split('/')[-1]}")
            except Exception as e:
                self.log_kernel(f"FALLO AL CARGAR ARCHIVO: {e}", "error")

    def purgar_memoria(self):
        self.txt_in.delete("1.0", tk.END)
        for item in self.tabla_tokens.get_children():
            self.tabla_tokens.delete(item)
        self.mostrar_en_visor_ast("")
        self.lbl_estado_pda.config(text="PDA PILA: EN ESPERA", fg=self.color_texto_cian)
        self.lbl_resultado.config(text="RESULTADO: ---", fg=self.color_texto_amarillo)
        self.txt_log.config(state="normal")
        self.txt_log.delete("1.0", tk.END)
        self.txt_log.config(state="disabled")
        self.log_kernel("MEMORIA PURGADA. SISTEMA LIMPIO.")

    # --- EJECUCIÓN PARTE 1: ANALIZADOR LÉXICO ---
    def ejecutar_lexer(self):
        texto_fuente = self.txt_in.get("1.0", tk.END).strip()

        if not texto_fuente:
            self.log_kernel("NO HAY CÓDIGO PARA ANALIZAR.", "error")
            return

        if programa is None:
            self.log_kernel("MÓDULO 'programa.py' NO ENCONTRADO PARA PARTE 1.", "error")
            return

        self.log_kernel("EJECUTANDO MOTOR AFD (PARTE 1)...")

        for item in self.tabla_tokens.get_children():
            self.tabla_tokens.delete(item)

        try:
            tokens, errores, simbolos = programa.analizar_lexico(texto_fuente)

            for t in tokens:
                posicion = f"{t['linea']}:{t['columna']}"
                self.tabla_tokens.insert("", tk.END, values=(posicion, t['token'], t['lexema']))

            if errores:
                self.log_kernel(f"SE ENCONTRARON {len(errores)} ERRORES LÉXICOS.", "error")
                for e in errores:
                    self.log_kernel(f"Línea {e['linea']}:{e['columna']} -> {e['mensaje']}", "error")

            self.log_kernel(f"ANÁLISIS LÉXICO COMPLETADO. TOKENS_DETECTADOS: {len(tokens)}")

        except Exception as e:
            self.log_kernel(f"FALLO EN EL MOTOR LÉXICO: {e}", "error")

    # --- EJECUCIÓN PARTE 2: CALCULADORA, PDA, AST Y EVALUACIÓN ---
    def ejecutar_parte2(self):
        expresion = self.txt_in.get("1.0", tk.END).strip()

        if not expresion:
            self.log_kernel("NO HAY EXPRESIÓN ARITMÉTICA PARA EVALUAR.", "error")
            return

        self.log_kernel("INICIANDO PARTE 2: ANALIZADOR SINTÁCTICO Y EVALUADOR AST...")

        # Limpiar vistas previas
        for item in self.tabla_tokens.get_children():
            self.tabla_tokens.delete(item)
        self.mostrar_en_visor_ast("")

        try:
            # Etapa A.1: Tokenización
            tokens = AnalizadorParte2.tokenizar(expresion)
            for t in tokens:
                pos = f"{t['linea']}:{t['columna']}"
                self.tabla_tokens.insert("", tk.END, values=(pos, t['token'], t['lexema']))
            self.log_kernel(f"ETAPA A: {len(tokens)} TOKENS EXTRAÍDOS CORRECTAMENTE.")

            # Etapa A.2: Validación Sintáctica y Balanceo con Pila (PDA)
            traza_pda = AnalizadorParte2.validar_pda(tokens)
            self.lbl_estado_pda.config(text="PDA PILA: BALANCEADO [OK]", fg=self.color_texto_verde)
            self.log_kernel("ETAPA A (PDA): PARÉNTESIS BALANCEADOS Y SINTAXIS VÁLIDA.")

            # Etapa B: Construcción del AST
            raiz_ast = AnalizadorParte2.construir_ast(tokens)
            self.log_kernel("ETAPA B: ÁRBOL DE SINTAXIS ABSTRACTA (AST) CONSTRUIDO.")

            # Etapa C: Visualización del AST y Recorrido Postorden
            dibujo_arbol = AnalizadorParte2.dibujar_ast(raiz_ast)
            postorden = " ".join(AnalizadorParte2.recorrido_postorden(raiz_ast))
            texto_traza = "\n".join(
                f" {estado}  lee {simbolo:<3} pila: {pila}" for estado, simbolo, pila in traza_pda
            )
            texto_visor = (
                "=== ESTRUCTURA JERÁRQUICA AST ===\n\n"
                f"{dibujo_arbol}\n"
                "=== RECORRIDO POSTORDEN (RPN) ===\n"
                f"{postorden}\n\n"
                "=== TRAZA DEL AUTÓMATA DE PILA ===\n"
                f"{texto_traza}\n"
            )
            self.mostrar_en_visor_ast(texto_visor)
            self.log_kernel("ETAPA C: AST RENDERIZADO EN EL VISOR.")

            # Etapa D: Evaluación de la Expresión
            resultado = AnalizadorParte2.evaluar_ast(raiz_ast)
            # Si el resultado es entero exacto (ej. 8.0), mostrarlo limpio
            if isinstance(resultado, float) and resultado.is_integer():
                resultado = int(resultado)

            self.lbl_resultado.config(text=f"RESULTADO: {resultado}", fg=self.color_texto_amarillo)
            self.log_kernel(f"ETAPA D: EVALUACIÓN COMPLETADA CON ÉXITO -> {resultado}")

        except SyntaxError as err_sintactico:
            self.lbl_estado_pda.config(text="PDA PILA: ERROR SINTÁCTICO", fg=self.color_texto_rojo)
            self.lbl_resultado.config(text="RESULTADO: INVÁLIDO", fg=self.color_texto_rojo)
            self.mostrar_en_visor_ast(f"[FALLO EN AUTÓMATA DE PILA]\n\n{err_sintactico}")
            self.log_kernel(f"FALLO SINTÁCTICO (PDA): {err_sintactico}", "error")

        except ZeroDivisionError as err_cero:
            self.lbl_resultado.config(text="RESULTADO: DIV / 0", fg=self.color_texto_rojo)
            self.log_kernel(f"ERROR MATEMÁTICO: {err_cero}", "error")

        except ValueError as err_lexico:
            self.lbl_estado_pda.config(text="PDA PILA: ERROR LÉXICO", fg=self.color_texto_rojo)
            self.lbl_resultado.config(text="RESULTADO: ERROR", fg=self.color_texto_rojo)
            self.mostrar_en_visor_ast(f"[ERROR LÉXICO DETECTADO]\n\n{err_lexico}")
            self.log_kernel(f"ERROR LÉXICO EN EXPRESIÓN: {err_lexico}", "error")

        except Exception as e:
            self.log_kernel(f"ERROR INESPERADO EN PARTE 2: {e}", "error")


if __name__ == "__main__":
    root = tk.Tk()
    app = LexerApp(root)
    root.mainloop()