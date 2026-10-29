import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import programa # Importamos el analizador léxico que hicimos

class LexerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ANALIZADOR LEXICO // v1.0")
        self.root.geometry("1000x650")
        self.root.configure(bg="#050505") # Fondo oscuro principal

        # --- ESTILOS (Colores neón de la imagen) ---
        self.color_bg = "#000000"
        self.color_borde = "#00FF00"
        self.color_texto_verde = "#00FF00"
        self.color_texto_cian = "#00FFFF"
        self.color_texto_rojo = "#FF0033"
        self.fuente_consola = ("Consolas", 10, "bold")

        self.setup_ui()
        self.log_kernel("SISTEMA INICIADO. ESPERANDO ENTRADA...")

    def setup_ui(self):
        # 1. PANEL SUPERIOR (Botones)
        frame_top = tk.Frame(self.root, bg=self.color_bg, highlightbackground=self.color_borde, highlightthickness=1)
        frame_top.pack(fill="x", padx=10, pady=10)

        # Botón Cargar
        btn_cargar = tk.Button(frame_top, text="[ 📁 Cargar .txt ]", bg=self.color_bg, fg=self.color_texto_cian, 
                               font=self.fuente_consola, activebackground="#222", activeforeground=self.color_texto_cian,
                               bd=0, command=self.cargar_archivo)
        btn_cargar.pack(side="left", padx=10, pady=10)

        # Botón Ejecutar
        btn_ejecutar = tk.Button(frame_top, text="[ ▶ Ejecutar Lexer ]", bg=self.color_bg, fg=self.color_texto_verde, 
                                 font=self.fuente_consola, activebackground="#222", activeforeground=self.color_texto_verde,
                                 bd=0, command=self.ejecutar_lexer)
        btn_ejecutar.pack(side="left", padx=10)

        # Botón Purgar
        btn_purgar = tk.Button(frame_top, text="[ 🗑 Purgar Memoria ]", bg=self.color_bg, fg=self.color_texto_rojo, 
                               font=self.fuente_consola, activebackground="#222", activeforeground=self.color_texto_rojo,
                               bd=0, command=self.purgar_memoria)
        btn_purgar.pack(side="left", padx=10)


        # 2. PANEL CENTRAL (Contenedor para Código y Tokens)
        frame_mid = tk.Frame(self.root, bg=self.color_bg)
        frame_mid.pack(fill="both", expand=True, padx=10)

        # 2.1 SYSTEM.IN (Izquierda)
        frame_in = tk.Frame(frame_mid, bg=self.color_bg)
        frame_in.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        lbl_in = tk.Label(frame_in, text="SYSTEM.IN (Source Code)", bg=self.color_bg, fg=self.color_texto_cian, font=self.fuente_consola)
        lbl_in.pack(anchor="w")
        
        self.txt_in = tk.Text(frame_in, bg=self.color_bg, fg=self.color_texto_verde, font=self.fuente_consola, 
                              insertbackground=self.color_texto_verde, highlightbackground=self.color_texto_cian, highlightthickness=1)
        self.txt_in.pack(fill="both", expand=True)

        # 2.2 DATA_STREAM (Derecha - Treeview)
        frame_out = tk.Frame(frame_mid, bg=self.color_bg)
        frame_out.pack(side="right", fill="both", expand=True, padx=(5, 0))

        lbl_out = tk.Label(frame_out, text="DATA_STREAM (Tokens)", bg=self.color_bg, fg=self.color_texto_cian, font=self.fuente_consola)
        lbl_out.pack(anchor="w")

        # Estilo personalizado para el Treeview (Tabla)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background=self.color_bg, foreground=self.color_texto_verde, 
                        fieldbackground=self.color_bg, font=("Consolas", 10), rowheight=25, borderwidth=0)
        style.configure("Treeview.Heading", background=self.color_bg, foreground=self.color_texto_cian, 
                        font=("Consolas", 10, "bold"), borderwidth=1)
        style.map("Treeview", background=[('selected', '#222222')])

        columnas = ("POS", "TOKEN_ID", "LEXEMA")
        self.tabla_tokens = ttk.Treeview(frame_out, columns=columnas, show="headings", style="Treeview")
        
        self.tabla_tokens.heading("POS", text="POS")
        self.tabla_tokens.heading("TOKEN_ID", text="TOKEN_ID")
        self.tabla_tokens.heading("LEXEMA", text="LEXEMA")
        
        self.tabla_tokens.column("POS", width=80, anchor="center")
        self.tabla_tokens.column("TOKEN_ID", width=200, anchor="w")
        self.tabla_tokens.column("LEXEMA", width=150, anchor="w")
        
        self.tabla_tokens.pack(fill="both", expand=True)


        # 3. PANEL INFERIOR (Logs)
        frame_bot = tk.Frame(self.root, bg=self.color_bg)
        frame_bot.pack(fill="x", padx=10, pady=10)

        lbl_log = tk.Label(frame_bot, text="KERNEL_LOGS", bg=self.color_bg, fg=self.color_texto_cian, font=self.fuente_consola)
        lbl_log.pack(anchor="w")

        self.txt_log = tk.Text(frame_bot, bg=self.color_bg, fg=self.color_texto_verde, font=self.fuente_consola, 
                               height=6, highlightbackground=self.color_texto_cian, highlightthickness=1)
        self.txt_log.pack(fill="x")
        self.txt_log.config(state="disabled") # Para que el usuario no escriba aquí

    # --- FUNCIONES DE LA INTERFAZ ---

    def log_kernel(self, mensaje, tipo="info"):
        self.txt_log.config(state="normal")
        prefijo = "> "
        if tipo == "error":
            prefijo = "[!] ERROR: "
        
        self.txt_log.insert(tk.END, f"{prefijo}{mensaje}\n")
        self.txt_log.see(tk.END) # Auto-scroll hacia abajo
        self.txt_log.config(state="disabled")

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
        # Limpiar texto de entrada
        self.txt_in.delete("1.0", tk.END)
        # Limpiar tabla
        for item in self.tabla_tokens.get_children():
            self.tabla_tokens.delete(item)
        # Limpiar logs
        self.txt_log.config(state="normal")
        self.txt_log.delete("1.0", tk.END)
        self.txt_log.config(state="disabled")
        self.log_kernel("MEMORIA PURGADA. SISTEMA LIMPIO.")

    def ejecutar_lexer(self):
        texto_fuente = self.txt_in.get("1.0", tk.END).strip()
        
        if not texto_fuente:
            self.log_kernel("NO HAY CÓDIGO PARA ANALIZAR.", "error")
            return

        self.log_kernel("EJECUTANDO MOTOR AFD...")
        
        # 1. Limpiamos la tabla antes de la nueva ejecución
        for item in self.tabla_tokens.get_children():
            self.tabla_tokens.delete(item)

        # 2. LLAMAMOS AL ARCHIVO programa.py
        try:
            tokens, errores, simbolos = programa.analizar_lexico(texto_fuente)
            
            # 3. Llenamos la tabla visual (Treeview)
            for t in tokens:
                posicion = f"{t['linea']}:{t['columna']}"
                self.tabla_tokens.insert("", tk.END, values=(posicion, t['token'], t['lexema']))
                
            # 4. Mostramos errores en la consola inferior
            if errores:
                self.log_kernel(f"SE ENCONTRARON {len(errores)} ERRORES LÉXICOS.", "error")
                for e in errores:
                    self.log_kernel(f"Línea {e['linea']}:{e['columna']} -> {e['mensaje']}", "error")
            
            self.log_kernel(f"ANALISIS COMPLETADO. TOKENS_DETECTADOS: {len(tokens)}")
            
        except Exception as e:
            self.log_kernel(f"FALLO EN EL MOTOR LEXICO: {e}", "error")

if __name__ == "__main__":
    root = tk.Tk()
    app = LexerApp(root)
    root.mainloop()