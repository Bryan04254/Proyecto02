"""
Módulo tile: Define las clases de casillas/terrenos del mapa.
"""

from abc import ABC, abstractmethod
from enum import Enum


class TipoTile(Enum):
    """Enum para identificar tipos de casillas."""
    CAMINO = "camino"
    MURO = "muro"
    LIANA = "liana"
    TUNEL = "tunel"


class Tile(ABC):
    """
    Clase base abstracta para las casillas del mapa.
    
    Cada casilla define si permite el paso del jugador y/o enemigos.
    """
    
    def __init__(self, tipo: TipoTile):
        """
        Inicializa una casilla.
        
        Args:
            tipo: Tipo de casilla según el enum TipoTile.
        """
        self.tipo = tipo
    
    @abstractmethod
    def permite_paso_jugador(self) -> bool:
        """
        Indica si el jugador puede pasar por esta casilla.
        
        Returns:
            True si el jugador puede pasar, False en caso contrario.
        """
        pass
    
    @abstractmethod
    def permite_paso_enemigo(self) -> bool:
        """
        Indica si los enemigos pueden pasar por esta casilla.
        
        Returns:
            True si los enemigos pueden pasar, False en caso contrario.
        """
        pass
    
    def __repr__(self) -> str:
        """Representación de la casilla."""
        return f"{self.__class__.__name__}()"


class Camino(Tile):
    """
    Casilla de camino: tanto jugador como enemigos pueden pasar.
    """
    
    def __init__(self):
        super().__init__(TipoTile.CAMINO)
    
    def permite_paso_jugador(self) -> bool:
        return True
    
    def permite_paso_enemigo(self) -> bool:
        return True


class Muro(Tile):
    """
    Casilla de muro: nadie puede pasar.
    """
    
    def __init__(self):
        super().__init__(TipoTile.MURO)
    
    def permite_paso_jugador(self) -> bool:
        return False
    
    def permite_paso_enemigo(self) -> bool:
        return False


class Liana(Tile):
    """
    Casilla de liana: solo enemigos pueden pasar (obstáculo para el jugador).
    """
    
    def __init__(self):
        super().__init__(TipoTile.LIANA)
    
    def permite_paso_jugador(self) -> bool:
        return False
    
    def permite_paso_enemigo(self) -> bool:
        return True


class Tunel(Tile):
    """
    Casilla de túnel: solo el jugador puede pasar (enemigos no).
    """
    
    def __init__(self):
        super().__init__(TipoTile.TUNEL)
    
    def permite_paso_jugador(self) -> bool:
        return True
    
    def permite_paso_enemigo(self) -> bool:
        return False

