# import ply.yacc as yacc
import sys;
import ast

sys.path.append("/workspaces/compiladores/AnalizadorLexico")

spacedBase = '  '

class Tree():
    def __init__(self, name, level):
        self.name = name
        self.nodes = []
        self.level = level
        
    def addNode(self, n ):
        self.nodes.append( n )
        
    def print(self):
        tabArr = [spacedBase] * self.level
        tabStr = "".join( tabArr )
        
        print( tabStr + self.name )
        
        for n in self.nodes:
            n.print()

class Node():
    def __init__(self, name, level):
        self.name = name
        self.level = level
        
    def print(self):
        tabArr = [spacedBase] * self.level
        tabStr = "".join( tabArr )
        
        print( tabStr + self.name )

def analizar_codigo(expresion_analizada, level):
    valor = None
    
    # CUERPO PRINCIPAL
    if type(expresion_analizada) == ast.Module:
        arbol = Tree( "Cuerpo principal", level )
        
        for item in expresion_analizada.body:
            arbolSec = analizar_codigo( item, level + 1 )
            if not arbolSec is None: 
                arbol.addNode( arbolSec )
        
        valor = arbol
        
    # DEFINICION DE FUNCION
    elif type(expresion_analizada) == ast.FunctionDef:
        name_function = 'Funcion - ' + expresion_analizada.name
        
        arbol_func = Tree( name_function , level )
        
        arbol_func.addNode( 
            analizar_codigo( expresion_analizada.args, level + 1 )
        )
        
        arbol_func_cuerpo = Tree( 'Cuerpo de Función', level + 1 )
        for item in expresion_analizada.body:
            arbolSec = analizar_codigo( item, level + 2 )
            
            if not arbolSec is None: 
                arbol_func_cuerpo.addNode( arbolSec )
        
        arbol_func.addNode( arbol_func_cuerpo )
        
        valor = arbol_func
        
    # ARGUMENTOS DE FUNCION
    elif type(expresion_analizada) == ast.arguments:        
        arbol_arg = Tree( 'Args', level )
        
        for item in expresion_analizada.args:
            nodo = Node( f'arg - { item.arg }', level + 1 )
            arbol_arg.addNode( nodo )
        
        if( not (expresion_analizada.kwarg is None) ):
            nodo = Node( f'kwarg - { expresion_analizada.kwarg }', level + 1 )
            arbol_arg.addNode( nodo )
        
        valor = arbol_arg
        
    # RETORNO
    elif type(expresion_analizada) == ast.Return:
        arbol_rt = Tree( 
            'Return', 
            level 
        )
        
        arbolSec = analizar_codigo( expresion_analizada.value , level + 1 )
        arbol_rt.addNode( arbolSec )
        
        valor = arbol_rt
        
    # ESTRUCTURA DE CONTROL - IF
    elif type(expresion_analizada) == ast.If:
        arbol_if_gen = Tree( 'Estructura de control IF', level )
        
        arbol_if = Tree( 'Condición', level + 1 )
        arbol_if.addNode( analizar_codigo( expresion_analizada.test, level + 2 ) )
        
        arbol_if_cuerpo = Tree( 'Cuerpo de Condición', level + 1 )
        for item in expresion_analizada.body:
            arbolSec = analizar_codigo( item, level + 2 )
            
            if not arbolSec is None: 
                arbol_if_cuerpo.addNode( arbolSec )
                
        arbol_if_gen.addNode( arbol_if )
        arbol_if_gen.addNode( arbol_if_cuerpo )
        
        valor = arbol_if_gen
        
    # COMPARACION / Tipo AND o Tipo OR
    elif type(expresion_analizada) == ast.Compare:
        arbol_com = Tree( 
            'Comparacion', 
            level 
        )
        
        arbolSec = analizar_codigo( expresion_analizada.left, level + 1 )
        arbol_com.addNode( arbolSec )
        
        for ind in range( len( expresion_analizada.comparators ) ):
            if ind < len( expresion_analizada.ops ):

                operator = expresion_analizada.ops[ ind ]
                
                # FORMAS DE COMPARACION
                if type( operator ) == ast.Eq:
                    arbol_com.addNode( Node('igual a', level + 1) )
                elif type( operator ) == ast.NotEq:
                    arbol_com.addNode( Node('no igual a', level + 1) )
                elif type( operator ) == ast.Lt:
                    arbol_com.addNode( Node('menor a', level + 1) )
                elif type( operator ) == ast.LtE:
                    arbol_com.addNode( Node('menor o igual a', level + 1) )
                elif type( operator ) == ast.Gt:
                    arbol_com.addNode( Node('mayor a', level + 1) )
                elif type( operator ) == ast.GtE:
                    arbol_com.addNode( Node('mayor o igual a', level + 1) )
                elif type( operator ) == ast.Is:
                    arbol_com.addNode( Node('es', level + 1) )
                elif type( operator ) == ast.IsNot:
                    arbol_com.addNode( Node('no es', level + 1) )
                elif type( operator ) == ast.In:
                    arbol_com.addNode( Node('en', level + 1) )
                elif type( operator ) == ast.NotIn:
                    arbol_com.addNode( Node('no en', level + 1) )
            
            # VALORES DE COMPARACION
            comp = expresion_analizada.comparators[ ind ]
            
            arbolSec = analizar_codigo( comp, level + 1 )
            arbol_com.addNode( arbolSec )
    
        valor = arbol_com
        
    # OPERACION BOOLEANA
    elif type(expresion_analizada) == ast.BoolOp:
        operacion = ""
        
        if type(expresion_analizada.op) == ast.And: operacion = "And"
        elif type(expresion_analizada.op) == ast.Or: operacion = "Or"
        
        arbol_op = Tree( 
            operacion, 
            level 
        )
        
        for item in expresion_analizada.values:
            arbolSec = analizar_codigo( item, level + 1 )
            arbol_op.addNode( arbolSec )
            
        valor = arbol_op
    
    # OPERACION BINARIA
    elif type(expresion_analizada) == ast.BinOp:
        arbol_op = Tree( 
            "Operacion binaria", 
            level 
        )
        
        operacion = ""
        
        if type(expresion_analizada.op) == ast.Add: operacion = "Suma"
        elif type(expresion_analizada.op) == ast.Sub: operacion = "Resta"
        elif type(expresion_analizada.op) == ast.Mult: operacion = "Multiplica"
        elif type(expresion_analizada.op) == ast.Div: operacion = "Divide"
        elif type(expresion_analizada.op) == ast.FloorDiv: operacion = "And"
        elif type(expresion_analizada.op) == ast.Mod: operacion = "Modulo de"
        elif type(expresion_analizada.op) == ast.Pow: operacion = "Potencia"
        elif type(expresion_analizada.op) == ast.MatMult: operacion = "Multiplica matematicamente"
        
        arbol_left = analizar_codigo( expresion_analizada.left, level + 1 )
        arbol_op.addNode( arbol_left )
        
        arbol_op.addNode( Node( str(operacion) , level + 1 ) )
        
        arbol_right = analizar_codigo( expresion_analizada.right, level + 1 )
        arbol_op.addNode( arbol_right )
            
        valor = arbol_op
    
    # NOMBRE / VARIABLE
    elif type(expresion_analizada) == ast.Name:
        valor = Node( expresion_analizada.id, level )
    
    # VALOR CONSTANTE
    elif type(expresion_analizada) == ast.Constant:
        valor = Node( str(expresion_analizada.value) , level )
    
    # TUPLA
    elif type(expresion_analizada) == ast.Tuple:
        arbol_tp = Tree( 
            'Tupla', 
            level 
        )
        
        for item in expresion_analizada.elts:
            arbolSec = analizar_codigo( item, level + 1 )
            arbol_tp.addNode( arbolSec )
            
        valor = arbol_tp
    
    elif type(expresion_analizada) == ast.Call:
        arbol_call = Tree( 
            'Llamada a ' + expresion_analizada.func.id, 
            level 
        )
        
        for item in expresion_analizada.args:
            nodo = analizar_codigo( item, level + 1 )
            arbol_call.addNode( nodo )
            
        valor = arbol_call
    
    elif type(expresion_analizada) == ast.Expr:
        # Llamada a la función - Padre
        valor = analizar_codigo( expresion_analizada.value, level )
    
    return valor

if __name__ == "__main__":
        contenido = '''def factorial( n: int, n2: int ) -> int :
    if n == 0 or n == 1:
        return 1;
    return "la respuesta es" , n * factorial( n - 1 );

print( factorial(9) )'''
        expresion_analizada = ast.parse(contenido)
        
        arbol = analizar_codigo(expresion_analizada, 0)
        arbol.print()
        
        #print(ast.dump(expresion_analizada, indent=4))
        