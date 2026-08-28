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
            'popup_fondo': (30, 30, 40, 200),  # semi-transparente
            'popup_borde': (200, 180, 100),
        }
        # Colores para jugadores
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

        self.pantalla_actual = "inicio"   # "inicio", "cantidad_jugadores", "reglas", "juego", "fin"
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

        # Botón tirar dado (solo en modo interactivo)
        self.boton_tirar = pygame.Rect(160, 700, 200, 60)
        self.boton_hover = False

        # Posiciones del tablero
        self.casilla = 60
        self.x = 50
        self.y = 50
        self.dadox = 1200
        self.dadoy = 200
        self.dado = 80
        self.info_y = 650  # posición Y donde empieza el dashboard

        # Botón para cerrar el pop-up de reglas
        self.boton_continuar_reglas = pygame.Rect(1500//2 - 100, 780, 200, 50)
        self.boton_continuar_reglas_hover = False

    def ejecutar(self):
        while True:
            self.procesar_eventos()
            self.actualizar()
            self.dibujar()
            self.reloj.tick(60)

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

    # ---------- EVENTOS INICIO ----------
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

    # ---------- EVENTOS CANTIDAD JUGADORES ----------
    def procesar_cantidad_jugadores(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if self.boton_menos.collidepoint(evento.pos):
                if self.cantidad_jugadores > 2:
                    self.cantidad_jugadores -= 1
            elif self.boton_mas.collidepoint(evento.pos):
                if self.cantidad_jugadores < 4:
                    self.cantidad_jugadores += 1
            elif self.boton_continuar.collidepoint(evento.pos):
                # Inicializamos el estado del juego y pasamos a la pantalla de reglas
                self.estado = juego.estado_inicial(self.cantidad_jugadores)
                self.jugadores = [f"Jugador {i+1}" for i in range(self.cantidad_jugadores)]
                self.pantalla_actual = "reglas"
                self.mensaje = "Reglas del juego"
        elif evento.type == pygame.MOUSEMOTION:
            if self.boton_continuar:
                self.boton_continuar_hover = self.boton_continuar.collidepoint(evento.pos)

    # ---------- EVENTOS REGLAS ----------
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
        """Cierra el pop-up de reglas y comienza el juego."""
        self.pantalla_actual = "juego"
        self.mensaje = f"¡Comienza el juego! Turno de {self.jugadores[0]}"

    # ---------- EVENTOS JUEGO ----------
    def procesar_eventos_juego(self, evento):
        if self.modo_juego == "interactivo":
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if self.boton_tirar.collidepoint(evento.pos) and not self.juego_terminado:
                    self.tirar_dado()
            elif evento.type == pygame.MOUSEMOTION:
                self.boton_hover = self.boton_tirar.collidepoint(evento.pos)

        # En modo automático, manejamos el tiempo en actualizar()

    # ---------- ACTUALIZAR ----------
    def actualizar(self):
        if self.pantalla_actual == "juego" and self.modo_juego == "automatico" and not self.juego_terminado:
            ahora = pygame.time.get_ticks()
            if ahora - self.tiempo_ultimo_auto > 1000:  # cada 1 segundo
                self.tirar_dado()
                self.tiempo_ultimo_auto = ahora

    # ---------- TIRAR DADO (lógica principal) ----------
    def tirar_dado(self):
        if self.juego_terminado:
            return

        estado = self.estado
        idx = estado['actual']
        dado = random.randint(1, 6)
        self.estado = juego.mover_jugador(estado, idx, dado)
        self.estado['valor_del_dado'] = dado
        self.mensaje = f"Jugador {idx+1} sacó {dado}"

        # Verificar si hay competencia
        if juego.checkear_si_hay_competencia(self.estado, idx):
            self.resolver_competencia(idx)

        # Verificar efectos de casilla especial
        pos = self.estado['posiciones'][idx]
        if pos in CELDAS_ESPECIALES:
            clave = CELDAS_ESPECIALES[pos]
            # Para P2 necesitamos un nuevo dado
            nuevo_dado = None
            if clave == 'P2':
                nuevo_dado = random.randint(1, 6)
            self.estado = juego.aplicar_efecto_celda_especial(self.estado, idx, nuevo_dado)
            self.mensaje = self.estado.get('mensaje', self.mensaje)

        # Verificar ganador
        if self.estado['posiciones'][idx] >= PUNTUACION_PARA_GANAR:
            self.juego_terminado = True
            self.mensaje = f"¡Jugador {idx+1} ha ganado!"
            self.estado['ganador'] = idx
            return

        # Pasar turno al siguiente (que no pierda turno)
        self.avanzar_turno()

    def resolver_competencia(self, idx_jugador):
        """Resuelve una competencia entre el jugador actual y el que está en su misma casilla."""
        estado = self.estado
        pos = estado['posiciones'][idx_jugador]
        # Encontrar al otro jugador en la misma posición
        otro = None
        for i, p in enumerate(estado['posiciones']):
            if i != idx_jugador and p == pos:
                otro = i
                break
        if otro is None:
            return

        dado1 = random.randint(1, 6)
        dado2 = random.randint(1, 6)
        self.mensaje = f"Competencia: Jugador {idx_jugador+1} ({dado1}) vs Jugador {otro+1} ({dado2})"

        # Aplicar resolución
        nuevo_estado = juego.resolver_competencia(estado, idx_jugador, otro, dado1, dado2)
        self.estado = nuevo_estado

        # Si hay empate, el estado tendrá 'competencia_empate' True
        if nuevo_estado.get('competencia_empate', False):
            self.mensaje = "Empate, se repite la competencia"
            self.resolver_competencia(idx_jugador)  # recursivo
        else:
            self.mensaje = nuevo_estado.get('mensaje', self.mensaje)

    def avanzar_turno(self):
        """Avanza al siguiente jugador que no pierda turno."""
        estado = self.estado
        total = len(estado['posiciones'])
        siguiente = (estado['actual'] + 1) % total
        # Buscar el siguiente que no pierda turno
        for _ in range(total):
            if not estado['pierde_turno'][siguiente]:
                break
            # Si pierde turno, lo desactivamos y pasamos al siguiente
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
        elif self.pantalla_actual == "fin":
            self.pantalla_fin()
        pygame.display.flip()

    # ---------- PANTALLA INICIO ----------
    def pantalla_inicio(self):
        self.ventana.fill(self.colores['fondo'])
        titulo = self.fuente_grande.render("¡Bienvenidos!", True, (255, 215, 0))
        titulo_rect = titulo.get_rect(center=(1500//2, 150))
        self.ventana.blit(titulo, titulo_rect)

        subtitulo = self.fuente_mediana.render("Juego de Tablero", True, (220, 220, 240))
        subtitulo_rect = subtitulo.get_rect(center=(1500//2, 210))
        self.ventana.blit(subtitulo, subtitulo_rect)

        # Botón Automático
        color_auto = self.colores['auto'] if not self.boton_auto_hover else self.colores['boton_hover']
        pygame.draw.rect(self.ventana, color_auto, self.boton_automatico, border_radius=15)
        texto = self.fuente_mediana.render("Juego Automático", True, self.colores['texto_oscuro'])
        texto_rect = texto.get_rect(center=self.boton_automatico.center)
        self.ventana.blit(texto, texto_rect)

        # Botón Interactivo
        color_inter = self.colores['interactivo'] if not self.boton_interactivo_hover else self.colores['boton_hover']
        pygame.draw.rect(self.ventana, color_inter, self.boton_interactivo, border_radius=15)
        texto = self.fuente_mediana.render("Juego Interactivo", True, self.colores['texto_oscuro'])
        texto_rect = texto.get_rect(center=self.boton_interactivo.center)
        self.ventana.blit(texto, texto_rect)

        pie = self.fuente_pequena.render("Programación Avanzada - 2026", True, (180, 180, 200))
        pie_rect = pie.get_rect(center=(1500//2, 750))
        self.ventana.blit(pie, pie_rect)

    # ---------- PANTALLA CANTIDAD JUGADORES ----------
    def pantalla_cantidad_jugadores(self):
        self.ventana.fill(self.colores['fondo'])
        titulo = self.fuente_grande.render("Selecciona la cantidad de jugadores", True, (255, 215, 0))
        titulo_rect = titulo.get_rect(center=(1500//2, 150))
        self.ventana.blit(titulo, titulo_rect)

        selector_y = 300
        ancho_total = 60 + 30 + 60 + 30 + 60
        x_inicio = 1500//2 - ancho_total//2

        # Botón menos
        x_menos = x_inicio
        self.boton_menos = pygame.Rect(x_menos, selector_y, 60, 60)
        pygame.draw.rect(self.ventana, self.colores['boton_menos'], self.boton_menos, border_radius=10)
        texto_menos = self.fuente_grande.render("-", True, (235, 237, 240))
        rect_menos = texto_menos.get_rect(center=self.boton_menos.center)
        self.ventana.blit(texto_menos, rect_menos)

        # Número
        x_numero = x_menos + 60 + 30
        texto_cant = self.fuente_titulo.render(str(self.cantidad_jugadores), True, self.colores['dorado'])
        rect_cant = texto_cant.get_rect(center=(x_numero + 30, selector_y + 30))
        self.ventana.blit(texto_cant, rect_cant)

        # Botón más
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

    # ---------- PANTALLA REGLAS ----------
    def pantalla_reglas(self):
        # Dibujamos el fondo del tablero (igual que en la pantalla de juego)
        self.dibujar_tablero()
        self.dibujar_dado()
        self.dibujar_dashboard()  # placeholder

        # Pop-up semitransparente
        s = pygame.Surface((1500, 900), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.ventana.blit(s, (0, 0))

        popup_rect = pygame.Rect(150, 100, 1200, 700)
        pygame.draw.rect(self.ventana, (50, 55, 70), popup_rect, border_radius=20)
        pygame.draw.rect(self.ventana, (200, 180, 100), popup_rect, 4, border_radius=20)

        # Título
        titulo = self.fuente_grande.render("Reglas del Juego", True, (255, 215, 0))
        self.ventana.blit(titulo, (1500//2 - titulo.get_width()//2, 130))

        # Texto de reglas (viñetas)
        reglas_texto = [
            "• Los jugadores comienzan en la casilla INICIO y avanzan tirando un dado (1-6).",
            "• El juego termina cuando un jugador alcanza la casilla FIN.",
            "• Si caes en una casilla especial (P1, P2, P3, C1, C2), se aplica su efecto.",
            "• Si dos jugadores caen en la misma casilla, compiten por ella:",
            "  - El que saque mayor dado se queda, el otro retrocede 2 casilla.",
            "  - Si al retroceder cae en otra casilla ocupada, retrocede de a 1 casilla hasta llegar a una vacía (o al inicio).",
            "• No hay rebote: si te faltan menos casillas que el dado, llegas a FIN.",
            "",
            "Casillas especiales:",
            "  P1: El jugador elige a otro para que pierda su próximo turno.",
            "  P2: Tira el dado nuevamente y avanza lo que salga.",
            "  P3: Avanza 2 casillas.",
            "  C1: Pierde su próximo turno.",
            "  C2: Retrocede 3 casillas."
        ]

        # Diccionario de colores para cada tipo de casilla especial
        colores_casillas = {
            'P1': self.colores.get('P1', (245, 215, 175)),
            'P2': self.colores.get('P2', (245, 215, 175)),
            'P3': self.colores.get('P3', (245, 215, 175)),
            'C1': self.colores.get('C1', (235, 190, 235)),
            'C2': self.colores.get('C2', (235, 190, 235)),
        }

        y_texto = 200
        for linea in reglas_texto:
            # Determinar color de la línea
            if linea.startswith("  P1"):
                color = colores_casillas['P1']
            elif linea.startswith("  P2"):
                color = colores_casillas['P2']
            elif linea.startswith("  P3"):
                color = colores_casillas['P3']
            elif linea.startswith("  C1"):
                color = colores_casillas['C1']
            elif linea.startswith("  C2"):
                color = colores_casillas['C2']
            elif linea.startswith("  "):
                # Sub-items (como los guiones de competencia)
                color = (200, 200, 210)
            else:
                color = (235, 237, 240)

            # Renderizar con el color elegido
            if linea.strip() == "":
                y_texto += 10  # espacio extra para línea vacía
                continue
            texto = self.fuente_reglas.render(linea, True, color)
            # Posición X: si la línea empieza con espacio, la sangramos un poco más
            if linea.startswith("  "):
                x = 200
            else:
                x = 180
            self.ventana.blit(texto, (x, y_texto))
            y_texto += 30

        # Mensaje final en negrita y grande
        msg_final = self.fuente_grande.render("Apretar ESPACIO para continuar", True, (255, 255, 200))
        msg_rect = msg_final.get_rect(center=(1500//2, 720))
        self.ventana.blit(msg_final, msg_rect)

        # Botón verde "Continuar"
        color_btn = (100, 200, 100) if not self.boton_continuar_reglas_hover else (130, 230, 130)
        pygame.draw.rect(self.ventana, color_btn, self.boton_continuar_reglas, border_radius=15)
        texto_btn = self.fuente_mediana.render("Continuar", True, (235, 237, 240))
        rect_btn = texto_btn.get_rect(center=self.boton_continuar_reglas.center)
        self.ventana.blit(texto_btn, rect_btn)

    # ---------- PANTALLA JUEGO ----------
    def pantalla_juego(self):
        self.dibujar_tablero()
        self.dibujar_dado()
        self.dibujar_dashboard()

        # Botón tirar dado (solo en modo interactivo)
        if self.modo_juego == "interactivo" and not self.juego_terminado:
            color = self.colores['boton'] if not self.boton_hover else self.colores['boton_hover']
            pygame.draw.rect(self.ventana, color, self.boton_tirar, border_radius=15)
            texto = self.fuente_mediana.render("Tirar Dado", True, (235, 237, 240))
            texto_rect = texto.get_rect(center=self.boton_tirar.center)
            self.ventana.blit(texto, texto_rect)

        if self.juego_terminado:
            # Mensaje de fin de juego
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
        # Fondo del tablero
        tablero_rect = pygame.Rect(self.x - 10, self.y - 10,
                                   10 * (self.casilla + 2) + 20,
                                   10 * (self.casilla + 2) + 20)
        interior_rect = pygame.Rect(self.x, self.y,
                                    10 * (self.casilla + 2) - 2,
                                    10 * (self.casilla + 2) - 2)
        pygame.draw.rect(self.ventana, (180, 170, 160), interior_rect)
        pygame.draw.rect(self.ventana, (200, 180, 100), tablero_rect, 4, border_radius=10)

        # Dibujar cada casilla
        for i, (fila, col) in enumerate(CAMINO):
            x = self.x + col * (self.casilla + 2)
            y = self.y + fila * (self.casilla + 2)
            rect = (x, y, self.casilla, self.casilla)

            # Color de la casilla
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

            # Texto de la casilla
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

        # Dibujar fichas de jugadores (si existe estado)
        if self.estado:
            posiciones = self.estado['posiciones']
            for idx, pos in enumerate(posiciones):
                if pos >= len(CAMINO):
                    continue  # podría estar en FIN (índice 35 no está en CAMINO)
                fila, col = CAMINO[pos]
                cx = self.x + col * (self.casilla + 2) + self.casilla // 2
                cy = self.y + fila * (self.casilla + 2) + self.casilla // 2
                # Desplazamiento para que no se superpongan
                offset_x = (idx % 2) * 15 - 7
                offset_y = (idx // 2) * 15 - 7
                pygame.draw.circle(self.ventana, self.colores_jugadores[idx % len(self.colores_jugadores)],
                                   (cx + offset_x, cy + offset_y), 12)
                # Número del jugador
                num = self.fuente_pequena.render(str(idx+1), True, (255, 255, 255))
                self.ventana.blit(num, (cx + offset_x - 6, cy + offset_y - 8))

    # ---------- DIBUJAR DADO ----------
    def dibujar_dado(self):
        x, y = self.dadox, self.dadoy
        tam = self.dado
        valor = 1
        if self.estado and self.estado.get('valor_del_dado') is not None:
            valor = self.estado['valor_del_dado']

        dado_rect = pygame.Rect(x, y, tam, tam)
        pygame.draw.rect(self.ventana, (245, 240, 225), dado_rect, border_radius=12)
        pygame.draw.rect(self.ventana, (90, 98, 115), dado_rect, 3, border_radius=12)

        # Puntos del dado
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

    # ---------- DIBUJAR DASHBOARD ----------
    def dibujar_dashboard(self):
        # Panel de información (turno, mensajes, etc.)
        panel_y = self.info_y
        pygame.draw.rect(self.ventana, (40, 45, 60), (20, panel_y, 1460, 220), border_radius=15)
        pygame.draw.rect(self.ventana, (100, 110, 130), (20, panel_y, 1460, 220), 3, border_radius=15)

        if self.estado:
            # Turno actual
            turno = self.estado['actual'] + 1
            texto_turno = self.fuente_mediana.render(f"Turno: Jugador {turno}", True, (255, 215, 0))
            self.ventana.blit(texto_turno, (40, panel_y + 20))

            # Mensaje
            if self.mensaje:
                msg = self.fuente_mediana.render(self.mensaje, True, (235, 237, 240))
                self.ventana.blit(msg, (40, panel_y + 70))

            # Posiciones de los jugadores
            pos_text = "Posiciones: "
            for i, p in enumerate(self.estado['posiciones']):
                pos_text += f"J{i+1}: {p}  "
            pos_render = self.fuente_pequena.render(pos_text, True, (200, 200, 210))
            self.ventana.blit(pos_render, (40, panel_y + 120))

            # Pierde turno
            pierde = [i for i, v in enumerate(self.estado['pierde_turno']) if v]
            if pierde:
                pierde_text = "Pierden turno: " + ", ".join([f"J{p+1}" for p in pierde])
                pierde_render = self.fuente_pequena.render(pierde_text, True, (255, 150, 150))
                self.ventana.blit(pierde_render, (40, panel_y + 150))
        else:
            # Si no hay estado, mostrar mensaje de espera
            msg = self.fuente_mediana.render("Esperando inicio del juego...", True, (200, 200, 210))
            self.ventana.blit(msg, (40, panel_y + 30))

    # ---------- PANTALLA FIN (si se necesita) ----------
    def pantalla_fin(self):
        # Por ahora no se usa, pero podría mostrar el ganador
        pass