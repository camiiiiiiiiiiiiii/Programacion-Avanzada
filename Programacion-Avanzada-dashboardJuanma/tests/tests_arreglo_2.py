import unittest
import random
from logic.logica import (
    estado_inicial,
    mover_jugador,
    resolver_competencia,
    checkear_si_hay_competencia,
    aplicar_efecto_celda_especial
)
from logic.datos_tablero import PUNTUACION_PARA_GANAR


class TestLogica(unittest.TestCase):

    def setUp(self):
        """Crear estados iniciales para cada test."""
        self.estado_2 = estado_inicial(2)
        self.estado_4 = estado_inicial(4)
        random.seed(42)  # Fijar semilla para resultados reproducibles

    # ---------- estado_inicial ----------
    def test_estado_inicial(self):
        estado = estado_inicial(3)
        self.assertEqual(len(estado['posiciones']), 3)
        self.assertEqual(estado['posiciones'], (0, 0, 0))
        self.assertEqual(estado['pierde_turno'], (False, False, False))
        self.assertEqual(estado['actual'], 0)
        self.assertIsNone(estado['ganador'])
        self.assertIsNone(estado['valor_del_dado'])
        self.assertEqual(estado['mensaje'], '')

    # ---------- mover_jugador ----------
    def test_mover_jugador_normal(self):
        estado = self.estado_2
        nuevo = mover_jugador(estado, 0, 3)
        self.assertEqual(nuevo['posiciones'][0], 3)
        self.assertEqual(nuevo['posiciones'][1], 0)  # El otro no se mueve

    def test_mover_jugador_supera_meta(self):
        estado = dict(self.estado_2, posiciones=(34, 0))
        nuevo = mover_jugador(estado, 0, 5)  # 34+5=39 > 35
        self.assertEqual(nuevo['posiciones'][0], PUNTUACION_PARA_GANAR)

    def test_mover_jugador_recursivo_competencia(self):
        """
        Si al retroceder (pasos negativos) caes en una casilla ocupada,
        se debe retroceder una casilla adicional (recursión).
        """
        # Jugador 0 en 5, jugador 1 en 3. Retrocedemos a 0 desde 5 con -2 -> cae en 3 (ocupado)
        estado = dict(
            posiciones=(5, 3),
            pierde_turno=(False, False),
            actual=0,
            ganador=None,
            valor_del_dado=None,
            mensaje=''
        )
        nuevo = mover_jugador(estado, 0, -2)
        # Debería quedar en 2 (porque al caer en 3, hay competencia y retrocede 1 más)
        self.assertEqual(nuevo['posiciones'][0], 2)
        self.assertEqual(nuevo['posiciones'][1], 3)

    # ---------- checkear_si_hay_competencia ----------
    def test_checkear_competencia_true(self):
        estado = dict(posiciones=(5, 5, 3))
        self.assertTrue(checkear_si_hay_competencia(estado, 0))
        self.assertTrue(checkear_si_hay_competencia(estado, 1))
        self.assertFalse(checkear_si_hay_competencia(estado, 2))

    def test_checkear_competencia_false(self):
        estado = dict(posiciones=(5, 6, 3))
        self.assertFalse(checkear_si_hay_competencia(estado, 0))
        self.assertFalse(checkear_si_hay_competencia(estado, 1))

    # ---------- resolver_competencia ----------
    def test_resolver_competencia_gana_jugador0(self):
        estado = dict(
            posiciones=(5, 5),
            pierde_turno=(False, False),
            actual=0,
            ganador=None,
            valor_del_dado=None,
            mensaje=''
        )
        nuevo = resolver_competencia(estado, 0, 1, 6, 3)
        self.assertEqual(nuevo['posiciones'][0], 5)  # se queda
        self.assertEqual(nuevo['posiciones'][1], 3)  # retrocede 2
        self.assertNotIn('competencia_empate', nuevo)

    def test_resolver_competencia_gana_jugador1(self):
        estado = dict(
            posiciones=(5, 5),
            pierde_turno=(False, False),
            actual=0,
            ganador=None,
            valor_del_dado=None,
            mensaje=''
        )
        nuevo = resolver_competencia(estado, 0, 1, 2, 5)
        self.assertEqual(nuevo['posiciones'][0], 3)
        self.assertEqual(nuevo['posiciones'][1], 5)
        self.assertNotIn('competencia_empate', nuevo)

    def test_resolver_competencia_empate(self):
        estado = dict(
            posiciones=(5, 5),
            pierde_turno=(False, False),
            actual=0,
            ganador=None,
            valor_del_dado=None,
            mensaje=''
        )
        nuevo = resolver_competencia(estado, 0, 1, 4, 4)
        self.assertTrue(nuevo.get('competencia_empate', False))
        self.assertEqual(nuevo['posiciones'], estado['posiciones'])  # sin cambios

    # ---------- aplicar_efecto_celda_especial ----------
    def test_aplicar_efecto_P1_con_castigo(self):
        # Jugador 0 en casilla 5 (P1), castiga a jugador 1
        estado = dict(
            posiciones=(5, 0, 0),
            pierde_turno=(False, False, False),
            actual=0,
            ganador=None,
            valor_del_dado=None,
            mensaje=''
        )
        nuevo = aplicar_efecto_celda_especial(estado, 0, idx_castigado=1)
        self.assertTrue(nuevo['pierde_turno'][1])
        self.assertFalse(nuevo['pierde_turno'][0])
        self.assertEqual(nuevo['posiciones'], estado['posiciones'])

    def test_aplicar_efecto_P1_auto_sin_castigo(self):
        # Sin idx_castigado, elige aleatorio (con semilla fija, elige el primer posible)
        estado = dict(
            posiciones=(5, 0, 0),
            pierde_turno=(False, False, False),
            actual=0,
            ganador=None,
            valor_del_dado=None,
            mensaje=''
        )
        random.seed(42)  # Asegura que random.choice([1,2]) devuelva 1
        nuevo = aplicar_efecto_celda_especial(estado, 0)
        self.assertTrue(nuevo['pierde_turno'][1])

    def test_aplicar_efecto_P2(self):
        # Casilla 11 es P2, nuevo_dado = 4
        estado = dict(
            posiciones=(11, 0),
            pierde_turno=(False, False),
            actual=0,
            ganador=None,
            valor_del_dado=None,
            mensaje=''
        )
        nuevo = aplicar_efecto_celda_especial(estado, 0, nuevo_dado=4)
        self.assertEqual(nuevo['posiciones'][0], 15)  # 11+4

    def test_aplicar_efecto_P3(self):
        # Casilla 22 es P3, avanza 2
        estado = dict(
            posiciones=(22, 0),
            pierde_turno=(False, False),
            actual=0,
            ganador=None,
            valor_del_dado=None,
            mensaje=''
        )
        nuevo = aplicar_efecto_celda_especial(estado, 0)
        self.assertEqual(nuevo['posiciones'][0], 24)  # 22+2

    def test_aplicar_efecto_C1(self):
        # Casilla 16 es C1, pierde turno
        estado = dict(
            posiciones=(16, 0),
            pierde_turno=(False, False),
            actual=0,
            ganador=None,
            valor_del_dado=None,
            mensaje=''
        )
        nuevo = aplicar_efecto_celda_especial(estado, 0)
        self.assertTrue(nuevo['pierde_turno'][0])
        self.assertEqual(nuevo['posiciones'], estado['posiciones'])

    def test_aplicar_efecto_C2(self):
        # Casilla 25 es C2, retrocede 3
        estado = dict(
            posiciones=(25, 0),
            pierde_turno=(False, False),
            actual=0,
            ganador=None,
            valor_del_dado=None,
            mensaje=''
        )
        nuevo = aplicar_efecto_celda_especial(estado, 0)
        self.assertEqual(nuevo['posiciones'][0], 22)  # 25-3


if __name__ == '__main__':
    unittest.main()