"""
Módulo mapa: Define la clase Mapa que representa el laberinto.
"""

from typing import Tuple, Optional, List
from collections import deque

# Importación que funciona tanto como módulo como ejecutado directamente
try:
    from .tile import Tile, Camino, Muro
except ImportError:
    # Si falla la importación relativa, intentar absoluta
    from modelo.tile import Tile, Camino, Muro


class Mapa:
    """
    Clase que representa el mapa del laberinto como una matriz 2D de casillas.
    
    El mapa tiene un tamaño (ancho, alto), una posición inicial del jugador
    y al menos una salida.
    """
    
    def __init__(self, ancho: int, alto: int, casillas: List[List[Tile]], 
                 posicion_inicio: Tuple[int, int], 
                 posiciones_salida: List[Tuple[int, int]]):
        """
        Inicializa un mapa.
        
        Args:
            ancho: Ancho del mapa (número de columnas).
            alto: Alto del mapa (número de filas).
            casillas: Matriz 2D de objetos Tile.
            posicion_inicio: Tupla (fila, columna) de la posición inicial del jugador.
            posiciones_salida: Lista de tuplas (fila, columna) con las posiciones de salida.
        
        Raises:
            ValueError: Si las dimensiones no coinciden o las posiciones son inválidas.
        """
        # ============================================
        # VALIDACIONES DE INTEGRIDAD DEL MAPA
        # ============================================
        
        # Validar dimensiones positivas
        if ancho <= 0 or alto <= 0:
            raise ValueError("El ancho y alto del mapa deben ser mayores a 0")
        
        # Validar que el número de filas coincida con el alto especificado
        if len(casillas) != alto:
            raise ValueError(f"El número de filas en casillas ({len(casillas)}) no coincide con alto ({alto})")
        
        # Validar que el número de columnas coincida con el ancho especificado
        # (solo si hay al menos una fila)
        if len(casillas) > 0 and len(casillas[0]) != ancho:
            raise ValueError(f"El número de columnas en casillas ({len(casillas[0])}) no coincide con ancho ({ancho})")
        
        # Validar posición inicial del jugador
        fila_inicio, col_inicio = posicion_inicio
        if not (0 <= fila_inicio < alto and 0 <= col_inicio < ancho):
            raise ValueError(f"Posición inicial inválida: {posicion_inicio} fuera de límites ({alto}x{ancho})")
        
        # Validar que haya al menos una salida
        if not posiciones_salida or len(posiciones_salida) == 0:
            raise ValueError("Debe haber al menos una salida")
        
        # Validar que todas las salidas estén dentro de los límites del mapa
        for fila_salida, col_salida in posiciones_salida:
            if not (0 <= fila_salida < alto and 0 <= col_salida < ancho):
                raise ValueError(f"Posición de salida inválida: ({fila_salida}, {col_salida}) fuera de límites ({alto}x{ancho})")
        
        # ============================================
        # INICIALIZACIÓN DE ATRIBUTOS
        # ============================================
        self.ancho = ancho
        self.alto = alto
        self.casillas = casillas  # Matriz 2D de objetos Tile
        self.posicion_inicio = posicion_inicio  # Posición inicial del jugador
        self.posiciones_salida = posiciones_salida  # Lista de posiciones de salida
        
        # Mantener compatibilidad hacia atrás: primera salida como salida principal
        # (algunos métodos antiguos pueden usar posicion_salida en singular)
        self.posicion_salida = posiciones_salida[0]
    
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
    
    def es_transitable_por_jugador(self, fila: int, columna: int, modo: str = "escapa") -> bool:
        """
        Verifica si una casilla permite el paso del jugador.
        
        Args:
            fila: Fila de la casilla.
            columna: Columna de la casilla.
            modo: Modo de juego ("escapa" o "cazador"). En modo cazador, las reglas se invierten.
            
        Returns:
            True si el jugador puede pasar, False en caso contrario.
        """
        if not self.es_posicion_valida(fila, columna):
            return False
        
        # Obtener el tile en la posición especificada
        tile = self.casillas[fila][columna]
        
        # ============================================
        # REGLAS ESPECIALES PARA MODO CAZADOR
        # ============================================
        # En modo cazador, las reglas de transición se invierten:
        # - Jugador puede pasar por Liana (verde) pero NO por Tunel (azul)
        # - Esto crea una mecánica diferente donde el jugador y los enemigos
        #   tienen acceso a diferentes áreas del mapa
        if modo == "cazador":
            from modelo.tile import Liana, Tunel
            if isinstance(tile, Liana):
                return True  # En modo cazador, el jugador puede pasar por Liana
            elif isinstance(tile, Tunel):
                return False  # En modo cazador, el jugador NO puede pasar por Tunel
        
        # En modo escapa, usar las reglas normales del tile
        return tile.permite_paso_jugador()
    
    def es_transitable_por_enemigo(self, fila: int, columna: int, modo: str = "escapa") -> bool:
        """
        Verifica si una casilla permite el paso de enemigos.
        
        Args:
            fila: Fila de la casilla.
            columna: Columna de la casilla.
            modo: Modo de juego ("escapa" o "cazador"). En modo cazador, las reglas se invierten.
            
        Returns:
            True si los enemigos pueden pasar, False en caso contrario.
        """
        if not self.es_posicion_valida(fila, columna):
            return False
        
        # Obtener el tile en la posición especificada
        tile = self.casillas[fila][columna]
        
        # ============================================
        # REGLAS ESPECIALES PARA MODO CAZADOR
        # ============================================
        # En modo cazador, las reglas de transición se invierten:
        # - Enemigos pueden pasar por Tunel (azul) pero NO por Liana (verde)
        # - Esto complementa las reglas del jugador para crear mecánicas asimétricas
        if modo == "cazador":
            from modelo.tile import Liana, Tunel
            if isinstance(tile, Tunel):
                return True  # En modo cazador, los enemigos pueden pasar por Tunel
            elif isinstance(tile, Liana):
                return False  # En modo cazador, los enemigos NO pueden pasar por Liana
        
        # En modo escapa, usar las reglas normales del tile
        return tile.permite_paso_enemigo()
    
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
        Obtiene la posición de la primera salida (compatibilidad hacia atrás).
        
        Returns:
            Tupla (fila, columna) con la posición de la primera salida.
        """
        return self.posicion_salida
    
    def obtener_posiciones_salida(self) -> List[Tuple[int, int]]:
        """
        Obtiene todas las posiciones de salida.
        
        Returns:
            Lista de tuplas (fila, columna) con las posiciones de salida.
        """
        return self.posiciones_salida
    
    def es_posicion_salida(self, fila: int, columna: int) -> bool:
        """
        Verifica si una posición es una salida.
        
        Args:
            fila: Fila a verificar.
            columna: Columna a verificar.
            
        Returns:
            True si la posición es una salida, False en caso contrario.
        """
        return (fila, columna) in self.posiciones_salida
    
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
            hasta: Posición destino. Si es None, verifica si hay camino a cualquiera de las salidas.
            
        Returns:
            True si existe un camino válido, False en caso contrario.
        """
        if desde is None:
            desde = self.posicion_inicio
        if hasta is None:
            # Si no se especifica destino, verificar si hay camino a cualquiera de las salidas
            return any(self.existe_camino_valido(desde, salida) for salida in self.posiciones_salida)
        
        # Extraer coordenadas de inicio y fin
        fila_inicio, col_inicio = desde
        fila_fin, col_fin = hasta
        
        # Verificar que las posiciones sean válidas y transitables para el jugador
        if not self.es_transitable_por_jugador(fila_inicio, col_inicio):
            return False
        if not self.es_transitable_por_jugador(fila_fin, col_fin):
            return False
        
        # ============================================
        # BFS (Breadth-First Search) PARA ENCONTRAR CAMINO
        # ============================================
        # BFS explora el mapa nivel por nivel hasta encontrar el destino
        # Es ideal para encontrar el camino más corto en un grafo no ponderado
        
        # Inicializar estructuras de datos para BFS
        visitado = [[False for _ in range(self.ancho)] for _ in range(self.alto)]  # Matriz de visitados
        cola = deque([(fila_inicio, col_inicio)])  # Cola FIFO para BFS
        visitado[fila_inicio][col_inicio] = True  # Marcar inicio como visitado
        
        # Direcciones posibles: arriba, abajo, izquierda, derecha
        direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        # BFS: explorar nivel por nivel
        while cola:
            fila, col = cola.popleft()  # Obtener siguiente posición de la cola
            
            # Si llegamos al destino, existe un camino
            if (fila, col) == (fila_fin, col_fin):
                return True
            
            # Explorar vecinos (4 direcciones)
            for df, dc in direcciones:
                nueva_fila = fila + df
                nueva_col = col + dc
                
                # Verificar que la nueva posición sea válida, no visitada y transitable
                if (0 <= nueva_fila < self.alto and 
                    0 <= nueva_col < self.ancho and 
                    not visitado[nueva_fila][nueva_col] and
                    self.es_transitable_por_jugador(nueva_fila, nueva_col)):
                    
                    # Marcar como visitado y agregar a la cola para explorar después
                    visitado[nueva_fila][nueva_col] = True
                    cola.append((nueva_fila, nueva_col))
        
        # No se encontró camino
        return False
    
    def __repr__(self) -> str:
        """Representación del mapa."""
        return f"Mapa({self.ancho}x{self.alto}, inicio={self.posicion_inicio}, salidas={len(self.posiciones_salida)})"

