from llvmlite import ir
import sys;
import ast
import random
import string

sys.path.append("/workspaces/compiladores/AnalizadorSemantico")

from analizador_semantico import AnalizadorSemantico

class GeneradorCodigo:
    analizador_semantico = None
    expresion_general = None
    
    def __init__(self, expresion_general) -> None:
        self.expresion_general = expresion_general
        analizador_semantico = AnalizadorSemantico()
        analizador_semantico.analizar(self.expresion_general)
        self.analizador_semantico = analizador_semantico

    def get_ir_type(self, string_type, lenght = 0):
        if string_type == "int":
            return ir.IntType(32)
        elif string_type == "str":
            return ir.ArrayType(ir.IntType(8), lenght)
        elif "list" in string_type:
            type_interno = string_type.replace( "list[", '' ).replace( "]", '' )
            return ir.ArrayType( self.get_ir_type(type_interno) , lenght)

    def generar_codigo(self, expresion_analizada, modulo, variables_disponibles = {}, asignacion = None ):
        valor = None
        
        # CUERPO PRINCIPAL
        if type(expresion_analizada) == ast.Module:
            pass
        # DEFINICION DE FUNCION
        elif type(expresion_analizada) == ast.FunctionDef:
            funcion_semantica = self.analizador_semantico.obtener_informacion_funciones( expresion_analizada.name )
            tipo_retorno = self.get_ir_type( funcion_semantica["type"] )
            tipos_argumentos = self.generar_codigo( expresion_analizada.args, modulo)
            
            funcion_tipo = ir.FunctionType(tipo_retorno, tipos_argumentos)
            funcion = ir.Function(modulo, funcion_tipo, name=expresion_analizada.name)
            
            variables_disponibles_fn = {}
            
            for index in range(len(expresion_analizada.args)):
                arg_semantico = expresion_analizada.args[index]
                
                arg_generado = funcion.args[index]
                arg_generado.name = arg_semantico.arg
                
                variables_disponibles_fn[ arg_semantico.arg ] = arg_generado.name
            
            bloque = funcion.append_basic_block(name="Cuerpo de Funcion")
            constructor = ir.IRBuilder(bloque)
            
            for item in expresion_analizada.body:
                dict_arg = {**variables_disponibles,**variables_disponibles_fn};
                
                self.generar_codigo( item, constructor, variables_disponibles=dict_arg)
            
            valor = funcion
            
        # ARGUMENTOS DE FUNCION
        elif type(expresion_analizada) == ast.arguments:        
            ls_tipos_argumentos = []
            
            for item in expresion_analizada.args:
                variable_semantica = self.analizador_semantico.obtener_informacion_variable( item.arg )
                tipo_variable = self.get_ir_type( variable_semantica["type"] )
                ls_tipos_argumentos.append( tipo_variable )
            
            tipos_argumentos = tuple(ls_tipos_argumentos)
            
            valor = tipos_argumentos
            
        # RETORNO
        elif type(expresion_analizada) == ast.Return:
            pass
            
        # ESTRUCTURA DE CONTROL - IF
        elif type(expresion_analizada) == ast.If:
            pass
            
        # COMPARACION / Tipo AND o Tipo OR
        elif type(expresion_analizada) == ast.Compare:
            pass
            
        # OPERACION BOOLEANA
        elif type(expresion_analizada) == ast.BoolOp:
            pass
        
        # OPERACION BINARIA
        elif type(expresion_analizada) == ast.BinOp:
            if type(expresion_analizada.op) == ast.Add: 
                left_var = self.generar_codigo( expresion_analizada.left, modulo, variables_disponibles)
                right_var = self.generar_codigo( expresion_analizada.right, modulo, variables_disponibles)
                
                if type( left_var.type ) == ir.FloatType or type( right_var.type ) == ir.FloatType:
                    if asignacion is None:
                        valor = modulo.fadd( left_var, right_var )
                    elif type( left_var.type ) == ir.IntType or type( right_var.type ) == ir.IntType:
                        valor = modulo.fadd( left_var, right_var, name=asignacion )
                elif type( left_var.type ) == ir.IntType or type( right_var.type ) == ir.IntType:
                    if asignacion is None:
                        valor = modulo.add( left_var, right_var )
                    elif type( left_var.type ) == ir.IntType or type( right_var.type ) == ir.IntType:
                        valor = modulo.add( left_var, right_var, name=asignacion )

            elif type(expresion_analizada.op) == ast.Sub: 
                left_var = self.generar_codigo( expresion_analizada.left, modulo, variables_disponibles)
                right_var = self.generar_codigo( expresion_analizada.right, modulo, variables_disponibles)



            elif type(expresion_analizada.op) == ast.Mult: 
                left_var = self.generar_codigo( expresion_analizada.left, modulo, variables_disponibles)
                right_var = self.generar_codigo( expresion_analizada.right, modulo, variables_disponibles)



            elif type(expresion_analizada.op) == ast.Div: 
                left_var = self.generar_codigo( expresion_analizada.left, modulo, variables_disponibles)
                right_var = self.generar_codigo( expresion_analizada.right, modulo, variables_disponibles)



            elif type(expresion_analizada.op) == ast.FloorDiv: 
                left_var = self.generar_codigo( expresion_analizada.left, modulo, variables_disponibles)
                right_var = self.generar_codigo( expresion_analizada.right, modulo, variables_disponibles)


            elif type(expresion_analizada.op) == ast.Mod: 
                left_var = self.generar_codigo( expresion_analizada.left, modulo, variables_disponibles)
                right_var = self.generar_codigo( expresion_analizada.right, modulo, variables_disponibles)



            elif type(expresion_analizada.op) == ast.Pow: 
                left_var = self.generar_codigo( expresion_analizada.left, modulo, variables_disponibles)
                right_var = self.generar_codigo( expresion_analizada.right, modulo, variables_disponibles)



            elif type(expresion_analizada.op) == ast.MatMult: 
                left_var = self.generar_codigo( expresion_analizada.left, modulo, variables_disponibles)
                right_var = self.generar_codigo( expresion_analizada.right, modulo, variables_disponibles)



            
        # ASIGNACIONES
        elif type(expresion_analizada) == ast.Assign:
            var_gen = self.generar_codigo( expresion_analizada.value, modulo, variables_disponibles=dict_arg)
            

        # NOMBRE / VARIABLE
        elif type(expresion_analizada) == ast.Name:
            valor = variables_disponibles[ expresion_analizada.id ]
        
        # VALOR CONSTANTE
        elif type(expresion_analizada) == ast.Constant:
            type_calc = ""
            
            if isinstance(valor, ast.Str):
                type_calc = "str"
            elif isinstance(valor, ast.Num):
                type_calc = type(valor.n).__name__
            elif isinstance(valor, ast.List):
                type_calc = "list"
            elif isinstance(valor, ast.Dict):
                type_calc = "dict"
            elif isinstance(valor, ast.Tuple):
                type_calc = "tuple"
                
            ir_type = None
            
            if isinstance(valor, ast.Str):
                ir_type = self.get_ir_type( type_calc, len(expresion_analizada.value) )
            else:
                ir_type = self.get_ir_type( type_calc )
            
            valor = ir.Constant( ir_type , expresion_analizada.value)
            
        # TUPLA
        elif type(expresion_analizada) == ast.Tuple:
            pass
        
        # LISTA
        elif type(expresion_analizada) == ast.List:
            pass
        
        # DICCIONARIO
        elif type(expresion_analizada) == ast.Dict:
            pass

        # INVOCACIÓN
        elif type(expresion_analizada) == ast.Call:
            pass
        
        elif type(expresion_analizada) == ast.Expr:
            pass
        
        return valor

