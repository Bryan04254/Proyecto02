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
    Las reglas de transición pueden variar según el modo de juego
    (especialmente en modo "cazador" donde se invierten algunas reglas).
    """
    
    def __init__(self, tipo: TipoTile):
        """
        Inicializa una casilla.
        
        Args:
            tipo: Tipo de casilla según el enum TipoTile.
                  Identifica el tipo de terreno (Camino, Muro, Liana, Tunel).
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
    Casilla de camino: terreno básico transitables.
    
    Tanto el jugador como los enemigos pueden pasar por caminos.
    Es el tipo de casilla más común y versátil del mapa.
    """
    
    def __init__(self):
        super().__init__(TipoTile.CAMINO)
    
    def permite_paso_jugador(self) -> bool:
        """El jugador siempre puede pasar por caminos."""
        return True
    
    def permite_paso_enemigo(self) -> bool:
        """Los enemigos siempre pueden pasar por caminos."""
        return True


class Muro(Tile):
    """
    Casilla de muro: obstáculo infranqueable.
    
    Ni el jugador ni los enemigos pueden pasar por muros.
    Los muros forman las paredes del laberinto y bloquean el paso.
    """
    
    def __init__(self):
        super().__init__(TipoTile.MURO)
    
    def permite_paso_jugador(self) -> bool:
        """El jugador NO puede pasar por muros."""
        return False
    
    def permite_paso_enemigo(self) -> bool:
        """Los enemigos NO pueden pasar por muros."""
        return False


class Liana(Tile):
    """
    Casilla de liana: terreno especial con reglas asimétricas.
    
    En modo "escapa":
    - Los enemigos pueden pasar por lianas (verde)
    - El jugador NO puede pasar por lianas
    
    En modo "cazador" (reglas invertidas):
    - El jugador puede pasar por lianas
    - Los enemigos NO pueden pasar por lianas
    """
    
    def __init__(self):
        super().__init__(TipoTile.LIANA)
    
    def permite_paso_jugador(self) -> bool:
        """
        En modo escapa: el jugador NO puede pasar.
        En modo cazador: el jugador SÍ puede pasar (regla invertida en Mapa).
        """
        return False  # Por defecto no, pero Mapa invierte esto en modo cazador
    
    def permite_paso_enemigo(self) -> bool:
        """
        En modo escapa: los enemigos SÍ pueden pasar.
        En modo cazador: los enemigos NO pueden pasar (regla invertida en Mapa).
        """
        return True  # Por defecto sí, pero Mapa invierte esto en modo cazador


class Tunel(Tile):
    """
    Casilla de túnel: terreno especial con reglas asimétricas.
    
    En modo "escapa":
    - El jugador puede pasar por túneles (azul)
    - Los enemigos NO pueden pasar por túneles
    
    En modo "cazador" (reglas invertidas):
    - El jugador NO puede pasar por túneles
    - Los enemigos SÍ pueden pasar por túneles
    """
    
    def __init__(self):
        super().__init__(TipoTile.TUNEL)
    
    def permite_paso_jugador(self) -> bool:
        """
        En modo escapa: el jugador SÍ puede pasar.
        En modo cazador: el jugador NO puede pasar (regla invertida en Mapa).
        """
        return True  # Por defecto sí, pero Mapa invierte esto en modo cazador
    
    def permite_paso_enemigo(self) -> bool:
        """
        En modo escapa: los enemigos NO pueden pasar.
        En modo cazador: los enemigos SÍ pueden pasar (regla invertida en Mapa).
        """
        return False  # Por defecto no, pero Mapa invierte esto en modo cazador

