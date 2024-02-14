import sys
import shlex

palabras_reservadas = [
    "False", "class", "from", "or",
    "None", "continue", "global", "pass",
    "True", "def", "if", "raise",
    "and", "del", "import", "return",
    "as", "elif", "in", "try",
    "assert", "else", "is", "while",
    "async", "except", "lambda", "with",
    "await", "finally", "nonlocal", "yield",
    "break", "for", "not"
]

operadores = [
    "+", "-","*","/","%","**","//",
    ">","<","==",">=","<=","!=",
    "&","|","^","~",">>","<<",
    "=","+=","-=","*=","/=","%=","**=","//=","&=","|=","^=",">>=","<<=",
]

simbolos = [
    "(", ")","{","}","[","]",":","$","!"
]

def leer_archivo(nombre_archivo):
    try:
        with open(nombre_archivo, 'r') as archivo:
            contenido = archivo.read()
            analizar_lex(contenido)
    except FileNotFoundError:
        print(f"El archivo '{nombre_archivo}' no fue encontrado.")
    except Exception as e:
        print(f"Ocurrió un error al leer el archivo: {e}")

def analizar_lex(texto):
    arr_renglones = texto.split('\n');
    categorizacion = []

    for renglon in arr_renglones:
        tokens = shlex.shlex(renglon);
        
        for token in tokens:
            print('{!r}'.format(token))

def categorizar_token(token):
    categoria = ''
    
    if token in palabras_reservadas:
        categoria = 'Palabra reservada'
    elif  token in operadores:
        categoria = 'Operador'
    elif  token in simbolos:
        categoria = 'Simbolos especiales'

    return {
        "token": token,
        "categoria": categoria,
    }

if __name__ == "__main__":
        nombre_archivo = sys.argv[1]
        leer_archivo(nombre_archivo)
