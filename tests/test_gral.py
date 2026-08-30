import unittest
import random
from logic.logica import (
    estado_inicial,
    mover_jugador,
    resolver_competencia,
    checkear_si_hay_competencia,
    aplicar_efecto_celda_especial,
    generador_turnos,
    mover_y_aplicar_efecto
)
from logic.datos_tablero import PUNTUACION_PARA_GANAR, CELDAS_ESPECIALES


class TestLogicaCompleto(unittest.TestCase):

    def setUp(self):
        """Semilla fija para reproducibilidad en tests que usan random."""
        random.seed(42)
        self.estado_2 = estado_inicial(2)
        self.estado_3 = estado_inicial(3)
        self.estado_4 = estado_inicial(4)

    # ========== 1. ESTADO INICIAL ==========
    def test_estado_inicial_cantidad(self):
        for n in [2, 3, 4]:
            estado = estado_inicial(n)
            self.assertEqual(len(estado['posiciones']), n)
            self.assertEqual(estado['posiciones'], (0,) * n)
            self.assertEqual(estado['pierde_turno'], (False,) * n)
            self.assertEqual(estado['actual'], 0)
            self.assertIsNone(estado['ganador'])
            self.assertIsNone(estado['valor_del_dado'])
            self.assertEqual(estado['mensaje'], '')

    def test_estado_inicial_inmutable(self):
        estado = estado_inicial(3)
        pos_original = estado['posiciones']
        estado['posiciones'] = (1, 2, 3)  # modificación directa
        self.assertNotEqual(estado['posiciones'], pos_original)  # pero no debe afectar a futuros estados

    # ========== 2. MOVIMIENTO BÁSICO ==========
    def test_mover_jugador_avance_normal(self):
        estado = self.estado_3
        nuevo = mover_jugador(estado, 0, 3)
        self.assertEqual(nuevo['posiciones'][0], 3)
        self.assertEqual(nuevo['posiciones'][1], 0)
        self.assertEqual(nuevo['posiciones'][2], 0)
        # estado original no se modifica
        self.assertEqual(estado['posiciones'][0], 0)

    def test_mover_jugador_limite_superior(self):
        estado = self.estado_2
        # Poner al jugador 0 en 33, tira 5 -> 38, debe quedar en 35
        estado_mod = dict(estado, posiciones=(33, 0))
        nuevo = mover_jugador(estado_mod, 0, 5)
        self.assertEqual(nuevo['posiciones'][0], PUNTUACION_PARA_GANAR)

    def test_mover_jugador_limite_inferior(self):
        estado = self.estado_2
        # Jugador 0 en 2, retrocede -5 -> debe quedar en 0
        estado_mod = dict(estado, posiciones=(2, 5))
        nuevo = mover_jugador(estado_mod, 0, -5)
        self.assertEqual(nuevo['posiciones'][0], 0)
        # El otro jugador no se modifica
        self.assertEqual(nuevo['posiciones'][1], 5)

    def test_mover_jugador_retroceso_sin_ocupado(self):
        estado = self.estado_3
        estado_mod = dict(estado, posiciones=(5, 3, 8))
        nuevo = mover_jugador(estado_mod, 0, -2)  # de 5 a 3, pero 3 está ocupado por jugador 1
        # Esperamos que retroceda uno más: 3 -> 2 (si 2 está libre)
        self.assertEqual(nuevo['posiciones'][0], 2)
        self.assertEqual(nuevo['posiciones'][1], 3)
        self.assertEqual(nuevo['posiciones'][2], 8)

    def test_mover_jugador_retroceso_con_encadenado(self):
        # Ocupar 3, 2, 1; jugador 0 en 5 retrocede -2 -> cae en 3 (ocupado) -> -1 -> 2 (ocupado) -> -1 -> 1 (ocupado) -> -1 -> 0
        estado = dict(
            posiciones=(5, 3, 2, 1),
            pierde_turno=(False, False, False, False),
            actual=0,
            ganador=None,
            valor_del_dado=None,
            mensaje=''
        )
        nuevo = mover_jugador(estado, 0, -2)
        self.assertEqual(nuevo['posiciones'][0], 0)
        # Los demás no cambian
        self.assertEqual(nuevo['posiciones'][1], 3)
        self.assertEqual(nuevo['posiciones'][2], 2)
        self.assertEqual(nuevo['posiciones'][3], 1)

    def test_mover_jugador_recursion_limit(self):
        # No debería entrar en recursión infinita aunque todas las casillas estén ocupadas
        estado = dict(
            posiciones=(4, 3, 2, 1, 0),  # 5 jugadores, todas ocupadas desde 0 hasta 4
            pierde_turno=(False, False, False, False, False),
            actual=0,
            ganador=None,
            valor_del_dado=None,
            mensaje=''
        )
        nuevo = mover_jugador(estado, 0, -2)  # de 4 a 2 -> ocupado, recursión hasta 0
        self.assertEqual(nuevo['posiciones'][0], 0)

    # ========== 3. COMPETENCIA ==========
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
        self.assertEqual(nuevo['posiciones'], estado['posiciones'])

    def test_resolver_competencia_retroceso_con_ocupado(self):
        # Jugador 0 en 5, jugador 1 en 5, jugador 2 en 3. Jugador 1 pierde y retrocede de 5 a 3, pero 3 ocupado -> debe retroceder a 2
        estado = dict(
            posiciones=(5, 5, 3),
            pierde_turno=(False, False, False),
            actual=0,
            ganador=None,
            valor_del_dado=None,
            mensaje=''
        )
        # Gana jugador 0 (dado1=6, dado2=3) -> perdedor es jugador 1
        nuevo = resolver_competencia(estado, 0, 1, 6, 3)
        self.assertEqual(nuevo['posiciones'][0], 5)
        self.assertEqual(nuevo['posiciones'][1], 2)  # retrocede 2 y luego 1 más por ocupado
        self.assertEqual(nuevo['posiciones'][2], 3)

    # ========== 4. CHECKEAR COMPETENCIA ==========
    def test_checkear_si_hay_competencia_true(self):
        estado = dict(posiciones=(5, 5, 3))
        self.assertTrue(checkear_si_hay_competencia(estado, 0))
        self.assertTrue(checkear_si_hay_competencia(estado, 1))
        self.assertFalse(checkear_si_hay_competencia(estado, 2))

    def test_checkear_si_hay_competencia_false(self):
        estado = dict(posiciones=(5, 6, 3))
        self.assertFalse(checkear_si_hay_competencia(estado, 0))
        self.assertFalse(checkear_si_hay_competencia(estado, 1))

    # ========== 5. EFECTOS ESPECIALES ==========
    def test_efecto_P1_con_castigo(self):
        estado = dict(
            posiciones=(5, 0, 0),  # jugador 0 en P1
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
        self.assertEqual(nuevo['mensaje'], "P1: Jugador 1 castiga a Jugador 2")

    def test_efecto_P1_sin_castigo_auto(self):
        # Modo automático: elige aleatoriamente (con semilla fija)
        estado = dict(
            posiciones=(5, 0, 0),
            pierde_turno=(False, False, False),
            actual=0,
            ganador=None,
            valor_del_dado=None,
            mensaje=''
        )
        random.seed(42)  # asegura que elija el primer posible (índice 1)
        nuevo = aplicar_efecto_celda_especial(estado, 0)
        self.assertTrue(nuevo['pierde_turno'][1])
        self.assertFalse(nuevo['pierde_turno'][0])
        self.assertEqual(nuevo['mensaje'], "P1: Jugador 1 castiga a Jugador 2")

    def test_efecto_P1_sin_otros_jugadores(self):
        # Solo 1 jugador? No debería ocurrir, pero por seguridad
        estado = dict(
            posiciones=(5,),
            pierde_turno=(False,),
            actual=0,
            ganador=None,
            valor_del_dado=None,
            mensaje=''
        )
        nuevo = aplicar_efecto_celda_especial(estado, 0)
        # No debe modificar nada
        self.assertEqual(nuevo, estado)

    def test_efecto_P2(self):
        estado = dict(
            posiciones=(11, 0),
            pierde_turno=(False, False),
            actual=0,
            ganador=None,
            valor_del_dado=None,
            mensaje=''
        )
        nuevo = aplicar_efecto_celda_especial(estado, 0, nuevo_dado=4)
        self.assertEqual(nuevo['posiciones'][0], 15)
        self.assertEqual(nuevo['mensaje'], "P2: Jugador 1 tira de nuevo y avanza 4 lugares")

    def test_efecto_P3(self):
        estado = dict(
            posiciones=(22, 0),
            pierde_turno=(False, False),
            actual=0,
            ganador=None,
            valor_del_dado=None,
            mensaje=''
        )
        nuevo = aplicar_efecto_celda_especial(estado, 0)
        self.assertEqual(nuevo['posiciones'][0], 24)
        self.assertEqual(nuevo['mensaje'], "P3: Jugador 1 avanza dos lugares")

    def test_efecto_C1(self):
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
        self.assertEqual(nuevo['mensaje'], "C1: Jugador 1 pierde el prox turno")

    def test_efecto_C2(self):
        estado = dict(
            posiciones=(25, 0),
            pierde_turno=(False, False),
            actual=0,
            ganador=None,
            valor_del_dado=None,
            mensaje=''
        )
        nuevo = aplicar_efecto_celda_especial(estado, 0)
        self.assertEqual(nuevo['posiciones'][0], 22)
        self.assertEqual(nuevo['mensaje'], "C2: Jugador 1 retrodece 3 lugares")

    def test_efecto_C2_con_retroceso_encadenado(self):
        # Si C2 retrocede a una casilla ocupada, debe activar recursión
        estado = dict(
            posiciones=(25, 22, 23),
            pierde_turno=(False, False, False),
            actual=0,
            ganador=None,
            valor_del_dado=None,
            mensaje=''
        )
        nuevo = aplicar_efecto_celda_especial(estado, 0)
        # Jugador 0 retrocede de 25 a 22, pero 22 ocupado por jugador 1 -> debe ir a 21
        self.assertEqual(nuevo['posiciones'][0], 21)
        self.assertEqual(nuevo['posiciones'][1], 22)  # no cambia
        self.assertEqual(nuevo['posiciones'][2], 23)  # no cambia

    # ========== 6. GENERADOR DE TURNOS ==========
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
            pierde_turno=(False, True, False),
            actual=0
        )
        gen = generador_turnos(estado)
        self.assertEqual(next(gen), 0)  # primero devuelve 0
        self.assertEqual(next(gen), 2)  # salta 1
        self.assertEqual(next(gen), 0)
        self.assertEqual(next(gen), 2)

    def test_generador_turnos_todos_perdedores_excepto_uno(self):
        estado = dict(
            posiciones=(0, 0, 0),
            pierde_turno=(False, True, True),
            actual=0
        )
        gen = generador_turnos(estado)
        self.assertEqual(next(gen), 0)
        self.assertEqual(next(gen), 0)  # solo 0 puede jugar

    # ========== 7. COMPOSICIÓN mover_y_aplicar_efecto ==========
    def test_mover_y_aplicar_efecto_sin_especial(self):
        estado = self.estado_3
        nuevo = mover_y_aplicar_efecto(estado, 0, 3)
        self.assertEqual(nuevo['posiciones'][0], 3)
        self.assertEqual(nuevo['mensaje'], '')

    def test_mover_y_aplicar_efecto_con_P3(self):
        estado = dict(
            posiciones=(20, 0),
            pierde_turno=(False, False),
            actual=0,
            ganador=None,
            valor_del_dado=None,
            mensaje=''
        )
        nuevo = mover_y_aplicar_efecto(estado, 0, 2)  # cae en 22 (P3)
        self.assertEqual(nuevo['posiciones'][0], 24)  # 22+2
        self.assertEqual(nuevo['mensaje'], "P3: Jugador 1 avanza dos lugares")

    def test_mover_y_aplicar_efecto_con_P2_autogenerado(self):
        estado = dict(
            posiciones=(11, 0),
            pierde_turno=(False, False),
            actual=0,
            ganador=None,
            valor_del_dado=None,
            mensaje=''
        )
        # Pasamos nuevo_dado explícitamente para que el test sea determinista
        nuevo = mover_y_aplicar_efecto(estado, 0, 0, nuevo_dado=3)
        self.assertEqual(nuevo['posiciones'][0], 14)
        self.assertIn('P2', nuevo['mensaje'])

    def test_mover_y_aplicar_efecto_con_P1_auto(self):
        estado = dict(
            posiciones=(3, 0, 0),
            pierde_turno=(False, False, False),
            actual=0,
            ganador=None,
            valor_del_dado=None,
            mensaje=''
        )
        random.seed(42)
        nuevo = mover_y_aplicar_efecto(estado, 0, 2)  # cae en 5 (P1), sin idx_castigado -> elige aleatorio
        self.assertTrue(nuevo['pierde_turno'][1])
        self.assertEqual(nuevo['mensaje'], "P1: Jugador 1 castiga a Jugador 2")

    # ========== 8. INMUTABILIDAD ==========
    def test_inmutabilidad_mover_jugador(self):
        estado = self.estado_4
        original_pos = estado['posiciones']
        original_pierde = estado['pierde_turno']
        mover_jugador(estado, 0, 3)
        self.assertEqual(estado['posiciones'], original_pos)
        self.assertEqual(estado['pierde_turno'], original_pierde)

    def test_inmutabilidad_resolver_competencia(self):
        estado = dict(
            posiciones=(5, 5),
            pierde_turno=(False, False),
            actual=0,
            ganador=None,
            valor_del_dado=None,
            mensaje=''
        )
        original = dict(estado)
        resolver_competencia(estado, 0, 1, 6, 3)
        self.assertEqual(estado, original)

    def test_inmutabilidad_aplicar_efecto(self):
        estado = dict(
            posiciones=(5, 0, 0),
            pierde_turno=(False, False, False),
            actual=0,
            ganador=None,
            valor_del_dado=None,
            mensaje=''
        )
        original = dict(estado)
        aplicar_efecto_celda_especial(estado, 0, idx_castigado=1)
        self.assertEqual(estado, original)


if __name__ == '__main__':
    unittest.main()