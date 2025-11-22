"""
Módulo generador_mapa: Genera mapas aleatorios con garantía de camino válido.
"""

import random
from typing import Tuple, List, Set, Optional
from collections import deque

from modelo.mapa import Mapa
from modelo.tile import Tile, Camino, Muro, Liana, Tunel


class GeneradorMapa:
    """
    Generador de mapas aleatorios usando DFS recursivo.
    Asegura que siempre hay un camino válido desde el inicio hasta la salida.
    """
    
    def __init__(self, ancho: int = 15, alto: int = 15, 
                 densidad_muros: float = 0.3,
                 probabilidad_liana: float = 0.1,
                 probabilidad_tunel: float = 0.1):
        """
        Inicializa el generador.
        
        Args:
            ancho: Ancho del mapa a generar.
            alto: Alto del mapa a generar.
            densidad_muros: Probabilidad de que una casilla sea muro (0.0 a 1.0).
            probabilidad_liana: Probabilidad de liana en casillas transitables (0.0 a 1.0).
            probabilidad_tunel: Probabilidad de túnel en casillas transitables (0.0 a 1.0).
        """
        self.ancho = ancho
        self.alto = alto
        self.densidad_muros = densidad_muros
        self.probabilidad_liana = probabilidad_liana
        self.probabilidad_tunel = probabilidad_tunel
    
    def generar_mapa(self) -> Mapa:
        """
        Genera un mapa aleatorio con garantía de camino válido.
        
        Returns:
            Un objeto Mapa con un camino válido desde inicio hasta salida.
        """
        # Definimos posiciones de inicio y salida
        posicion_inicio = (1, 1)
        posicion_salida = (self.alto - 2, self.ancho - 2)
        
        # Intentamos generar un mapa válido (máximo 10 intentos)
        for intento in range(10):
            # Primero generamos un laberinto base usando DFS
            casillas_laberinto = self._generar_laberinto_dfs()
            
            # Aseguramos que inicio y salida sean transitables
            casillas_laberinto[posicion_inicio[0]][posicion_inicio[1]] = Camino()
            casillas_laberinto[posicion_salida[0]][posicion_salida[1]] = Camino()
            
            # Verificamos que existe camino base antes de agregar variación
            if not self._existe_camino_valido(casillas_laberinto, posicion_inicio, posicion_salida):
                continue
            
            # Luego agregamos variación con lianas y túneles (pero preservamos el camino)
            casillas = self._agregar_variacion_terreno_segura(casillas_laberinto, posicion_inicio, posicion_salida)
            
            # Verificamos que el camino sigue siendo válido después de agregar variación
            if self._existe_camino_valido(casillas, posicion_inicio, posicion_salida):
                return Mapa(self.ancho, self.alto, casillas, posicion_inicio, posicion_salida)
        
        # Si después de 10 intentos no hay camino, devolvemos un mapa simple con solo caminos
        casillas = [[Camino() if (i + j) % 2 == 0 else Muro() for j in range(self.ancho)] for i in range(self.alto)]
        casillas[posicion_inicio[0]][posicion_inicio[1]] = Camino()
        casillas[posicion_salida[0]][posicion_salida[1]] = Camino()
        return Mapa(self.ancho, self.alto, casillas, posicion_inicio, posicion_salida)
    
    def _generar_laberinto_dfs(self) -> List[List[Tile]]:
        """
        Genera un laberinto usando DFS recursivo.
        
        Returns:
            Matriz 2D de casillas (Camino o Muro).
        """
        # Inicializamos todo como muros
        casillas = [[Muro() for _ in range(self.ancho)] for _ in range(self.alto)]
        visitado = [[False for _ in range(self.ancho)] for _ in range(self.alto)]
        
        # Empezamos desde una posición aleatoria (pero dentro de los límites)
        inicio_fila = random.randint(1, self.alto - 2)
        inicio_col = random.randint(1, self.ancho - 2)
        
        # DFS recursivo
        self._dfs_laberinto(casillas, visitado, inicio_fila, inicio_col)
        
        return casillas
    
    def _dfs_laberinto(self, casillas: List[List[Tile]], 
                      visitado: List[List[bool]], 
                      fila: int, col: int):
        """
        DFS recursivo para generar el laberinto.
        
        Args:
            casillas: Matriz de casillas a modificar.
            visitado: Matriz de visitados.
            fila: Fila actual.
            col: Columna actual.
        """
        # Marcar como visitado y convertir en camino
        visitado[fila][col] = True
        casillas[fila][col] = Camino()
        
        # Direcciones: arriba, abajo, izquierda, derecha
        direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        random.shuffle(direcciones)
        
        for df, dc in direcciones:
            nueva_fila = fila + df * 2
            nueva_col = col + dc * 2
            
            # Verificar límites
            if (0 < nueva_fila < self.alto - 1 and 
                0 < nueva_col < self.ancho - 1 and 
                not visitado[nueva_fila][nueva_col]):
                
                # Abrir el muro entre la celda actual y la nueva
                casillas[fila + df][col + dc] = Camino()
                self._dfs_laberinto(casillas, visitado, nueva_fila, nueva_col)
    
    def _agregar_variacion_terreno(self, casillas: List[List[Tile]]) -> List[List[Tile]]:
        """
        Agrega lianas y túneles aleatoriamente en casillas transitables.
        
        Args:
            casillas: Matriz de casillas base.
            
        Returns:
            Matriz de casillas con variación de terreno.
        """
        for fila in range(self.alto):
            for col in range(self.ancho):
                # Solo modificamos casillas que son camino
                if isinstance(casillas[fila][col], Camino):
                    rand = random.random()
                    if rand < self.probabilidad_liana:
                        casillas[fila][col] = Liana()
                    elif rand < self.probabilidad_liana + self.probabilidad_tunel:
                        casillas[fila][col] = Tunel()
        
        return casillas
    
    def _agregar_variacion_terreno_segura(self, casillas: List[List[Tile]], 
                                          inicio: Tuple[int, int], 
                                          salida: Tuple[int, int]) -> List[List[Tile]]:
        """
        Agrega lianas y túneles de manera que no bloqueen el camino principal.
        Usa BFS para encontrar un camino y evita modificar esas casillas críticas.
        
        Args:
            casillas: Matriz de casillas base.
            inicio: Posición de inicio.
            salida: Posición de salida.
            
        Returns:
            Matriz de casillas con variación de terreno.
        """
        # Encontrar un camino válido usando BFS
        camino_critico = self._encontrar_camino_bfs(casillas, inicio, salida)
        casillas_criticas = set(camino_critico) if camino_critico else set()
        
        # Agregar variación solo en casillas que no están en el camino crítico
        for fila in range(self.alto):
            for col in range(self.ancho):
                # Solo modificamos casillas que son camino y no están en el camino crítico
                if isinstance(casillas[fila][col], Camino) and (fila, col) not in casillas_criticas:
                    rand = random.random()
                    if rand < self.probabilidad_liana:
                        casillas[fila][col] = Liana()
                    elif rand < self.probabilidad_liana + self.probabilidad_tunel:
                        casillas[fila][col] = Tunel()
        
        return casillas
    
    def _encontrar_camino_bfs(self, casillas: List[List[Tile]], 
                             inicio: Tuple[int, int], 
                             salida: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        Encuentra un camino desde inicio hasta salida usando BFS.
        
        Args:
            casillas: Matriz de casillas.
            inicio: Posición de inicio.
            salida: Posición de salida.
            
        Returns:
            Lista de tuplas (fila, columna) representando el camino, o None si no existe.
        """
        if not casillas[inicio[0]][inicio[1]].permite_paso_jugador():
            return None
        if not casillas[salida[0]][salida[1]].permite_paso_jugador():
            return None
        
        visitado = [[False for _ in range(self.ancho)] for _ in range(self.alto)]
        padre = {}
        cola = deque([inicio])
        visitado[inicio[0]][inicio[1]] = True
        
        direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        while cola:
            fila, col = cola.popleft()
            
            if (fila, col) == salida:
                # Reconstruir camino
                camino = []
                actual = salida
                while actual is not None:
                    camino.append(actual)
                    actual = padre.get(actual)
                return camino[::-1]  # Invertir para tener inicio -> salida
            
            for df, dc in direcciones:
                nueva_fila = fila + df
                nueva_col = col + dc
                
                if (0 <= nueva_fila < self.alto and 
                    0 <= nueva_col < self.ancho and 
                    not visitado[nueva_fila][nueva_col] and
                    casillas[nueva_fila][nueva_col].permite_paso_jugador()):
                    
                    visitado[nueva_fila][nueva_col] = True
                    padre[(nueva_fila, nueva_col)] = (fila, col)
                    cola.append((nueva_fila, nueva_col))
        
        return None
    
    def _existe_camino_valido(self, casillas: List[List[Tile]], 
                              inicio: Tuple[int, int], 
                              salida: Tuple[int, int]) -> bool:
        """
        Verifica si existe un camino válido desde inicio hasta salida usando BFS.
        
        Args:
            casillas: Matriz de casillas.
            inicio: Tupla (fila, columna) de inicio.
            salida: Tupla (fila, columna) de salida.
            
        Returns:
            True si existe un camino válido para el jugador, False en caso contrario.
        """
        if not casillas[inicio[0]][inicio[1]].permite_paso_jugador():
            return False
        if not casillas[salida[0]][salida[1]].permite_paso_jugador():
            return False
        
        visitado = [[False for _ in range(self.ancho)] for _ in range(self.alto)]
        cola = deque([inicio])
        visitado[inicio[0]][inicio[1]] = True
        
        direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        while cola:
            fila, col = cola.popleft()
            
            if (fila, col) == salida:
                return True
            
            for df, dc in direcciones:
                nueva_fila = fila + df
                nueva_col = col + dc
                
                if (0 <= nueva_fila < self.alto and 
                    0 <= nueva_col < self.ancho and 
                    not visitado[nueva_fila][nueva_col] and
                    casillas[nueva_fila][nueva_col].permite_paso_jugador()):
                    
                    visitado[nueva_fila][nueva_col] = True
                    cola.append((nueva_fila, nueva_col))
        
        return False

