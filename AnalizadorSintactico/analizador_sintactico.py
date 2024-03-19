import sys;
from abc import ABC, abstractmethod;

sys.path.append("/workspaces/compiladores/AnalizadorLexico")

from analizador_lexico import analizar_lex, leer_archivo

class Arbol(ABC):
        @abstractmethod
        def set_nodo_siguiente(self, arg1):
                pass

class OperacionBinaria(Arbol):
        tipo = None
        nodo_derecho = None
        nodo_izquierdo = None

class Definicion(Arbol):
        tipo = None
        nodo_asignado = None
        nodo_asignacion = None
        
        def __init__(self, tipoGenerico, tipo):
                self.tipoGenerico = tipoGenerico
                self.tipo = tipo
                
        def set_nodo_siguiente(self, arg1):
                self.nodo_asignacion = arg1

        def __str__(self):
                cadena = self.tipo + "(nombre="+self.nodo_asignado+", definicion="+self.nodo_asignacion+")"
                return cadena
        
class Clase(Definicion):
        atributos = []
        metodos = []
        
        def __init__(self, nombre):
                Definicion.__init__(self, "Clase", nombre)
                Definicion.set_nodo_siguiente( self )
                
        def __str__(self):
                cadena = "(atributos=["
                
                for atr in self.atributos:
                      cadena += str(atr)
                
                cadena += "], definicion=["
                
                for met in self.metodos:
                      cadena += str(met)
                      
                cadena += "]"

                return cadena

class Call():
        tipo = None
        nombre = None
        body = None
        
        def __init__(self, tipo, nombre):
                self.tipo = tipo
                self.nombre = nombre
        
        def set_body(self, arg1):
                self.body = arg1

        def __str__(self):
                cadena = self.tipo+"(nombre="+self.nombre+", body="+self.body+")"
                return cadena

class Funcion(Call):
        atributos = []
        
        def __init__(self, nombre):
                Call.__init__(self, "Funcion", nombre)
                
        def __str__(self):
                cadena=Call.tipo+"(nombre="+Call.nombre+", atributos=["
                
                for atr in self.atributos:
                      cadena += str(atr)
                
                cadena += "], body="+Call.body+")"
                return cadena

class EstControl(Call):
        def __init__(self, tipo):
                Call.__init__(self, "EstControl", tipo)
                
class CicloFor(EstControl):
        iterador = None
        iterable = None
        
        def __init__(self):
                Call.__init__(self, "EstControl", "For")
        
        def __str__(self):
                cadena = EstControl.tipo+"(nombre="+EstControl.nombre+","
                
                cadena += "iterador="+self.iterador+","
                cadena += "iterable="+self.iterable+","
                
                cadena += "body="+EstControl.body+")"
                return cadena

class Body():
        cola = []
        
        def agregarOperacion(self, op):
                self.cola.push(op)
        
        def __str__(self):
                cadena = "["
                
                for op in self.cola:
                      cadena +=  str(op)
                
                cadena += "]"
                return cadena
        

class Data():
        tipo = None
        valor = None
        
class Instruccion():
        tipo = None

if __name__ == "__main__":
        nombre_archivo = sys.argv[1]
        contenido = leer_archivo(nombre_archivo)
        json_string = analizar_lex(contenido)