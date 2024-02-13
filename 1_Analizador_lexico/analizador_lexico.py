import sys

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
        for caracter in renglon:
            if caracter in '(){}[]':
                categorizacion.append({
                    caracter,
                    'Sim'
                })

    print( categorizacion )

    

if __name__ == "__main__":
        nombre_archivo = sys.argv[1]
        leer_archivo(nombre_archivo)
