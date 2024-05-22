from llvmlite import ir

# Crear un módulo LLVM.
modulo = ir.Module(name="modulo_ejemplo")

# Definir el tipo de retorno y los tipos de los argumentos de la función.
tipo_retorno = ir.IntType(32)
tipos_argumentos = (ir.IntType(32), ir.IntType(32))

# Crear la firma de la función.
funcion_tipo = ir.FunctionType(tipo_retorno, tipos_argumentos)

# Crear la función.
funcion = ir.Function(modulo, funcion_tipo, name="suma")

# Nombrar los argumentos de la función.
x, y = funcion.args
x.name = "x"
y.name = "y"

# Crear un bloque de entrada para la función.
bloque = funcion.append_basic_block(name="entrada")

# Crear un constructor IR.
constructor = ir.IRBuilder(bloque)

# Sumar los argumentos de la función.
resultado = constructor.add(x, y, name="resultado")

# Retornar el resultado.
# constructor.ret(resultado)

# Imprimir el módulo LLVM generado.
print( type( resultado ) )
print( resultado.name )