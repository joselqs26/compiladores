import sys;
from abc import ABC, abstractmethod;

sys.path.append("/workspaces/compiladores/AnalizadorLexico")

from analizador_lexico import analizar_lex, leer_archivo, CATEGORIA_PALABRA_CLAVE, CATEGORIA_OPERADOR, CATEGORIA_SIMBOLO, CATEGORIA_NUMERO, CATEGORIA_CADENA, CATEGORIA_IDENTIFICADOR, CATEGORIA_FIN


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
                self.nodo_asignado = None
                self.nodo_asignacion = None
                
        def set_nodo_asignado(self, nodo_asignado):
                self.nodo_asignado = nodo_asignado
                
        def set_nodo_siguiente(self, arg1):
                self.nodo_asignacion = arg1
        
        def set_nodo_siguiente(self, arg1):
                self.nodo_asignacion = arg1
        
        def get_nodo_siguiente(self):
                return self.nodo_asignacion
        
        def existe_nodo_asignado(self):
                return not self.nodo_asignado is None
        
        def existe_nodo_asignacion(self):
                return not self.nodo_asignacion is None

        def __str__(self):
                cadena = self.tipo + "(nombre="+self.nodo_asignado
                return cadena


class Variable(Definicion):
        def __init__(self):
                super().__init__("Variable")

        def __str__(self):
                cadena = super().__str__() 
                
                cadena += ",asignacion=" + str( super().get_nodo_siguiente() )
                
                cadena += ")"
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
                self.cola.append(op)
        
        def __str__(self):
                cadena = "Body["
                
                cadenas_ops = []
                
                for op in self.cola:
                      cadenas_ops.append( str(op) )
                      
                cadena += ",".join( cadenas_ops )      
                
                cadena += "]"
                return cadena

class Data():
        tipo = None
        valor = None
        
        def __init__(self, tipo, valor):
                self.tipo = tipo
                self.valor = valor
        
        def __str__(self) -> str:
                return self.tipo + '(valor='+self.valor+')'
        
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
                                                if self.nodo_actual.existe_nodo_asignado():
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
                                elif isinstance( self.nodo_actual , Variable) and self.token_anterior['categoria'] != CATEGORIA_FIN:
                                        print( self.token_anterior['categoria'] )
                                        
                                        if self.nodo_actual.existe_nodo_asignacion():
                                                if isinstance( self.nodo_actual.nodo_asignacion, Body):
                                                        self.nodo_actual.nodo_asignacion.agregarOperacion( objToken['token'] )
                                                else :
                                                        nodo_temp = self.nodo_actual.nodo_asignacion
                                                        self.nodo_actual.set_nodo_siguiente( Body() )
                                                        self.nodo_actual.nodo_asignacion.agregarOperacion( nodo_temp )
                                                        self.nodo_actual.nodo_asignacion.agregarOperacion( objToken['token'] )
                        elif objToken['categoria'] == CATEGORIA_NUMERO:
                                if isinstance( self.nodo_actual , Variable):
                                        if self.nodo_actual.existe_nodo_asignacion():
                                                if isinstance( self.nodo_actual.nodo_asignacion, Body):
                                                        self.nodo_actual.nodo_asignacion.agregarOperacion( Data( 'Numero', objToken['token'] ) )
                                                else :
                                                        nodo_temp = self.nodo_actual.nodo_asignacion
                                                        self.nodo_actual.set_nodo_siguiente( Body() )
                                                        self.nodo_actual.nodo_asignacion.agregarOperacion( nodo_temp )
                                                        self.nodo_actual.nodo_asignacion.agregarOperacion( Data( 'Numero', objToken['token'] ) )
                                        else:
                                                self.nodo_actual.set_nodo_siguiente( Data( 'Numero', objToken['token'] ) )
                        elif objToken['categoria'] == CATEGORIA_OPERADOR:
                                if objToken['token'] == '=':
                                        if self.token_anterior['categoria'] == CATEGORIA_IDENTIFICADOR:
                                                self.asignar_secuencia( Variable() )
                                                self.nodo_actual.set_nodo_asignado( self.token_anterior['token'] )
                        
                        self.token_anterior = objToken;
                
                return self.arbol_padre
                            
        def asignar_secuencia(self, nodo):
                if( self.arbol_padre is None ):
                        self.arbol_padre = nodo
                else:
                        if isinstance( self.nodo_actual , Body):
                                self.arbol_padre.agregarOperacion( nodo )
                        else:
                                temp = self.arbol_padre
                                
                                self.arbol_padre = Body()
                                self.arbol_padre.agregarOperacion( temp )
                                self.arbol_padre.agregarOperacion( nodo )
                
                self.nodo_actual = nodo

if __name__ == "__main__":
        nombre_archivo = sys.argv[1]
        contenido = leer_archivo(nombre_archivo)
        json_string = analizar_lex(contenido)
        print( json_string )
        
        constr = ConstructorArbolSintactico()
        arbol = constr.construir_arbol(json_string)
        print( arbol )