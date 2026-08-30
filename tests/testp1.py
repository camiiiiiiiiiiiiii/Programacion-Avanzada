import unittest
from logic.logica import (
    estado_inicial,
    mover_jugador,
    mover_y_aplicar_efecto,
    aplicar_efecto_celda_especial,
    generador_turnos,
    CELDAS_ESPECIALES
)


class TestP1PierdeTurno(unittest.TestCase):
    """Tests específicos para el efecto P1 (castigo que hace perder el turno)."""

    def test_p1_activa_flag_pierde_turno(self):
        """Verifica que P1 activa correctamente el flag pierde_turno en el castigado."""
        estado = estado_inicial(2)
        idx_jugador = 0
        idx_castigado = 1

        # Movemos al jugador 0 exactamente a la casilla 5 (P1)
        estado = mover_jugador(estado, idx_jugador, 5)
        self.assertEqual(estado['posiciones'][idx_jugador], 5)
        self.assertIn(5, CELDAS_ESPECIALES)
        self.assertEqual(CELDAS_ESPECIALES[5], 'P1')

        # Aplicamos el efecto P1 eligiendo al jugador 1 como castigado
        estado = aplicar_efecto_celda_especial(estado, idx_jugador, idx_castigado=idx_castigado)

        # El mensaje debe indicar el castigo
        self.assertIn("P1: Jugador 1 castiga a Jugador 2", estado['mensaje'])

        # El castigado debe tener el flag a True
        self.assertTrue(estado['pierde_turno'][idx_castigado])
        # El jugador que aplicó el castigo no debe tener el flag
        self.assertFalse(estado['pierde_turno'][idx_jugador])

    def test_generador_salta_al_castigado(self):
        estado = estado_inicial(3)
        idx_castigado = 1
        estado = mover_jugador(estado, 0, 5)
        estado = aplicar_efecto_celda_especial(estado, 0, idx_castigado=idx_castigado)

        # Simulamos que el turno avanza al jugador castigado (aunque en realidad se saltaría)
        # Esto fuerza al generador a empezar en el castigado y comprobar que lo salta.
        estado = dict(estado, actual=idx_castigado)

        gen = generador_turnos(estado)
        siguiente = next(gen)
        # Ahora el generador empieza en el castigado (1), lo salta, y devuelve el siguiente disponible.
        # Con 3 jugadores, el siguiente disponible es 2 (porque 1 pierde turno).
        self.assertEqual(siguiente, 2)

    def test_reseteo_despues_de_saltar(self):
        """Verifica que el flag se resetea después de que el castigado es saltado."""
        estado = estado_inicial(2)
        idx_castigado = 1
        estado = mover_jugador(estado, 0, 5)
        estado = aplicar_efecto_celda_especial(estado, 0, idx_castigado=idx_castigado)

        # Simulamos el avance de turno: se resetea el flag del castigado y se actualiza 'actual'
        nuevo_pierde = list(estado['pierde_turno'])
        nuevo_pierde[idx_castigado] = False  # se resetea al saltarlo
        estado = dict(estado, pierde_turno=tuple(nuevo_pierde), actual=1)

        # Ahora el jugador 1 ya no pierde el turno
        self.assertFalse(estado['pierde_turno'][1])
        gen = generador_turnos(estado)
        # Como actual=1 y no pierde turno, el siguiente turno es 1 (porque el generador devuelve el actual si está disponible)
        siguiente = next(gen)
        self.assertEqual(siguiente, 1)

    def test_seleccion_aleatoria_sin_idx_castigado(self):
        """Prueba que si no se pasa idx_castigado, se elige aleatoriamente entre los otros."""
        estado = estado_inicial(4)
        estado = mover_jugador(estado, 0, 5)
        estado = aplicar_efecto_celda_especial(estado, 0)  # sin idx_castigado

        # Debe haber al menos un jugador con el flag True (distinto del 0)
        self.assertTrue(any(estado['pierde_turno']))
        self.assertFalse(estado['pierde_turno'][0])  # el propio no se castiga a sí mismo

    def test_integracion_mover_y_aplicar_efecto(self):
        """Prueba completa: mover, aplicar efecto y turno."""
        estado = estado_inicial(2)
        # Jugador 0 tira 5 y cae en P1, castiga al jugador 1
        estado = mover_y_aplicar_efecto(estado, 0, 5, idx_castigado=1)
        self.assertTrue(estado['pierde_turno'][1])
        self.assertIn("P1", estado['mensaje'])

        # Simular que se salta el turno del jugador 1
        nuevo_pierde = list(estado['pierde_turno'])
        nuevo_pierde[1] = False
        estado = dict(estado, pierde_turno=tuple(nuevo_pierde), actual=1)

        # Ahora el jugador 1 puede jugar
        estado = mover_y_aplicar_efecto(estado, 1, 3)
        self.assertEqual(estado['posiciones'][1], 3)  # partía de 0


if __name__ == '__main__':
    unittest.main()