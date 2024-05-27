from llvmlite import ir

# Crear un módulo LLVM.
modulo = ir.Module(name="modulo_ejemplo")

# Definir el tipo de retorno y los tipos de los argumentos de la función suma.
tipo_retorno = ir.IntType(32)
tipos_argumentos = (ir.IntType(32), ir.IntType(32))

# Crear la firma de la función suma.
funcion_tipo = ir.FunctionType(tipo_retorno, tipos_argumentos)

# Crear la función suma.
funcion_suma = ir.Function(modulo, funcion_tipo, name="suma")

# Nombrar los argumentos de la función suma.
x, y = funcion_suma.args
x.name = "x"
y.name = "y"

# Crear un bloque de entrada para la función suma.
bloque_suma = funcion_suma.append_basic_block(name="entrada")

# Crear un constructor IR para la función suma.
constructor_suma = ir.IRBuilder(bloque_suma)

# Sumar los argumentos de la función suma.
resultado_suma = constructor_suma.add(x, y, name="resultado")

# Retornar el resultado en la función suma.
constructor_suma.ret(resultado_suma)

# Crear una función main que invoque la función suma.
tipo_retorno_main = ir.IntType(32)
tipos_argumentos_main = []

# Crear la firma de la función main.
funcion_tipo_main = ir.FunctionType(tipo_retorno_main, tipos_argumentos_main)

# Crear la función main.
funcion_main = ir.Function(modulo, funcion_tipo_main, name="main")

# Crear un bloque de entrada para la función main.
bloque_main = funcion_main.append_basic_block(name="entrada")

# Crear un constructor IR para la función main.
constructor_main = ir.IRBuilder(bloque_main)

# Invocar la función suma con valores constantes.
valor1 = ir.Constant(ir.IntType(32), 10)
valor2 = ir.Constant(ir.IntType(32), 20)
resultado_llamada = constructor_main.call(funcion_suma, [valor1, valor2], name="llamada_suma")

# Retornar el resultado de la llamada a la función suma en la función main.
constructor_main.ret(resultado_llamada)

# Imprimir el módulo LLVM.
print(modulo)
