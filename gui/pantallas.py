"""
Pantallas del juego: Menú principal, juego, puntajes, fin de juego.
"""

import pygame
import math
import random
from typing import Tuple, Optional, List, Callable
from datetime import datetime

from modelo.mapa import Mapa
from modelo.jugador import Jugador
from logica.generador_mapa import GeneradorMapa
from sistema.puntajes import ScoreBoard, Puntaje, ModoJuego

from .config import Colores, Config
from .componentes import Boton, BarraEnergia, SistemaParticulas, CuadroTexto
from .renderizador import RenderizadorMapa


class PantallaBase:
    """Clase base para todas las pantallas."""
    
    def __init__(self, ancho: int, alto: int):
        self.ancho = ancho
        self.alto = alto
        self.siguiente_pantalla = None
        self.datos_retorno = {}
        
    def manejar_evento(self, evento: pygame.event.Event):
        """Maneja eventos de la pantalla."""
        pass
    
    def actualizar(self, dt: float):
        """Actualiza la lógica de la pantalla."""
        pass
    
    def dibujar(self, superficie: pygame.Surface):
        """Dibuja la pantalla."""
        pass


class MenuPrincipal(PantallaBase):
    """Menú principal del juego con animaciones y estilo retro."""
    
    def __init__(self, ancho: int, alto: int):
        super().__init__(ancho, alto)
        
        # Fuentes
        self.fuente_titulo = None
        self.fuente_subtitulo = None
        self.fuente_boton = None
        self.fuente_info = None
        
        # Estado
        self.tiempo = 0
        self.particulas = SistemaParticulas()
        self.estrellas = self._generar_estrellas(100)
        
        # Input del nombre
        self.cuadro_nombre = CuadroTexto(
            ancho // 2 - 200, 320, 400, 50,
            placeholder="Tu nombre..."
        )
        self.nombre_jugador = ""
        
        # Botones
        self.botones = []
        self._inicializar_botones()
        
    def _generar_estrellas(self, cantidad: int) -> List[dict]:
        """Genera estrellas de fondo."""
        estrellas = []
        for _ in range(cantidad):
            estrellas.append({
                'x': random.randint(0, self.ancho),
                'y': random.randint(0, self.alto),
                'tamano': random.uniform(1, 3),
                'velocidad': random.uniform(0.5, 2),
                'parpadeo_offset': random.uniform(0, math.pi * 2)
            })
        return estrellas
    
    def _inicializar_botones(self):
        """Inicializa los botones del menú."""
        centro_x = self.ancho // 2
        
        self.botones = [
            Boton(centro_x - 150, 410, 300, 55, "MODO ESCAPA",
                  color=Colores.CYAN_NEON,
                  accion=lambda: self._seleccionar_modo("escapa")),
            Boton(centro_x - 150, 485, 300, 55, "MODO CAZADOR",
                  color=Colores.MAGENTA_NEON,
                  accion=lambda: self._seleccionar_modo("cazador")),
            Boton(centro_x - 150, 560, 300, 55, "PUNTAJES",
                  color=Colores.AMARILLO_NEON,
                  accion=self._ver_puntajes),
            Boton(centro_x - 150, 635, 300, 55, "SALIR",
                  color=Colores.ROJO_NEON,
                  accion=self._salir),
        ]
    
    def _seleccionar_modo(self, modo: str):
        """Selecciona un modo de juego."""
        nombre = self.cuadro_nombre.obtener_texto()
        if not nombre:
            nombre = "Jugador"
        
        self.nombre_jugador = nombre
        self.siguiente_pantalla = "juego"
        self.datos_retorno = {
            "modo": modo,
            "nombre": nombre
        }
    
    def _ver_puntajes(self):
        """Navega a la pantalla de puntajes."""
        self.siguiente_pantalla = "puntajes"
    
    def _salir(self):
        """Sale del juego."""
        self.siguiente_pantalla = "salir"
    
    def inicializar_fuentes(self):
        """Inicializa las fuentes después de iniciar pygame."""
        pygame.font.init()
        self.fuente_titulo = pygame.font.Font(None, 86)
        self.fuente_subtitulo = pygame.font.Font(None, 36)
        self.fuente_boton = pygame.font.Font(None, 32)
        self.fuente_info = pygame.font.Font(None, 24)
    
    def manejar_evento(self, evento: pygame.event.Event):
        """Maneja eventos del menú."""
        self.cuadro_nombre.manejar_evento(evento)
        
        for boton in self.botones:
            boton.manejar_evento(evento)
    
    def actualizar(self, dt: float):
        """Actualiza animaciones del menú."""
        self.tiempo += dt
        
        # Actualizar cuadro de texto
        self.cuadro_nombre.actualizar(dt)
        
        # Actualizar botones
        pos_mouse = pygame.mouse.get_pos()
        for boton in self.botones:
            boton.actualizar(pos_mouse, dt)
        
        # Actualizar estrellas
        for estrella in self.estrellas:
            estrella['y'] += estrella['velocidad']
            if estrella['y'] > self.alto:
                estrella['y'] = 0
                estrella['x'] = random.randint(0, self.ancho)
        
        # Actualizar partículas
        self.particulas.actualizar(dt)
        
        # Emitir partículas ocasionalmente
        if random.random() < 0.1:
            x = random.randint(0, self.ancho)
            self.particulas.emitir(x, 0, Colores.CYAN_NEON, 1)
    
    def dibujar(self, superficie: pygame.Surface):
        """Dibuja el menú principal."""
        # Fondo con gradiente
        superficie.fill(Colores.FONDO_OSCURO)
        
        # Dibujar estrellas
        for estrella in self.estrellas:
            alpha = int(100 + 100 * math.sin(self.tiempo * 2 + estrella['parpadeo_offset']))
            color = (*Colores.TEXTO_SECUNDARIO[:3],)
            tamano = int(estrella['tamano'])
            pygame.draw.circle(superficie, color, 
                             (int(estrella['x']), int(estrella['y'])), tamano)
        
        # Dibujar partículas
        self.particulas.dibujar(superficie)
        
        # Título con efecto de glow
        self._dibujar_titulo(superficie)
        
        # Subtítulo
        subtitulo = self.fuente_subtitulo.render(
            "Un juego de laberinto con emoción", True, Colores.TEXTO_SECUNDARIO
        )
        subtitulo_rect = subtitulo.get_rect(center=(self.ancho // 2, 200))
        superficie.blit(subtitulo, subtitulo_rect)
        
        # Instrucción para el nombre
        instruccion = self.fuente_info.render(
            "Ingresa tu nombre para guardar tus puntajes:", True, Colores.TEXTO
        )
        instruccion_rect = instruccion.get_rect(center=(self.ancho // 2, 285))
        superficie.blit(instruccion, instruccion_rect)
        
        # Cuadro de nombre
        self.cuadro_nombre.dibujar(superficie, self.fuente_boton)
        
        # Botones
        for boton in self.botones:
            boton.dibujar(superficie, self.fuente_boton)
        
        # Instrucciones de controles
        self._dibujar_controles(superficie)
    
    def _dibujar_titulo(self, superficie: pygame.Surface):
        """Dibuja el título con efectos."""
        titulo_texto = "ESCAPA DEL LABERINTO"
        
        # Efecto de onda en el color
        offset_color = int(50 * math.sin(self.tiempo * 2))
        color_titulo = (
            max(0, min(255, Colores.CYAN_NEON[0] + offset_color)),
            Colores.CYAN_NEON[1],
            max(0, min(255, Colores.CYAN_NEON[2] - offset_color))
        )
        
        # Sombra
        sombra = self.fuente_titulo.render(titulo_texto, True, Colores.FONDO_PANEL)
        sombra_rect = sombra.get_rect(center=(self.ancho // 2 + 3, 103))
        superficie.blit(sombra, sombra_rect)
        
        # Título principal
        titulo = self.fuente_titulo.render(titulo_texto, True, color_titulo)
        titulo_rect = titulo.get_rect(center=(self.ancho // 2, 100))
        superficie.blit(titulo, titulo_rect)
    
    def _dibujar_controles(self, superficie: pygame.Surface):
        """Dibuja las instrucciones de controles."""
        controles = [
            "CONTROLES:",
            "Flechas / WASD  Mover",
            "SHIFT    Correr (gasta energia)",
            "ESC      Pausar / Menu"
        ]
        
        # Posicionar controles en la esquina inferior izquierda
        # para evitar superposición con los botones
        x_inicio = 30  # Margen izquierdo
        y_inicio = self.alto - 100  # Desde abajo con margen
        
        for i, texto in enumerate(controles):
            color = Colores.CYAN_NEON if i == 0 else Colores.TEXTO_SECUNDARIO
            render = self.fuente_info.render(texto, True, color)
            y_pos = y_inicio + i * 22
            # Alinear a la izquierda en lugar del centro
            rect = render.get_rect(left=x_inicio, top=y_pos)
            superficie.blit(render, rect)


class PantallaJuego(PantallaBase):
    """Pantalla principal del juego."""
    
    def __init__(self, ancho: int, alto: int, modo: str, nombre_jugador: str):
        super().__init__(ancho, alto)
        
        self.modo = modo
        self.nombre_jugador = nombre_jugador
        
        # Componentes del juego
        self.mapa = None
        self.jugador = None
        self.renderizador = RenderizadorMapa()
        self.barra_energia = None
        self.particulas = SistemaParticulas()
        
        # Estado del juego
        self.tiempo_juego = 0
        self.tiempo_limite = Config.TIEMPO_PARTIDA_ESCAPA if modo == "escapa" else Config.TIEMPO_PARTIDA_CAZADOR
        self.puntos = 0
        self.pausado = False
        self.juego_terminado = False
        self.victoria = False
        self.movimientos = 0
        
        # Fuentes
        self.fuente_ui = None
        self.fuente_titulo = None
        self.fuente_grande = None
        
        # Botones de pausa
        self.botones_pausa = []
        
        # Inicializar juego
        self._inicializar_juego()
    
    def _inicializar_juego(self):
        """Inicializa los componentes del juego."""
        # Generar mapa
        generador = GeneradorMapa(ancho=Config.MAPA_ANCHO, alto=Config.MAPA_ALTO)
        self.mapa = generador.generar_mapa()
        
        # Crear jugador
        pos_inicio = self.mapa.obtener_posicion_inicio_jugador()
        self.jugador = Jugador(pos_inicio[0], pos_inicio[1], energia_maxima=Config.ENERGIA_INICIAL)
        
        # Barra de energía
        self.barra_energia = BarraEnergia(Config.PANEL_X + 20, 180, 250, 30)
        
        # Resetear renderizador
        self.renderizador.resetear_posicion_jugador(self.jugador)
    
    def inicializar_fuentes(self):
        """Inicializa las fuentes."""
        self.fuente_ui = pygame.font.Font(None, 28)
        self.fuente_titulo = pygame.font.Font(None, 42)
        self.fuente_grande = pygame.font.Font(None, 72)
        
        # Crear botones de pausa
        centro_x = self.ancho // 2
        self.botones_pausa = [
            Boton(centro_x - 120, 350, 240, 50, "▶ CONTINUAR",
                  color=Colores.VERDE_NEON,
                  accion=self._continuar),
            Boton(centro_x - 120, 420, 240, 50, "REINICIAR",
                  color=Colores.AMARILLO_NEON,
                  accion=self._reiniciar),
            Boton(centro_x - 120, 490, 240, 50, "MENU",
                  color=Colores.ROJO_NEON,
                  accion=self._ir_menu),
        ]
    
    def _continuar(self):
        """Continúa el juego."""
        self.pausado = False
    
    def _reiniciar(self):
        """Reinicia la partida."""
        self._inicializar_juego()
        self.tiempo_juego = 0
        self.puntos = 0
        self.movimientos = 0
        self.pausado = False
        self.juego_terminado = False
        self.victoria = False
    
    def _ir_menu(self):
        """Vuelve al menú principal."""
        self.siguiente_pantalla = "menu"
    
    def manejar_evento(self, evento: pygame.event.Event):
        """Maneja eventos del juego."""
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                if self.juego_terminado:
                    self._ir_menu()
                else:
                    self.pausado = not self.pausado
                return
            
            if self.pausado or self.juego_terminado:
                return
            
            # Movimiento del jugador
            corriendo = pygame.key.get_mods() & pygame.KMOD_SHIFT
            movio = False
            
            if evento.key == pygame.K_UP or evento.key == pygame.K_w:
                movio = self.jugador.mover_arriba(self.mapa, corriendo)
            elif evento.key == pygame.K_DOWN or evento.key == pygame.K_s:
                movio = self.jugador.mover_abajo(self.mapa, corriendo)
            elif evento.key == pygame.K_LEFT or evento.key == pygame.K_a:
                movio = self.jugador.mover_izquierda(self.mapa, corriendo)
            elif evento.key == pygame.K_RIGHT or evento.key == pygame.K_d:
                movio = self.jugador.mover_derecha(self.mapa, corriendo)
            
            if movio:
                self.movimientos += 1
                # Partículas al moverse
                pos = self.jugador.obtener_posicion()
                x = Config.MAPA_OFFSET_X + pos[1] * Config.TAMANO_CELDA + Config.TAMANO_CELDA // 2
                y = Config.MAPA_OFFSET_Y + pos[0] * Config.TAMANO_CELDA + Config.TAMANO_CELDA // 2
                color = Colores.NARANJA_NEON if corriendo else Colores.CYAN_NEON
                self.particulas.emitir(x, y, color, 3)
                
                # Verificar victoria
                if self.jugador.ha_llegado_a_salida(self.mapa):
                    self._terminar_juego(True)
        
        # Eventos de botones en pausa
        if self.pausado:
            for boton in self.botones_pausa:
                boton.manejar_evento(evento)
    
    def _terminar_juego(self, victoria: bool):
        """Termina el juego."""
        self.juego_terminado = True
        self.victoria = victoria
        
        if victoria:
            # Calcular puntos
            tiempo_restante = max(0, self.tiempo_limite - self.tiempo_juego)
            energia_restante = self.jugador.obtener_energia_actual()
            
            # Fórmula de puntos: base + bonus por tiempo + bonus por energía - penalización movimientos
            self.puntos = 1000 + int(tiempo_restante * 10) + energia_restante * 5 - self.movimientos * 2
            self.puntos = max(100, self.puntos)  # Mínimo 100 puntos
            
            # Guardar puntaje
            scoreboard = ScoreBoard(Config.obtener_ruta_puntajes())
            scoreboard.registrar_puntaje(self.modo, self.nombre_jugador, self.puntos)
    
    def actualizar(self, dt: float):
        """Actualiza la lógica del juego."""
        if self.pausado or self.juego_terminado:
            # Actualizar botones de pausa
            if self.pausado:
                pos_mouse = pygame.mouse.get_pos()
                for boton in self.botones_pausa:
                    boton.actualizar(pos_mouse, dt)
            return
        
        # Actualizar tiempo
        self.tiempo_juego += dt
        
        # Verificar tiempo límite
        if self.tiempo_juego >= self.tiempo_limite:
            self._terminar_juego(False)
            return
        
        # Recuperar energía gradualmente
        self.jugador.actualizar_energia(dt, tasa_recuperacion=2)
        
        # Actualizar componentes visuales
        self.renderizador.actualizar(dt, self.jugador)
        self.barra_energia.actualizar(self.jugador.obtener_porcentaje_energia(), dt)
        self.particulas.actualizar(dt)
    
    def dibujar(self, superficie: pygame.Surface):
        """Dibuja la pantalla del juego."""
        superficie.fill(Colores.FONDO_OSCURO)
        
        # Dibujar mapa
        self.renderizador.dibujar(
            superficie, self.mapa, self.jugador,
            offset=(Config.MAPA_OFFSET_X, Config.MAPA_OFFSET_Y)
        )
        
        # Dibujar partículas
        self.particulas.dibujar(superficie)
        
        # Panel lateral
        self._dibujar_panel_lateral(superficie)
        
        # Overlay de pausa
        if self.pausado:
            self._dibujar_pausa(superficie)
        
        # Overlay de fin de juego
        if self.juego_terminado:
            self._dibujar_fin_juego(superficie)
    
    def _dibujar_panel_lateral(self, superficie: pygame.Surface):
        """Dibuja el panel de información lateral."""
        # Fondo del panel
        panel_rect = pygame.Rect(Config.PANEL_X, 0, Config.PANEL_ANCHO, self.alto)
        pygame.draw.rect(superficie, Colores.FONDO_MENU, panel_rect)
        pygame.draw.line(superficie, Colores.CYAN_NEON, 
                        (Config.PANEL_X, 0), (Config.PANEL_X, self.alto), 2)
        
        # Título del modo
        modo_texto = "MODO ESCAPA" if self.modo == "escapa" else "MODO CAZADOR"
        color_modo = Colores.CYAN_NEON if self.modo == "escapa" else Colores.MAGENTA_NEON
        titulo = self.fuente_titulo.render(modo_texto, True, color_modo)
        superficie.blit(titulo, (Config.PANEL_X + 20, 20))
        
        # Nombre del jugador
        nombre = self.fuente_ui.render(f"Jugador: {self.nombre_jugador}", True, Colores.TEXTO)
        superficie.blit(nombre, (Config.PANEL_X + 20, 70))
        
        # Tiempo
        tiempo_restante = max(0, self.tiempo_limite - self.tiempo_juego)
        minutos = int(tiempo_restante) // 60
        segundos = int(tiempo_restante) % 60
        color_tiempo = Colores.TEXTO if tiempo_restante > 30 else Colores.ROJO_NEON
        tiempo = self.fuente_titulo.render(f"Tiempo: {minutos:02d}:{segundos:02d}", True, color_tiempo)
        superficie.blit(tiempo, (Config.PANEL_X + 20, 110))
        
        # Energía
        energia_label = self.fuente_ui.render("⚡ Energía:", True, Colores.TEXTO)
        superficie.blit(energia_label, (Config.PANEL_X + 20, 155))
        self.barra_energia.dibujar(superficie, self.fuente_ui)
        
        # Estadísticas
        stats_y = 240
        stats = [
            f"📍 Movimientos: {self.movimientos}",
            f"💎 Puntos est.: {self._calcular_puntos_estimados()}",
        ]
        
        for i, stat in enumerate(stats):
            texto = self.fuente_ui.render(stat, True, Colores.TEXTO_SECUNDARIO)
            superficie.blit(texto, (Config.PANEL_X + 20, stats_y + i * 35))
        
        # Leyenda de tiles
        self._dibujar_leyenda(superficie, Config.PANEL_X + 20, 350)
        
        # Controles
        self._dibujar_controles_mini(superficie, Config.PANEL_X + 20, 550)
    
    def _calcular_puntos_estimados(self) -> int:
        """Calcula los puntos estimados actuales."""
        tiempo_restante = max(0, self.tiempo_limite - self.tiempo_juego)
        energia = self.jugador.obtener_energia_actual()
        puntos = 1000 + int(tiempo_restante * 10) + energia * 5 - self.movimientos * 2
        return max(100, puntos)
    
    def _dibujar_leyenda(self, superficie: pygame.Surface, x: int, y: int):
        """Dibuja la leyenda de tipos de tile."""
        titulo = self.fuente_ui.render("📋 LEYENDA:", True, Colores.TEXTO)
        superficie.blit(titulo, (x, y))
        
        items = [
            (Colores.CAMINO, "Camino - Puedes pasar"),
            (Colores.MURO, "Muro - Bloqueado"),
            (Colores.TUNEL, "Túnel - Solo tú puedes"),
            (Colores.LIANA, "Liana - Solo enemigos"),
            (Colores.INICIO, "Inicio"),
            (Colores.SALIDA, "Salida ★"),
        ]
        
        for i, (color, texto) in enumerate(items):
            rect_y = y + 30 + i * 28
            pygame.draw.rect(superficie, color, (x, rect_y, 18, 18), border_radius=3)
            label = self.fuente_ui.render(texto, True, Colores.TEXTO_SECUNDARIO)
            superficie.blit(label, (x + 26, rect_y))
    
    def _dibujar_controles_mini(self, superficie: pygame.Surface, x: int, y: int):
        """Dibuja los controles en formato compacto."""
        titulo = self.fuente_ui.render("CONTROLES:", True, Colores.TEXTO)
        superficie.blit(titulo, (x, y))
        
        controles = [
            "Flechas / WASD - Mover",
            "SHIFT - Correr",
            "ESC - Pausar"
        ]
        
        for i, ctrl in enumerate(controles):
            texto = self.fuente_ui.render(ctrl, True, Colores.TEXTO_DESHABILITADO)
            superficie.blit(texto, (x, y + 28 + i * 24))
    
    def _dibujar_pausa(self, superficie: pygame.Surface):
        """Dibuja el overlay de pausa."""
        # Fondo semi-transparente
        overlay = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        superficie.blit(overlay, (0, 0))
        
        # Título
        titulo = self.fuente_grande.render("⏸ PAUSA", True, Colores.AMARILLO_NEON)
        titulo_rect = titulo.get_rect(center=(self.ancho // 2, 250))
        superficie.blit(titulo, titulo_rect)
        
        # Botones
        for boton in self.botones_pausa:
            boton.dibujar(superficie, self.fuente_ui)
    
    def _dibujar_fin_juego(self, superficie: pygame.Surface):
        """Dibuja el overlay de fin de juego."""
        # Fondo semi-transparente
        overlay = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        superficie.blit(overlay, (0, 0))
        
        # Título según resultado
        if self.victoria:
            titulo_texto = "🎉 ¡VICTORIA! 🎉"
            color_titulo = Colores.VERDE_NEON
        else:
            titulo_texto = "💀 TIEMPO AGOTADO 💀"
            color_titulo = Colores.ROJO_NEON
        
        titulo = self.fuente_grande.render(titulo_texto, True, color_titulo)
        titulo_rect = titulo.get_rect(center=(self.ancho // 2, 200))
        superficie.blit(titulo, titulo_rect)
        
        # Estadísticas finales
        if self.victoria:
            stats = [
                f"Puntos: {self.puntos}",
                f"Tiempo: {int(self.tiempo_juego)}s",
                f"Movimientos: {self.movimientos}",
                f"Energía final: {self.jugador.obtener_energia_actual()}%"
            ]
            
            for i, stat in enumerate(stats):
                texto = self.fuente_titulo.render(stat, True, Colores.TEXTO)
                rect = texto.get_rect(center=(self.ancho // 2, 300 + i * 45))
                superficie.blit(texto, rect)
        
        # Instrucción
        instruccion = self.fuente_ui.render(
            "Presiona ESC para volver al menú", True, Colores.TEXTO_SECUNDARIO
        )
        instruccion_rect = instruccion.get_rect(center=(self.ancho // 2, 550))
        superficie.blit(instruccion, instruccion_rect)


class PantallaPuntajes(PantallaBase):
    """Pantalla de tabla de clasificación."""
    
    def __init__(self, ancho: int, alto: int):
        super().__init__(ancho, alto)
        
        self.scoreboard = ScoreBoard(Config.obtener_ruta_puntajes())
        self.modo_actual = "escapa"
        self.tiempo = 0
        
        # Fuentes
        self.fuente_titulo = None
        self.fuente_subtitulo = None
        self.fuente_tabla = None
        self.fuente_boton = None
        
        # Botones
        self.botones = []
    
    def inicializar_fuentes(self):
        """Inicializa las fuentes."""
        self.fuente_titulo = pygame.font.Font(None, 72)
        self.fuente_subtitulo = pygame.font.Font(None, 42)
        self.fuente_tabla = pygame.font.Font(None, 32)
        self.fuente_boton = pygame.font.Font(None, 28)
        
        # Crear botones
        centro_x = self.ancho // 2
        self.botones = [
            Boton(centro_x - 250, 180, 200, 45, "ESCAPA",
                  color=Colores.CYAN_NEON,
                  accion=lambda: self._cambiar_modo("escapa")),
            Boton(centro_x + 50, 180, 200, 45, "CAZADOR",
                  color=Colores.MAGENTA_NEON,
                  accion=lambda: self._cambiar_modo("cazador")),
            Boton(centro_x - 100, 620, 200, 45, "VOLVER",
                  color=Colores.AMARILLO_NEON,
                  accion=self._volver),
        ]
    
    def _cambiar_modo(self, modo: str):
        """Cambia el modo de puntajes mostrado."""
        self.modo_actual = modo
    
    def _volver(self):
        """Vuelve al menú principal."""
        self.siguiente_pantalla = "menu"
    
    def manejar_evento(self, evento: pygame.event.Event):
        """Maneja eventos."""
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            self._volver()
            return
        
        for boton in self.botones:
            boton.manejar_evento(evento)
    
    def actualizar(self, dt: float):
        """Actualiza la pantalla."""
        self.tiempo += dt
        
        pos_mouse = pygame.mouse.get_pos()
        for boton in self.botones:
            boton.actualizar(pos_mouse, dt)
    
    def dibujar(self, superficie: pygame.Surface):
        """Dibuja la pantalla de puntajes."""
        superficie.fill(Colores.FONDO_OSCURO)
        
        # Título
        titulo = self.fuente_titulo.render("TABLA DE PUNTAJES", True, Colores.ORO)
        titulo_rect = titulo.get_rect(center=(self.ancho // 2, 80))
        superficie.blit(titulo, titulo_rect)
        
        # Subtítulo del modo actual
        modo_texto = "Modo Escapa" if self.modo_actual == "escapa" else "Modo Cazador"
        color_modo = Colores.CYAN_NEON if self.modo_actual == "escapa" else Colores.MAGENTA_NEON
        subtitulo = self.fuente_subtitulo.render(modo_texto, True, color_modo)
        subtitulo_rect = subtitulo.get_rect(center=(self.ancho // 2, 140))
        superficie.blit(subtitulo, subtitulo_rect)
        
        # Botones de modo
        for boton in self.botones[:2]:
            boton.dibujar(superficie, self.fuente_boton)
        
        # Tabla de puntajes
        self._dibujar_tabla(superficie)
        
        # Botón volver
        self.botones[2].dibujar(superficie, self.fuente_boton)
    
    def _dibujar_tabla(self, superficie: pygame.Surface):
        """Dibuja la tabla de puntajes."""
        top5 = self.scoreboard.obtener_top5(self.modo_actual)
        
        # Fondo de la tabla
        tabla_rect = pygame.Rect(self.ancho // 2 - 350, 250, 700, 340)
        pygame.draw.rect(superficie, Colores.FONDO_PANEL, tabla_rect, border_radius=15)
        pygame.draw.rect(superficie, Colores.TEXTO_SECUNDARIO, tabla_rect, width=2, border_radius=15)
        
        # Encabezados
        headers = ["#", "JUGADOR", "PUNTOS"]
        header_x = [tabla_rect.x + 50, tabla_rect.x + 180, tabla_rect.x + 500]
        
        for i, header in enumerate(headers):
            texto = self.fuente_tabla.render(header, True, Colores.TEXTO)
            superficie.blit(texto, (header_x[i], tabla_rect.y + 20))
        
        # Línea separadora
        pygame.draw.line(superficie, Colores.TEXTO_SECUNDARIO,
                        (tabla_rect.x + 20, tabla_rect.y + 55),
                        (tabla_rect.x + tabla_rect.width - 20, tabla_rect.y + 55), 1)
        
        if not top5:
            # Mensaje de no hay puntajes
            mensaje = self.fuente_tabla.render("No hay puntajes registrados", True, Colores.TEXTO_DESHABILITADO)
            mensaje_rect = mensaje.get_rect(center=(self.ancho // 2, tabla_rect.y + 180))
            superficie.blit(mensaje, mensaje_rect)
            return
        
        # Filas de puntajes
        colores_medalla = [Colores.ORO, Colores.PLATA, Colores.BRONCE, Colores.TEXTO, Colores.TEXTO]
        
        for i, puntaje in enumerate(top5):
            y = tabla_rect.y + 75 + i * 50
            color = colores_medalla[i]
            
            # Fondo de fila con hover effect
            fila_rect = pygame.Rect(tabla_rect.x + 10, y - 5, tabla_rect.width - 20, 45)
            
            # Medalla/Número
            if i < 3:
                medallas = ["🥇", "🥈", "🥉"]
                num_texto = medallas[i]
            else:
                num_texto = str(i + 1)
            
            num = self.fuente_tabla.render(num_texto, True, color)
            superficie.blit(num, (header_x[0], y))
            
            # Nombre
            nombre = self.fuente_tabla.render(puntaje.nombre_jugador, True, color)
            superficie.blit(nombre, (header_x[1], y))
            
            # Puntos
            puntos = self.fuente_tabla.render(f"{int(puntaje.puntos):,}", True, color)
            superficie.blit(puntos, (header_x[2], y))


class PantallaFinJuego(PantallaBase):
    """Pantalla de fin de juego (alternativa standalone)."""
    
    def __init__(self, ancho: int, alto: int, victoria: bool, puntos: int, 
                 tiempo: float, movimientos: int, modo: str):
        super().__init__(ancho, alto)
        
        self.victoria = victoria
        self.puntos = puntos
        self.tiempo = tiempo
        self.movimientos = movimientos
        self.modo = modo
        self.tiempo_animacion = 0
        
        # Fuentes
        self.fuente_titulo = None
        self.fuente_stats = None
        self.fuente_boton = None
        
        # Botones
        self.botones = []
        self.particulas = SistemaParticulas()
    
    def inicializar_fuentes(self):
        """Inicializa las fuentes."""
        self.fuente_titulo = pygame.font.Font(None, 86)
        self.fuente_stats = pygame.font.Font(None, 42)
        self.fuente_boton = pygame.font.Font(None, 32)
        
        centro_x = self.ancho // 2
        self.botones = [
            Boton(centro_x - 150, 500, 300, 55, "JUGAR DE NUEVO",
                  color=Colores.VERDE_NEON,
                  accion=self._jugar_nuevo),
            Boton(centro_x - 150, 570, 300, 55, "MENU PRINCIPAL",
                  color=Colores.CYAN_NEON,
                  accion=self._ir_menu),
        ]
    
    def _jugar_nuevo(self):
        """Inicia una nueva partida."""
        self.siguiente_pantalla = "juego_nuevo"
        self.datos_retorno = {"modo": self.modo}
    
    def _ir_menu(self):
        """Vuelve al menú."""
        self.siguiente_pantalla = "menu"
    
    def manejar_evento(self, evento: pygame.event.Event):
        """Maneja eventos."""
        for boton in self.botones:
            boton.manejar_evento(evento)
    
    def actualizar(self, dt: float):
        """Actualiza la pantalla."""
        self.tiempo_animacion += dt
        
        pos_mouse = pygame.mouse.get_pos()
        for boton in self.botones:
            boton.actualizar(pos_mouse, dt)
        
        # Partículas de celebración
        if self.victoria and random.random() < 0.3:
            x = random.randint(100, self.ancho - 100)
            color = random.choice([Colores.ORO, Colores.CYAN_NEON, Colores.MAGENTA_NEON])
            self.particulas.emitir(x, 50, color, 2)
        
        self.particulas.actualizar(dt)
    
    def dibujar(self, superficie: pygame.Surface):
        """Dibuja la pantalla de fin."""
        superficie.fill(Colores.FONDO_OSCURO)
        
        # Partículas
        self.particulas.dibujar(superficie)
        
        # Título
        if self.victoria:
            titulo_texto = "🎉 ¡VICTORIA! 🎉"
            color = Colores.VERDE_NEON
        else:
            titulo_texto = "💀 GAME OVER 💀"
            color = Colores.ROJO_NEON
        
        titulo = self.fuente_titulo.render(titulo_texto, True, color)
        titulo_rect = titulo.get_rect(center=(self.ancho // 2, 120))
        superficie.blit(titulo, titulo_rect)
        
        # Estadísticas
        if self.victoria:
            stats = [
                f"Puntos: {self.puntos:,}",
                f"Tiempo: {int(self.tiempo)}s",
                f"Movimientos: {self.movimientos}"
            ]
            
            for i, stat in enumerate(stats):
                texto = self.fuente_stats.render(stat, True, Colores.TEXTO)
                rect = texto.get_rect(center=(self.ancho // 2, 250 + i * 60))
                superficie.blit(texto, rect)
        
        # Botones
        for boton in self.botones:
            boton.dibujar(superficie, self.fuente_boton)

