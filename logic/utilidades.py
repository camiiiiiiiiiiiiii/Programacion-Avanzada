import functools

def log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Imprimir llamada
        print(f"[LOG] Llamando a {func.__name__} con args={args}, kwargs={kwargs}")
        # Ejecutar la función
        resultado = func(*args, **kwargs)
        # Imprimir resultado (si es un dict, mostramos el mensaje si existe)
        if isinstance(resultado, dict):
            mensaje = resultado.get('mensaje', 'sin mensaje')
            print(f"[LOG] {func.__name__} retornó: {mensaje}")
        else:
            print(f"[LOG] {func.__name__} retornó: {resultado}")
        return resultado
    return wrapper