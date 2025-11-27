"""
Módulo trampa: Define la clase Trampa y el gestor de trampas.
"""

from typing import Tuple, List, Optional
from enum import Enum


class EstadoTrampa(Enum):
    """Estados posibles de una trampa."""
    ACTIVA = "activa"
    INACTIVA = "inactiva"


class Trampa:
    """
    Clase que representa una trampa en el mapa.
    
    Las trampas pueden ser colocadas por el jugador y eliminan enemigos
    que pasen sobre ellas.
    """
    
    def __init__(self, fila: int, columna: int):
        """
        Inicializa una trampa.
        
        Args:
            fila: Fila donde se coloca la trampa.
            columna: Columna donde se coloca la trampa.
        """
        self.fila = fila
        self.columna = columna
        self.estado = EstadoTrampa.ACTIVA
    
    def obtener_posicion(self) -> Tuple[int, int]:
        """
        Obtiene la posición de la trampa.
        
        Returns:
            Tupla (fila, columna) con la posición.
        """
        return (self.fila, self.columna)
    
    def esta_activa(self) -> bool:
        """
        Verifica si la trampa está activa.
        
        Returns:
            True si está activa, False en caso contrario.
        """
        return self.estado == EstadoTrampa.ACTIVA
    
    def desactivar(self) -> None:
        """Desactiva la trampa."""
        self.estado = EstadoTrampa.INACTIVA
    
    def __repr__(self) -> str:
        """Representación de la trampa."""
        return f"Trampa(pos=({self.fila}, {self.columna}), estado={self.estado.value})"


class GestorTrampas:
    """
    Gestor que maneja las trampas del jugador.
    
    Controla:
    - Límite máximo de trampas activas (3)
    - Cooldown entre colocaciones (5 segundos)
    - Detección de colisiones con enemigos
    """
    
    MAX_TRAMPAS_ACTIVAS = 3
    COOLDOWN_COLOCACION = 5.0  # segundos
    PUNTOS_POR_ENEMIGO_ELIMINADO = 10
    
    def __init__(self):
        """Inicializa el gestor de trampas."""
        self.trampas: List[Trampa] = []
        self.tiempo_ultima_colocacion = -self.COOLDOWN_COLOCACION  # Permite colocar inmediatamente
    
    def puede_colocar_trampa(self, tiempo_actual: float) -> bool:
        """
        Verifica si se puede colocar una nueva trampa.
        
        Args:
            tiempo_actual: Tiempo actual del juego en segundos.
            
        Returns:
            True si se puede colocar, False en caso contrario.
        """
        # Verificar límite de trampas activas
        trampas_activas = sum(1 for t in self.trampas if t.esta_activa())
        if trampas_activas >= self.MAX_TRAMPAS_ACTIVAS:
            return False
        
        # Verificar cooldown
        tiempo_desde_ultima = tiempo_actual - self.tiempo_ultima_colocacion
        if tiempo_desde_ultima < self.COOLDOWN_COLOCACION:
            return False
        
        return True
    
    def colocar_trampa(self, fila: int, columna: int, tiempo_actual: float) -> bool:
        """
        Coloca una nueva trampa en la posición especificada.
        
        Args:
            fila: Fila donde colocar la trampa.
            columna: Columna donde colocar la trampa.
            tiempo_actual: Tiempo actual del juego en segundos.
            
        Returns:
            True si se colocó exitosamente, False en caso contrario.
        """
        if not self.puede_colocar_trampa(tiempo_actual):
            return False
        
        # Verificar que no haya ya una trampa en esa posición
        for trampa in self.trampas:
            if trampa.obtener_posicion() == (fila, columna) and trampa.esta_activa():
                return False
        
        # Crear y agregar la nueva trampa
        nueva_trampa = Trampa(fila, columna)
        self.trampas.append(nueva_trampa)
        self.tiempo_ultima_colocacion = tiempo_actual
        
        return True
    
    def obtener_trampas_activas(self) -> List[Trampa]:
        """
        Obtiene la lista de trampas activas.
        
        Returns:
            Lista de trampas activas.
        """
        return [t for t in self.trampas if t.esta_activa()]
    
    def verificar_colisiones_enemigos(self, enemigos: List) -> int:
        """
        Verifica si algún enemigo está en la posición de una trampa activa.
        Si es así, elimina al enemigo y desactiva la trampa.
        
        Args:
            enemigos: Lista de enemigos a verificar.
            
        Returns:
            Número de enemigos eliminados.
        """
        enemigos_eliminados = 0
        
        for trampa in self.trampas:
            if not trampa.esta_activa():
                continue
            
            trampa_pos = trampa.obtener_posicion()
            
            for enemigo in enemigos:
                if enemigo.esta_vivo() and enemigo.obtener_posicion() == trampa_pos:
                    enemigo.matar()
                    trampa.desactivar()
                    enemigos_eliminados += 1
                    break  # Una trampa solo puede eliminar un enemigo
        
        # Limpiar trampas inactivas (opcional, para mantener la lista limpia)
        self.trampas = [t for t in self.trampas if t.esta_activa()]
        
        return enemigos_eliminados
    
    def obtener_tiempo_restante_cooldown(self, tiempo_actual: float) -> float:
        """
        Obtiene el tiempo restante del cooldown.
        
        Args:
            tiempo_actual: Tiempo actual del juego en segundos.
            
        Returns:
            Tiempo restante en segundos (0 si ya puede colocar).
        """
        tiempo_desde_ultima = tiempo_actual - self.tiempo_ultima_colocacion
        restante = self.COOLDOWN_COLOCACION - tiempo_desde_ultima
        return max(0.0, restante)
    
    def limpiar_trampas_inactivas(self) -> None:
        """Elimina las trampas inactivas de la lista."""
        self.trampas = [t for t in self.trampas if t.esta_activa()]
    
    def __repr__(self) -> str:
        """Representación del gestor."""
        trampas_activas = len(self.obtener_trampas_activas())
        return f"GestorTrampas(trampas_activas={trampas_activas}/{self.MAX_TRAMPAS_ACTIVAS})"

