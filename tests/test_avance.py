import unittest
from gui.interfaz import JuegoGUI
import logic.logica as juego

class TestAvanceTurno(unittest.TestCase):
    def test_reseteo_flags(self):
        gui = JuegoGUI()
        # Colocar al jugador 0 en la casilla 5 (P1)
        estado = juego.estado_inicial(3)
        estado = juego.mover_jugador(estado, 0, 5)  # ahora está en posición 5
        gui.estado = estado
        gui.jugadores = ["Jugador 1", "Jugador 2", "Jugador 3"]

        # Ahora aplicar el efecto P1 sobre sí mismo (castigarse a sí mismo)
        gui.estado = juego.aplicar_efecto_celda_especial(gui.estado, 0, idx_castigado=0)
        self.assertTrue(gui.estado['pierde_turno'][0])

        # Avanzar turno una vez (debe saltar al jugador 1 y resetear el flag del 0)
        gui.avanzar_turno()
        self.assertEqual(gui.estado['actual'], 1)
        self.assertFalse(gui.estado['pierde_turno'][0])  # debe estar False

        # Avanzar otra vez (ahora debe ir al jugador 2, ya que el 1 no tiene flag)
        gui.avanzar_turno()
        self.assertEqual(gui.estado['actual'], 2)
        # Los flags deben seguir todos False (porque ya se resetearon)
        self.assertFalse(any(gui.estado['pierde_turno']))