if __name__ == "__main__":
        contenido = '''def calcular_suma(a: float, b: int) -> int:
    resultado = a + b
    return resultado
'''
    # def es_par(numero:int) -> int:
    #     return numero % 2 == 0

    # def listar_numeros_pares(lista: list[float]) -> list[float]:
    #     pares: List[int] = [] 
    #     for num in lista:
    #         if es_par(num):
    #             pares.append(num)
    #     return pares

    # # Ejemplo de uso de las funciones
    # suma = calcular_suma(5, 3)
    # print("La suma es:", suma)

    # numeros = [1, 2, 3, 4, 5, 6]
    # pares = listar_numeros_pares(numeros)
    # print("Números pares en la lista:", pares)

        modulo = ir.Module(name="modulo_principal")

        expresion_analizada = ast.parse(contenido)
        print(ast.dump(expresion_analizada))
        
        genCode = GeneradorCodigo()
        genCode.generar_codigo(expresion_analizada, modulo, 0)
        
        # analizador_semantico = AnalizadorSemantico()
        # arbol_abstracto = analizador_sintactico.generar_codigo("codigo_tres.txt")
        # analizador_semantico.analizar(expresion_analizada)
        # print( analizador_semantico.tabla_simbolos )
        
        #print(ast.dump(expresion_analizada, indent=4))
        