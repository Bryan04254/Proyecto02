"""
Módulo mapa: Define la clase Mapa que representa el laberinto.
"""

from typing import Tuple, Optional, List
from .tile import Tile, Camino, Muro


class Mapa:
    """
    Clase que representa el mapa del laberinto como una matriz 2D de casillas.
    
    El mapa tiene un tamaño (ancho, alto), una posición inicial del jugador
    y al menos una salida.
    """
    
    def __init__(self, ancho: int, alto: int, casillas: List[List[Tile]], 
                 posicion_inicio: Tuple[int, int], 
                 posicion_salida: Tuple[int, int]):
        """
        Inicializa un mapa.
        
        Args:
            ancho: Ancho del mapa (número de columnas).
            alto: Alto del mapa (número de filas).
            casillas: Matriz 2D de objetos Tile.
            posicion_inicio: Tupla (fila, columna) de la posición inicial del jugador.
            posicion_salida: Tupla (fila, columna) de la posición de salida.
        """
        self.ancho = ancho
        self.alto = alto
        self.casillas = casillas
        self.posicion_inicio = posicion_inicio
        self.posicion_salida = posicion_salida
    
    def es_posicion_valida(self, fila: int, columna: int) -> bool:
        """
        Verifica si una posición está dentro de los límites del mapa.
        
        Args:
            fila: Fila a verificar.
            columna: Columna a verificar.
            
        Returns:
            True si la posición es válida, False en caso contrario.
        """
        return 0 <= fila < self.alto and 0 <= columna < self.ancho
    
    def es_transitable_por_jugador(self, fila: int, columna: int) -> bool:
        """
        Verifica si una casilla permite el paso del jugador.
        
        Args:
            fila: Fila de la casilla.
            columna: Columna de la casilla.
            
        Returns:
            True si el jugador puede pasar, False en caso contrario.
        """
        if not self.es_posicion_valida(fila, columna):
            return False
        return self.casillas[fila][columna].permite_paso_jugador()
    
    def es_transitable_por_enemigo(self, fila: int, columna: int) -> bool:
        """
        Verifica si una casilla permite el paso de enemigos.
        
        Args:
            fila: Fila de la casilla.
            columna: Columna de la casilla.
            
        Returns:
            True si los enemigos pueden pasar, False en caso contrario.
        """
        if not self.es_posicion_valida(fila, columna):
            return False
        return self.casillas[fila][columna].permite_paso_enemigo()
    
    def obtener_casilla(self, fila: int, columna: int) -> Optional[Tile]:
        """
        Obtiene la casilla en la posición especificada.
        
        Args:
            fila: Fila de la casilla.
            columna: Columna de la casilla.
            
        Returns:
            El objeto Tile en esa posición, o None si la posición no es válida.
        """
        if not self.es_posicion_valida(fila, columna):
            return None
        return self.casillas[fila][columna]
    
    def obtener_posicion_salida(self) -> Tuple[int, int]:
        """
        Obtiene la posición de la salida.
        
        Returns:
            Tupla (fila, columna) con la posición de la salida.
        """
        return self.posicion_salida
    
    def obtener_posicion_inicio_jugador(self) -> Tuple[int, int]:
        """
        Obtiene la posición inicial del jugador.
        
        Returns:
            Tupla (fila, columna) con la posición inicial del jugador.
        """
        return self.posicion_inicio
    
    def __repr__(self) -> str:
        """Representación del mapa."""
        return f"Mapa({self.ancho}x{self.alto}, inicio={self.posicion_inicio}, salida={self.posicion_salida})"

