import csv
import os

def cargar_palabras_reservadas():
    """Lee el archivo de palabras reservadas si existe."""
    reservadas = {}
    ruta = "files/palabras_reservadas.csv"
    
    if os.path.exists(ruta):
        try:
            with open(ruta, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    reservadas[row['lexema']] = row['token']
        except Exception as e:
            print(f"Aviso: No se pudo cargar {ruta}: {e}")
    else:
        # Fallback sencillo por si el archivo no está en la ruta
        reservadas = {"int": "TK_RES_INT", "if": "TK_RES_IF", "while": "TK_RES_WHILE"}
        
    return reservadas

def analizar_lexico(texto_fuente):
    palabras_reservadas = cargar_palabras_reservadas()
    
    tokens = []
    errores = []
    tabla_simbolos = {}
    
    linea = 1
    columna = 1
    
    i = 0
    longitud = len(texto_fuente)
    
    # Bucle principal del Autómata Finito Determinista (AFD)
    while i < longitud:
        char = texto_fuente[i]
        
        # 1. Omitir espacios y saltos de línea (Estado 0)
        if char in [' ', '\t', '\r', '\n']:
            if char == '\n':
                linea += 1
                columna = 1
            else:
                columna += 1
            i += 1
            continue
            
        inicio_columna = columna
        lexema = ""
        
        # 2. Transición: Identificadores y Palabras Reservadas (Letras seguidas de letras o números)
        if char.isalpha() or char == '_':
            while i < longitud and (texto_fuente[i].isalnum() or texto_fuente[i] == '_'):
                lexema += texto_fuente[i]
                columna += 1
                i += 1
                
            # Verificamos si es palabra reservada
            token_id = palabras_reservadas.get(lexema, "TK_IDENTIFICADOR")
            
            tokens.append({
                'token': token_id, 'lexema': lexema, 'linea': linea, 'columna': inicio_columna
            })
            
            # Agregamos a la tabla de símbolos si es un identificador nuevo
            if token_id == "TK_IDENTIFICADOR" and lexema not in tabla_simbolos:
                tabla_simbolos[lexema] = {'tipo': 'Variable/Identificador', 'linea': linea}
                
            continue # Volver al inicio del ciclo
            
        # 3. Transición: Números (Enteros simples para mantenerlo fácil)
        if char.isdigit():
            while i < longitud and texto_fuente[i].isdigit():
                lexema += texto_fuente[i]
                columna += 1
                i += 1
                
            tokens.append({
                'token': "TK_NUMERO_ENTERO", 'lexema': lexema, 'linea': linea, 'columna': inicio_columna
            })
            continue
            
        # 4. Transición: Operadores y Símbolos de un solo carácter (o dobles como ==)
        simbolos_simples = {
            ';': 'TK_PUNTO_COMA', ',': 'TK_COMA', 
            '(': 'TK_PAR_IZQ', ')': 'TK_PAR_DER',
            '{': 'TK_LLAVE_IZQ', '}': 'TK_LLAVE_DER',
            '+': 'TK_SUMA', '-': 'TK_RESTA', '*': 'TK_MULT', '/': 'TK_DIV'
        }
        
        # Chequear operadores dobles primero (ej. ==, <=, >=)
        if char in ['=', '<', '>', '!']:
            lexema = char
            columna += 1
            i += 1
            # Miramos el siguiente caracter
            if i < longitud and texto_fuente[i] == '=':
                lexema += '='
                columna += 1
                i += 1
                
            # Asignar token según el lexema resultante
            if lexema == '=': token_id = "TK_IGUAL"
            elif lexema == '==': token_id = "TK_DOBLE_IGUAL"
            elif lexema == '<': token_id = "TK_MENOR_QUE"
            elif lexema == '<=': token_id = "TK_MENOR_IGUAL"
            elif lexema == '>': token_id = "TK_MAYOR_QUE"
            elif lexema == '>=': token_id = "TK_MAYOR_IGUAL"
            elif lexema == '!=': token_id = "TK_DIFERENTE"
            else: token_id = "TK_OPERADOR_DESCONOCIDO" # Por si acaso
                
            tokens.append({'token': token_id, 'lexema': lexema, 'linea': linea, 'columna': inicio_columna})
            continue

        # Chequear símbolos simples
        if char in simbolos_simples:
            tokens.append({
                'token': simbolos_simples[char], 'lexema': char, 'linea': linea, 'columna': inicio_columna
            })
            columna += 1
            i += 1
            continue
            
        # 5. MANEJO DE ERRORES (Transición no definida)
        # Si llega aquí, es un carácter que no reconoció el autómata (ej. @, $, etc.)
        errores.append({
            'caracter': char,
            'linea': linea,
            'columna': inicio_columna,
            'mensaje': f"Caracter no válido: '{char}'"
        })
        
        # Avanzamos para no trabar el programa (Recuperación de errores)
        columna += 1
        i += 1

    return tokens, errores, tabla_simbolos