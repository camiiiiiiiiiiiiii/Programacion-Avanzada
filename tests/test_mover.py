import unittest
from logic.logica import mover_jugador, estado_inicial, checkear_si_hay_competencia
from logic.datos_tablero import PUNTUACION_PARA_GANAR

class TestMoverJugador(unittest.TestCase):
    def test_retroceso_encadenado_sin_recursion_infinita(self):
        """
        Escenario: varios jugadores en posiciones consecutivas (3, 2, 1).
        Retrocedemos al jugador 0 desde 3 con -2 -> cae en 1 (ocupado),
        debe retroceder a 0 (que debe estar libre) y detenerse.
        """
        estado = dict(
            posiciones=(3, 2, 1, 0),  # 4 jugadores
            pierde_turno=(False, False, False, False),
            actual=0,
            ganador=None,
            valor_del_dado=None,
            mensaje=''
        )
        # Movemos al jugador 0 con -2
        nuevo_estado = mover_jugador(estado, 0, -2)

        # Esperamos que quede en 0 (porque 1 está ocupado y 0 libre)
        self.assertEqual(nuevo_estado['posiciones'][0], 0)
        # Verificamos que el resto no haya cambiado
        self.assertEqual(nuevo_estado['posiciones'][1], 2)
        self.assertEqual(nuevo_estado['posiciones'][2], 1)
        self.assertEqual(nuevo_estado['posiciones'][3], 0)

    def test_retroceso_hasta_limite_inferior(self):
        """
        Si un jugador está en la casilla 1 y retrocede 2, debe quedarse en 0,
        sin recursión adicional porque ya no puede retroceder más.
        """
        estado = dict(
            posiciones=(1, 5, 3),
            pierde_turno=(False, False, False),
            actual=0,
            ganador=None,
            valor_del_dado=None,
            mensaje=''
        )
        nuevo_estado = mover_jugador(estado, 0, -2)
        self.assertEqual(nuevo_estado['posiciones'][0], 0)
        # Aunque haya otro jugador en 0 (no en este caso), la función debería
        # limitarse a 0 y no intentar retroceder más.

    def test_retroceso_con_todos_ocupados(self):
        """
        Si todas las casillas desde la actual hasta 0 están ocupadas,
        el jugador debería quedar en 0 y no entrar en recursión infinita.
        """
        # Creamos un estado con posiciones 0,1,2,3 ocupadas por otros jugadores
        # y el jugador 0 está en 4 y retrocede -2 -> cae en 2 (ocupado),
        # luego -1 -> 1 (ocupado), luego -1 -> 0 (ocupado también).
        # Debe quedarse en 0 (por límite inferior) y no entrar en bucle.
        estado = dict(
            posiciones=(4, 0, 1, 2),  # jugador 0 en 4, los otros en 0,1,2
            pierde_turno=(False, False, False, False),
            actual=0,
            ganador=None,
            valor_del_dado=None,
            mensaje=''
        )
        nuevo_estado = mover_jugador(estado, 0, -2)
        self.assertEqual(nuevo_estado['posiciones'][0], 0)
        # El resto debe quedar igual
        self.assertEqual(nuevo_estado['posiciones'][1], 0)
        self.assertEqual(nuevo_estado['posiciones'][2], 1)
        self.assertEqual(nuevo_estado['posiciones'][3], 2)

if __name__ == '__main__':
    unittest.main()