import sys
import shlex
import re
import json

# TODO: AGRUPACIONES DE SIMBOLOS ESPECIALES
# TODO: CARACTERES UNICODE

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
    "(", ")","{","}","[","]",":","$","!",".",",","\t"
]

def leer_archivo(nombre_archivo):
    try:
        with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
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
        match = re.match(r'^\t+', renglon)
        
        tokens = list( shlex.shlex(renglon, punctuation_chars="\n".join(operadores + simbolos)) );

        if match and len(tokens) != 0:
            tabs = len(match.group(0))

            for i in range(0, tabs):
                categorizacion.append({
                    "token": "\t",
                    "categoria": 'Simbolos especiales',
                })

        for token in tokens:
            categorizacion.append(
                categorizar_token(token)
            )
    
    json_string = json.dumps(categorizacion, indent=4)
    print(json_string)

def is_number_const(token):
    reg_entero_float = re.compile('^-?\d+(\.\d+)?$')
    reg_not_cientifica = re.compile('^-?\d+(\.\d+)?[eE][-+]?\d+$')
    reg_complex = re.compile('^-?\d+(\.\d+)?[jJ]$')

    val_entero_float = re.fullmatch(reg_entero_float, token)
    val_not_cientifica = re.fullmatch(reg_not_cientifica, token)
    val_complex = re.fullmatch(reg_complex, token)

    return  val_entero_float is not None or val_not_cientifica is not None or val_complex is not None

def is_string_const(token):
    reg_double_quoute = re.compile('^"(?:\.|(\\\")|[^\""\n])*"$')
    reg_single_quoute = re.compile("^'(?:\.|(\\\')|[^\''\n])*'$")

    val_double_quoute = re.fullmatch(reg_double_quoute, token)
    val_single_quoute = re.fullmatch(reg_single_quoute, token)

    return  val_double_quoute is not None or val_single_quoute is not None

def is_valid_identifier(token):
    reg_identifier = re.compile('^([a-zA-Z_]|_[a-zA-Z]){1}[a-zA-Z0-9_]*$')

    val_identifier = re.fullmatch(reg_identifier, token)

    return  val_identifier is not None

def categorizar_token(token):
    categoria = ''
    
    if token in palabras_reservadas:
        categoria = 'Palabra reservada'
    elif token in operadores:
        categoria = 'Operador'
    elif token in simbolos:
        categoria = 'Simbolos especiales'
    elif is_number_const(token):
        categoria = 'Const numerica'
    elif is_string_const(token):
        categoria = 'Const cadena'
    elif is_valid_identifier(token):
        categoria = 'Identificador'
    else:
        categoria = 'ERROR!'


    return {
        "token": token,
        "categoria": categoria,
    }

if __name__ == "__main__":
        nombre_archivo = sys.argv[1]
        leer_archivo(nombre_archivo)
