import sys
import pygame
import logic.logica as juego
from logic.datos_tablero import CAMINO

class JuegoGUI:
    def __init__(self):
        """Inicializa la interfaz gráfica del juego."""
        pygame.init()
        self.ventana = pygame.display.set_mode((1500,900))
        pygame.display.set_caption("Entregable 1 - Programacion Funcional")
        self.reloj = pygame.time.Clock()

        self.colores = {
            'fondo': (25, 27, 36),        # Fondo oscuro
            'texto': (235, 237, 240),      # Texto claro
            'texto_oscuro': (45, 48, 55),  # Texto oscuro
            'dorado': (220, 180, 80),      # Dorado para títulos
            'borde': (190, 184, 192),      # Borde gris
            'auto': (205, 220, 215),       # Color modo automático
            'interactivo': (205, 215, 235), # Color modo interactivo
            'boton': (70, 75, 90),         # Color botón normal
            'boton_hover': (90, 98, 115),
            'boton_menos': (120, 128, 145),  
            'boton_mas': (120, 128, 145),
            'casilla': (235, 237, 240),  # <-- NUEVO
            'inicio': (170, 210, 190),   # <-- NUEVO
            'fin': (220, 180, 190),      # <-- NUEVO
            'P1': (245, 215, 175),       # <-- NUEVO
            'P2': (245, 215, 175),       # <-- NUEVO
            'P3': (245, 215, 175),       # <-- NUEVO
            'C1': (235, 190, 235),       # <-- NUEVO
            'C2': (235, 190, 235),       # <-- NUEVO
            'dado': (245, 240, 225),     # <-- NUEVO
        }
        
        
        self.fuente_pequena = pygame.font.SysFont("Arial", 18)
        self.fuente_mediana = pygame.font.SysFont("Arial", 24)
        self.fuente_grande = pygame.font.SysFont("Arial", 48)
        self.fuente_titulo = pygame.font.SysFont("Arial", 64, bold=True)

        self.boton_automatico = pygame.Rect(400, 350, 250, 60)
        self.boton_interactivo = pygame.Rect(900, 350, 250, 60)

        self.pantalla_actual = "inicio"  # inicio, juego, fin
        self.modo_juego = None  # "automatico" o "interactivo"
        self.mensaje = "¡Bienvenidos al Juego!"
        self.boton_auto_hover = False
        self.boton_interactivo_hover = False

        # Después de self.modo_juego = None
        self.cantidad_jugadores = 2  # Valor por defecto
        self.boton_mas = None
        self.boton_menos = None
        self.boton_continuar = None

        self.casilla = 60
        self.x = 50
        self.y = 50
        self.dadox = 1200
        self.dadoy = 200
        self.dado = 80
        self.info = 650  # Posición Y donde empieza la info inferior
        self.estado = None
        self.jugadores = []
        self.juego_terminado = False
        self.animando = False
        # Botón para tirar dado
        self.boton_tirar = pygame.Rect(160, 700, 200, 60)
        self.boton_hover = False

    def ejecutar(self):
        """Bucle principal del juego."""
        while True:
            self.procesar_eventos()
            self.actualizar()
            self.dibujar()
            self.reloj.tick(60)  # Limitar a 60 FPS

    def procesar_eventos(self):
        """Procesa los eventos de Pygame."""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if self.pantalla_actual == "inicio":
                self._procesar_eventos_inicio(evento)
            elif self.pantalla_actual == "cantidad_jugadores":
                self.procesar_cantidad_jugadores(evento)
            elif self.pantalla_actual == "juego":
                self.procesar_eventos_juego(evento)

    def _procesar_eventos_inicio(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if self.boton_automatico.collidepoint(evento.pos):
                self.modo_juego = "automatico"
                self.boton_auto_hover = False
                self.pantalla_actual = "cantidad_jugadores"
            elif self.boton_interactivo.collidepoint(evento.pos):
                self.modo_juego = "interactivo"
                self.boton_interactivo_hover = False
                self.pantalla_actual = "cantidad_jugadores" 
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            self.boton_auto_hover = self.boton_automatico.collidepoint(evento.pos)
            self.boton_interactivo_hover = self.boton_interactivo.collidepoint(evento.pos)

    def actualizar(self):
        pass

    def dibujar(self):
        self.ventana.fill(self.colores['fondo'])
        if self.pantalla_actual == "inicio":
            self.pantalla_inicio()
        elif self.pantalla_actual == "cantidad_jugadores":
            self.pantalla_cantidad_jugadores()
        elif self.pantalla_actual == "juego":
            self.pantalla_juego()
        pygame.display.flip()

    def pantalla_juego(self):
        self.dibujar_tablero()

    def pantalla_inicio(self):
        self.ventana.fill(self.colores['fondo'])
        titulo = self.fuente_grande.render("¡Bienvenidos!", True, (255, 215, 0))
        titulo_rect = titulo.get_rect(center=(1500//2, 150))
        self.ventana.blit(titulo, titulo_rect)
        subtitulo = self.fuente_mediana.render("Juego de Tablero", True, (220, 220, 240))
        subtitulo_rect = subtitulo.get_rect(center=(1500//2, 210))
        self.ventana.blit(subtitulo, subtitulo_rect)
        
        # Línea decorativa
        pygame.draw.line(self.ventana, (70, 75, 88),
                        (1500//2 - 170, 240),
                        (1500//2 + 170, 240),
                        1)
        
        # Botón Automático
        if self.modo_juego == "automatico":
            color_auto = self.colores['auto_hover']
        else:
            color_auto = self.colores['auto'] if not self.boton_auto_hover else self.colores['auto_hover']
        pygame.draw.rect(self.ventana, color_auto, self.boton_automatico, border_radius=15)
        texto = self.fuente_mediana.render("Juego Automático", True, self.colores['texto_oscuro'])
        texto_rect = texto.get_rect(center=self.boton_automatico.center)
        self.ventana.blit(texto, texto_rect)

        # Botón Interactivo
        if self.modo_juego == "interactivo":
            color_inter = self.colores['interactivo_hover']
        else:
            color_inter = self.colores['interactivo'] if not self.boton_interactivo_hover else self.colores['interactivo_hover']
        pygame.draw.rect(self.ventana, color_inter, self.boton_interactivo, border_radius=15)
        texto = self.fuente_mediana.render("Juego Interactivo", True, self.colores['texto_oscuro'])
        texto_rect = texto.get_rect(center=self.boton_interactivo.center)
        self.ventana.blit(texto, texto_rect)

        # Pie de página
        pie = self.fuente_pequena.render("Programación Avanzada - 2026", True, (180, 180, 200))
        pie_rect = pie.get_rect(center=(1500//2, 750))
        self.ventana.blit(pie, pie_rect)
        
        # Mensaje de estado (si existe)
        if self.mensaje and self.mensaje != "¡Bienvenidos al Juego!":
            texto_mensaje = self.fuente_mediana.render(self.mensaje, True, (255, 215, 0))
            rect_mensaje = texto_mensaje.get_rect(center=(1500//2, 560))
            self.ventana.blit(texto_mensaje, rect_mensaje)

        #poner reglas del juego e instrucciones
    
    def procesar_cantidad_jugadores(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if self.boton_menos.collidepoint(evento.pos):
                if self.cantidad_jugadores > 2:
                    self.cantidad_jugadores -= 1
                    print (f"Cantidad de jugadores: {self.cantidad_jugadores}")
            elif self.boton_mas.collidepoint(evento.pos):
                if self.cantidad_jugadores < 4:
                    self.cantidad_jugadores += 1
                    print (f"Cantidad de jugadores: {self.cantidad_jugadores}")
            elif self.boton_continuar.collidepoint(evento.pos):
                # Aquí se podría iniciar el juego con la cantidad de jugadores seleccionada
                print(f"Modo: {self.modo_juego}, Jugadores: {self.cantidad_jugadores}")
                self.pantalla_actual = "juego"

                self.estado = juego.estado_inicial(self.cantidad_jugadores)
                self.jugadores = [f"Jugador {i+1}" for i in range(self.cantidad_jugadores)]
            
                self.pantalla_actual = "juego"
                self.mensaje = f"¡Comienza el juego! Turno de {self.jugadores[0]}"


        elif evento.type == pygame.MOUSEMOTION:
            if self.boton_continuar:
                self.boton_continuar_hover = self.boton_continuar.collidepoint(evento.pos)

    def pantalla_cantidad_jugadores(self):
        self.ventana.fill(self.colores['fondo'])
        titulo = self.fuente_grande.render("Selecciona la cantidad de jugadores", True, (255, 215, 0))
        titulo_rect = titulo.get_rect(center=(1500//2, 150))
        self.ventana.blit(titulo, titulo_rect)

        selector_y = 300
        ancho_total = 60 + 30 + 60 + 30 + 60  # ancho del boton menos + espacio + ancho del numero + espacio + ancho del boton mas
        x_inicio = 1500//2 - ancho_total//2  # 750 - 120 = 630
        #boton menos
        x_menos = x_inicio
        self.boton_menos = pygame.Rect(x_menos, selector_y, 60, 60)
        pygame.draw.rect(self.ventana, self.colores['boton_menos'], self.boton_menos, border_radius=10)
        texto_menos = self.fuente_grande.render("-", True, (235, 237, 240))
        rect_menos = texto_menos.get_rect(center=self.boton_menos.center)
        self.ventana.blit(texto_menos, rect_menos)

        x_numero = x_menos + 60 + 30
        texto_cant = self.fuente_titulo.render(str(self.cantidad_jugadores), True, self.colores['dorado'])
        rect_cant = texto_cant.get_rect(center=(x_numero + 30, selector_y + 30))
        self.ventana.blit(texto_cant, rect_cant)

        #boton mas
        x_mas = x_numero + 60 + 30
        self.boton_mas = pygame.Rect(x_mas, selector_y, 60, 60)
        pygame.draw.rect(self.ventana, self.colores['boton_mas'], self.boton_mas, border_radius=10)
        texto_mas = self.fuente_grande.render("+", True, (235, 237, 240))
        rect_mas = texto_mas.get_rect(center=self.boton_mas.center)
        self.ventana.blit(texto_mas, rect_mas)


        # Rango de jugadores
        rango = self.fuente_pequena.render("(2 a 4 jugadores)", True, (180, 180, 200))
        rango_rect = rango.get_rect(center=(1500//2, 460))
        self.ventana.blit(rango, rango_rect)

        self.boton_continuar = pygame.Rect(1500//2 - 150, 500, 300, 60)
        pygame.draw.rect(self.ventana, (100, 200, 100), self.boton_continuar, border_radius=15)
        texto_cont = self.fuente_mediana.render("Continuar", True, (235, 237, 240))
        rect_cont = texto_cont.get_rect(center=self.boton_continuar.center)
        self.ventana.blit(texto_cont, rect_cont)
        
        # Pie de página
        pie = self.fuente_pequena.render("Programación Avanzada - 2026", True, (180, 180, 200))
        pie_rect = pie.get_rect(center=(1500//2, 750))
        self.ventana.blit(pie, pie_rect)

    # def dibujar_tablero(self):
    #     # Fondo del tablero
    #     tablero_rect = pygame.Rect(self.x - 10, self.y - 10, 
    #                             10 * (self.casilla + 2) + 20, 
    #                             10 * (self.casilla + 2) + 20)
    #     interior_rect = pygame.Rect(self.x, self.y, 
    #                             10 * (self.casilla + 2) - 2, 
    #                             10 * (self.casilla + 2) - 2)
    #     pygame.draw.rect(self.ventana, (180, 170, 160), interior_rect)
    #     pygame.draw.rect(self.ventana, (200, 180, 100), tablero_rect, 4, border_radius=10)

    #     # Dibujar cada casilla
    #     for i, (fila, col) in enumerate(CAMINO):
    #         x = self.x + col * (self.casilla + 2)
    #         y = self.y + fila * (self.casilla + 2)
    #         rect = (x, y, self.casilla, self.casilla)
            
    #         # Color de la casilla
    #         color = self.colores.get('casilla', (235, 237, 240))
    #         if i in juego.CELDAS_ESPECIALES:
    #             tipo = juego.CELDAS_ESPECIALES[i]
    #             if tipo in self.colores:
    #                 color = self.colores[tipo]
    #         elif i == 0:  
    #             color = self.colores.get('inicio', (170, 210, 190))
    #         elif i == len(CAMINO) - 1:  
    #             color = self.colores.get('fin', (220, 180, 190))
            
    #         pygame.draw.rect(self.ventana, color, rect)
    #         pygame.draw.rect(self.ventana, self.colores.get('borde', (190, 184, 192)), rect, 2)
            
    #         # Texto de la casilla
    #         if i in juego.CELDAS_ESPECIALES:
    #             tipo = juego.CELDAS_ESPECIALES[i]
    #             texto_casilla = self.fuente_pequena.render(tipo, True, (50, 50, 50))
    #             self.ventana.blit(texto_casilla, (x + 5, y + 5))
    #         elif i == 0:
    #             texto_casilla = self.fuente_pequena.render("INICIO", True, (50, 50, 50))
    #             self.ventana.blit(texto_casilla, (x + 5, y + 5))
    #         elif i == len(CAMINO) - 1:
    #             texto_casilla = self.fuente_pequena.render("FIN", True, (50, 50, 50))
    #             self.ventana.blit(texto_casilla, (x + 5, y + 5))

    # def dibujar_dado(self):
    #     x, y = self.dadox, self.dadoy
    #     tam = self.dado
    #     valor = 1
    #     if self.estado:
    #         valor = self.estado.get('valor_del_dado', 1)
        
    #     dado_rect = pygame.Rect(x, y, tam, tam)
    #     pygame.draw.rect(self.ventana, (245, 240, 225), dado_rect, border_radius=12)
    #     pygame.draw.rect(self.ventana, (90, 98, 115), dado_rect, 3, border_radius=12)
        
    #     # Puntos del dado
    #     puntos = {
    #         1: [(0, 0)],
    #         2: [(-tam//4, -tam//4), (tam//4, tam//4)],
    #         3: [(-tam//4, -tam//4), (0, 0), (tam//4, tam//4)],
    #         4: [(-tam//4, -tam//4), (-tam//4, tam//4), (tam//4, -tam//4), (tam//4, tam//4)],
    #         5: [(-tam//4, -tam//4), (-tam//4, tam//4), (0, 0), (tam//4, -tam//4), (tam//4, tam//4)],
    #         6: [(-tam//4, -tam//4), (-tam//4, 0), (-tam//4, tam//4), (tam//4, -tam//4), (tam//4, 0), (tam//4, tam//4)]
    #     }
        
    #     for dx, dy in puntos.get(valor, []):
    #         cx = x + tam//2 + dx
    #         cy = y + tam//2 + dy
    #         pygame.draw.circle(self.ventana, (35, 35, 40), (cx, cy), tam//10)