from llvmlite import ir
import sys
import ast

sys.path.append("/workspaces/compiladores/AnalizadorSemantico")

from analizador_semantico import AnalizadorSemantic

class GeneradorCodigo:
    
    # Expresion y objeto para la generacion de la tabla de símbolos
    expresion_general = None
    analizador_semantico = None
    modulo_computado = None
    
    # Diccionario general de variables disponibles como objetos de la libreria IR
    variables_disponibles = {}
    
    # Inicialización de las variables disponibles y la tabla de símbolos
    def __init__(self, expresion_general) -> None:
        self.expresion_general = expresion_general
        analizador_semantico = AnalizadorSemantic()
        analizador_semantico.analizar(self.expresion_general)
        self.modulo_computado = ir.Module(name="dependencia_principal")
        self.analizador_semantico = analizador_semantico
        self.variables_disponibles = {}

    # Función de tranformación - Convierte el tipo de la tabla de simbolos
    # al tip correspondiente de la librería IR    
    def get_ir_type(self, string_type, lenght = 0):
        if string_type == "int":
            return ir.IntType(32)
        if string_type == "float":
            return ir.FloatType()
        elif string_type == "str":
            return ir.ArrayType(ir.IntType(8), lenght)
        elif "list" in string_type:
            type_interno = string_type.replace( "list[", '' ).replace( "]", '' )
            return ir.ArrayType( self.get_ir_type(type_interno) , lenght)

    # Función de creación de archivo para ejecución de código
    # Almacena el codigo en el archivo con el nombre enviado como parametro 
    def guardar_codigo_intermedio(self, name_file):
        with open(name_file, 'w') as archivo:
            archivo.write(str( self.modulo_computado ))
        print(f"Módulo guardado en {name_file}")

    # Función de cohersion de tipos - Convierte una variable dada 
    # de un tipo a otro en el flujo del programa
    # dependencia         -> Objeto contexto de la librería IR. Normalmente un módulo o contructor
    #                        Permite la adicion de operaciones, variables y contextos de forma incremental
    # variable            -> Variable a convertir
    # tipo_final          -> Tipo final en el que se retornará la variable a convertir
    def transform_type(self, dependencia, variable, tipo_final):
        variable_transformada = variable
        
        if type( variable.type ) == tipo_final:
            return variable
        elif type( variable.type ) == ir.IntType and tipo_final == ir.FloatType:
            variable_transformada = dependencia.sitofp(variable, ir.FloatType())
            
        return variable_transformada

    # Función recursiva de generación de código
    # expresion_analizada -> Nodo de la librería AST. Permite recorrer el árbol 
    # dependencia         -> Objeto contexto de la librería IR. Normalmente un módulo o contructor
    #                        Permite la adicion de operaciones, variables y contextos de forma incremental
    # asignacion          -> Auxiliar para la creación de nuevas variables
    def generar_codigo(self, expresion_analizada = None, dependencia = None, asignacion = None ):
        valor = None
        
        # CUERPO PRINCIPAL
        if expresion_analizada is None and type(self.expresion_general) == ast.Module:
            
            tipo_retorno_main = ir.FloatType()
            tipos_argumentos_main = []

            # Crear la firma de la función main.
            funcion_tipo_main = ir.FunctionType(tipo_retorno_main, tipos_argumentos_main)

            # Crear la función main.
            funcion_main = ir.Function( self.modulo_computado , funcion_tipo_main, name="main")

            # Crear un bloque de entrada para la función main.
            bloque_main = funcion_main.append_basic_block(name="main")
            constructor_main = ir.IRBuilder(bloque_main)
            
            items = []
            
            # Se genera el código para cada apartado independiente del body general
            for item in self.expresion_general.body:
                items_val = self.generar_codigo( item, constructor_main ) 
                items.append( items_val )
                
            funcion_main.function_type.return_type = items[ len( items ) - 1 ].type 
            
            var_return = str( items[ len( items ) - 1 ] ).split( '=' )[0]
            constructor_main.ret( self.variables_disponibles[ var_return ] )
        
        # DEFINICION DE FUNCION
        elif type(expresion_analizada) == ast.FunctionDef:
            
            # Se obtiene el tipo de retorno de la función
            funcion_semantica = self.analizador_semantico.obtener_informacion_funciones( expresion_analizada.name )
            
            # Se obtiene el tipo como objeto de librería IR
            tipo_retorno = self.get_ir_type( funcion_semantica["type"] )
            
            # Se obtiene el listado de tipos de los argumentos
            tipos_argumentos = self.generar_codigo( expresion_analizada.args, dependencia)
            
            # Genera la firma de la función
            funcion_tipo = ir.FunctionType(tipo_retorno, tipos_argumentos)
            
            # Genera la estructura de la función en el contexto
            funcion = ir.Function(self.modulo_computado, funcion_tipo, name=expresion_analizada.name)
            
            self.variables_disponibles[ expresion_analizada.name ] = funcion
            
            # Itera por los argumentos para agregarlos como variables disponibles
            for index in range(len(expresion_analizada.args.args)):
                arg_semantico = expresion_analizada.args.args[index]
                
                arg_generado = funcion.args[index]
                arg_generado.name = arg_semantico.arg
                
                self.variables_disponibles[ arg_semantico.arg ] = arg_generado
            
            # Se crea el contexto para la ejecución de la función
            bloque = funcion.append_basic_block(name="function_body")
            constructor = ir.IRBuilder(bloque)
            
            # Se genera el código para cada apartado independiente del cuerpo de la función
            for item in expresion_analizada.body:
                self.generar_codigo( item, constructor )
            
            valor = funcion
            
        # ARGUMENTOS DE FUNCION
        elif type(expresion_analizada) == ast.arguments:        
            ls_tipos_argumentos = []
            
            # Cálcula el tipo IR para cada argumento de una función
            for item in expresion_analizada.args:
                variable_semantica = self.analizador_semantico.obtener_informacion_variable( item.arg )
                tipo_variable = self.get_ir_type( variable_semantica["type"] )
                ls_tipos_argumentos.append( tipo_variable )
            
            valor = ls_tipos_argumentos
            
        # RETORNO
        elif type(expresion_analizada) == ast.Return:
            # Se genera el código para la invoación de retorno y se agrega al contexto
            retorno = self.generar_codigo( expresion_analizada.value, dependencia)
            dependencia.ret( retorno )
            
        # ESTRUCTURA DE CONTROL - IF
        elif type(expresion_analizada) == ast.If:
            condicion = self.generar_codigo(expresion_analizada.test, dependencia)
            then_block = dependencia.append_basic_block(name="then")
            else_block = dependencia.append_basic_block(name="else")
            merge_block = dependencia.append_basic_block(name="ifcont")
            dependencia.cbranch(condicion, then_block, else_block)

            # Genera el código para el bloque 'then'
            dependencia.position_at_end(then_block)
            for item in expresion_analizada.body:
                self.generar_codigo(item, dependencia)
            dependencia.branch(merge_block)

            # Genera el código para el bloque 'else'
            dependencia.position_at_end(else_block)
            for item in expresion_analizada.orelse:
                self.generar_codigo(item, dependencia)
            dependencia.branch(merge_block)

            # Continúa con el bloque de merge
            dependencia.position_at_end(merge_block)
            
        # COMPARACION / Tipo AND o Tipo OR
        elif type(expresion_analizada) == ast.Compare:
            left_val = self.generar_codigo(expresion_analizada.left, dependencia)

            for operation, right in zip(expresion_analizada.ops, expresion_analizada.comparators):
                right_val = self.generar_codigo(right, dependencia)

                if type( left_val.type ) == ir.FloatType or type( right_val.type ) == ir.FloatType:
                    
                    # Cohersión de tipos de entero a float
                    left_val = self.transform_type( dependencia, left_val, ir.FloatType)
                    right_val = self.transform_type( dependencia, right_val, ir.FloatType)
                    
                    if isinstance(operation, ast.Eq):
                        valor = dependencia.fcmp_ordered('==', left_val, right_val)
                    elif isinstance(operation, ast.NotEq):
                        valor = dependencia.fcmp_ordered('!=', left_val, right_val)
                    elif isinstance(operation, ast.Lt):
                        valor = dependencia.fcmp_ordered('<', left_val, right_val)
                    elif isinstance(operation, ast.LtE):
                        valor = dependencia.fcmp_ordered('<=', left_val, right_val)
                    elif isinstance(operation, ast.Gt):
                        valor = dependencia.fcmp_ordered('>', left_val, right_val)
                    elif isinstance(operation, ast.GtE):
                        valor = dependencia.fcmp_ordered('>=', left_val, right_val)

                elif type( left_var.type ) == ir.IntType and type( right_var.type ) == ir.IntType:

                    if isinstance(operation, ast.Eq):
                        valor = dependencia.icmp_signed('==', left_val, right_val)
                    elif isinstance(operation, ast.NotEq):
                        valor = dependencia.icmp_signed('!=', left_val, right_val)
                    elif isinstance(operation, ast.Lt):
                        valor = dependencia.icmp_signed('<', left_val, right_val)
                    elif isinstance(operation, ast.LtE):
                        valor = dependencia.icmp_signed('<=', left_val, right_val)
                    elif isinstance(operation, ast.Gt):
                        valor = dependencia.icmp_signed('>', left_val, right_val)
                    elif isinstance(operation, ast.GtE):
                        valor = dependencia.icmp_signed('>=', left_val, right_val)
            
        # OPERACION BOOLEANA
        elif type(expresion_analizada) == ast.BoolOp:
            if isinstance(expresion_analizada.op, ast.And):
                initial = self.generar_codigo(expresion_analizada.values[0], dependencia)
                for value in expresion_analizada.values[1:]:
                    next_val = self.generar_codigo(value, dependencia)
                    initial = dependencia.and_(initial, next_val)
                valor = initial
            elif isinstance(expresion_analizada.op, ast.Or):
                initial = self.generar_codigo(expresion_analizada.values[0], dependencia)
                for value in expresion_analizada.values[1:]:
                    next_val = self.generar_codigo(value, dependencia)
                    initial = dependencia.or_(initial, next_val)
                valor = initial
        
        # OPERACION BINARIA
        elif type(expresion_analizada) == ast.BinOp:            
            left_var = self.generar_codigo( expresion_analizada.left, dependencia)
            right_var = self.generar_codigo( expresion_analizada.right, dependencia)
            
            if type(expresion_analizada.op) == ast.Add: 
                
                # Suma de Float
                if type( left_var.type ) == ir.FloatType or type( right_var.type ) == ir.FloatType:
                    
                    # Cohersión de tipos de entero a float
                    left_var = self.transform_type( dependencia, left_var, ir.FloatType)
                    right_var = self.transform_type( dependencia, right_var, ir.FloatType)
                    
                    valor = dependencia.fadd(left_var, right_var, name=asignacion) if asignacion else dependencia.fadd(left_var, right_var)
                
                # Suma de Int
                elif type( left_var.type ) == ir.IntType and type( right_var.type ) == ir.IntType:
                    valor = dependencia.add(left_var, right_var, name=asignacion) if asignacion else dependencia.add(left_var, right_var)

            elif type(expresion_analizada.op) == ast.Sub:
                
                # Resta de Float
                if type(left_var.type) == ir.FloatType or type(right_var.type) == ir.FloatType:
                    
                    # Cohersión de tipos de entero a float
                    left_var = self.transform_type( dependencia, left_var, ir.FloatType)
                    right_var = self.transform_type( dependencia, right_var, ir.FloatType)
                    
                    valor = dependencia.fsub(left_var, right_var, name=asignacion) if asignacion else dependencia.fsub(left_var, right_var)
                
                # Resta de Int
                elif type( left_var.type ) == ir.IntType and type( right_var.type ) == ir.IntType:
                    valor = dependencia.sub(left_var, right_var, name=asignacion) if asignacion else dependencia.sub(left_var, right_var)

            elif type(expresion_analizada.op) == ast.Mult:
                
                # Multiplicación de Float
                if type(left_var.type) == ir.FloatType or type(right_var.type) == ir.FloatType:
                    
                    # Cohersión de tipos de entero a float
                    left_var = self.transform_type( dependencia, left_var, ir.FloatType)
                    right_var = self.transform_type( dependencia, right_var, ir.FloatType)
                    
                    valor = dependencia.fmul(left_var, right_var, name=asignacion) if asignacion else dependencia.fmul(left_var, right_var)
                
                # Multiplicación de Int
                elif type( left_var.type ) == ir.IntType and type( right_var.type ) == ir.IntType:
                    valor = dependencia.mul(left_var, right_var, name=asignacion) if asignacion else dependencia.mul(left_var, right_var)

            elif type(expresion_analizada.op) == ast.Div:
                
                # División de Float
                if type(left_var.type) == ir.FloatType or type(right_var.type) == ir.FloatType:
                    
                    # Cohersión de tipos de entero a float
                    left_var = self.transform_type( dependencia, left_var, ir.FloatType)
                    right_var = self.transform_type( dependencia, right_var, ir.FloatType)
                    
                    valor = dependencia.fdiv(left_var, right_var, name=asignacion) if asignacion else dependencia.fdiv(left_var, right_var)
                
                # División de Int
                elif type( left_var.type ) == ir.IntType and type( right_var.type ) == ir.IntType:
                    valor = dependencia.sdiv(left_var, right_var, name=asignacion) if asignacion else dependencia.sdiv(left_var, right_var)

            elif type(expresion_analizada.op) == ast.FloorDiv:
                
                # División entera de Float
                if type(left_var.type) == ir.FloatType or type(right_var.type) == ir.FloatType:
                    raise TypeError("Floor division no es compatible con float.")
                
                # División entera de Int
                elif type( left_var.type ) == ir.IntType and type( right_var.type ) == ir.IntType:
                    valor = dependencia.sdiv(left_var, right_var, name=asignacion) if asignacion else dependencia.sdiv(left_var, right_var)


            elif type(expresion_analizada.op) == ast.Mod:
                
                # Módulo de Float
                if type(left_var.type) == ir.FloatType or type(right_var.type) == ir.FloatType:
                    raise TypeError("Modulo no es compatible con float.")
                
                # Módulo de Int
                else:
                    valor = dependencia.srem(left_var, right_var, name=asignacion) if asignacion else dependencia.srem(left_var, right_var)
            
        # ASIGNACIONES
        elif type(expresion_analizada) == ast.Assign:
            
            target = self.generar_codigo(expresion_analizada.targets[0], dependencia)
        
            if isinstance(target, str):
                # Si el target es un string puro, debe generase su código y agregarse como variable disponible            
                valor = self.generar_codigo(expresion_analizada.value, dependencia, asignacion=target)
                
                # Registro de la variable en el diccionario
                ir_type = self.get_ir_type(self.analizador_semantico.obtener_informacion_variable(target)["type"])
                
                self.variables_disponibles[target] = valor
                
            else:
                # Si el target es una clase más compleja como una variable existente,
                # debe generarse su código, y posteriormente actualizar la variable disponible de forma inmediata
                valor = self.generar_codigo(expresion_analizada.value, dependencia, asignacion=target.name)
                self.variables_disponibles[target.name] = valor
            
        # ASIGNACIONES ANOTADAS
        elif type(expresion_analizada) == ast.AnnAssign:
            # Obtener el nombre del target y su tipo
            target = expresion_analizada.target.id
            tipo_anotado = self.get_ir_type(expresion_analizada.annotation.id)
            
            # Generar el valor a asignar
            valor = self.generar_codigo(expresion_analizada.value, dependencia, asignacion=target)
            
            # Registrar la variable en el diccionario de variables disponibles
            alloca = dependencia.alloca(tipo_anotado, name=target)
            dependencia.store(valor, alloca)
            self.variables_disponibles[target] = alloca

        # NOMBRE / VARIABLE
        elif type(expresion_analizada) == ast.Name:
            
            # Artículado a ASIGNACIONES
            # Se retorna el objeto IR siempre que exista en las variables disponibles globales
            # En caso contrarío, se resuelve un str para su posterior declaración
            if expresion_analizada.id in self.variables_disponibles:
                valor = self.variables_disponibles[ expresion_analizada.id ]
            else:
                valor = expresion_analizada.id
        
        # VALOR CONSTANTE
        elif type(expresion_analizada) == ast.Constant:
            type_calc = ""
            if isinstance(expresion_analizada.value, str):
                type_calc = "str"
            elif isinstance(expresion_analizada.value, (int, float)):
                type_calc = type(expresion_analizada.value).__name__
            elif isinstance(expresion_analizada.value, list):
                type_calc = "list"
            elif isinstance(expresion_analizada.value, dict):
                type_calc = "dict"
            elif isinstance(expresion_analizada.value, tuple):
                type_calc = "tuple"
            
            ir_type = self.get_ir_type(type_calc, len(expresion_analizada.value) if type_calc == "str" else 0)
            valor = ir.Constant(ir_type, expresion_analizada.value)
            
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
            ls_tipos_argumentos = []
            
            # Cálcula el tipo IR para cada argumento de una función
            for item in expresion_analizada.args:
                variable = self.generar_codigo( item, dependencia )
                ls_tipos_argumentos.append( variable )
            
            valor = dependencia.call(
                self.variables_disponibles[ expresion_analizada.func.id ], 
                ls_tipos_argumentos
            )
        
        elif type(expresion_analizada) == ast.Expr:
            valor = self.generar_codigo( expresion_analizada.value, dependencia )
            
        self.variables_disponibles[ str( valor ).split( '=' )[0] ] = valor
        return valor

if __name__ == "__main__":

        contenido = '''def calcular_suma(a: float, b: int) -> float:
    resultado = a + b
    return resultado
    
calcular_suma(3.0, 4)
'''
        contenido2 = '''def calcular_suma(a: float, b: int) -> float:
    resultado:float = 0.0
    if a > b:
        resultado = a - b
    else:
        resultado = a + b
    return resultado
    
calcular_suma(3.0, 4)
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

        expresion_analizada = ast.parse(contenido)
        #print(ast.dump(expresion_analizada))
        
        genCode = GeneradorCodigo(expresion_analizada)
        genCode.generar_codigo()
        genCode.guardar_codigo_intermedio( "codigo_intermedio.ll" )
        
        # analizador_semantico = AnalizadorSemantico()
        # arbol_abstracto = analizador_sintactico.generar_codigo("codigo_tres.txt")
        # analizador_semantico.analizar(expresion_analizada)
        # print( analizador_semantico.tabla_simbolos )
        
        #print(ast.dump(expresion_analizada, indent=4))
        