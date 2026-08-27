import sys
import pygame
import random
from logic import logica as juego
from logic.datos_tablero import CAMINO, PUNTUACION_PARA_GANAR, CELDAS_ESPECIALES

class JuegoGUI:
    def __init__(self):
        # Inicialización de Pygame
        pygame.init()
        self.ventana = pygame.display.set_mode((1600, 900))
        pygame.display.set_caption("Juego de Mesa - Entregable 1")
        
        # Configuración del reloj para controlar FPS
        self.reloj = pygame.time.Clock()
        
        # ===== CONFIGURACIÓN DEL TABLERO =====
        self.casilla = 65  # Tamaño de cada casilla
        self.x = 30  # Margen izquierdo
        self.y = 30  # Margen superior
        self.panel = 300  # Ancho del panel lateral
        self.panelx = 750  # Posición X del panel
        self.panely = 300  # Posición Y del panel
        
        # ===== CONFIGURACIÓN DEL DADO =====
        self.dadox = 750  # Posición X del dado
        self.dadoy = 160  # Posición Y del dado
        self.dado = 90  # Tamaño del dado
        
        # ===== BOTONES =====
        self.boton_tirar = pygame.Rect(750, 500, 200, 60)
        self.boton_auto = pygame.Rect(400, 350, 250, 60)
        self.boton_interactivo = pygame.Rect(900, 350, 250, 60)
        self.boton_iniciar = pygame.Rect(550, 450, 200, 50)
        self.boton_volver = pygame.Rect(550, 520, 200, 50)
        self.boton_empezar = pygame.Rect(550, 450, 200, 50)
        
        # ===== COLORES =====
        self.colores = {
            'fondo': (25, 27, 36),
            'casilla': (235, 237, 240),
            'borde': (190, 184, 192),
            'texto': (235, 237, 240),
            'texto_oscuro': (45, 48, 55),
            'dorado': (220, 180, 80),
            'boton': (70, 75, 90),
            'boton_hover': (90, 98, 115),
            'boton_activo': (100, 200, 100),
            'dado': (245, 240, 225),
            'dado_numero': (35, 35, 40),
            'inicio': (170, 210, 190),
            'fin': (220, 180, 190),
            'jugador1': (210, 130, 150),
            'jugador2': (110, 185, 220),
            'jugador3': (220, 180, 80),
            'jugador4': (80, 200, 150),
            'P1': (245, 215, 175),  # Premio 1 - Castiga a otro
            'P2': (245, 215, 175),  # Premio 2 - Tira de nuevo
            'P3': (245, 215, 175),  # Premio 3 - Avanza 2
            'C1': (235, 190, 235),  # Castigo 1 - Pierde turno
            'C2': (235, 190, 235),  # Castigo 2 - Retrocede 3
            'auto': (205, 220, 215),
            'interactivo': (205, 215, 235),
        }
        
        # Colores específicos para cada jugador
        self.colores_jugadores = [
            (210, 130, 150),  # Rosado
            (110, 185, 220),  # Celeste
            (220, 180, 80),   # Dorado
            (80, 200, 150)    # Verde
        ]
        
        # ===== FUENTES =====
        self.fuente_pequena = pygame.font.SysFont("Arial", 16)
        self.fuente_mediana = pygame.font.SysFont("Arial", 24)
        self.fuente_dado = pygame.font.SysFont("Arial", 72)
        self.fuente_grande = pygame.font.SysFont("Arial", 48)
        self.fuente_titulo = pygame.font.SysFont("Arial", 64, bold=True)
        self.fuente_tablero = pygame.font.SysFont("Arial", 14)
        self.fuente_mensaje = pygame.font.SysFont("Arial", 20)
        
        # ===== VARIABLES DE ESTADO =====
        self.mensaje = "¡Bienvenidos al Juego!"
        self.pantalla_actual = "inicio"  # inicio, cantidad_jugadores, pedir_nombres, juego, fin
        self.modo_juego = None  # "automatico" o "interactivo"
        self.cantidad_jugadores = 2  # Por defecto
        self.nombres_jugadores = ["", "", "", ""]
        self.nombre_actual = 0
        self.mostrar_cursor = True
        self.tiempo_cursor = 0
        
        # ===== VARIABLES DEL JUEGO =====
        self.estado = None  # Estado del juego
        self.juego_terminado = False
        self.ganador = None
        self.animando = False
        self.tiempo_espera = 0
        self.esperando = False
        self.valor_dado = None
        self.ultimo_movimiento = None
        self.color_boton_actual = self.colores['boton']
        
        # ===== VARIABLES DE ANIMACIÓN =====
        self.animacion_dado = False
        self.frames_animacion = 0
        self.valor_dado_animacion = 1
        
        # ===== INICIALIZAR GENERADOR DE DADOS =====
        self.generador_dados = juego.dice_generator()
        
        # ===== CACHE DE POSICIONES DEL TABLERO =====
        self.posiciones_tablero = self._calcular_posiciones_tablero()
    
    def _calcular_posiciones_tablero(self):
        """Calcula las posiciones de todas las casillas del tablero."""
        posiciones = []
        for i in range(36):  # 0 a 35
            if i < 10:
                # Fila inferior (izquierda a derecha)
                x = self.x + i * self.casilla
                y = self.y + 8 * self.casilla
            elif i < 19:
                # Columna derecha (arriba)
                x = self.x + 9 * self.casilla
                y = self.y + (17 - i) * self.casilla
            elif i < 28:
                # Fila superior (derecha a izquierda)
                x = self.x + (28 - i) * self.casilla
                y = self.y + 0 * self.casilla
            else:
                # Columna izquierda (abajo)
                x = self.x + 0 * self.casilla
                y = self.y + (i - 27) * self.casilla
            posiciones.append((x, y))
        return posiciones
    
    def ejecutar(self):
        """Bucle principal del juego."""
        while True:
            self.procesar_eventos()
            self.actualizar()
            self.dibujar()
            
            self.reloj.tick(30)  # 30 FPS
    
    def procesar_eventos(self):
        """Procesa todos los eventos de Pygame."""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Delegar el procesamiento según la pantalla actual
            if self.pantalla_actual == "inicio":
                self._procesar_eventos_inicio(evento)
            elif self.pantalla_actual == "cantidad_jugadores":
                self._procesar_eventos_cantidad(evento)
            elif self.pantalla_actual == "pedir_nombres":
                self._procesar_eventos_nombres(evento)
            elif self.pantalla_actual == "juego":
                self._procesar_eventos_juego(evento)
            elif self.pantalla_actual == "fin":
                self._procesar_eventos_fin(evento)
    
    def actualizar(self):
        """Actualiza el estado del juego (animaciones, temporizadores, etc.)."""
        # Cursor parpadeante
        self.tiempo_cursor += 1
        if self.tiempo_cursor >= 30:
            self.tiempo_cursor = 0
            self.mostrar_cursor = not self.mostrar_cursor
        
        # Animación del dado
        if self.animacion_dado:
            self.frames_animacion += 1
            if self.frames_animacion % 5 == 0:
                self.valor_dado_animacion = random.randint(1, 6)
            if self.frames_animacion >= 30:  # 1 segundo de animación
                self.animacion_dado = False
                self.frames_animacion = 0
                self._ejecutar_tiro_dado()
        
        # Modo automático
        if self.modo_juego == "automatico" and not self.juego_terminado and not self.animando:
            if self.esperando:
                self.tiempo_espera -= 1
                if self.tiempo_espera <= 0:
                    self.esperando = False
                    self._realizar_turno_automatico()
    
    def dibujar(self):
        """Dibuja todo en la pantalla."""
        self.ventana.fill(self.colores['fondo'])
        
        if self.pantalla_actual == "inicio":
            self._dibujar_pantalla_inicio()
        elif self.pantalla_actual == "cantidad_jugadores":
            self._dibujar_pantalla_cantidad()
        elif self.pantalla_actual == "pedir_nombres":
            self._dibujar_pantalla_nombres()
        elif self.pantalla_actual == "juego":
            self._dibujar_pantalla_juego()
        elif self.pantalla_actual == "fin":
            self._dibujar_pantalla_fin()
        
        pygame.display.flip()
    
    # ===== MÉTODOS DE PROCESAMIENTO DE EVENTOS =====
    
    def _procesar_eventos_inicio(self, evento):
        """Procesa eventos en la pantalla de inicio."""
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if self.boton_auto.collidepoint(evento.pos):
                self.modo_juego = "automatico"
                self.pantalla_actual = "cantidad_jugadores"
                self.mensaje = "Modo Automático seleccionado"
            elif self.boton_interactivo.collidepoint(evento.pos):
                self.modo_juego = "interactivo"
                self.pantalla_actual = "cantidad_jugadores"
                self.mensaje = "Modo Interactivo seleccionado"
    
    def _procesar_eventos_cantidad(self, evento):
        """Procesa eventos en la pantalla de selección de cantidad de jugadores."""
        if evento.type == pygame.MOUSEBUTTONDOWN:
            # Botones para aumentar/disminuir jugadores
            if hasattr(self, 'boton_mas') and self.boton_mas.collidepoint(evento.pos):
                if self.cantidad_jugadores < 4:
                    self.cantidad_jugadores += 1
            elif hasattr(self, 'boton_menos') and self.boton_menos.collidepoint(evento.pos):
                if self.cantidad_jugadores > 2:
                    self.cantidad_jugadores -= 1
            elif hasattr(self, 'boton_continuar') and self.boton_continuar.collidepoint(evento.pos):
                if self.modo_juego == "interactivo":
                    self.pantalla_actual = "pedir_nombres"
                    self.nombre_actual = 0
                else:
                    self._iniciar_juego_automatico()
    
    def _procesar_eventos_nombres(self, evento):
        """Procesa eventos en la pantalla de ingreso de nombres."""
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN:
                if self.nombres_jugadores[self.nombre_actual].strip():
                    self.nombre_actual += 1
                    if self.nombre_actual >= self.cantidad_jugadores:
                        self._iniciar_juego_interactivo()
            elif evento.key == pygame.K_BACKSPACE:
                self.nombres_jugadores[self.nombre_actual] = self.nombres_jugadores[self.nombre_actual][:-1]
            else:
                if len(self.nombres_jugadores[self.nombre_actual]) < 15:
                    self.nombres_jugadores[self.nombre_actual] += evento.unicode
        
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if hasattr(self, 'boton_volver') and self.boton_volver.collidepoint(evento.pos):
                self.pantalla_actual = "cantidad_jugadores"
                self.nombre_actual = 0
                self.nombres_jugadores = ["", "", "", ""]
    
    def _procesar_eventos_juego(self, evento):
        """Procesa eventos en la pantalla de juego."""
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if self.boton_tirar.collidepoint(evento.pos):
                if not self.juego_terminado and not self.animando and not self.esperando:
                    if self.modo_juego == "interactivo":
                        self._iniciar_tiro_dado()
        elif evento.type == pygame.MOUSEMOTION:
            if self.boton_tirar.collidepoint(evento.pos):
                self.color_boton_actual = self.colores['boton_hover']
            else:
                self.color_boton_actual = self.colores['boton']
    
    def _procesar_eventos_fin(self, evento):
        """Procesa eventos en la pantalla de fin."""
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if hasattr(self, 'boton_reiniciar') and self.boton_reiniciar.collidepoint(evento.pos):
                self._reiniciar_juego()
    
    # ===== MÉTODOS DE DIBUJO =====
    
    def _dibujar_pantalla_inicio(self):
        """Dibuja la pantalla de inicio."""
        # Título
        titulo = self.fuente_titulo.render("JUEGO DE MESA", True, self.colores['dorado'])
        rect_titulo = titulo.get_rect(center=(800, 150))
        self.ventana.blit(titulo, rect_titulo)
        
        # Subtítulo
        subtitulo = self.fuente_mediana.render("Selecciona un modo de juego", True, self.colores['texto'])
        rect_sub = subtitulo.get_rect(center=(800, 220))
        self.ventana.blit(subtitulo, rect_sub)
        
        # Botón Modo Automático
        pygame.draw.rect(self.ventana, self.colores['auto'], self.boton_auto, border_radius=15)
        pygame.draw.rect(self.ventana, self.colores['borde'], self.boton_auto, 2, border_radius=15)
        texto_auto = self.fuente_grande.render("🤖 Automático", True, self.colores['texto_oscuro'])
        rect_auto = texto_auto.get_rect(center=self.boton_auto.center)
        self.ventana.blit(texto_auto, rect_auto)
        
        # Botón Modo Interactivo
        pygame.draw.rect(self.ventana, self.colores['interactivo'], self.boton_interactivo, border_radius=15)
        pygame.draw.rect(self.ventana, self.colores['borde'], self.boton_interactivo, 2, border_radius=15)
        texto_inter = self.fuente_grande.render("👤 Interactivo", True, self.colores['texto_oscuro'])
        rect_inter = texto_inter.get_rect(center=self.boton_interactivo.center)
        self.ventana.blit(texto_inter, rect_inter)
        
        # Instrucciones
        instrucciones = [
            "🎯 El objetivo es llegar a la casilla 35",
            "⭐ Las casillas doradas son premios (P1, P2, P3)",
            "⚠️ Las casillas moradas son castigos (C1, C2)",
            "👥 Si caes en la misma casilla que otro jugador, ¡compiten!"
        ]
        y_inst = 480
        for inst in instrucciones:
            texto = self.fuente_mediana.render(inst, True, self.colores['texto'])
            self.ventana.blit(texto, (400, y_inst))
            y_inst += 40
    
    def _dibujar_pantalla_cantidad(self):
        """Dibuja la pantalla de selección de cantidad de jugadores."""
        # Título
        titulo = self.fuente_grande.render("Cantidad de Jugadores", True, self.colores['texto'])
        rect_titulo = titulo.get_rect(center=(800, 200))
        self.ventana.blit(titulo, rect_titulo)
        
        # Selector de cantidad
        selector_x = 700
        selector_y = 300
        
        # Botón menos
        self.boton_menos = pygame.Rect(selector_x, selector_y, 60, 60)
        pygame.draw.rect(self.ventana, self.colores['boton'], self.boton_menos, border_radius=10)
        texto_menos = self.fuente_grande.render("-", True, self.colores['texto'])
        rect_menos = texto_menos.get_rect(center=self.boton_menos.center)
        self.ventana.blit(texto_menos, rect_menos)
        
        # Cantidad
        texto_cant = self.fuente_titulo.render(str(self.cantidad_jugadores), True, self.colores['dorado'])
        rect_cant = texto_cant.get_rect(center=(selector_x + 140, selector_y + 30))
        self.ventana.blit(texto_cant, rect_cant)
        
        # Botón más
        self.boton_mas = pygame.Rect(selector_x + 220, selector_y, 60, 60)
        pygame.draw.rect(self.ventana, self.colores['boton'], self.boton_mas, border_radius=10)
        texto_mas = self.fuente_grande.render("+", True, self.colores['texto'])
        rect_mas = texto_mas.get_rect(center=self.boton_mas.center)
        self.ventana.blit(texto_mas, rect_mas)
        
        # Información del modo
        modo_texto = "Modo Automático" if self.modo_juego == "automatico" else "Modo Interactivo"
        texto_modo = self.fuente_mediana.render(f"Modo: {modo_texto}", True, self.colores['texto'])
        rect_modo = texto_modo.get_rect(center=(800, 420))
        self.ventana.blit(texto_modo, rect_modo)
        
        # Botón continuar
        self.boton_continuar = pygame.Rect(650, 480, 300, 60)
        pygame.draw.rect(self.ventana, self.colores['boton_activo'], self.boton_continuar, border_radius=15)
        texto_cont = self.fuente_grande.render("Continuar", True, self.colores['texto'])
        rect_cont = texto_cont.get_rect(center=self.boton_continuar.center)
        self.ventana.blit(texto_cont, rect_cont)
    
    def _dibujar_pantalla_nombres(self):
        """Dibuja la pantalla de ingreso de nombres."""
        self.ventana.fill(self.colores['fondo'])
        
        # Título
        titulo = self.fuente_grande.render("Ingresa los nombres", True, self.colores['texto'])
        rect_titulo = titulo.get_rect(center=(800, 100))
        self.ventana.blit(titulo, rect_titulo)
        
        # Instrucción
        instruccion = self.fuente_mediana.render("Presiona ENTER para confirmar cada nombre", True, self.colores['texto'])
        rect_inst = instruccion.get_rect(center=(800, 150))
        self.ventana.blit(instruccion, rect_inst)
        
        # Campos de nombre
        for i in range(self.cantidad_jugadores):
            y_pos = 200 + i * 70
            
            # Label
            label = self.fuente_mediana.render(f"Jugador {i+1}:", True, self.colores['texto'])
            self.ventana.blit(label, (500, y_pos + 10))
            
            # Campo de texto
            campo_rect = pygame.Rect(650, y_pos, 300, 40)
            if i == self.nombre_actual:
                pygame.draw.rect(self.ventana, self.colores['dorado'], campo_rect, 2)
            else:
                pygame.draw.rect(self.ventana, self.colores['borde'], campo_rect, 2)
            
            # Nombre ingresado
            nombre = self.nombres_jugadores[i] if i < len(self.nombres_jugadores) else ""
            if nombre:
                texto_nombre = self.fuente_mediana.render(nombre, True, self.colores['texto'])
                self.ventana.blit(texto_nombre, (660, y_pos + 8))
            
            # Cursor parpadeante
            if i == self.nombre_actual and self.mostrar_cursor:
                cursor_x = 660 + self.fuente_mediana.size(nombre)[0] + 2
                pygame.draw.line(self.ventana, self.colores['texto'], 
                               (cursor_x, y_pos + 8), (cursor_x, y_pos + 32), 2)
        
        # Botón volver
        self.boton_volver = pygame.Rect(650, 550, 300, 50)
        pygame.draw.rect(self.ventana, (150, 50, 50), self.boton_volver, border_radius=10)
        texto_volver = self.fuente_mediana.render("Volver", True, self.colores['texto'])
        rect_volver = texto_volver.get_rect(center=self.boton_volver.center)
        self.ventana.blit(texto_volver, rect_volver)
    
    def _dibujar_pantalla_juego(self):
        """Dibuja la pantalla principal del juego."""
        # Dibujar tablero
        self._dibujar_tablero()
        
        # Dibujar jugadores
        self._dibujar_jugadores()
        
        # Dibujar panel lateral
        self._dibujar_panel()
    
    def _dibujar_pantalla_fin(self):
        """Dibuja la pantalla de fin del juego."""
        # Fondo semitransparente
        overlay = pygame.Surface((1600, 900))
        overlay.set_alpha(180)
        overlay.fill(self.colores['fondo'])
        self.ventana.blit(overlay, (0, 0))
        
        # Marco de fin
        fin_rect = pygame.Rect(400, 250, 800, 400)
        pygame.draw.rect(self.ventana, self.colores['dorado'], fin_rect, border_radius=30)
        pygame.draw.rect(self.ventana, self.colores['borde'], fin_rect, 5, border_radius=30)
        
        # Título
        titulo = self.fuente_titulo.render("🏆 ¡JUEGO TERMINADO! 🏆", True, self.colores['texto_oscuro'])
        rect_titulo = titulo.get_rect(center=(800, 320))
        self.ventana.blit(titulo, rect_titulo)
        
        # Ganador
        if self.ganador:
            nombre = self.ganador if isinstance(self.ganador, str) else f"Jugador {self.ganador + 1}"
            ganador_texto = self.fuente_titulo.render(f"¡{nombre} ha ganado!", True, (200, 50, 50))
            rect_ganador = ganador_texto.get_rect(center=(800, 420))
            self.ventana.blit(ganador_texto, rect_ganador)
        
        # Botón reiniciar
        self.boton_reiniciar = pygame.Rect(600, 500, 400, 60)
        pygame.draw.rect(self.ventana, self.colores['boton_activo'], self.boton_reiniciar, border_radius=15)
        texto_reiniciar = self.fuente_grande.render("🔄 Jugar de nuevo", True, self.colores['texto'])
        rect_reiniciar = texto_reiniciar.get_rect(center=self.boton_reiniciar.center)
        self.ventana.blit(texto_reiniciar, rect_reiniciar)
    
    # ===== MÉTODOS DE DIBUJO DEL TABLERO =====
    
    def _dibujar_tablero(self):
        """Dibuja el tablero completo."""
        for i in range(36):
            x, y = self.posiciones_tablero[i]
            
            # Determinar color de la casilla
            color = self.colores['casilla']
            if i == 0:
                color = self.colores['inicio']  # Casilla de inicio
            elif i == 35:
                color = self.colores['fin']  # Casilla final
            elif i in CELDAS_ESPECIALES:
                efecto = CELDAS_ESPECIALES[i]
                if efecto.startswith('P'):
                    color = self.colores['P1']  # Premio
                elif efecto.startswith('C'):
                    color = self.colores['C1']  # Castigo
            
            # Dibujar casilla
            pygame.draw.rect(self.ventana, color, (x, y, self.casilla, self.casilla))
            pygame.draw.rect(self.ventana, self.colores['borde'], 
                           (x, y, self.casilla, self.casilla), 1)
            
            # Número de casilla
            if i < 36:
                num_texto = self.fuente_tablero.render(str(i), True, self.colores['texto_oscuro'])
                self.ventana.blit(num_texto, (x + 3, y + 3))
            
            # Efecto especial
            if i in CELDAS_ESPECIALES:
                efecto = CELDAS_ESPECIALES[i]
                efecto_texto = self.fuente_tablero.render(efecto, True, self.colores['texto_oscuro'])
                self.ventana.blit(efecto_texto, (x + 20, y + 25))
    
    def _dibujar_jugadores(self):
        """Dibuja todos los jugadores en el tablero."""
        if not self.estado:
            return
        
        posiciones = self.estado['posiciones']
        for i, pos in enumerate(posiciones):
            if pos < 36:  # Asegurar que está en el tablero
                x, y = self.posiciones_tablero[pos]
                color = self.colores_jugadores[i % len(self.colores_jugadores)]
                
                # Dibujar círculo del jugador
                centro_x = x + self.casilla // 2
                centro_y = y + self.casilla // 2
                radio = 12
                
                # Sombra
                pygame.draw.circle(self.ventana, (0, 0, 0, 50), 
                                 (centro_x + 2, centro_y + 2), radio)
                # Círculo principal
                pygame.draw.circle(self.ventana, color, (centro_x, centro_y), radio)
                pygame.draw.circle(self.ventana, self.colores['borde'], 
                                 (centro_x, centro_y), radio, 2)
                
                # Número del jugador
                num_texto = self.fuente_pequena.render(str(i + 1), True, self.colores['texto'])
                rect_num = num_texto.get_rect(center=(centro_x, centro_y))
                self.ventana.blit(num_texto, rect_num)
    
    def _dibujar_panel(self):
        """Dibuja el panel lateral con información del juego."""
        panel_x = 1200
        panel_y = 30
        panel_ancho = 370
        panel_alto = 840
        
        # Fondo del panel
        pygame.draw.rect(self.ventana, self.colores['boton'], 
                        (panel_x, panel_y, panel_ancho, panel_alto), border_radius=15)
        pygame.draw.rect(self.ventana, self.colores['borde'], 
                        (panel_x, panel_y, panel_ancho, panel_alto), 2, border_radius=15)
        
        # Título del panel
        titulo = self.fuente_mediana.render("📊 INFORMACIÓN", True, self.colores['texto'])
        rect_titulo = titulo.get_rect(center=(panel_x + panel_ancho//2, panel_y + 30))
        self.ventana.blit(titulo, rect_titulo)
        
        # Dado
        self._dibujar_dado(panel_x, panel_y + 80)
        
        # Información del jugador actual
        if self.estado:
            actual = self.estado['actual']
            nombre = self._get_nombre_jugador(actual)
            
            texto_turno = self.fuente_mediana.render(f"Turno: {nombre}", True, self.colores['texto'])
            self.ventana.blit(texto_turno, (panel_x + 20, panel_y + 230))
            
            # Posiciones de los jugadores
            y_pos = panel_y + 270
            for i, pos in enumerate(self.estado['posiciones']):
                nombre_jug = self._get_nombre_jugador(i)
                color = self.colores_jugadores[i % len(self.colores_jugadores)]
                
                # Círculo de color
                pygame.draw.circle(self.ventana, color, (panel_x + 30, y_pos + 10), 8)
                
                # Nombre y posición
                texto = self.fuente_pequena.render(f"{nombre_jug}: Casilla {pos}", True, self.colores['texto'])
                self.ventana.blit(texto, (panel_x + 50, y_pos + 2))
                
                # Pierde turno
                if self.estado['pierde_turno'][i]:
                    texto_pierde = self.fuente_pequena.render("⏭️", True, (255, 100, 100))
                    self.ventana.blit(texto_pierde, (panel_x + 280, y_pos + 2))
                
                y_pos += 35
        
        # Mensaje
        if self.mensaje:
            y_mensaje = panel_y + 500
            texto_mensaje = self.fuente_mensaje.render(self.mensaje, True, self.colores['texto'])
            rect_mensaje = texto_mensaje.get_rect(center=(panel_x + panel_ancho//2, y_mensaje))
            self.ventana.blit(texto_mensaje, rect_mensaje)
        
        # Botón tirar dado
        boton_y = panel_y + 600
        self.boton_tirar = pygame.Rect(panel_x + 60, boton_y, 250, 60)
        
        if self.juego_terminado:
            color_boton = (100, 100, 100)
            texto_boton = "🎯 Juego Terminado"
        elif self.modo_juego == "automatico":
            color_boton = (100, 150, 200)
            texto_boton = "🤖 Modo Automático"
        else:
            color_boton = self.color_boton_actual
            texto_boton = "🎲 Tirar Dado"
        
        pygame.draw.rect(self.ventana, color_boton, self.boton_tirar, border_radius=10)
        texto_btn = self.fuente_mediana.render(texto_boton, True, self.colores['texto'])
        rect_btn = texto_btn.get_rect(center=self.boton_tirar.center)
        self.ventana.blit(texto_btn, rect_btn)
        
        # Información de celdas especiales
        self._dibujar_leyenda(panel_x, panel_y + 700)
    
    def _dibujar_dado(self, x, y):
        """Dibuja el dado con puntitos."""
        dado_tam = 100
        centro_x = x + 185
        centro_y = y + 50
        
        # Fondo del dado
        if self.animacion_dado:
            valor = self.valor_dado_animacion
        else:
            valor = self.valor_dado if self.valor_dado else 1
        
        # Dibujar dado
        pygame.draw.rect(self.ventana, self.colores['dado'], 
                        (centro_x - dado_tam//2, centro_y - dado_tam//2, dado_tam, dado_tam), 
                        border_radius=15)
        pygame.draw.rect(self.ventana, self.colores['borde'], 
                        (centro_x - dado_tam//2, centro_y - dado_tam//2, dado_tam, dado_tam), 
                        3, border_radius=15)
        
        # Puntitos del dado
        puntos = {
            1: [(0, 0)],
            2: [(-1, -1), (1, 1)],
            3: [(-1, -1), (0, 0), (1, 1)],
            4: [(-1, -1), (1, -1), (-1, 1), (1, 1)],
            5: [(-1, -1), (1, -1), (0, 0), (-1, 1), (1, 1)],
            6: [(-1, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (1, 1)]
        }
        
        for dx, dy in puntos.get(valor, []):
            px = centro_x + dx * 25
            py = centro_y + dy * 25
            pygame.draw.circle(self.ventana, self.colores['dado_numero'], 
                             (px, py), 12)
    
    def _dibujar_leyenda(self, x, y):
        """Dibuja la leyenda de celdas especiales."""
        titulo = self.fuente_pequena.render("🎯 Celdas Especiales:", True, self.colores['texto'])
        self.ventana.blit(titulo, (x + 20, y))
        
        leyendas = [
            ("🟡 P1", "Castiga a otro jugador"),
            ("🟡 P2", "Tira de nuevo"),
            ("🟡 P3", "Avanza 2 casillas"),
            ("🟣 C1", "Pierde el próximo turno"),
            ("🟣 C2", "Retrocede 3 casillas")
        ]
        
        y_pos = y + 30
        for leyenda, desc in leyendas:
            texto = self.fuente_pequena.render(f"{leyenda}: {desc}", True, self.colores['texto'])
            self.ventana.blit(texto, (x + 20, y_pos))
            y_pos += 25
    
    def _get_nombre_jugador(self, idx):
        """Obtiene el nombre del jugador según el índice."""
        if self.modo_juego == "interactivo" and idx < len(self.nombres_jugadores):
            return self.nombres_jugadores[idx] or f"Jugador {idx+1}"
        return f"Jugador {idx+1}"
    
    # ===== MÉTODOS DE LÓGICA DEL JUEGO =====
    
    def _iniciar_juego_automatico(self):
        """Inicia el juego en modo automático."""
        self.pantalla_actual = "juego"
        self.estado = juego.estado_inicial(self.cantidad_jugadores)
        self.mensaje = "🤖 Modo Automático - ¡Comienza el juego!"
        self.juego_terminado = False
        self.esperando = False
        self.animando = False
        self.valor_dado = None
        
        # Iniciar el primer turno automático
        self._programar_siguiente_turno()
    
    def _iniciar_juego_interactivo(self):
        """Inicia el juego en modo interactivo."""
        self.pantalla_actual = "juego"
        self.estado = juego.estado_inicial(self.cantidad_jugadores)
        self.estado['jugadores'] = self.nombres_jugadores[:self.cantidad_jugadores]
        self.mensaje = f"👤 Turno de {self._get_nombre_jugador(0)}"
        self.juego_terminado = False
        self.animando = False
        self.esperando = False
        self.valor_dado = None
        
        # Actualizar el mensaje de turno
        self._actualizar_mensaje_turno()
    
    def _programar_siguiente_turno(self):
        """Programa el siguiente turno en modo automático."""
        if not self.juego_terminado:
            self.esperando = True
            self.tiempo_espera = 30  # 1 segundo a 30 FPS
    
    def _realizar_turno_automatico(self):
        """Realiza un turno automático."""
        if self.juego_terminado or self.animando:
            return
        
        self.animando = True
        self._iniciar_tiro_dado()
    
    def _iniciar_tiro_dado(self):
        """Inicia la animación del dado."""
        self.animacion_dado = True
        self.frames_animacion = 0
        self.valor_dado_animacion = random.randint(1, 6)
    
    def _ejecutar_tiro_dado(self):
        """Ejecuta el tiro del dado después de la animación."""
        # Obtener el valor del dado usando el generador
        self.valor_dado = next(self.generador_dados)
        
        # Obtener el jugador actual
        idx_jugador = self.estado['actual']
        nombre = self._get_nombre_jugador(idx_jugador)
        
        # Verificar si el jugador pierde el turno
        if self.estado['pierde_turno'][idx_jugador]:
            # Reiniciar pierde_turno
            nuevo_pierde = list(self.estado['pierde_turno'])
            nuevo_pierde[idx_jugador] = False
            self.estado = dict(self.estado, pierde_turno=tuple(nuevo_pierde))
            
            self.mensaje = f"⏭️ {nombre} pierde el turno"
            self._siguiente_turno()
            return
        
        # Mover al jugador
        self.mensaje = f"🎲 {nombre} sacó {self.valor_dado}"
        self.estado = juego.mover_jugador(self.estado, idx_jugador, self.valor_dado)
        
        # Verificar si hay competencia
        if juego.checkear_si_hay_competencia(self.estado, idx_jugador):
            # Simular competencia (en una implementación real, esto sería interactivo)
            self._resolver_competencia(idx_jugador)
            return
        
        # Verificar si el jugador ganó
        if self.estado['posiciones'][idx_jugador] >= PUNTUACION_PARA_GANAR:
            self._terminar_juego(idx_jugador)
            return
        
        # Aplicar efecto de celda especial
        pos = self.estado['posiciones'][idx_jugador]
        if pos in CELDAS_ESPECIALES:
            efecto = CELDAS_ESPECIALES[pos]
            self.estado = juego.aplicar_efecto_celda_especial(self.estado, idx_jugador)
            
            # Si el efecto es P2, necesitamos otro tiro
            if efecto == 'P2':
                self.animando = True
                self._iniciar_tiro_dado()  # Tiro extra
                return
        
        # Siguiente turno
        self._siguiente_turno()
    
    def _resolver_competencia(self, idx_jugador):
        """Resuelve una competencia entre jugadores."""
        pos = self.estado['posiciones'][idx_jugador]
        otros = [i for i in range(len(self.estado['posiciones'])) 
                if i != idx_jugador and self.estado['posiciones'][i] == pos]
        
        if not otros:
            self._siguiente_turno()
            return
        
        # Simular dados para la competencia
        dado1 = next(self.generador_dados)
        dado2 = next(self.generador_dados)
        
        self.mensaje = f"⚔️ ¡Competencia! {self._get_nombre_jugador(idx_jugador)} vs {self._get_nombre_jugador(otros[0])}"
        
        if dado1 > dado2:
            # Jugador actual gana
            self.estado = juego.mover_jugador(self.estado, otros[0], -2)
            self.mensaje = f"✅ {self._get_nombre_jugador(idx_jugador)} gana la competencia"
        elif dado1 < dado2:
            # Otro jugador gana
            self.estado = juego.mover_jugador(self.estado, idx_jugador, -2)
            self.mensaje = f"✅ {self._get_nombre_jugador(otros[0])} gana la competencia"
        else:
            # Empate - tirar de nuevo (en una implementación completa)
            self.mensaje = "🤝 Empate en la competencia, se repite"
            self._resolver_competencia(idx_jugador)
            return
        
        # Verificar si alguien ganó
        if self.estado['posiciones'][idx_jugador] >= PUNTUACION_PARA_GANAR:
            self._terminar_juego(idx_jugador)
            return
        
        if self.estado['posiciones'][otros[0]] >= PUNTUACION_PARA_GANAR:
            self._terminar_juego(otros[0])
            return
        
        self._siguiente_turno()
    
    def _siguiente_turno(self):
        """Pasa al siguiente turno."""
        if self.juego_terminado:
            return
        
        # Calcular siguiente jugador
        cant = self.cantidad_jugadores
        actual = self.estado['actual']
        siguiente = (actual + 1) % cant
        
        # Saltar jugadores que pierden turno
        while self.estado['pierde_turno'][siguiente]:
            # Reiniciar pierde_turno
            nuevo_pierde = list(self.estado['pierde_turno'])
            nuevo_pierde[siguiente] = False
            self.estado = dict(self.estado, pierde_turno=tuple(nuevo_pierde))
            
            siguiente = (siguiente + 1) % cant
        
        self.estado = dict(self.estado, actual=siguiente)
        self._actualizar_mensaje_turno()
        
        # Programar siguiente turno si es automático
        if self.modo_juego == "automatico":
            self._programar_siguiente_turno()
        
        self.animando = False
    
    def _actualizar_mensaje_turno(self):
        """Actualiza el mensaje con el turno actual."""
        if self.estado:
            actual = self.estado['actual']
            nombre = self._get_nombre_jugador(actual)
            if self.modo_juego == "interactivo":
                self.mensaje = f"🎯 Turno de {nombre}"
            else:
                self.mensaje = f"🤖 Turno automático de {nombre}"
    
    def _terminar_juego(self, idx_ganador):
        """Termina el juego con un ganador."""
        self.juego_terminado = True
        self.ganador = self._get_nombre_jugador(idx_ganador)
        self.mensaje = f"🏆 ¡{self.ganador} ha ganado el juego!"
        self.pantalla_actual = "fin"
    
    def _reiniciar_juego(self):
        """Reinicia el juego."""
        self.pantalla_actual = "inicio"
        self.juego_terminado = False
        self.ganador = None
        self.estado = None
        self.valor_dado = None
        self.mensaje = "¡Bienvenidos al Juego!"
        self.nombres_jugadores = ["", "", "", ""]
        self.nombre_actual = 0
        self.animando = False
        self.esperando = False

# Punto de entrada
if __name__ == "__main__":
    juego_gui = JuegoGUI()
    juego_gui.ejecutar()