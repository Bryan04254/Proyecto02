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
        # Posición de la trampa en el mapa
        self.fila = fila
        self.columna = columna
        # Estado inicial: todas las trampas empiezan activas
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
        """
        Desactiva la trampa.
        
        Se llama cuando un enemigo pasa sobre la trampa y es eliminado.
        La trampa desaparece del mapa después de ser desactivada.
        """
        self.estado = EstadoTrampa.INACTIVA
    
    def __repr__(self) -> str:
        """Representación de la trampa."""
        return f"Trampa(pos=({self.fila}, {self.columna}), estado={self.estado.value})"


class GestorTrampas:
    """
    Gestor que maneja las trampas del jugador.
    
    Controla:
    - Límite máximo de trampas activas (configurable, por defecto 3)
    - Cooldown entre colocaciones (5 segundos)
    - Detección de colisiones con enemigos
    """
    
    MAX_TRAMPAS_ACTIVAS_DEFAULT = 3
    COOLDOWN_COLOCACION = 5.0  # segundos
    PUNTOS_POR_ENEMIGO_ELIMINADO = 10
    
    def __init__(self, max_trampas_activas: int = None):
        """
        Inicializa el gestor de trampas.
        
        Args:
            max_trampas_activas: Límite máximo de trampas activas. Si es None, usa el valor por defecto.
        """
        # Lista de todas las trampas (activas e inactivas)
        self.trampas: List[Trampa] = []
        # Límite máximo de trampas activas simultáneamente (por defecto 3)
        self.max_trampas_activas = max_trampas_activas if max_trampas_activas is not None else self.MAX_TRAMPAS_ACTIVAS_DEFAULT
        # Tiempo de la última colocación (inicializado negativo para permitir primera colocación inmediata)
        self.tiempo_ultima_colocacion = -self.COOLDOWN_COLOCACION
    
    def puede_colocar_trampa(self, tiempo_actual: float) -> bool:
        """
        Verifica si se puede colocar una nueva trampa.
        El cooldown se maneja en el modo de juego (sistema de regeneración).
        
        Args:
            tiempo_actual: Tiempo actual del juego en segundos.
            
        Returns:
            True si se puede colocar, False en caso contrario.
        """
        # Verificar límite de trampas activas en el mapa
        trampas_activas = sum(1 for t in self.trampas if t.esta_activa())
        if trampas_activas >= self.max_trampas_activas:
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
        # Verificar límite de trampas activas en el mapa
        trampas_activas = sum(1 for t in self.trampas if t.esta_activa())
        if trampas_activas >= self.max_trampas_activas:
            return False
        
        # Verificar que no haya ya una trampa en esa posición
        for trampa in self.trampas:
            if trampa.obtener_posicion() == (fila, columna) and trampa.esta_activa():
                return False
        
        # Crear y agregar la nueva trampa
        nueva_trampa = Trampa(fila, columna)
        self.trampas.append(nueva_trampa)
        
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
        Si es así, elimina al enemigo inmediatamente y la trampa desaparece del mapa.
        
        Args:
            enemigos: Lista de enemigos a verificar.
            
        Returns:
            Número de enemigos eliminados.
        """
        enemigos_eliminados = 0
        trampas_a_desactivar = []
        
        # Obtener todas las trampas activas primero
        trampas_activas = [t for t in self.trampas if t.esta_activa()]
        
        # Verificar colisiones para cada trampa activa
        # Iterar sobre todas las trampas activas en el mapa
        for trampa in trampas_activas:
            trampa_pos = trampa.obtener_posicion()
            trampa_fila, trampa_col = trampa_pos
            
            # Verificar cada enemigo para detectar colisiones
            for enemigo in enemigos:
                # Saltar enemigos que ya están muertos
                if not enemigo.esta_vivo():
                    continue
                
                # Obtener posición del enemigo
                enemigo_pos = enemigo.obtener_posicion()
                enemigo_fila, enemigo_col = enemigo_pos
                
                # Verificar colisión: si el enemigo está en la misma posición que la trampa
                if enemigo_fila == trampa_fila and enemigo_col == trampa_col:
                    # Eliminar al enemigo inmediatamente
                    enemigo.matar()
                    # Marcar trampa para desactivar (desaparece del mapa después de usar)
                    trampas_a_desactivar.append(trampa)
                    enemigos_eliminados += 1
                    # Una trampa solo puede eliminar un enemigo por frame
                    break
        
        # Desactivar las trampas que eliminaron enemigos (desaparecen del mapa)
        for trampa in trampas_a_desactivar:
            trampa.desactivar()
        
        # Limpiar trampas inactivas de la lista (las trampas desaparecen)
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
        """
        Elimina las trampas inactivas de la lista.
        
        Este método limpia la lista de trampas, removiendo aquellas que
        fueron desactivadas (por ejemplo, después de eliminar un enemigo).
        """
        self.trampas = [t for t in self.trampas if t.esta_activa()]
    
    def __repr__(self) -> str:
        """Representación del gestor."""
        trampas_activas = len(self.obtener_trampas_activas())
        return f"GestorTrampas(trampas_activas={trampas_activas}/{self.max_trampas_activas})"

