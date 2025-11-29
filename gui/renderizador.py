"""
Renderizador del mapa del laberinto con efectos visuales.
"""

import pygame
import math
from typing import Tuple, Optional
from modelo.tile import Tile, Camino, Muro, Liana, Tunel, TipoTile
from modelo.mapa import Mapa
from modelo.jugador import Jugador
from modelo.trampa import Trampa
from modelo.enemigo import Enemigo, EstadoEnemigo
from typing import List, Optional
from .config import Colores, Config


class RenderizadorMapa:
    """
    Renderiza el mapa del juego con efectos visuales.
    
    Esta clase se encarga de dibujar todos los elementos del mapa:
    - Tiles (caminos, muros, lianas, túneles)
    - Jugador con animaciones
    - Enemigos
    - Trampas
    - Posiciones especiales (inicio, salidas)
    
    Incluye efectos visuales como animaciones suaves, brillos y partículas.
    """
    
    def __init__(self, tamano_celda: int = Config.TAMANO_CELDA):
        """
        Inicializa el renderizador del mapa.
        
        Args:
            tamano_celda: Tamaño en píxeles de cada celda del mapa.
        """
        self.tamano_celda = tamano_celda  # Tamaño de cada celda en píxeles
        self.tiempo = 0  # Tiempo acumulado para animaciones
        self.posicion_jugador_visual = None  # Posición visual del jugador (para animación suave/interpolación)
        
    def actualizar(self, dt: float, jugador: Jugador = None):
        """
        Actualiza animaciones del renderizador.
        
        Actualiza el tiempo acumulado y la posición visual del jugador
        usando interpolación para crear movimiento suave.
        
        Args:
            dt: Tiempo transcurrido desde el último frame (segundos).
            jugador: Instancia del jugador para actualizar su posición visual.
        """
        # Actualizar tiempo acumulado (para animaciones basadas en tiempo)
        self.tiempo += dt
        
        # ============================================
        # INTERPOLACIÓN DE POSICIÓN DEL JUGADOR
        # ============================================
        # Actualizar posición visual del jugador con interpolación suave
        # Esto crea un efecto de movimiento fluido en lugar de saltos discretos
        if jugador and self.posicion_jugador_visual:
            # Obtener posición lógica actual del jugador
            pos_actual = jugador.obtener_posicion()
            # Convertir a coordenadas de píxeles
            target_x = pos_actual[1] * self.tamano_celda
            target_y = pos_actual[0] * self.tamano_celda
            
            # Calcular diferencia entre posición visual y posición objetivo
            diff_x = target_x - self.posicion_jugador_visual[0]
            diff_y = target_y - self.posicion_jugador_visual[1]
            
            # Interpolar suavemente hacia la posición objetivo
            velocidad = 15 * dt  # Velocidad de interpolación
            self.posicion_jugador_visual = (
                self.posicion_jugador_visual[0] + diff_x * velocidad,
                self.posicion_jugador_visual[1] + diff_y * velocidad
            )
    
    def _obtener_color_tile(self, tile: Tile) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
        """
        Obtiene el color de fondo y borde para un tile.
        
        Cada tipo de tile tiene un color de fondo y un color de borde
        que lo distingue visualmente en el mapa.
        
        Args:
            tile: Objeto Tile del cual obtener los colores.
            
        Returns:
            Tupla (color_fondo, color_borde) en formato RGB.
        """
        if isinstance(tile, Muro):
            return Colores.MURO, Colores.MURO_BORDE
        elif isinstance(tile, Liana):
            return Colores.LIANA, Colores.LIANA_BORDE
        elif isinstance(tile, Tunel):
            return Colores.TUNEL, Colores.TUNEL_BORDE
        else:  # Camino (tile por defecto)
            return Colores.CAMINO, Colores.CAMINO_ILUMINADO
    
    def _dibujar_celda(self, superficie: pygame.Surface, tile: Tile, 
                       x: int, y: int, es_especial: str = None):
        """
        Dibuja una celda individual del mapa.
        
        Dibuja el fondo, borde y efectos especiales según el tipo de tile.
        Cada tipo de tile tiene un patrón visual distintivo.
        
        Args:
            superficie: Superficie de pygame donde dibujar.
            tile: Objeto Tile a dibujar.
            x: Posición X en píxeles.
            y: Posición Y en píxeles.
            es_especial: Tipo especial (no se usa actualmente, pero se mantiene por compatibilidad).
        """
        # Crear rectángulo para la celda (con margen de 1 píxel)
        rect = pygame.Rect(x, y, self.tamano_celda - 1, self.tamano_celda - 1)
        
        # Obtener colores del tile
        color_fondo, color_borde = self._obtener_color_tile(tile)
        
        # Dibujar fondo de la celda
        pygame.draw.rect(superficie, color_fondo, rect, border_radius=3)
        
        # Dibujar borde sutil (solo para tiles especiales, no para caminos)
        if not isinstance(tile, Camino):
            pygame.draw.rect(superficie, color_borde, rect, width=1, border_radius=3)
        
        # ============================================
        # EFECTOS ESPECIALES POR TIPO DE TILE
        # ============================================
        
        # Efectos especiales para muros (patrón de ladrillo)
        if isinstance(tile, Muro):
            # Dibujar líneas horizontales para simular ladrillos
            linea_y = y + self.tamano_celda // 3
            pygame.draw.line(superficie, color_borde, (x + 2, linea_y), 
                           (x + self.tamano_celda - 3, linea_y), 1)
            linea_y = y + 2 * self.tamano_celda // 3
            pygame.draw.line(superficie, color_borde, (x + 2, linea_y), 
                           (x + self.tamano_celda - 3, linea_y), 1)
        
        # Efectos especiales para lianas (líneas verticales)
        elif isinstance(tile, Liana):
            # Dibujar 3 líneas verticales para simular lianas
            for i in range(3):
                lx = x + 8 + i * 8
                pygame.draw.line(superficie, color_borde, (lx, y + 2), 
                               (lx, y + self.tamano_celda - 3), 2)
        
        # Efectos especiales para túneles (círculos concéntricos)
        elif isinstance(tile, Tunel):
            # Dibujar círculos concéntricos para simular un túnel
            centro = (x + self.tamano_celda // 2, y + self.tamano_celda // 2)
            pygame.draw.circle(superficie, color_borde, centro, 8, 2)  # Círculo exterior
            pygame.draw.circle(superficie, Colores.FONDO_OSCURO, centro, 4)  # Círculo interior
    
    def _dibujar_posicion_especial(self, superficie: pygame.Surface, 
                                   x: int, y: int, es_inicio: bool = True):
        """
        Dibuja marcador para posición de inicio o salida.
        
        Dibuja un rectángulo con borde destacado para marcar posiciones
        importantes del mapa. Las salidas tienen un efecto de pulso
        para hacerlas más visibles.
        
        Args:
            superficie: Superficie de pygame donde dibujar.
            x: Posición X en píxeles.
            y: Posición Y en píxeles.
            es_inicio: True si es posición de inicio, False si es salida.
        """
        # Crear rectángulo para el marcador
        rect = pygame.Rect(x + 2, y + 2, self.tamano_celda - 5, self.tamano_celda - 5)
        
        if es_inicio:
            # Color verde para inicio
            color = Colores.INICIO
            simbolo = "▶"  # Símbolo de inicio (no se usa actualmente)
        else:
            # Color rojo para salida
            color = Colores.SALIDA
            simbolo = "★"  # Símbolo de salida (no se usa actualmente)
            
            # Efecto de pulso para la salida (hace que sea más visible)
            alpha = int(150 + 100 * math.sin(self.tiempo * 4))
            glow = pygame.Surface((self.tamano_celda + 10, self.tamano_celda + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*color, alpha), glow.get_rect(), border_radius=6)
            superficie.blit(glow, (x - 5, y - 5))
        
        # Dibujar borde del marcador
        pygame.draw.rect(superficie, color, rect, width=3, border_radius=4)
    
    def _dibujar_jugador(self, superficie: pygame.Surface, x: float, y: float, modo: str = "escapa"):
        """
        Dibuja al jugador con efectos visuales.
        
        Dibuja el jugador como un círculo con efectos de brillo y pulso.
        El color del jugador varía según el modo de juego:
        - Modo escapa: amarillo (color por defecto)
        - Modo cazador: rojo (el jugador es el cazador)
        
        Args:
            superficie: Superficie de pygame donde dibujar.
            x: Posición X en píxeles (puede ser float para interpolación).
            y: Posición Y en píxeles (puede ser float para interpolación).
            modo: Modo de juego ("escapa" o "cazador").
        """
        # Calcular centro y radio del jugador
        centro_x = int(x + self.tamano_celda // 2)
        centro_y = int(y + self.tamano_celda // 2)
        radio = self.tamano_celda // 3
        
        # Color del jugador según el modo
        if modo == "cazador":
            color_jugador = Colores.ROJO_NEON
            color_glow = (*Colores.ROJO_NEON, 100)
        else:
            color_jugador = Colores.JUGADOR
            color_glow = (*Colores.JUGADOR_GLOW, 100)
        
        # Glow exterior
        glow_radio = radio + 4 + int(2 * math.sin(self.tiempo * 5))
        glow_surface = pygame.Surface((glow_radio * 4, glow_radio * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, color_glow, 
                         (glow_radio * 2, glow_radio * 2), glow_radio)
        superficie.blit(glow_surface, (centro_x - glow_radio * 2, centro_y - glow_radio * 2))
        
        # Jugador principal
        pygame.draw.circle(superficie, color_jugador, (centro_x, centro_y), radio)
        
        # Brillo interno
        brillo_pos = (centro_x - 3, centro_y - 3)
        pygame.draw.circle(superficie, Colores.TEXTO, brillo_pos, 3)
    
    def _dibujar_trampa(self, superficie: pygame.Surface, x: int, y: int):
        """
        Dibuja una trampa en el mapa.
        
        Las trampas se dibujan como un círculo rojo con una X en el centro
        y un efecto de pulso para hacerlas visibles.
        
        Args:
            superficie: Superficie de pygame donde dibujar.
            x: Posición X en píxeles.
            y: Posición Y en píxeles.
        """
        # Calcular centro de la celda
        centro_x = int(x + self.tamano_celda // 2)
        centro_y = int(y + self.tamano_celda // 2)
        
        # Efecto de pulso (el radio varía con el tiempo)
        pulso = int(3 * math.sin(self.tiempo * 8))
        radio = self.tamano_celda // 4 + pulso
        
        # Círculo exterior con glow (brillo rojo)
        glow_surface = pygame.Surface((radio * 4, radio * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*Colores.ROJO_NEON, 150), 
                         (radio * 2, radio * 2), radio + 2)
        superficie.blit(glow_surface, (centro_x - radio * 2, centro_y - radio * 2))
        
        # Trampa principal: círculo con borde rojo
        pygame.draw.circle(superficie, Colores.ROJO_NEON, (centro_x, centro_y), radio, 2)
        
        # Dibujar X en el centro (símbolo de trampa)
        offset = radio - 2
        pygame.draw.line(superficie, Colores.ROJO_NEON, 
                        (centro_x - offset, centro_y - offset),
                        (centro_x + offset, centro_y + offset), 2)
        pygame.draw.line(superficie, Colores.ROJO_NEON,
                        (centro_x - offset, centro_y + offset),
                        (centro_x + offset, centro_y - offset), 2)
    
    def _dibujar_enemigo(self, superficie: pygame.Surface, x: int, y: int, en_spawn: bool = False, modo: str = "escapa"):
        """
        Dibuja un enemigo en el mapa.
        
        Los enemigos se dibujan como círculos con efectos de brillo.
        El color varía según el modo de juego:
        - Modo escapa: magenta (enemigos persiguen al jugador)
        - Modo cazador: verde (enemigos huyen del jugador)
        
        Si el enemigo está en spawn, se dibuja con opacidad reducida.
        
        Args:
            superficie: Superficie de pygame donde dibujar.
            x: Posición X en píxeles.
            y: Posición Y en píxeles.
            en_spawn: True si el enemigo está en el spawn (apareciendo).
            modo: Modo de juego ("escapa" o "cazador").
        """
        # Calcular centro y radio del enemigo
        centro_x = int(x + self.tamano_celda // 2)
        centro_y = int(y + self.tamano_celda // 2)
        radio = self.tamano_celda // 3
        
        # Color del enemigo según el modo
        if modo == "cazador":
            color_enemigo = Colores.VERDE_NEON  # Verde en modo cazador
        else:
            color_enemigo = Colores.MAGENTA_NEON  # Magenta en modo escapa
        
        # Si está en spawn, dibujar con opacidad reducida (semi-transparente)
        alpha = 150 if en_spawn else 255
        
        # Glow exterior pulsante (efecto de brillo alrededor del enemigo)
        glow_radio = radio + 2 + int(2 * math.sin(self.tiempo * 6))
        glow_surface = pygame.Surface((glow_radio * 4, glow_radio * 4), pygame.SRCALPHA)
        glow_alpha = 80 if en_spawn else 120  # Opacidad del glow
        pygame.draw.circle(glow_surface, (*color_enemigo, glow_alpha),
                         (glow_radio * 2, glow_radio * 2), glow_radio)
        superficie.blit(glow_surface, (centro_x - glow_radio * 2, centro_y - glow_radio * 2))
        
        # Enemigo principal con opacidad
        if en_spawn:
            # Crear superficie temporal para aplicar alpha (transparencia)
            temp_surface = pygame.Surface((radio * 2 + 4, radio * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(temp_surface, (*color_enemigo, alpha), (radio + 2, radio + 2), radio)
            superficie.blit(temp_surface, (centro_x - radio - 2, centro_y - radio - 2))
        else:
            # Enemigo completamente visible
            pygame.draw.circle(superficie, color_enemigo, (centro_x, centro_y), radio)
        
        # Ojos (dos puntos negros) - solo si no está en spawn
        # Esto le da personalidad al enemigo
        if not en_spawn:
            pygame.draw.circle(superficie, Colores.FONDO_OSCURO, 
                             (centro_x - 3, centro_y - 2), 2)  # Ojo izquierdo
            pygame.draw.circle(superficie, Colores.FONDO_OSCURO,
                             (centro_x + 3, centro_y - 2), 2)  # Ojo derecho
    
    def dibujar(self, superficie: pygame.Surface, mapa: Mapa, 
                jugador: Jugador = None, offset: Tuple[int, int] = (0, 0),
                trampas: Optional[List[Trampa]] = None,
                enemigos: Optional[List[Enemigo]] = None,
                modo: str = "escapa"):
        """
        Dibuja el mapa completo con todos sus elementos.
        
        Este es el método principal de renderizado que dibuja:
        - Todas las celdas del mapa (tiles)
        - Posiciones especiales (inicio y salidas)
        - Trampas activas
        - Enemigos vivos
        - Jugador con interpolación suave
        
        Args:
            superficie: Superficie de pygame donde dibujar.
            mapa: Objeto Mapa a dibujar.
            jugador: Jugador a dibujar (opcional).
            offset: Offset (x, y) en píxeles para posicionar el mapa en la pantalla.
            trampas: Lista de trampas a dibujar (opcional).
            enemigos: Lista de enemigos a dibujar (opcional).
            modo: Modo de juego ("escapa" o "cazador") - afecta colores.
        """
        offset_x, offset_y = offset
        pos_inicio = mapa.obtener_posicion_inicio_jugador()
        posiciones_salida = mapa.obtener_posiciones_salida()
        
        # ============================================
        # DIBUJAR TODAS LAS CELDAS DEL MAPA
        # ============================================
        # Iterar sobre todas las celdas y dibujar cada tile
        for fila in range(mapa.alto):
            for col in range(mapa.ancho):
                tile = mapa.obtener_casilla(fila, col)
                # Calcular posición en píxeles
                x = offset_x + col * self.tamano_celda
                y = offset_y + fila * self.tamano_celda
                
                # Dibujar la celda (tile)
                self._dibujar_celda(superficie, tile, x, y)
                
                # Marcar posiciones especiales (inicio y salidas)
                if (fila, col) == pos_inicio:
                    self._dibujar_posicion_especial(superficie, x, y, es_inicio=True)
                elif (fila, col) in posiciones_salida:
                    self._dibujar_posicion_especial(superficie, x, y, es_inicio=False)
        
        # ============================================
        # DIBUJAR TRAMPAS
        # ============================================
        # Dibujar todas las trampas activas
        if trampas:
            for trampa in trampas:
                if trampa.esta_activa():
                    pos = trampa.obtener_posicion()
                    x = offset_x + pos[1] * self.tamano_celda
                    y = offset_y + pos[0] * self.tamano_celda
                    self._dibujar_trampa(superficie, x, y)
        
        # ============================================
        # DIBUJAR ENEMIGOS
        # ============================================
        # Dibujar todos los enemigos vivos
        if enemigos:
            for enemigo in enemigos:
                if enemigo.esta_vivo():
                    pos = enemigo.obtener_posicion()
                    x = offset_x + pos[1] * self.tamano_celda
                    y = offset_y + pos[0] * self.tamano_celda
                    # Dibujar con opacidad reducida si está en spawn (apareciendo)
                    self._dibujar_enemigo(superficie, x, y, en_spawn=enemigo.estado == EstadoEnemigo.EN_SPAWN, modo=modo)
        
        # ============================================
        # DIBUJAR JUGADOR
        # ============================================
        # Dibujar el jugador con interpolación suave
        if jugador:
            pos = jugador.obtener_posicion()
            
            # Inicializar posición visual si es necesario (primera vez)
            if self.posicion_jugador_visual is None:
                self.posicion_jugador_visual = (
                    pos[1] * self.tamano_celda,
                    pos[0] * self.tamano_celda
                )
            
            # Usar posición visual interpolada para movimiento suave
            jugador_x = offset_x + self.posicion_jugador_visual[0]
            jugador_y = offset_y + self.posicion_jugador_visual[1]
            self._dibujar_jugador(superficie, jugador_x, jugador_y, modo)
    
    def resetear_posicion_jugador(self, jugador: Jugador):
        """
        Resetea la posición visual del jugador.
        
        Útil cuando el jugador se teletransporta o cambia de posición
        de forma instantánea (por ejemplo, al reiniciar el juego).
        Esto evita que la interpolación cause un movimiento visual extraño.
        
        Args:
            jugador: Instancia del jugador.
        """
        if jugador:
            pos = jugador.obtener_posicion()
            # Sincronizar posición visual con posición lógica
            self.posicion_jugador_visual = (
                pos[1] * self.tamano_celda,
                pos[0] * self.tamano_celda
            )
    
    def obtener_tamano_mapa_pixeles(self, mapa: Mapa) -> Tuple[int, int]:
        """
        Obtiene el tamaño del mapa en píxeles.
        
        Calcula el tamaño total del mapa multiplicando las dimensiones
        en celdas por el tamaño de cada celda en píxeles.
        
        Args:
            mapa: Objeto Mapa del cual obtener el tamaño.
            
        Returns:
            Tupla (ancho, alto) en píxeles.
        """
        return (mapa.ancho * self.tamano_celda, mapa.alto * self.tamano_celda)

