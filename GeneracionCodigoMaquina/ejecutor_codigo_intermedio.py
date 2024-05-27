from llvmlite import ir, binding
import sys

if __name__ == "__main__":
        nombre_archivo = sys.argv[1]
        
        # Leer el IR del archivo
        with open(nombre_archivo, 'r') as archivo:
            llvm_ir = archivo.read()

        # Inicializar el motor de ejecución LLVM
        binding.initialize()
        binding.initialize_native_target()
        binding.initialize_native_asmprinter()

        # Crear un objeto de módulo en memoria con el IR generado
        modulo_ll = binding.parse_assembly(llvm_ir)
        modulo_ll.verify()

        # Crear un motor JIT para ejecutar el código LLVM
        target_machine = binding.Target.from_default_triple().create_target_machine()
        with binding.create_mcjit_compiler(modulo_ll, target_machine) as execution_engine:
            # Obtener la función suma y prepararla para la ejecución
            execution_engine.finalize_object()
            execution_engine.run_static_constructors()

            # Obtener un puntero a la función suma compilada
            func_ptr = execution_engine.get_function_address("main")

            # Convertir el puntero a una función callable en Python
            from ctypes import CFUNCTYPE, c_float

            main_func = CFUNCTYPE(c_float)(func_ptr)

            # Invocar la función suma y obtener el resultado
            resultado = main_func()
            print(f"{resultado}")