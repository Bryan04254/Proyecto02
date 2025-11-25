"""
Renderizador del mapa del laberinto con efectos visuales.
"""

import pygame
import math
from typing import Tuple, Optional
from modelo.tile import Tile, Camino, Muro, Liana, Tunel, TipoTile
from modelo.mapa import Mapa
from modelo.jugador import Jugador
from .config import Colores, Config


class RenderizadorMapa:
    """Renderiza el mapa del juego con efectos visuales."""
    
    def __init__(self, tamano_celda: int = Config.TAMANO_CELDA):
        self.tamano_celda = tamano_celda
        self.tiempo = 0
        self.posicion_jugador_visual = None  # Para animación suave
        
    def actualizar(self, dt: float, jugador: Jugador = None):
        """Actualiza animaciones."""
        self.tiempo += dt
        
        # Actualizar posición visual del jugador con interpolación
        if jugador and self.posicion_jugador_visual:
            pos_actual = jugador.obtener_posicion()
            target_x = pos_actual[1] * self.tamano_celda
            target_y = pos_actual[0] * self.tamano_celda
            
            diff_x = target_x - self.posicion_jugador_visual[0]
            diff_y = target_y - self.posicion_jugador_visual[1]
            
            velocidad = 15 * dt
            self.posicion_jugador_visual = (
                self.posicion_jugador_visual[0] + diff_x * velocidad,
                self.posicion_jugador_visual[1] + diff_y * velocidad
            )
    
    def _obtener_color_tile(self, tile: Tile) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
        """Obtiene el color de fondo y borde para un tile."""
        if isinstance(tile, Muro):
            return Colores.MURO, Colores.MURO_BORDE
        elif isinstance(tile, Liana):
            return Colores.LIANA, Colores.LIANA_BORDE
        elif isinstance(tile, Tunel):
            return Colores.TUNEL, Colores.TUNEL_BORDE
        else:  # Camino
            return Colores.CAMINO, Colores.CAMINO_ILUMINADO
    
    def _dibujar_celda(self, superficie: pygame.Surface, tile: Tile, 
                       x: int, y: int, es_especial: str = None):
        """Dibuja una celda individual."""
        rect = pygame.Rect(x, y, self.tamano_celda - 1, self.tamano_celda - 1)
        
        color_fondo, color_borde = self._obtener_color_tile(tile)
        
        # Dibujar fondo
        pygame.draw.rect(superficie, color_fondo, rect, border_radius=3)
        
        # Borde sutil
        if not isinstance(tile, Camino):
            pygame.draw.rect(superficie, color_borde, rect, width=1, border_radius=3)
        
        # Efectos especiales para muros (patrón)
        if isinstance(tile, Muro):
            # Patrón de ladrillo
            linea_y = y + self.tamano_celda // 3
            pygame.draw.line(superficie, color_borde, (x + 2, linea_y), 
                           (x + self.tamano_celda - 3, linea_y), 1)
            linea_y = y + 2 * self.tamano_celda // 3
            pygame.draw.line(superficie, color_borde, (x + 2, linea_y), 
                           (x + self.tamano_celda - 3, linea_y), 1)
        
        # Efectos especiales para lianas (líneas verticales)
        elif isinstance(tile, Liana):
            for i in range(3):
                lx = x + 8 + i * 8
                pygame.draw.line(superficie, color_borde, (lx, y + 2), 
                               (lx, y + self.tamano_celda - 3), 2)
        
        # Efectos especiales para túneles (círculos)
        elif isinstance(tile, Tunel):
            centro = (x + self.tamano_celda // 2, y + self.tamano_celda // 2)
            pygame.draw.circle(superficie, color_borde, centro, 8, 2)
            pygame.draw.circle(superficie, Colores.FONDO_OSCURO, centro, 4)
    
    def _dibujar_posicion_especial(self, superficie: pygame.Surface, 
                                   x: int, y: int, es_inicio: bool = True):
        """Dibuja marcador para posición de inicio o salida."""
        rect = pygame.Rect(x + 2, y + 2, self.tamano_celda - 5, self.tamano_celda - 5)
        
        if es_inicio:
            color = Colores.INICIO
            simbolo = "▶"
        else:
            color = Colores.SALIDA
            simbolo = "★"
            
            # Efecto de pulso para la salida
            alpha = int(150 + 100 * math.sin(self.tiempo * 4))
            glow = pygame.Surface((self.tamano_celda + 10, self.tamano_celda + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*color, alpha), glow.get_rect(), border_radius=6)
            superficie.blit(glow, (x - 5, y - 5))
        
        pygame.draw.rect(superficie, color, rect, width=3, border_radius=4)
    
    def _dibujar_jugador(self, superficie: pygame.Surface, x: float, y: float):
        """Dibuja al jugador con efectos."""
        centro_x = int(x + self.tamano_celda // 2)
        centro_y = int(y + self.tamano_celda // 2)
        radio = self.tamano_celda // 3
        
        # Glow exterior
        glow_radio = radio + 4 + int(2 * math.sin(self.tiempo * 5))
        glow_surface = pygame.Surface((glow_radio * 4, glow_radio * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*Colores.JUGADOR_GLOW, 100), 
                         (glow_radio * 2, glow_radio * 2), glow_radio)
        superficie.blit(glow_surface, (centro_x - glow_radio * 2, centro_y - glow_radio * 2))
        
        # Jugador principal
        pygame.draw.circle(superficie, Colores.JUGADOR, (centro_x, centro_y), radio)
        
        # Brillo interno
        brillo_pos = (centro_x - 3, centro_y - 3)
        pygame.draw.circle(superficie, Colores.TEXTO, brillo_pos, 3)
    
    def dibujar(self, superficie: pygame.Surface, mapa: Mapa, 
                jugador: Jugador = None, offset: Tuple[int, int] = (0, 0)):
        """
        Dibuja el mapa completo.
        
        Args:
            superficie: Superficie de pygame donde dibujar.
            mapa: Objeto Mapa a dibujar.
            jugador: Jugador a dibujar (opcional).
            offset: Offset (x, y) para posicionar el mapa.
        """
        offset_x, offset_y = offset
        pos_inicio = mapa.obtener_posicion_inicio_jugador()
        pos_salida = mapa.obtener_posicion_salida()
        
        # Dibujar todas las celdas
        for fila in range(mapa.alto):
            for col in range(mapa.ancho):
                tile = mapa.obtener_casilla(fila, col)
                x = offset_x + col * self.tamano_celda
                y = offset_y + fila * self.tamano_celda
                
                self._dibujar_celda(superficie, tile, x, y)
                
                # Marcar posiciones especiales
                if (fila, col) == pos_inicio:
                    self._dibujar_posicion_especial(superficie, x, y, es_inicio=True)
                elif (fila, col) == pos_salida:
                    self._dibujar_posicion_especial(superficie, x, y, es_inicio=False)
        
        # Dibujar jugador
        if jugador:
            pos = jugador.obtener_posicion()
            
            # Inicializar posición visual si es necesario
            if self.posicion_jugador_visual is None:
                self.posicion_jugador_visual = (
                    pos[1] * self.tamano_celda,
                    pos[0] * self.tamano_celda
                )
            
            jugador_x = offset_x + self.posicion_jugador_visual[0]
            jugador_y = offset_y + self.posicion_jugador_visual[1]
            self._dibujar_jugador(superficie, jugador_x, jugador_y)
    
    def resetear_posicion_jugador(self, jugador: Jugador):
        """Resetea la posición visual del jugador."""
        if jugador:
            pos = jugador.obtener_posicion()
            self.posicion_jugador_visual = (
                pos[1] * self.tamano_celda,
                pos[0] * self.tamano_celda
            )
    
    def obtener_tamano_mapa_pixeles(self, mapa: Mapa) -> Tuple[int, int]:
        """Obtiene el tamaño del mapa en píxeles."""
        return (mapa.ancho * self.tamano_celda, mapa.alto * self.tamano_celda)

