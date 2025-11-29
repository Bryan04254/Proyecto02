"""
Módulo jugador: Define la clase Jugador con movimiento y sistema de energía.
"""

from typing import Tuple, Optional

# Importación que funciona tanto como módulo como ejecutado directamente
try:
    from .mapa import Mapa
except ImportError:
    # Si falla la importación relativa, intentar absoluta
    from modelo.mapa import Mapa


class Jugador:
    """
    Clase que representa al jugador en el juego.
    
    El jugador tiene posición, energía y puede moverse por el mapa.
    """
    
    # Constantes de consumo de energía (reducidas para mejor balance)
    ENERGIA_CAMINAR = 0.5  # Reducido de 1 a 0.5
    ENERGIA_CORRER = 1.5   # Reducido de 3 a 1.5
    
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
        self.movimientos_desde_ultima_perdida = 0  # Contador para perder 1% cada 3 movimientos
    
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
        # Por defecto usa modo "escapa", pero esto se puede sobrescribir en modo_cazador
        if not mapa.es_transitable_por_jugador(nueva_fila, nueva_col, modo="escapa"):
            return False
        
        # Consumir energía (shift no aumenta velocidad, solo consume más energía)
        if corriendo:
            if not self.puede_correr():
                return False
            self.consumir_energia(self.ENERGIA_CORRER)
        else:
            self.consumir_energia(self.ENERGIA_CAMINAR)
        
        # Realizar el movimiento (la velocidad es la misma, corriendo solo consume más energía)
        self.fila = nueva_fila
        self.columna = nueva_col
        
        # Perder 0.5% de energía cada 5 movimientos (reducido para mejor balance)
        self.movimientos_desde_ultima_perdida += 1
        if self.movimientos_desde_ultima_perdida >= 5:
            porcentaje_perdida = self.energia_maxima * 0.005  # 0.5% de la energía máxima
            self.energia_actual = max(0, self.energia_actual - porcentaje_perdida)
            self.movimientos_desde_ultima_perdida = 0
        
        return True
    
    def puede_correr(self) -> bool:
        """
        Verifica si el jugador tiene suficiente energía para correr.
        
        Returns:
            True si puede correr, False en caso contrario.
        """
        return self.energia_actual >= self.ENERGIA_CORRER
    
    def consumir_energia(self, cantidad: float) -> bool:
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
            self.energia_actual = max(0, self.energia_actual - cantidad)
            return True
        return False
    
    def recuperar_energia(self, cantidad: float) -> None:
        """
        Recupera energía del jugador.
        
        Args:
            cantidad: Cantidad de energía a recuperar.
        """
        if cantidad > 0:
            self.energia_actual = min(self.energia_maxima, self.energia_actual + cantidad)
    
    def actualizar_energia(self, delta_tiempo: float, tasa_recuperacion: float = 1.0) -> None:
        """
        Actualiza la energía del jugador con el tiempo (recuperación gradual).
        
        Args:
            delta_tiempo: Tiempo transcurrido (en segundos o unidades de tiempo).
            tasa_recuperacion: Energía recuperada por unidad de tiempo (por defecto 1.0 por segundo).
        """
        # Solo recuperar si no está corriendo y tiene menos del 100%
        if self.energia_actual < self.energia_maxima:
            energia_recuperada = delta_tiempo * tasa_recuperacion
            self.recuperar_energia(energia_recuperada)
    
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
        Verifica si el jugador ha llegado a alguna salida del mapa.
        
        Args:
            mapa: Mapa en el que se encuentra el jugador.
            
        Returns:
            True si el jugador está en alguna posición de salida, False en caso contrario.
        """
        posicion_actual = self.obtener_posicion()
        return mapa.es_posicion_salida(posicion_actual[0], posicion_actual[1])
    
    def __repr__(self) -> str:
        """Representación del jugador."""
        return f"Jugador(pos=({self.fila}, {self.columna}), energia={self.energia_actual}/{self.energia_maxima})"

