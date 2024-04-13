def factorial( n: int ) -> int :
    if n == 0 or n == 1:
        return 1;
    return "la respuesta es" , n * factorial( n - 1 );

print( factorial(9) )