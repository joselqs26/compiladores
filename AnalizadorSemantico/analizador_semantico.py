#pip install prettytable
import ast
#from analizador_sintactico import AnalizadorSintactico
from prettytable import PrettyTable

class AnalizadorSemantic:
    def __init__(self):
        self.tabla_simbolos = []
        self.functions = []

    def analizar(self, arbol):
        self.visit(arbol, "global") 
        self.imprimir_tabla_simbolos()

    def visit(self, nodo, ambito):
        if isinstance(nodo, ast.FunctionDef):
            for arg in nodo.args.args:
                if isinstance(arg.annotation, ast.Name):
                    self.agregar_variable(arg.arg, arg.annotation.id, nodo.name) 
                elif isinstance(arg.annotation, ast.Subscript): 
                    tipo_dato = self.obtener_tipo_subscript(arg.annotation)
                    self.agregar_variable(arg.arg, f"list[{tipo_dato}]", nodo.name) 
                    
            ambito = nodo.name 

            for statement in nodo.body:
                if isinstance(statement, ast.Return):
                    if isinstance(arg.annotation, ast.Name):
                        tipo_dato_retorno = nodo.returns.id if nodo.returns else "None"
                        name_function = nodo.name
                        return_function = tipo_dato_retorno
                        self.functions.append({"name": name_function, "type": return_function})
                    elif isinstance(arg.annotation, ast.Subscript): 
                        name_function = nodo.name
                        tipo_dato = self.obtener_tipo_subscript(arg.annotation)
                        self.functions.append({"name": name_function, "type": f"list[{tipo_dato}]"})

                elif isinstance(statement, ast.AnnAssign):
                    if isinstance(statement.target, ast.Name):
                        if isinstance(statement.annotation, ast.Name):
                            self.agregar_variable(statement.target.id, statement.annotation.id, ambito)
                        elif isinstance(statement.annotation, ast.Subscript):
                            tipo_dato = self.obtener_tipo_subscript(statement.annotation)
                            self.agregar_variable(statement.target.id, f"list[{tipo_dato}]", ambito)
                        

        elif isinstance(nodo, ast.Assign):
            for target in nodo.targets:

                if isinstance(target, ast.Name):
                    valor = nodo.value
                    tipo_dato = self.obtener_tipo_dato(valor)
                    self.agregar_variable(target.id, tipo_dato, ambito)   
  
        for child_node in ast.iter_child_nodes(nodo):
            self.visit(child_node, ambito)

    def obtener_tipo_subscript(self, tipo_subscript):
        if isinstance(tipo_subscript.slice, ast.Name):
            return tipo_subscript.slice.id
        elif isinstance(tipo_subscript.slice, ast.Subscript):
            return f"list[{self.obtener_tipo_subscript(tipo_subscript.slice.id)}]"
        else:
            return "None"
    
    def agregar_variable(self, nombre, tipo, ambito_actual):
        self.tabla_simbolos.append({"variable": nombre, "type": tipo, "scope": ambito_actual})

    def obtener_tipo_dato(self, valor):     
        if isinstance(valor, ast.Str):
            return "str"
        elif isinstance(valor, ast.Num):
            return type(valor.n).__name__
        elif isinstance(valor, ast.List):
            if valor.elts:
                tipos_elementos = {self.obtener_tipo_dato(el) for el in valor.elts}
                return f"list[{tipos_elementos.pop()}]"
            else:
                return "list"
        elif isinstance(valor, ast.Dict):
            return "dict"
        elif isinstance(valor, ast.Tuple):
            return "tuple"
        elif isinstance(valor, ast.NameConstant):
            return str(type(valor.value).__name__)
        elif isinstance(valor, ast.UnaryOp):  
            return self.obtener_tipo_dato(valor.operand)
        elif isinstance(valor, ast.BinOp): 
            return self.obtener_tipo_dato(valor.left)
        elif isinstance(valor, ast.Name):
        # Si es una variable, buscar su tipo en la tabla de símbolos
            for simbolo in self.tabla_simbolos:
                if simbolo["variable"] == valor.id:
                    return simbolo["type"]
        elif isinstance(valor, ast.Call): 
        #Cuando es funcion, busca en la lista que tipo de dato que esta retorna    
            for func in self.functions:
                if func["name"] == valor.func.id:
                    return func["type"]
        else:
            return "desconocido"


    def imprimir_tabla_simbolos(self):
        tabla = PrettyTable()
        tabla.field_names = ["Variable", "Tipo", "Ámbito"] 
        
        for simbolo in self.tabla_simbolos:
            tabla.add_row([simbolo["variable"], simbolo["type"], simbolo["scope"]]) 

        print(tabla)

    def obtener_informacion_variable(self, name):
        for simbolo in self.tabla_simbolos:
                if simbolo["variable"] == name:
                    return {'name': simbolo["variable"], 'type': simbolo["type"], 'scope': simbolo["scope"]}
                
    def obtener_informacion_funciones(self, name):
        for simbolo in self.functions:
                if simbolo["name"] == name:
                    return {'name': simbolo["name"], 'type': simbolo["type"]}            


# analizador_sintactico = AnalizadorSintactico()
# analizador_semantico = AnalizadorSemantico()
# arbol_abstracto = analizador_sintactico.analizar_codigo("codigo_tres.txt")
# analizador_semantico.analizar(arbol_abstracto)
