import ast

code = '''
def greet(name):
    print("Hello, " + name + "!")

    for x in name:
        print(x)
    
greet("John")
'''

tree = ast.parse(code)
print( ast.dump(tree) )