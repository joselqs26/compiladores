from llvmlite import ir
import sys
import ast

sys.path.append("/workspaces/compiladores/AnalizadorSemantico")

from analizador_semantico import AnalizadorSemantic

class GeneradorCodigo:
    
    # Expresion y objeto para la generacion de la tabla de símbolos
    expresion_general = None
    analizador_semantico = None
    
    # Diccionario general de variables disponibles como objetos de la libreria IR
    variables_disponibles = {}
    
    # Inicialización de las variables disponibles y la tabla de símbolos
    def __init__(self, expresion_general) -> None:
        self.expresion_general = expresion_general
        analizador_semantico = AnalizadorSemantic()
        analizador_semantico.analizar(self.expresion_general)
        self.analizador_semantico = analizador_semantico
        self.variables_disponibles = {}

    # Función de tranformación - Convierte el tipo de la tabla de simbolos
    # al tip correspondiente de la librería IR    
    def get_ir_type(self, string_type, length = 0):
        if string_type == "int":
            return ir.IntType(32)
        if string_type == "float":
            return ir.FloatType()
        elif string_type == "str":
            return ir.ArrayType(ir.IntType(8), length)
        elif "list" in string_type:
            type_interno = string_type.replace( "list[", '' ).replace( "]", '' )
            return ir.ArrayType( self.get_ir_type(type_interno) , length)
        elif "dict" in string_type:
            return ir.PointerType(ir.IntType(8))  # Simplification for a dictionary type

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
    def generar_codigo(self, expresion_analizada, dependencia, asignacion = None ):
        valor = None
        
        # CUERPO PRINCIPAL
        if type(expresion_analizada) == ast.Module:
            
            # Se genera el código para cada apartado independiente del body general
            for item in expresion_analizada.body:
                 self.generar_codigo( item, dependencia )
            
            valor = dependencia
        
        # DEFINICION DE FUNCION
        elif type(expresion_analizada) == ast.FunctionDef:
            # Se obtiene el tipo de retorno de la función
            funcion_semantica = self.analizador_semantico.obtener_informacion_funciones(expresion_analizada.name)
            # Se obtiene el tipo como objeto de librería IR
            tipo_retorno = self.get_ir_type(funcion_semantica["type"])
            # Se obtiene el listado de tipos de los argumentos
            tipos_argumentos = self.generar_codigo(expresion_analizada.args, dependencia)
            # Genera la firma de la función
            funcion_tipo = ir.FunctionType(tipo_retorno, tipos_argumentos)
            # Genera la estructura de la función en el contexto
            funcion = ir.Function(dependencia, funcion_tipo, name=expresion_analizada.name)
            
            # Crear el bloque inicial para las asignaciones
            bloque_inicio = funcion.append_basic_block(name="entry")
            constructor = ir.IRBuilder(bloque_inicio)
            
            # Itera por los argumentos para agregarlos como variables disponibles
            for index in range(len(expresion_analizada.args.args)):
                arg_semantico = expresion_analizada.args.args[index]
                arg_generado = funcion.args[index]
                arg_generado.name = arg_semantico.arg
                
                # Asignar los argumentos de la función
                if isinstance(arg_generado.type, ir.ArrayType):
                    # Convertir ArrayType a PointerType
                    arg_type = ir.PointerType(arg_generado.type.element)
                    arg_alloca = constructor.alloca(arg_type.pointee, name=arg_generado.name)
                    arg_generado_ptr = constructor.bitcast(arg_generado, arg_type)
                else:
                    arg_alloca = constructor.alloca(arg_generado.type, name=arg_generado.name)
                    arg_generado_ptr = arg_generado
                
                constructor.store(arg_generado_ptr, arg_alloca)
                self.variables_disponibles[arg_semantico.arg] = arg_alloca

            # Crear el bloque para el cuerpo de la función
            bloque = funcion.append_basic_block(name="Cuerpo de Funcion")
            constructor.position_at_end(bloque)
            
            # Se genera el código para cada apartado independiente del cuerpo de la función
            for item in expresion_analizada.body:
                self.generar_codigo(item, constructor)
            
            valor = funcion
            
        # ARGUMENTOS DE FUNCION
        elif type(expresion_analizada) == ast.arguments:        
            ls_tipos_argumentos = []

            # Calcula el tipo IR para cada argumento de una función
            for item in expresion_analizada.args:
                variable_semantica = self.analizador_semantico.obtener_informacion_variable(item.arg)
                tipo_variable = self.get_ir_type(variable_semantica["type"])
                
                # Convertir ArrayType a PointerType
                if isinstance(tipo_variable, ir.ArrayType):
                    tipo_variable = ir.PointerType(tipo_variable.element)
                
                # Manejar diccionarios
                if "dict" in variable_semantica["type"]:
                    key_type, value_type = variable_semantica["type"].replace("dict[", "").replace("]", "").split(", ")
                    key_ir_type = self.get_ir_type(key_type)
                    value_ir_type = self.get_ir_type(value_type)
                    # Crear una estructura que represente el diccionario
                    struct_type = ir.LiteralStructType([key_ir_type, value_ir_type])
                    tipo_variable = ir.PointerType(struct_type)
                
                ls_tipos_argumentos.append(tipo_variable)

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
            pass
            
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
            pass
        
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
                    valor = dependencia.add(left_var, right_var, name=asignacion) if asignacion else dependencia.sub(left_var, right_var)

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
                # Si el target es un string puro, debe generarse su código y agregarse como variable disponible            
                valor = self.generar_codigo(expresion_analizada.value, dependencia, asignacion=target)
                
                # Registro de la variable en el diccionario
                ir_type = self.get_ir_type(self.analizador_semantico.obtener_informacion_variable(target)["type"])
                alloca = dependencia.alloca(ir_type, name=target)
                dependencia.store(valor, alloca)
                self.variables_disponibles[target] = alloca
                
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
            
            # Articulado a ASIGNACIONES
            # Se retorna el objeto IR siempre que exista en las variables disponibles globales
            # En caso contrario, se resuelve un str para su posterior declaración
            if expresion_analizada.id in self.variables_disponibles:
                valor = self.variables_disponibles[expresion_analizada.id]
                # Si la variable es un puntero, cargar el valor apuntado
                if isinstance(valor.type, ir.PointerType):
                    valor = dependencia.load(valor)
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
            elementos = [self.generar_codigo(el, dependencia) for el in expresion_analizada.elts]
            if len(elementos) > 0:
                tipo_elemento = elementos[0].type
                tipo_lista = ir.ArrayType(tipo_elemento, len(elementos))
                alloca = dependencia.alloca(tipo_lista, name=asignacion)
                for i, elemento in enumerate(elementos):
                    ptr = dependencia.gep(alloca, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), i)], inbounds=True)
                    dependencia.store(elemento, ptr)
                valor = alloca
            else:
                raise ValueError("No se puede generar una lista vacía sin tipo.")
        
        # BUCLE FOR
        elif type(expresion_analizada) == ast.For:
            iter_var = expresion_analizada.target.id
            iter_list = self.generar_codigo(expresion_analizada.iter, dependencia)

            loop_block = dependencia.append_basic_block(name="loop")
            after_loop_block = dependencia.append_basic_block(name="afterloop")

            # Inicializar el índice del bucle
            index = ir.Constant(ir.IntType(32), 0)
            index_alloca = dependencia.alloca(index.type, name="index")
            dependencia.store(index, index_alloca)

            # Obtener el tamaño de la lista
            size = ir.Constant(ir.IntType(32), iter_list.type.pointee)
            cmp = dependencia.icmp_signed('<', dependencia.load(index_alloca), size)
            dependencia.cbranch(cmp, loop_block, after_loop_block)

            # Cuerpo del bucle
            dependencia.position_at_end(loop_block)

            # Obtener el elemento de la lista
            index = dependencia.load(index_alloca)
            element_ptr = dependencia.gep(iter_list, [index], inbounds=True)
            element = dependencia.load(element_ptr)
            self.variables_disponibles[iter_var] = element

            # Generar el cuerpo del bucle
            for stmt in expresion_analizada.body:
                self.generar_codigo(stmt, dependencia)

            # Incrementar el índice
            next_index = dependencia.add(index, ir.Constant(ir.IntType(32), 1))
            dependencia.store(next_index, index_alloca)

            # Saltar al inicio del bucle
            cmp = dependencia.icmp_signed('<', dependencia.load(index_alloca), size)
            dependencia.cbranch(cmp, loop_block, after_loop_block)

            # Después del bucle
            dependencia.position_at_end(after_loop_block)

        # DICCIONARIO
        elif type(expresion_analizada) == ast.Dict:
            # Inicializar la estructura del diccionario
            num_elements = len(expresion_analizada.keys)
            keys_type = ir.ArrayType(ir.IntType(32), num_elements)
            values_type = ir.ArrayType(ir.IntType(32), num_elements)
            keys_alloca = dependencia.alloca(keys_type, name="keys")
            values_alloca = dependencia.alloca(values_type, name="values")
            
            # Almacenar las claves y los valores
            for i, (key, value) in enumerate(zip(expresion_analizada.keys, expresion_analizada.values)):
                key_val = self.generar_codigo(key, dependencia)
                value_val = self.generar_codigo(value, dependencia)
                
                key_ptr = dependencia.gep(keys_alloca, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), i)], inbounds=True)
                value_ptr = dependencia.gep(values_alloca, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), i)], inbounds=True)
                
                dependencia.store(key_val, key_ptr)
                dependencia.store(value_val, value_ptr)
                
            valor = (keys_alloca, values_alloca)
        
        # INVOCACIÓN
        elif type(expresion_analizada) == ast.Call:
            pass
        
        elif type(expresion_analizada) == ast.Expr:
            valor = self.generar_codigo( expresion_analizada.value, dependencia )
        return valor

