"""
Módulo modelo: Contiene las clases principales del mundo del juego.
"""

from .tile import Tile, Camino, Muro, Liana, Tunel
from .mapa import Mapa
from .jugador import Jugador
from .enemigo import Enemigo, EstadoEnemigo
from .trampa import Trampa, GestorTrampas, EstadoTrampa

__all__ = ['Tile', 'Camino', 'Muro', 'Liana', 'Tunel', 'Mapa', 'Jugador', 
           'Enemigo', 'EstadoEnemigo', 'Trampa', 'GestorTrampas', 'EstadoTrampa']

