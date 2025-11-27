"""
Módulo logica: Contiene la lógica del juego (generación de mapas, dificultad).
"""

from .generador_mapa import GeneradorMapa
from .dificultad import Dificultad, ConfiguracionDificultad

__all__ = ['GeneradorMapa', 'Dificultad', 'ConfiguracionDificultad']

