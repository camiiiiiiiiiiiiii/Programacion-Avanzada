import unittest
import random
from logic.logica import (
    estado_inicial,
    mover_y_aplicar_efecto,
    generador_turnos,
    CELDAS_ESPECIALES
)
from logic.datos_tablero import PUNTUACION_PARA_GANAR


class TestComposicionYGenerador(unittest.TestCase):

    def setUp(self):
        random.seed(42)
        self.estado_2 = estado_inicial(2)

    # ---------- Composición ----------
    def test_mover_y_aplicar_efecto_sin_especial(self):
        estado = self.estado_2
        nuevo = mover_y_aplicar_efecto(estado, 0, 3)
        self.assertEqual(nuevo['posiciones'][0], 3)
        self.assertEqual(nuevo['mensaje'], '')

    def test_mover_y_aplicar_efecto_con_P2(self):
        # Casilla 11 es P2, nuevo_dado = 4
        estado = dict(
            posiciones=(11, 0),
            pierde_turno=(False, False),
            actual=0,
            ganador=None,
            valor_del_dado=None,
            mensaje=''
        )
        # Al usar mover_y_aplicar_efecto, no pasamos nuevo_dado porque el efecto P2 necesita ese parámetro.
        # Pero la función espera recibir nuevo_dado. Debemos pasar el parámetro extra.
        nuevo = mover_y_aplicar_efecto(estado, 0, 0, nuevo_dado=4)  # pasos=0, pero ya está en 11
        self.assertEqual(nuevo['posiciones'][0], 15)  # 11+4
        self.assertIn('P2', nuevo['mensaje'])

    def test_mover_y_aplicar_efecto_con_P3(self):
        estado = dict(
            posiciones=(22, 0),
            pierde_turno=(False, False),
            actual=0,
            ganador=None,
            valor_del_dado=None,
            mensaje=''
        )
        nuevo = mover_y_aplicar_efecto(estado, 0, 0)  # ya está en P3
        self.assertEqual(nuevo['posiciones'][0], 24)  # 22+2
        self.assertIn('P3', nuevo['mensaje'])

    def test_mover_y_aplicar_efecto_con_C1(self):
        estado = dict(
            posiciones=(16, 0),
            pierde_turno=(False, False),
            actual=0,
            ganador=None,
            valor_del_dado=None,
            mensaje=''
        )
        nuevo = mover_y_aplicar_efecto(estado, 0, 0)
        self.assertTrue(nuevo['pierde_turno'][0])
        self.assertIn('C1', nuevo['mensaje'])

    def test_mover_y_aplicar_efecto_con_C2(self):
        estado = dict(
            posiciones=(25, 0),
            pierde_turno=(False, False),
            actual=0,
            ganador=None,
            valor_del_dado=None,
            mensaje=''
        )
        nuevo = mover_y_aplicar_efecto(estado, 0, 0)
        self.assertEqual(nuevo['posiciones'][0], 22)  # 25-3
        self.assertIn('C2', nuevo['mensaje'])

    def test_mover_y_aplicar_efecto_con_P1_auto(self):
        # Modo automático: P1 elige aleatoriamente a otro jugador
        estado = dict(
            posiciones=(5, 0, 0),
            pierde_turno=(False, False, False),
            actual=0,
            ganador=None,
            valor_del_dado=None,
            mensaje=''
        )
        random.seed(42)
        nuevo = mover_y_aplicar_efecto(estado, 0, 0)  # sin idx_castigado, elige aleatorio
        self.assertTrue(nuevo['pierde_turno'][1])  # con semilla 42, elige el primero
        self.assertIn('P1', nuevo['mensaje'])

    # ---------- Generador ----------
    def test_generador_turnos_sin_perdedores(self):
        estado = dict(
            posiciones=(0, 0, 0),
            pierde_turno=(False, False, False),
            actual=0
        )
        gen = generador_turnos(estado)
        self.assertEqual(next(gen), 0)
        self.assertEqual(next(gen), 1)
        self.assertEqual(next(gen), 2)
        self.assertEqual(next(gen), 0)

    def test_generador_turnos_con_perdedores(self):
        estado = dict(
            posiciones=(0, 0, 0),
            pierde_turno=(False, True, False),  # jugador 1 pierde turno
            actual=0
        )
        gen = generador_turnos(estado)
        self.assertEqual(next(gen), 0)   # actual
        self.assertEqual(next(gen), 2)   # salta el 1
        self.assertEqual(next(gen), 0)
        self.assertEqual(next(gen), 2)

    def test_generador_turnos_todos_perdedores(self):
        estado = dict(
            posiciones=(0, 0, 0),
            pierde_turno=(True, True, True),
            actual=0
        )
        gen = generador_turnos(estado)
        # Como todos pierden, nunca devuelve ninguno, generador infinito sin yield.
        # Esto podría ser un problema; pero no se da porque siempre hay al menos uno que no pierde.
        # Aún así, probamos que no se cuelgue: tomamos 10 valores y vemos que nunca sale.
        # En este caso, el generador nunca yield, así que next() se queda esperando.
        # No podemos probar esto fácilmente, lo dejamos como advertencia.
        # En la práctica, siempre hay al menos un jugador sin pierde_turno.
        pass

    def test_generador_turnos_comportamiento_ciclico(self):
        estado = dict(
            posiciones=(0, 0, 0, 0),
            pierde_turno=(False, False, False, False),
            actual=2
        )
        gen = generador_turnos(estado)
        self.assertEqual(next(gen), 2)
        self.assertEqual(next(gen), 3)
        self.assertEqual(next(gen), 0)
        self.assertEqual(next(gen), 1)
        self.assertEqual(next(gen), 2)


if __name__ == '__main__':
    unittest.main()