if __name__ == "__main__":

        contenido = '''def calcular_suma(a: float, b: int) -> float:
    resultado = a + b
    return resultado

'''
        contenido2 = '''def calcular_suma(a: float, b: int) -> float:
    resultado:float = 0.0
    if a > b:
        resultado = a - b
    else:
        resultado = a + b
    return resultado
'''

        contenido3 = '''def sumar_lista(lista: list[int]) -> int:
    suma: int = 0
    for numero in lista:
        suma += numero
    return suma
'''

        contenido4 = '''def procesar_diccionario(dic: dict[int, float]) -> float:
    suma: float = 0.0
    for clave in dic:
        suma += dic[clave]
    return suma
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

        dependencia = ir.Module(name="dependencia_principal")

        expresion_analizada = ast.parse(contenido4)
        #print(ast.dump(expresion_analizada))
        
        genCode = GeneradorCodigo(expresion_analizada)
        moduloComputado = genCode.generar_codigo(expresion_analizada, dependencia)
        
        print( moduloComputado )
        
        # analizador_semantico = AnalizadorSemantico()
        # arbol_abstracto = analizador_sintactico.generar_codigo("codigo_tres.txt")
        # analizador_semantico.analizar(expresion_analizada)
        # print( analizador_semantico.tabla_simbolos )
        
        #print(ast.dump(expresion_analizada, indent=4))