import sys
import pygame
import logic.logica as juego
from logic.datos_tablero import CAMINO, CELDAS_ESPECIALES, PUNTUACION_PARA_GANAR
import random
import time

class JuegoGUI:
    def __init__(self):
        pygame.init()
        self.ventana = pygame.display.set_mode((1500, 900))
        pygame.display.set_caption("Entregable 1 - Programacion Funcional")
        self.reloj = pygame.time.Clock()

        # Colores
        self.colores = {
            'fondo': (25, 27, 36),
            'texto': (235, 237, 240),
            'texto_oscuro': (45, 48, 55),
            'dorado': (220, 180, 80),
            'borde': (190, 184, 192),
            'auto': (205, 220, 215),
            'interactivo': (205, 215, 235),
            'boton': (70, 75, 90),
            'boton_hover': (90, 98, 115),
            'boton_menos': (120, 128, 145),
            'boton_mas': (120, 128, 145),
            'casilla': (235, 237, 240),
            'inicio': (170, 210, 190),
            'fin': (220, 180, 190),
            'P1': (245, 215, 175),
            'P2': (245, 215, 175),
            'P3': (245, 215, 175),
            'C1': (235, 190, 235),
            'C2': (235, 190, 235),
            'dado': (245, 240, 225),
            'popup_fondo': (30, 30, 40, 200),
            'popup_borde': (200, 180, 100),
            'dashboard_fondo': (40, 45, 60),
            'dashboard_borde': (100, 110, 130),
            'cuadrante_fondo': (60, 65, 80),
            'cuadrante_turno': (255, 215, 0),
        }
        # Colores para fichas de jugadores
        self.colores_jugadores = [(255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 255, 100)]

        self.fuente_pequena = pygame.font.SysFont("Arial", 18)
        self.fuente_mediana = pygame.font.SysFont("Arial", 24)
        self.fuente_grande = pygame.font.SysFont("Arial", 48)
        self.fuente_titulo = pygame.font.SysFont("Arial", 64, bold=True)
        self.fuente_reglas = pygame.font.SysFont("Arial", 22)

        # Botones de inicio
        self.boton_automatico = pygame.Rect(400, 350, 250, 60)
        self.boton_interactivo = pygame.Rect(900, 350, 250, 60)
        self.boton_auto_hover = False
        self.boton_interactivo_hover = False

        self.pantalla_actual = "inicio"
        self.modo_juego = None
        self.mensaje = "¡Bienvenidos al Juego!"
        self.cantidad_jugadores = 2
        self.boton_mas = None
        self.boton_menos = None
        self.boton_continuar = None
        self.boton_continuar_hover = False

        # Variables del juego
        self.estado = None
        self.jugadores = []
        self.juego_terminado = False
        self.animando = False
        self.tiempo_ultimo_auto = 0
        self.en_competencia = False
        self.jugadores_empate = None

        # Botón tirar dado (se actualizará en dibujar_dashboard)
        self.boton_tirar = None
        self.boton_hover = False

        # ----- NUEVAS COORDENADAS -----
        self.dashboard_x = 20
        self.dashboard_y = 50
        self.dashboard_ancho = 300
        self.dashboard_alto = 780   # deja margen inferior

        self.dado_x = self.dashboard_x + 20
        self.dado_y = self.dashboard_y + 10
        self.dado_tam = 80

        self.mensaje_x = self.dashboard_x + 15
        self.mensaje_y = self.dado_y + self.dado_tam + 20
        self.mensaje_ancho = self.dashboard_ancho - 30

        self.jugadores_x = self.dashboard_x + 15
        self.jugadores_y = self.mensaje_y + 70   # espacio para mensaje
        self.jugador_cuadrante_w = 130
        self.jugador_cuadrante_h = 80
        self.separacion = 10

        self.tablero_x = 340
        self.tablero_y = 50
        self.casilla = 60

        # Botón para cerrar el pop-up de reglas
        self.boton_continuar_reglas = pygame.Rect(1500//2 - 100, 780, 200, 50)
        self.boton_continuar_reglas_hover = False

    def ejecutar(self):
        while True:
            self.procesar_eventos()
            self.actualizar()
            self.dibujar()
            self.reloj.tick(60)

    # ---------- EVENTOS (igual que antes) ----------
    def procesar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if self.pantalla_actual == "inicio":
                self._procesar_eventos_inicio(evento)
            elif self.pantalla_actual == "cantidad_jugadores":
                self.procesar_cantidad_jugadores(evento)
            elif self.pantalla_actual == "reglas":
                self.procesar_eventos_reglas(evento)
            elif self.pantalla_actual == "juego":
                self.procesar_eventos_juego(evento)

    def _procesar_eventos_inicio(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if self.boton_automatico.collidepoint(evento.pos):
                self.modo_juego = "automatico"
                self.pantalla_actual = "cantidad_jugadores"
            elif self.boton_interactivo.collidepoint(evento.pos):
                self.modo_juego = "interactivo"
                self.pantalla_actual = "cantidad_jugadores"
        elif evento.type == pygame.MOUSEMOTION:
            self.boton_auto_hover = self.boton_automatico.collidepoint(evento.pos)
            self.boton_interactivo_hover = self.boton_interactivo.collidepoint(evento.pos)

    def procesar_cantidad_jugadores(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if self.boton_menos.collidepoint(evento.pos):
                if self.cantidad_jugadores > 2:
                    self.cantidad_jugadores -= 1
            elif self.boton_mas.collidepoint(evento.pos):
                if self.cantidad_jugadores < 4:
                    self.cantidad_jugadores += 1
            elif self.boton_continuar.collidepoint(evento.pos):
                self.estado = juego.estado_inicial(self.cantidad_jugadores)
                self.jugadores = [f"Jugador {i+1}" for i in range(self.cantidad_jugadores)]
                self.pantalla_actual = "reglas"
                self.mensaje = "Reglas del juego"
        elif evento.type == pygame.MOUSEMOTION:
            if self.boton_continuar:
                self.boton_continuar_hover = self.boton_continuar.collidepoint(evento.pos)

    def procesar_eventos_reglas(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:
                self.cerrar_reglas()
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            if self.boton_continuar_reglas.collidepoint(evento.pos):
                self.cerrar_reglas()
        elif evento.type == pygame.MOUSEMOTION:
            self.boton_continuar_reglas_hover = self.boton_continuar_reglas.collidepoint(evento.pos)

    def cerrar_reglas(self):
        self.pantalla_actual = "juego"
        self.mensaje = f"¡Comienza el juego! Turno de {self.jugadores[0]}"

    def procesar_eventos_juego(self, evento):
        if self.modo_juego == "interactivo":
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if self.boton_tirar and self.boton_tirar.collidepoint(evento.pos) and not self.juego_terminado:
                    self.tirar_dado()
            elif evento.type == pygame.MOUSEMOTION:
                if self.boton_tirar:
                    self.boton_hover = self.boton_tirar.collidepoint(evento.pos)

    # ---------- ACTUALIZAR ----------
    def actualizar(self):
        if self.pantalla_actual == "juego" and self.modo_juego == "automatico" and not self.juego_terminado:
            ahora = pygame.time.get_ticks()
            if ahora - self.tiempo_ultimo_auto > 1000:
                self.tirar_dado()
                self.tiempo_ultimo_auto = ahora

    # ---------- TIRAR DADO ----------
    def tirar_dado(self):
        if self.juego_terminado:
            return

        estado = self.estado
        idx = estado['actual']
        dado = random.randint(1, 6)
        self.estado = juego.mover_jugador(estado, idx, dado)
        self.estado['valor_del_dado'] = dado
        self.mensaje = f"Jugador {idx+1} sacó {dado}"

        if juego.checkear_si_hay_competencia(self.estado, idx):
            self.resolver_competencia(idx)

        pos = self.estado['posiciones'][idx]
        if pos in CELDAS_ESPECIALES:
            clave = CELDAS_ESPECIALES[pos]
            nuevo_dado = None
            if clave == 'P2':
                nuevo_dado = random.randint(1, 6)
            self.estado = juego.aplicar_efecto_celda_especial(self.estado, idx, nuevo_dado)
            self.mensaje = self.estado.get('mensaje', self.mensaje)

        if self.estado['posiciones'][idx] >= PUNTUACION_PARA_GANAR:
            self.juego_terminado = True
            self.mensaje = f"¡Jugador {idx+1} ha ganado!"
            self.estado['ganador'] = idx
            return

        self.avanzar_turno()

    def resolver_competencia(self, idx_jugador):
        estado = self.estado
        pos = estado['posiciones'][idx_jugador]
        otro = None
        for i, p in enumerate(estado['posiciones']):
            if i != idx_jugador and p == pos:
                otro = i
                break
        if otro is None:
            return

        dado1 = random.randint(1, 6)
        dado2 = random.randint(1, 6)
        self.mensaje = f"Competencia: J{idx_jugador+1} ({dado1}) vs J{otro+1} ({dado2})"

        nuevo_estado = juego.resolver_competencia(estado, idx_jugador, otro, dado1, dado2)
        self.estado = nuevo_estado

        if nuevo_estado.get('competencia_empate', False):
            self.mensaje = "Empate, se repite la competencia"
            self.resolver_competencia(idx_jugador)
        else:
            self.mensaje = nuevo_estado.get('mensaje', self.mensaje)

    def avanzar_turno(self):
        estado = self.estado
        total = len(estado['posiciones'])
        siguiente = (estado['actual'] + 1) % total
        for _ in range(total):
            if not estado['pierde_turno'][siguiente]:
                break
            nuevo_pierde = list(estado['pierde_turno'])
            nuevo_pierde[siguiente] = False
            estado = dict(estado, pierde_turno=tuple(nuevo_pierde))
            siguiente = (siguiente + 1) % total
        self.estado = dict(estado, actual=siguiente)

    # ---------- DIBUJO ----------
    def dibujar(self):
        self.ventana.fill(self.colores['fondo'])
        if self.pantalla_actual == "inicio":
            self.pantalla_inicio()
        elif self.pantalla_actual == "cantidad_jugadores":
            self.pantalla_cantidad_jugadores()
        elif self.pantalla_actual == "reglas":
            self.pantalla_reglas()
        elif self.pantalla_actual == "juego":
            self.pantalla_juego()
        pygame.display.flip()

    # ---------- PANTALLAS ----------
    def pantalla_inicio(self):
        self.ventana.fill(self.colores['fondo'])
        titulo = self.fuente_grande.render("¡Bienvenidos!", True, (255, 215, 0))
        titulo_rect = titulo.get_rect(center=(1500//2, 150))
        self.ventana.blit(titulo, titulo_rect)

        subtitulo = self.fuente_mediana.render("Juego de Tablero", True, (220, 220, 240))
        subtitulo_rect = subtitulo.get_rect(center=(1500//2, 210))
        self.ventana.blit(subtitulo, subtitulo_rect)

        color_auto = self.colores['auto'] if not self.boton_auto_hover else self.colores['boton_hover']
        pygame.draw.rect(self.ventana, color_auto, self.boton_automatico, border_radius=15)
        texto = self.fuente_mediana.render("Juego Automático", True, self.colores['texto_oscuro'])
        texto_rect = texto.get_rect(center=self.boton_automatico.center)
        self.ventana.blit(texto, texto_rect)

        color_inter = self.colores['interactivo'] if not self.boton_interactivo_hover else self.colores['boton_hover']
        pygame.draw.rect(self.ventana, color_inter, self.boton_interactivo, border_radius=15)
        texto = self.fuente_mediana.render("Juego Interactivo", True, self.colores['texto_oscuro'])
        texto_rect = texto.get_rect(center=self.boton_interactivo.center)
        self.ventana.blit(texto, texto_rect)

        pie = self.fuente_pequena.render("Programación Avanzada - 2026", True, (180, 180, 200))
        pie_rect = pie.get_rect(center=(1500//2, 750))
        self.ventana.blit(pie, pie_rect)

    def pantalla_cantidad_jugadores(self):
        self.ventana.fill(self.colores['fondo'])
        titulo = self.fuente_grande.render("Selecciona la cantidad de jugadores", True, (255, 215, 0))
        titulo_rect = titulo.get_rect(center=(1500//2, 150))
        self.ventana.blit(titulo, titulo_rect)

        selector_y = 300
        ancho_total = 60 + 30 + 60 + 30 + 60
        x_inicio = 1500//2 - ancho_total//2

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

        x_mas = x_numero + 60 + 30
        self.boton_mas = pygame.Rect(x_mas, selector_y, 60, 60)
        pygame.draw.rect(self.ventana, self.colores['boton_mas'], self.boton_mas, border_radius=10)
        texto_mas = self.fuente_grande.render("+", True, (235, 237, 240))
        rect_mas = texto_mas.get_rect(center=self.boton_mas.center)
        self.ventana.blit(texto_mas, rect_mas)

        rango = self.fuente_pequena.render("(2 a 4 jugadores)", True, (180, 180, 200))
        rango_rect = rango.get_rect(center=(1500//2, 460))
        self.ventana.blit(rango, rango_rect)

        self.boton_continuar = pygame.Rect(1500//2 - 150, 500, 300, 60)
        color_cont = (100, 200, 100) if not self.boton_continuar_hover else (130, 230, 130)
        pygame.draw.rect(self.ventana, color_cont, self.boton_continuar, border_radius=15)
        texto_cont = self.fuente_mediana.render("Continuar", True, (235, 237, 240))
        rect_cont = texto_cont.get_rect(center=self.boton_continuar.center)
        self.ventana.blit(texto_cont, rect_cont)

        pie = self.fuente_pequena.render("Programación Avanzada - 2026", True, (180, 180, 200))
        pie_rect = pie.get_rect(center=(1500//2, 750))
        self.ventana.blit(pie, pie_rect)

    def pantalla_reglas(self):
        self.dibujar_tablero()
        self.dibujar_dashboard()

        # Pop-up semitransparente
        s = pygame.Surface((1500, 900), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.ventana.blit(s, (0, 0))

        popup_rect = pygame.Rect(150, 100, 1200, 700)
        pygame.draw.rect(self.ventana, (50, 55, 70), popup_rect, border_radius=20)
        pygame.draw.rect(self.ventana, (200, 180, 100), popup_rect, 4, border_radius=20)

        titulo = self.fuente_grande.render("Reglas del Juego", True, (255, 215, 0))
        self.ventana.blit(titulo, (1500//2 - titulo.get_width()//2, 130))

        reglas_texto = [
            "• Los jugadores comienzan en la casilla INICIO y avanzan tirando un dado (1-6).",
            "• El juego termina cuando un jugador alcanza la casilla FIN.",
            "• Si caes en una casilla especial (P1, P2, P3, C1, C2), se aplica su efecto.",
            "• Si dos jugadores caen en la misma casilla, compiten por ella:",
            "  - El que saque mayor dado se queda, el otro retrocede 2 casilleros.",
            "  - Si al retroceder cae en otra casilla ocupada, retrocede 1 más.",
            "• No hay rebote: si te faltan menos casillas que el dado, llegas a FIN.",
            "",
            "Casillas especiales:",
            "  P1: El jugador elige a otro para que pierda su próximo turno.",
            "  P2: Tira el dado nuevamente y avanza lo que salga.",
            "  P3: Avanza 2 casillas.",
            "  C1: Pierde su próximo turno.",
            "  C2: Retrocede 3 casillas."
        ]

        y_texto = 200
        for linea in reglas_texto:
            if linea.startswith("  "):
                texto = self.fuente_reglas.render(linea, True, (200, 200, 210))
                self.ventana.blit(texto, (200, y_texto))
            else:
                texto = self.fuente_reglas.render(linea, True, (235, 237, 240))
                self.ventana.blit(texto, (180, y_texto))
            y_texto += 30

        msg_final = self.fuente_grande.render("Apretar ESPACIO para continuar", True, (255, 255, 200))
        msg_rect = msg_final.get_rect(center=(1500//2, 720))
        self.ventana.blit(msg_final, msg_rect)

        color_btn = (100, 200, 100) if not self.boton_continuar_reglas_hover else (130, 230, 130)
        pygame.draw.rect(self.ventana, color_btn, self.boton_continuar_reglas, border_radius=15)
        texto_btn = self.fuente_mediana.render("Continuar", True, (235, 237, 240))
        rect_btn = texto_btn.get_rect(center=self.boton_continuar_reglas.center)
        self.ventana.blit(texto_btn, rect_btn)

    def pantalla_juego(self):
        self.dibujar_tablero()
        self.dibujar_dashboard()

        if self.juego_terminado:
            s = pygame.Surface((1500, 900), pygame.SRCALPHA)
            s.fill((0, 0, 0, 150))
            self.ventana.blit(s, (0, 0))
            ganador = self.estado['ganador']
            if ganador is not None:
                msg = self.fuente_grande.render(f"¡Jugador {ganador+1} GANA!", True, (255, 215, 0))
            else:
                msg = self.fuente_grande.render("¡Juego Terminado!", True, (255, 215, 0))
            msg_rect = msg.get_rect(center=(1500//2, 400))
            self.ventana.blit(msg, msg_rect)

    # ---------- DIBUJAR TABLERO ----------
    def dibujar_tablero(self):
        tablero_rect = pygame.Rect(self.tablero_x - 10, self.tablero_y - 10,
                                   10 * (self.casilla + 2) + 20,
                                   10 * (self.casilla + 2) + 20)
        interior_rect = pygame.Rect(self.tablero_x, self.tablero_y,
                                    10 * (self.casilla + 2) - 2,
                                    10 * (self.casilla + 2) - 2)
        pygame.draw.rect(self.ventana, (180, 170, 160), interior_rect)
        pygame.draw.rect(self.ventana, (200, 180, 100), tablero_rect, 4, border_radius=10)

        for i, (fila, col) in enumerate(CAMINO):
            x = self.tablero_x + col * (self.casilla + 2)
            y = self.tablero_y + fila * (self.casilla + 2)
            rect = (x, y, self.casilla, self.casilla)

            color = self.colores.get('casilla', (235, 237, 240))
            if i in CELDAS_ESPECIALES:
                tipo = CELDAS_ESPECIALES[i]
                if tipo in self.colores:
                    color = self.colores[tipo]
            elif i == 0:
                color = self.colores.get('inicio', (170, 210, 190))
            elif i == len(CAMINO) - 1:
                color = self.colores.get('fin', (220, 180, 190))

            pygame.draw.rect(self.ventana, color, rect)
            pygame.draw.rect(self.ventana, self.colores.get('borde', (190, 184, 192)), rect, 2)

            if i in CELDAS_ESPECIALES:
                tipo = CELDAS_ESPECIALES[i]
                texto_casilla = self.fuente_pequena.render(tipo, True, (50, 50, 50))
                self.ventana.blit(texto_casilla, (x + 5, y + 5))
            elif i == 0:
                texto_casilla = self.fuente_pequena.render("INICIO", True, (50, 50, 50))
                self.ventana.blit(texto_casilla, (x + 5, y + 5))
            elif i == len(CAMINO) - 1:
                texto_casilla = self.fuente_pequena.render("FIN", True, (50, 50, 50))
                self.ventana.blit(texto_casilla, (x + 5, y + 5))

        # Fichas de jugadores
        if self.estado:
            posiciones = self.estado['posiciones']
            for idx, pos in enumerate(posiciones):
                if pos >= len(CAMINO):
                    continue
                fila, col = CAMINO[pos]
                cx = self.tablero_x + col * (self.casilla + 2) + self.casilla // 2
                cy = self.tablero_y + fila * (self.casilla + 2) + self.casilla // 2
                offset_x = (idx % 2) * 15 - 7
                offset_y = (idx // 2) * 15 - 7
                pygame.draw.circle(self.ventana, self.colores_jugadores[idx % len(self.colores_jugadores)],
                                   (cx + offset_x, cy + offset_y), 12)
                num = self.fuente_pequena.render(str(idx+1), True, (255, 255, 255))
                self.ventana.blit(num, (cx + offset_x - 6, cy + offset_y - 8))

    # ---------- DIBUJAR DASHBOARD (NUEVO) ----------
    def dibujar_dashboard(self):
        # Fondo del dashboard
        panel_rect = pygame.Rect(self.dashboard_x, self.dashboard_y,
                                 self.dashboard_ancho, self.dashboard_alto)
        pygame.draw.rect(self.ventana, self.colores['dashboard_fondo'], panel_rect, border_radius=15)
        pygame.draw.rect(self.ventana, self.colores['dashboard_borde'], panel_rect, 3, border_radius=15)

        # Dado
        self._dibujar_dado(self.dado_x, self.dado_y, self.dado_tam)

        # Mensaje play-by-play
        if self.mensaje:
            lineas = self._dividir_texto(self.mensaje, self.fuente_mediana, self.mensaje_ancho)
            for i, linea in enumerate(lineas):
                texto = self.fuente_mediana.render(linea, True, (235, 237, 240))
                self.ventana.blit(texto, (self.mensaje_x, self.mensaje_y + i*30))
        else:
            texto = self.fuente_mediana.render("Esperando...", True, (200, 200, 210))
            self.ventana.blit(texto, (self.mensaje_x, self.mensaje_y))

        # Jugadores en cuadrícula 2x2
        if self.estado:
            num_jugadores = len(self.estado['posiciones'])
            cols = 2
            filas = (num_jugadores + 1) // 2  # redondeo hacia arriba
            ancho_cuadrante = self.jugador_cuadrante_w
            alto_cuadrante = self.jugador_cuadrante_h

            for i in range(num_jugadores):
                fila = i // cols
                col = i % cols
                x = self.jugadores_x + col * (ancho_cuadrante + self.separacion)
                y = self.jugadores_y + fila * (alto_cuadrante + self.separacion)
                rect = pygame.Rect(x, y, ancho_cuadrante, alto_cuadrante)

                # Fondo del cuadrante
                color_fondo = self.colores['cuadrante_fondo']
                pygame.draw.rect(self.ventana, color_fondo, rect, border_radius=8)

                # Borde: si es el turno actual, borde amarillo grueso
                if i == self.estado['actual']:
                    pygame.draw.rect(self.ventana, self.colores['cuadrante_turno'], rect, 4, border_radius=8)
                else:
                    pygame.draw.rect(self.ventana, (80, 85, 100), rect, 2, border_radius=8)

                # Nombre del jugador
                nombre = self.jugadores[i] if i < len(self.jugadores) else f"Jugador {i+1}"
                texto_nom = self.fuente_mediana.render(nombre, True, (235, 237, 240))
                self.ventana.blit(texto_nom, (rect.x + 10, rect.y + 8))

                # Casilla
                pos = self.estado['posiciones'][i]
                texto_pos = self.fuente_pequena.render(f"Casilla: {pos}", True, (200, 200, 210))
                self.ventana.blit(texto_pos, (rect.x + 10, rect.y + 45))

            # Botón "Tirar Dado" (solo interactivo)
            if self.modo_juego == "interactivo" and not self.juego_terminado:
                boton_y = self.jugadores_y + filas * (alto_cuadrante + self.separacion) + 20
                self.boton_tirar = pygame.Rect(self.dashboard_x + 40, boton_y, 220, 50)
                color_btn = self.colores['boton'] if not self.boton_hover else self.colores['boton_hover']
                pygame.draw.rect(self.ventana, color_btn, self.boton_tirar, border_radius=15)
                texto_btn = self.fuente_mediana.render("Tirar Dado", True, (235, 237, 240))
                texto_btn_rect = texto_btn.get_rect(center=self.boton_tirar.center)
                self.ventana.blit(texto_btn, texto_btn_rect)
        else:
            texto = self.fuente_mediana.render("Sin jugadores", True, (200, 200, 210))
            self.ventana.blit(texto, (self.jugadores_x, self.jugadores_y))

    # ---------- DIBUJAR DADO (privado) ----------
    def _dibujar_dado(self, x, y, tam):
        valor = 1
        if self.estado and self.estado.get('valor_del_dado') is not None:
            valor = self.estado['valor_del_dado']

        dado_rect = pygame.Rect(x, y, tam, tam)
        pygame.draw.rect(self.ventana, (245, 240, 225), dado_rect, border_radius=12)
        pygame.draw.rect(self.ventana, (90, 98, 115), dado_rect, 3, border_radius=12)

        puntos = {
            1: [(0, 0)],
            2: [(-tam//4, -tam//4), (tam//4, tam//4)],
            3: [(-tam//4, -tam//4), (0, 0), (tam//4, tam//4)],
            4: [(-tam//4, -tam//4), (-tam//4, tam//4), (tam//4, -tam//4), (tam//4, tam//4)],
            5: [(-tam//4, -tam//4), (-tam//4, tam//4), (0, 0), (tam//4, -tam//4), (tam//4, tam//4)],
            6: [(-tam//4, -tam//4), (-tam//4, 0), (-tam//4, tam//4), (tam//4, -tam//4), (tam//4, 0), (tam//4, tam//4)]
        }
        for dx, dy in puntos.get(valor, []):
            cx = x + tam//2 + dx
            cy = y + tam//2 + dy
            pygame.draw.circle(self.ventana, (35, 35, 40), (cx, cy), tam//10)

    # ---------- UTILIDAD ----------
    def _dividir_texto(self, texto, fuente, ancho_max):
        lineas = []
        palabras = texto.split(' ')
        linea_actual = ""
        for palabra in palabras:
            prueba = linea_actual + " " + palabra if linea_actual else palabra
            if fuente.size(prueba)[0] <= ancho_max:
                linea_actual = prueba
            else:
                if linea_actual:
                    lineas.append(linea_actual)
                linea_actual = palabra
        if linea_actual:
            lineas.append(linea_actual)
        return lineas