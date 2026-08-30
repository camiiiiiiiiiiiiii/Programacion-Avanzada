from logic.logica import estado_inicial, generador_turnos

# Estado de prueba
estado = {
    'posiciones': (0, 0, 0),
    'pierde_turno': (True, False, False),
    'actual': 0,
    'ganador': None,
    'valor_del_dado': None,
    'mensaje': ''
}

gen = generador_turnos(estado)

# Avanzamos un turno
sig1 = None
for _ in range(3):
    sig = next(gen)
    if not estado['pierde_turno'][sig]:
        sig1 = sig
        break
    else:
        nuevo_pierde = list(estado['pierde_turno'])
        nuevo_pierde[sig] = False
        estado = dict(estado, pierde_turno=tuple(nuevo_pierde))

print(f"Después del primer avance: actual={sig1}, pierde_turno={estado['pierde_turno']}")
# Debería ser actual=1, pierde_turno=(False, False, False)

# Avanzamos otro turno
sig2 = None
for _ in range(3):
    sig = next(gen)
    if not estado['pierde_turno'][sig]:
        sig2 = sig
        break
    else:
        nuevo_pierde = list(estado['pierde_turno'])
        nuevo_pierde[sig] = False
        estado = dict(estado, pierde_turno=tuple(nuevo_pierde))

print(f"Después del segundo avance: actual={sig2}, pierde_turno={estado['pierde_turno']}")
# Debería ser actual=2, pierde_turno=(False, False, False)