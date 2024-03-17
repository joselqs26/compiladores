import sys;
from AnalizadorLexico.analizador_lexico import analizar_lex, leer_archivo;

if __name__ == "__main__":
        nombre_archivo = sys.argv[1]
        contenido = leer_archivo(nombre_archivo)
        json_string = analizar_lex(contenido)