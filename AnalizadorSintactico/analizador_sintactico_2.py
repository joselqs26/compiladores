# import ply.yacc as yacc
import sys;
import ast

sys.path.append("/workspaces/compiladores/AnalizadorLexico")

class Tree:
    nodes = []
    name = ""
    
    def __init__(self, name):
        self.name = name
        
    def addNode(self, n ):
        self.nodes.append( n )
        
    def print(self, nTab = 0):
        tabArr = ['\t'] * nTab
        tabStr = "".join( tabArr )
        
        print( tabStr + self.name )
        print( len( self.nodes ) )
        
        for n in self.nodes:
            print( type( n ) )
            if type( n ) == Node:
                print( 1 )
            if type( n ) == Tree:
                print( len( n.nodes ) )
        #     n.print(nTab + 1)

class Node:
    name = ""

    def __init__(self, name):
        self.name = name
        
    def print(self, nTab = 0):
        tabArr = ['\t'] * nTab
        tabStr = "".join( tabArr )
        
        print( tabStr + self.name )

def analizar_codigo(expresion_analizada):
    valor = None
    
    # print( type( expresion_analizada ) )
    
    if type(expresion_analizada) == ast.Module:
        arbol = Tree( "Cuerpo principal" )
        
        for item in expresion_analizada.body:
            arbolSec = analizar_codigo( item )
            if not arbolSec is None: 
                print( len( arbolSec.nodes ) )
                
                arbol.addNode( arbolSec )
        
        valor = arbol
    elif type(expresion_analizada) == ast.FunctionDef:
        arbol_func = Tree( expresion_analizada.name )
        
        print( 'Add nodo función' )
        arbol_func.addNode( 
            analizar_codigo( expresion_analizada.args )
        )
        
        valor = arbol_func
    elif type(expresion_analizada) == ast.arguments:        
        arbol_arg = Tree( 'Args' )
        
        for item in expresion_analizada.args:
            nodo = Node( f'arg - { item.arg }' )
            print( 'Add nodo arg' )
            arbol_arg.addNode( nodo )
        
        if( not (expresion_analizada.kwarg is None) ):
            nodo = Node( f'kwarg - { expresion_analizada.kwarg }' )
            print( 'Add nodo kwarg' )
            arbol_arg.addNode( nodo )
        
        valor = arbol_arg
    elif type(expresion_analizada) == ast.Expr:
        pass
    
    return valor

if __name__ == "__main__":
        contenido = '''def factorial( n: int ) -> int :
    if n == 0 or n == 1:
        return 1;
    return "la respuesta es" , n * factorial( n - 1 );

print( factorial(9) )'''
        expresion_analizada = ast.parse(contenido)
        
        arbol = analizar_codigo(expresion_analizada)
        
        arbol.print()
        
        #print(ast.dump(expresion_analizada.body, indent=4))
        #print(expresion_analizada.body)