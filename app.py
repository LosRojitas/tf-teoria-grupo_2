"""
Minicompilador de Reglas de Negocio - Fase 1: Analizador Léxico
Tienda Online de Tecnología
Backend Flask con API REST
"""

from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)

# ============================================================
# ANALIZADOR LÉXICO (LEXER)
# ============================================================
# Especificación de tokens con prioridad estricta.
# El orden es crucial: los patrones más específicos van primero
# para evitar ambigüedades (ej. '==' antes que '=').
# ============================================================

TOKEN_SPEC = [
    # --- Literales ---
    ('STR_LIT',    r'"[^"]*"|\'[^\']*\''),          # Cadenas entre comillas
    ('NUM_FLOAT',  r'\d+\.\d+'),                     # Decimales (antes que enteros)
    ('NUM_INT',    r'\d+'),                           # Enteros
    ('BOOL_LIT',   r'\b(?:true|false)\b'),            # Booleanos

    # --- Palabras Reservadas (antes que ID) ---
    ('IF',         r'\b(?:SI|si)\b'),                 # Condicional SI
    ('THEN',       r'\b(?:ENTONCES|entonces)\b'),     # Consecuente ENTONCES

    # --- Operadores Lógicos (formas con palabras antes que ID) ---
    ('AND',        r'\bY\b|&&'),                      # Conjunción
    ('OR',         r'\bO\b|\|\|'),                    # Disyunción

    # --- Operadores Relacionales (multi-carácter antes que simples) ---
    ('EQ',         r'=='),                            # Igualdad
    ('NEQ',        r'!='),                            # Desigualdad
    ('LTE',        r'<='),                            # Menor o igual
    ('GTE',        r'>='),                            # Mayor o igual
    ('LT',         r'<'),                             # Menor que
    ('GT',         r'>'),                             # Mayor que

    # --- Operador Lógico NOT (después de NEQ para no capturar '!=' como '!') ---
    ('NOT',        r'\bNO\b|!'),                      # Negación

    # --- Asignación (después de '==') ---
    ('ASSIGN',     r'='),                             # Asignación

    # --- Operadores Aritméticos ---
    ('PLUS',       r'\+'),                            # Suma
    ('MINUS',      r'-'),                             # Resta
    ('MULT',       r'\*'),                            # Multiplicación
    ('DIV',        r'/'),                             # División

    # --- Puntuación ---
    ('L_PAREN',    r'\('),                            # Paréntesis izquierdo
    ('R_PAREN',    r'\)'),                            # Paréntesis derecho
    ('SEMICOLON',  r';'),                             # Punto y coma

    # --- Identificadores (al final para no capturar palabras reservadas) ---
    ('ID',         r'[a-zA-Z_]\w*'),                  # Variables

    # --- Tokens internos (no se reportan) ---
    ('NEWLINE',    r'\n'),                            # Saltos de línea
    ('SKIP',       r'[ \t]+'),                        # Espacios y tabulaciones
    ('ERROR',      r'.'),                             # Cualquier otro carácter
]

# Compilar el patrón maestro combinando todos los tokens
_master_pattern = '|'.join(
    f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPEC
)
_master_regex = re.compile(_master_pattern)


def lexer(source_code):
    """
    Analiza el código fuente y genera la lista de tokens y errores léxicos.

    Args:
        source_code (str): El texto del código fuente a analizar.

    Returns:
        tuple: (tokens, errors)
            - tokens: lista de dicts con 'token', 'lexema', 'linea'
            - errors: lista de dicts con 'mensaje', 'linea', 'columna', 'caracter'
    """
    tokens = []
    errors = []
    line_num = 1
    line_start = 0

    for match in _master_regex.finditer(source_code):
        kind = match.lastgroup
        value = match.group()
        column = match.start() - line_start + 1

        if kind == 'NEWLINE':
            line_num += 1
            line_start = match.end()
        elif kind == 'SKIP':
            continue
        elif kind == 'ERROR':
            errors.append({
                'mensaje': f"Carácter inválido '{value}'",
                'linea': line_num,
                'columna': column,
                'caracter': value
            })
        else:
            tokens.append({
                'token': kind,
                'lexema': value,
                'linea': line_num
            })

    return tokens, errors


# ============================================================
# RUTAS DE LA API
# ============================================================

@app.route('/')
def index():
    """Sirve la página principal del analizador léxico."""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Endpoint de la API que recibe código fuente y retorna
    la tabla de tokens y la lista de errores léxicos.
    """
    data = request.get_json()

    if not data or 'code' not in data:
        return jsonify({
            'error': 'No se proporcionó código fuente.',
            'tokens': [],
            'errors': []
        }), 400

    source_code = data['code']
    tokens, errors = lexer(source_code)

    return jsonify({
        'tokens': tokens,
        'errors': errors,
        'total_tokens': len(tokens),
        'total_errors': len(errors)
    })


# ============================================================
# PUNTO DE ENTRADA
# ============================================================

if __name__ == '__main__':
    app.run(debug=True, port=5000)
