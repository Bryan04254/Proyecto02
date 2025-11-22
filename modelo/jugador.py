"""
Módulo jugador: Define la clase Jugador con movimiento y sistema de energía.
"""

from typing import Tuple, Optional
from .mapa import Mapa


class Jugador:
    """
    Clase que representa al jugador en el juego.
    
    El jugador tiene posición, energía y puede moverse por el mapa.
    """
    
    # Constantes de consumo de energía
    ENERGIA_CAMINAR = 1
    ENERGIA_CORRER = 3
    
    def __init__(self, fila: int, columna: int, energia_maxima: int = 100):
        """
        Inicializa un jugador.
        
        Args:
            fila: Fila inicial del jugador.
            columna: Columna inicial del jugador.
            energia_maxima: Energía máxima del jugador.
        """
        self.fila = fila
        self.columna = columna
        self.energia_maxima = energia_maxima
        self.energia_actual = energia_maxima
    
    def obtener_posicion(self) -> Tuple[int, int]:
        """
        Obtiene la posición actual del jugador.
        
        Returns:
            Tupla (fila, columna) con la posición actual.
        """
        return (self.fila, self.columna)
    
    def mover_arriba(self, mapa: Mapa, corriendo: bool = False) -> bool:
        """
        Mueve al jugador hacia arriba (disminuye fila).
        
        Args:
            mapa: Mapa en el que se mueve el jugador.
            corriendo: Si True, el jugador corre (consume más energía).
            
        Returns:
            True si el movimiento fue exitoso, False en caso contrario.
        """
        return self._mover(mapa, self.fila - 1, self.columna, corriendo)
    
    def mover_abajo(self, mapa: Mapa, corriendo: bool = False) -> bool:
        """
        Mueve al jugador hacia abajo (aumenta fila).
        
        Args:
            mapa: Mapa en el que se mueve el jugador.
            corriendo: Si True, el jugador corre (consume más energía).
            
        Returns:
            True si el movimiento fue exitoso, False en caso contrario.
        """
        return self._mover(mapa, self.fila + 1, self.columna, corriendo)
    
    def mover_izquierda(self, mapa: Mapa, corriendo: bool = False) -> bool:
        """
        Mueve al jugador hacia la izquierda (disminuye columna).
        
        Args:
            mapa: Mapa en el que se mueve el jugador.
            corriendo: Si True, el jugador corre (consume más energía).
            
        Returns:
            True si el movimiento fue exitoso, False en caso contrario.
        """
        return self._mover(mapa, self.fila, self.columna - 1, corriendo)
    
    def mover_derecha(self, mapa: Mapa, corriendo: bool = False) -> bool:
        """
        Mueve al jugador hacia la derecha (aumenta columna).
        
        Args:
            mapa: Mapa en el que se mueve el jugador.
            corriendo: Si True, el jugador corre (consume más energía).
            
        Returns:
            True si el movimiento fue exitoso, False en caso contrario.
        """
        return self._mover(mapa, self.fila, self.columna + 1, corriendo)
    
    def _mover(self, mapa: Mapa, nueva_fila: int, nueva_col: int, corriendo: bool) -> bool:
        """
        Método interno que realiza el movimiento.
        
        Args:
            mapa: Mapa en el que se mueve el jugador.
            nueva_fila: Nueva fila destino.
            nueva_col: Nueva columna destino.
            corriendo: Si True, el jugador corre.
            
        Returns:
            True si el movimiento fue exitoso, False en caso contrario.
        """
        # Validar posición
        if not mapa.es_posicion_valida(nueva_fila, nueva_col):
            return False
        
        # Verificar si la casilla permite el paso del jugador
        if not mapa.es_transitable_por_jugador(nueva_fila, nueva_col):
            return False
        
        # Verificar energía si está corriendo
        if corriendo:
            if not self.puede_correr():
                return False
            self.consumir_energia(self.ENERGIA_CORRER)
        else:
            self.consumir_energia(self.ENERGIA_CAMINAR)
        
        # Realizar el movimiento
        self.fila = nueva_fila
        self.columna = nueva_col
        
        return True
    
    def puede_correr(self) -> bool:
        """
        Verifica si el jugador tiene suficiente energía para correr.
        
        Returns:
            True si puede correr, False en caso contrario.
        """
        return self.energia_actual >= self.ENERGIA_CORRER
    
    def consumir_energia(self, cantidad: int) -> bool:
        """
        Consume energía del jugador.
        
        Args:
            cantidad: Cantidad de energía a consumir.
            
        Returns:
            True si se consumió la energía, False si no había suficiente.
        """
        if cantidad <= 0:
            return False
        
        if self.energia_actual >= cantidad:
            self.energia_actual -= cantidad
            if self.energia_actual < 0:
                self.energia_actual = 0
            return True
        return False
    
    def recuperar_energia(self, cantidad: int) -> None:
        """
        Recupera energía del jugador.
        
        Args:
            cantidad: Cantidad de energía a recuperar.
        """
        if cantidad > 0:
            self.energia_actual += cantidad
            if self.energia_actual > self.energia_maxima:
                self.energia_actual = self.energia_maxima
    
    def actualizar_energia(self, delta_tiempo: float, tasa_recuperacion: float = 0.5) -> None:
        """
        Actualiza la energía del jugador con el tiempo (recuperación gradual).
        
        Args:
            delta_tiempo: Tiempo transcurrido (en segundos o unidades de tiempo).
            tasa_recuperacion: Energía recuperada por unidad de tiempo.
        """
        energia_recuperada = delta_tiempo * tasa_recuperacion
        self.recuperar_energia(int(energia_recuperada))
    
    def obtener_porcentaje_energia(self) -> float:
        """
        Obtiene el porcentaje de energía actual (0.0 a 1.0).
        
        Returns:
            Porcentaje de energía como float entre 0.0 y 1.0.
        """
        if self.energia_maxima == 0:
            return 0.0
        return self.energia_actual / self.energia_maxima
    
    def obtener_energia_actual(self) -> int:
        """
        Obtiene la energía actual del jugador.
        
        Returns:
            Energía actual.
        """
        return self.energia_actual
    
    def obtener_energia_maxima(self) -> int:
        """
        Obtiene la energía máxima del jugador.
        
        Returns:
            Energía máxima.
        """
        return self.energia_maxima
    
    def ha_llegado_a_salida(self, mapa: Mapa) -> bool:
        """
        Verifica si el jugador ha llegado a la salida del mapa.
        
        Args:
            mapa: Mapa en el que se encuentra el jugador.
            
        Returns:
            True si el jugador está en la posición de salida, False en caso contrario.
        """
        salida = mapa.obtener_posicion_salida()
        return self.obtener_posicion() == salida
    
    def __repr__(self) -> str:
        """Representación del jugador."""
        return f"Jugador(pos=({self.fila}, {self.columna}), energia={self.energia_actual}/{self.energia_maxima})"

