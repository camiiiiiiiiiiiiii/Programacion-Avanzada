from logic.datos_tablero import PUNTUACION_PARA_GANAR, CELDAS_ESPECIALES
from logic.utilidades import log
import random
# Estado inicial:
#   - todos los jugadores arrancan en la posición 0 (celda[9][0])
#   - ninguno pierde el turno -> pierde_turno = False xa cada jugador
#   - no hay ganador todavía -> ganador = None
#   - todavía no se tiró el dado -> valor_del_dado = None
#   - no se muestra ningún mensaje

def estado_inicial(cant_jugadores: int) -> dict:
    return {'posiciones': tuple(0 for _ in range(cant_jugadores)),
            'pierde_turno': tuple(False for _ in range(cant_jugadores)),
            'actual': 0,
            'ganador': None,
            'valor_del_dado': None,
            'mensaje': ''}

# Movimiento:
@log
def mover_jugador(estado: dict, idx_jugador: int, pasos_a_avanzar: int) -> dict:
    # Calculo la nueva posición usando la anterior y los pasos a avanzar que se obtuvieron en el dado
    nueva_posicion = estado['posiciones'][idx_jugador] + pasos_a_avanzar

    ''' Caso especial: si nos pasamos de las 35 casillas, significa que el jugador ganó.
        Decidimos que el programa tome la posición 35 para indicar que el jugador ganó,
        por lo que debemos setear la posición en 35.'''
    if nueva_posicion > PUNTUACION_PARA_GANAR:
        nueva_posicion = PUNTUACION_PARA_GANAR

    # Comprensión: reconstruimos todas las posiciones
    nuevas_posiciones = tuple(
        nueva_posicion if i == idx_jugador else p
        for i, p in enumerate(estado['posiciones'])
    )

    # devolvemso el diccionario estado que pasamos como input a la funcion, pero ahora con las nuevas posiciones
    nuevo_estado = dict(estado, posiciones = tuple(nuevas_posiciones))

    # Caso especial al retroceder dps de competencia:
    if (pasos_a_avanzar == -1) and checkear_si_hay_competencia(nuevo_estado, idx_jugador): # estoy retrocediendo, tengo que mirar si caigo donde hay otro. en ese caso voy otro para atrás
        return mover_jugador(nuevo_estado, idx_jugador, -1)

    return nuevo_estado

# Competencia (cuando dos jugadores terminan en la misma celda)
'''Si un jugador cae en la misma casilla que la de otro jugador, realizan una
competencia por quien se queda con la casilla, tirando el dado los dos. El que
obtenga el mayor valor permanece en la casilla y el que pierde, retrocede dos
casilleros. Si el perdedor vuelve a caer en una casilla ocupada por otro jugador,
retrocede una más.'''
@log
def resolver_competencia(estado: dict, idx_jugador_1: int, idx_jugador_2: int, dado1: int, dado2: int) -> dict:

    if dado1 > dado2: # jugador 1 gana => queda en la misma posicion => cambio posición jugador 2
        ganador, perdedor = idx_jugador_1, idx_jugador_2
    elif dado1 < dado2: # jugador 2 gana => queda en la misma posicion => cambio posición jugador 1
        ganador, perdedor = idx_jugador_2, idx_jugador_1
    else:
        return dict(estado, competencia_empate = True, mensaje = "Empate en competencia. Tirar de nuevo.")

    nuevo_estado = mover_jugador(estado, perdedor, -2)

    mensaje = f"Competencia: Jugador {ganador + 1} ({dado1}) vs Jugador {perdedor + 1} ({dado2}). Jugador {ganador + 1} gana!"

    return dict(nuevo_estado, mensaje = mensaje)

def checkear_si_hay_competencia(estado: dict, idx_jugador: int) -> bool:
    pos_actual = estado['posiciones'][idx_jugador]
    # Usamos filter para obtener los índices de los jugadores que están en la misma posición, excluyendo al actual
    otros = list(filter(lambda i: i != idx_jugador and estado['posiciones'][i] == pos_actual, range(len(estado['posiciones']))))
    return len(otros) > 0

# Registro global de efectos
EFECTOS_REGISTRY = {}

@log
def registrar_efecto(clave):
    """Decorador que registra una función en el registro de efectos."""
    def decorador(func):
        EFECTOS_REGISTRY[clave] = func
        return func
    return decorador

@registrar_efecto('P1')
def aplicar_p1(estado, idx_jugador, idx_castigado):
    """Aplica el efecto P1: el jugador idx_jugador castiga a idx_castigado."""
    nuevo_pierde_turno = list(estado['pierde_turno'])
    nuevo_pierde_turno[idx_castigado] = True
    return dict(
        estado,
        pierde_turno=tuple(nuevo_pierde_turno),
        mensaje=f"P1: Jugador {idx_jugador+1} castiga a Jugador {idx_castigado+1}"
    )

@registrar_efecto('P2')
@log
def aplicar_p2(estado, idx_jugador, **kwargs):
    nuevo_dado = kwargs.get('nuevo_dado')  # lo recibimos como argumento con nombre
    nuevo_estado = mover_jugador(estado, idx_jugador, nuevo_dado)
    return dict(nuevo_estado, mensaje=f"P2: Jugador {idx_jugador+1} tira de nuevo y avanza {nuevo_dado} lugares")

@registrar_efecto('P3')
@log
def aplicar_p3(estado, idx_jugador, **kwargs):
    nuevo_estado = mover_jugador(estado, idx_jugador, 2)
    return dict(nuevo_estado, mensaje=f"P3: Jugador {idx_jugador+1} avanza dos lugares")

@registrar_efecto('C1')
@log
def aplicar_c1(estado, idx_jugador, **kwargs):
    nuevo_pierde_turno = tuple(
        True if i == idx_jugador else p
        for i, p in enumerate(estado['pierde_turno'])
    )
    return dict(estado, pierde_turno=nuevo_pierde_turno, mensaje=f"C1: Jugador {idx_jugador+1} pierde el prox turno")

@registrar_efecto('C2')
@log
def aplicar_c2(estado, idx_jugador, **kwargs):
    nuevo_estado = mover_jugador(estado, idx_jugador, -3)
    return dict(nuevo_estado, mensaje=f"C2: Jugador {idx_jugador+1} retrodece 3 lugares")

@log
def aplicar_efecto_celda_especial(estado: dict, idx_jugador: int, nuevo_dado: int = None, idx_castigado: int = None) -> dict:
    posicion = estado['posiciones'][idx_jugador]
    clave = CELDAS_ESPECIALES[posicion]

    # Buscar la función en el registro
    func = EFECTOS_REGISTRY.get(clave)
    if func is None:
        # Si no hay efecto, devolvemos el estado sin cambios
        return estado

    # Caso especial: P1. Necesitamos un idx_castigado. Si no se pasa (modo auto) se genera random
    if clave == 'P1':
        # Si no se proporciona idx_castigado, elegir uno al azar (modo automático)
        if idx_castigado is None:
            posibles = [i for i in range(len(estado['posiciones'])) if i != idx_jugador]
            if posibles:
                idx_castigado = random.choice(posibles)
            else:
                # No hay otros jugadores, no se puede castigar
                return estado
        return func(estado, idx_jugador, idx_castigado)

    # Llamamos a la función pasando los argumentos fijos y extras en kwargs
    return func(estado, idx_jugador, nuevo_dado=nuevo_dado)
