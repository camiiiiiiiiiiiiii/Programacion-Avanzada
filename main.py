#!/usr/bin/env python3
import sys
import pygame

# Importar solo la interfaz
from gui.interfaz import JuegoGUI

def main():
    try:
        pygame.init()
        
        if not pygame.get_init():
            print("Error: No se pudo inicializar Pygame")
            sys.exit(1)
        
        print("Iniciando Juego de Mesa...")
        juego = JuegoGUI()
        juego.ejecutar()
        
    except KeyboardInterrupt:
        print("\n Juego interrumpido")
        pygame.quit()
        sys.exit(0)
    except Exception as e:
        print(f" Error: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()