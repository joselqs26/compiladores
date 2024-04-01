import sys;
from abc import ABC, abstractmethod;

sys.path.append("/workspaces/compiladores/AnalizadorLexico")

from analizador_lexico import analizar_lex, leer_archivo, CATEGORIA_PALABRA_CLAVE, CATEGORIA_OPERAADOR, CATEGORIA_SIMBOLO, CATEGORIA_NUMERO, CATEGORIA_CADENA, CATEGORIA_IDENTIFICADOR


# Clases de definición 

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
        
        def __init__(self, tipo):
                self.tipo = tipo
                
        def set_nodo_asignado(self, nodo_asignado):
                self.nodo_asignado = nodo_asignado
                
        def set_nodo_siguiente(self, arg1):
                self.nodo_asignacion = arg1

        def __str__(self):
                cadena = self.tipo + "(nombre="+self.nodo_asignado
                return cadena


class Importacion(Definicion):
        alias = None
        partes = []
        
        def __init__(self):
                super().__init__("Importacion")

        def set_alias(self, alias):
                self.alias = alias

        def add_parte_importada(self, asignacion ):
                self.partes.append( {
                        'Asignacion': asignacion, 'Alias': None 
                } )

        def existe_modulo_asignado(self):
                return not self.nodo_asignado is None

        def existes_partes(self):
                return len(self.partes) > 0

        def esta_la_ultima_parte_sin_alias(self):
                return self.partes[ len(self.partes) - 1 ]['Alias'] is None
        
        def asignar_alias_parte(self, alias ):
                self.partes[ len(self.partes) - 1 ]['Alias'] = alias

        def __str__(self):
                cadena = super().__str__() 
                
                if self.alias:
                       cadena += ',Alias=' + self.alias
                if( len(self.partes) > 0 ):
                        cadena += ",partes=["
                        
                        cadenas_partes = []
                        
                        for part in self.partes:
                                cadena_part = 'Parte(nombre=' + part['Asignacion']
                                if part['Alias']:
                                        cadena_part += ',Alias=' + part['Alias']
                                
                                cadena_part += ')'
                                cadenas_partes.append(cadena_part)
                        
                        cadena += ",".join( cadenas_partes )
                        
                        cadena += "]"
                        
                cadena += ")"
                return cadena
    
class Clase(Definicion):
        atributos = []
        metodos = []
        
        def __init__(self, nombre):
                Definicion.__init__(self, "Clase")
                Definicion.set_nodo_asignado( nombre )
                Definicion.set_nodo_siguiente( self )
                
        def __str__(self):
                cadena = "(atributos=["
                
                for atr in self.atributos:
                      cadena += str(atr)
                
                cadena += "], definicion=["
                
                for met in self.metodos:
                      cadena += str(met)
                      
                cadena += "])"

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

# Constructor de arbol

class ConstructorArbolSintactico:
        arbol_padre = None
        token_anterior = None
        nodo_actual = None
        
        def construir_arbol(self, token_arr):
                for objToken in token_arr:
                        
                        if objToken['categoria'] == CATEGORIA_PALABRA_CLAVE:
                                if objToken['token'] == 'from':
                                        self.asignar_secuencia( Importacion() )
                                elif objToken['token'] == 'import'and not isinstance( self.nodo_actual , Importacion):
                                        self.asignar_secuencia( Importacion() )
                                
                        elif objToken['categoria'] == CATEGORIA_IDENTIFICADOR:
                                if isinstance( self.nodo_actual , Importacion):
                                        if self.token_anterior['token'] == 'from':
                                                self.nodo_actual.set_nodo_asignado( objToken['token'] )
                                        
                                        elif self.token_anterior['token'] == 'import':
                                                if self.nodo_actual.existe_modulo_asignado():
                                                        self.nodo_actual.add_parte_importada( objToken['token'] )
                                                else:
                                                        self.nodo_actual.set_nodo_asignado( objToken['token'] )
                                        
                                        elif self.token_anterior['token'] == 'as':
                                                if self.nodo_actual.existes_partes():
                                                        self.nodo_actual.asignar_alias_parte( objToken['token'] )
                                                else:
                                                        self.nodo_actual.set_alias( objToken['token'] ) 
                                        
                                        elif self.token_anterior['token'] == ',':
                                                self.nodo_actual.add_parte_importada( objToken['token'] )
                                
                        self.token_anterior = objToken;
                
                return self.arbol_padre
                            
        def asignar_secuencia(self, nodo):
                if( self.arbol_padre is None ):
                        self.arbol_padre = nodo
                        self.nodo_actual = nodo
                else:
                        self.nodo_actual = nodo

if __name__ == "__main__":
        nombre_archivo = sys.argv[1]
        contenido = leer_archivo(nombre_archivo)
        json_string = analizar_lex(contenido)
        
        constr = ConstructorArbolSintactico()
        arbol = constr.construir_arbol(json_string)
        print( arbol )