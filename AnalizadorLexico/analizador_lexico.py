import sys
import shlex
import re

def sortFunc(e):
  return len(e)

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

operadores.sort(reverse=True, key=sortFunc)

arr_rev = operadores + simbolos

def leer_archivo(nombre_archivo):
    try:
        with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
            return archivo.read()
    except FileNotFoundError:
        print(f"El archivo '{nombre_archivo}' no fue encontrado.")
    except Exception as e:
        print(f"Ocurrió un error al leer el archivo: {e}")

def tokenizacion_rec( texto, num_simbol ):
    if len(arr_rev) - 1 == num_simbol:
        return [texto];

    simbolo = arr_rev[num_simbol]

    def separation( texto ):
        if( not simbolo in texto ):
            return [texto]
        elif ( simbolo == texto ):
            return [texto]

        sep_tuple = texto.partition(simbolo);
        sep_list = [i for i in sep_tuple if i != ''];
    
        arr_res = []
        for item in sep_list:
            arr_res += separation( item )

        return arr_res

    tokens = separation(texto);

    if len(tokens) == 1 and tokens[0] == simbolo:
        return tokens
    else:
        arr_res = []
        for token in tokens:
            arr_res += tokenizacion_rec( token, num_simbol + 1 )
        
        return arr_res;

def analizar_lex(texto):
    arr_renglones = texto.split('\n');
    categorizacion = []

    for renglon in arr_renglones:
        match = re.match(r'^\t+', renglon)
        
        tokens = list( shlex.shlex(renglon, punctuation_chars="".join(arr_rev)) );

        if match and len(tokens) != 0:
            tabs = len(match.group(0))

            for _ in range(0, tabs):
                categorizacion.append({
                    "token": "\t",
                    "categoria": 'Simbolos especiales',
                })

        for token in tokens:
            reg_simbolos = re.compile('[\+\-\*\/\%\>\<\&\|\^\(\)\{\}\[\]\:\$\!\.\,\t]')
            val_simbolos = re.match(reg_simbolos, token)

            if val_simbolos is not None:
                division = tokenizacion_rec(token, 0)

                for token_ in division:
                    categorizacion.append(
                        categorizar_token(token_)
                    )
            else:
                categorizacion.append(
                    categorizar_token(token)
                )
    
    return categorizacion

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
        contenido = leer_archivo(nombre_archivo)
        json_string = analizar_lex(contenido)
