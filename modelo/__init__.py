"""
Módulo modelo: Contiene las clases principales del mundo del juego.
"""

from .tile import Tile, Camino, Muro, Liana, Tunel
from .mapa import Mapa
from .jugador import Jugador

__all__ = ['Tile', 'Camino', 'Muro', 'Liana', 'Tunel', 'Mapa', 'Jugador']

