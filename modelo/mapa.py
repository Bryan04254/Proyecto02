"""
Módulo mapa: Define la clase Mapa que representa el laberinto.
"""

from typing import Tuple, Optional, List
from collections import deque
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
        
        Raises:
            ValueError: Si las dimensiones no coinciden o las posiciones son inválidas.
        """
        # Validaciones básicas
        if ancho <= 0 or alto <= 0:
            raise ValueError("El ancho y alto del mapa deben ser mayores a 0")
        
        if len(casillas) != alto:
            raise ValueError(f"El número de filas en casillas ({len(casillas)}) no coincide con alto ({alto})")
        
        if len(casillas) > 0 and len(casillas[0]) != ancho:
            raise ValueError(f"El número de columnas en casillas ({len(casillas[0])}) no coincide con ancho ({ancho})")
        
        fila_inicio, col_inicio = posicion_inicio
        fila_salida, col_salida = posicion_salida
        
        if not (0 <= fila_inicio < alto and 0 <= col_inicio < ancho):
            raise ValueError(f"Posición inicial inválida: {posicion_inicio} fuera de límites ({alto}x{ancho})")
        
        if not (0 <= fila_salida < alto and 0 <= col_salida < ancho):
            raise ValueError(f"Posición de salida inválida: {posicion_salida} fuera de límites ({alto}x{ancho})")
        
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
    
    def existe_camino_valido(self, desde: Optional[Tuple[int, int]] = None, 
                             hasta: Optional[Tuple[int, int]] = None) -> bool:
        """
        Verifica si existe un camino válido para el jugador entre dos posiciones.
        
        Args:
            desde: Posición de inicio. Si es None, usa la posición inicial del jugador.
            hasta: Posición destino. Si es None, usa la posición de salida.
            
        Returns:
            True si existe un camino válido, False en caso contrario.
        """
        if desde is None:
            desde = self.posicion_inicio
        if hasta is None:
            hasta = self.posicion_salida
        
        fila_inicio, col_inicio = desde
        fila_fin, col_fin = hasta
        
        # Verificar que las posiciones sean válidas y transitables
        if not self.es_transitable_por_jugador(fila_inicio, col_inicio):
            return False
        if not self.es_transitable_por_jugador(fila_fin, col_fin):
            return False
        
        # BFS para encontrar camino
        visitado = [[False for _ in range(self.ancho)] for _ in range(self.alto)]
        cola = deque([(fila_inicio, col_inicio)])
        visitado[fila_inicio][col_inicio] = True
        
        direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        while cola:
            fila, col = cola.popleft()
            
            if (fila, col) == (fila_fin, col_fin):
                return True
            
            for df, dc in direcciones:
                nueva_fila = fila + df
                nueva_col = col + dc
                
                if (0 <= nueva_fila < self.alto and 
                    0 <= nueva_col < self.ancho and 
                    not visitado[nueva_fila][nueva_col] and
                    self.es_transitable_por_jugador(nueva_fila, nueva_col)):
                    
                    visitado[nueva_fila][nueva_col] = True
                    cola.append((nueva_fila, nueva_col))
        
        return False
    
    def __repr__(self) -> str:
        """Representación del mapa."""
        return f"Mapa({self.ancho}x{self.alto}, inicio={self.posicion_inicio}, salida={self.posicion_salida})"

