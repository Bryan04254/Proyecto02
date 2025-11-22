"""
Módulo sistema: Contiene sistemas auxiliares (registro de jugador, puntajes).
"""

from .jugador_info import JugadorInfo, registrar_jugador
from .puntajes import Puntaje, ScoreBoard, ModoJuego

__all__ = ['JugadorInfo', 'registrar_jugador', 'Puntaje', 'ScoreBoard', 'ModoJuego']

