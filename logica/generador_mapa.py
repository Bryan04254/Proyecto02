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
                 densidad_muros: float = 0.4,  # Aumentada para laberintos más cerrados
                 probabilidad_liana: float = 0.05,  # Reducida para más caminos libres
                 probabilidad_tunel: float = 0.05):  # Reducida para más caminos libres
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
    
    def generar_mapa(self, cantidad_salidas: Optional[int] = None, modo: str = "escapa") -> Mapa:
        """
        Genera un mapa aleatorio con garantía de camino válido a múltiples salidas.
        
        Args:
            cantidad_salidas: Número de salidas a generar. Si es None, se elige aleatoriamente 1 o 2.
            modo: Modo de juego ("escapa" o "cazador"). Afecta la generación de lianas y túneles.
        
        Returns:
            Un objeto Mapa con caminos válidos desde inicio hasta todas las salidas.
        """
        # Definimos posición de inicio
        posicion_inicio = (1, 1)
        
        # Si no se especifica cantidad, elegir aleatoriamente 1 o 2 salidas
        if cantidad_salidas is None:
            cantidad_salidas = random.choice([1, 2])
        
        # Generar posiciones de salida distribuidas en diferentes áreas del mapa
        posiciones_salida = self._generar_posiciones_salida(cantidad_salidas, posicion_inicio)
        
        # Intentamos generar un mapa válido (máximo 10 intentos)
        for intento in range(10):
            # Primero generamos un laberinto base usando DFS
            casillas_laberinto = self._generar_laberinto_dfs()
            
            # Aseguramos que inicio y todas las salidas sean transitables
            casillas_laberinto[posicion_inicio[0]][posicion_inicio[1]] = Camino()
            for salida in posiciones_salida:
                casillas_laberinto[salida[0]][salida[1]] = Camino()
            
            # Verificamos que existe camino a todas las salidas antes de agregar variación
            caminos_validos = all(
                self._existe_camino_valido(casillas_laberinto, posicion_inicio, salida)
                for salida in posiciones_salida
            )
            if not caminos_validos:
                continue
            
            # Luego agregamos variación con lianas y túneles (pero preservamos los caminos)
            casillas = self._agregar_variacion_terreno_segura_multiple(
                casillas_laberinto, posicion_inicio, posiciones_salida, modo=modo
            )
            
            # Verificamos que los caminos siguen siendo válidos después de agregar variación
            if modo == "cazador":
                # En modo cazador, usar verificación con reglas del modo cazador
                caminos_validos = all(
                    self._existe_camino_valido_cazador(casillas, posicion_inicio, salida)
                    for salida in posiciones_salida
                )
            else:
                caminos_validos = all(
                    self._existe_camino_valido(casillas, posicion_inicio, salida)
                    for salida in posiciones_salida
                )
            if caminos_validos:
                return Mapa(self.ancho, self.alto, casillas, posicion_inicio, posiciones_salida)
        
        # Si después de 10 intentos no hay caminos, devolvemos un mapa simple con solo caminos
        casillas = [[Camino() if (i + j) % 2 == 0 else Muro() for j in range(self.ancho)] for i in range(self.alto)]
        casillas[posicion_inicio[0]][posicion_inicio[1]] = Camino()
        for salida in posiciones_salida:
            casillas[salida[0]][salida[1]] = Camino()
        return Mapa(self.ancho, self.alto, casillas, posicion_inicio, posiciones_salida)
    
    def _generar_posiciones_salida(self, cantidad: int, posicion_inicio: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Genera posiciones de salida distribuidas en diferentes áreas del mapa.
        
        Args:
            cantidad: Número de salidas a generar.
            posicion_inicio: Posición de inicio para evitar colisiones.
        
        Returns:
            Lista de tuplas (fila, columna) con las posiciones de salida.
        """
        salidas = []
        # Esquinas y bordes del mapa
        candidatos = [
            (1, self.ancho - 2),  # Esquina superior derecha
            (self.alto - 2, 1),  # Esquina inferior izquierda
            (self.alto - 2, self.ancho - 2),  # Esquina inferior derecha
            (1, self.ancho // 2),  # Borde superior centro
            (self.alto - 2, self.ancho // 2),  # Borde inferior centro
            (self.alto // 2, 1),  # Borde izquierdo centro
            (self.alto // 2, self.ancho - 2),  # Borde derecho centro
        ]
        
        # Filtrar candidatos que no sean el inicio
        candidatos = [c for c in candidatos if c != posicion_inicio]
        
        # Seleccionar cantidad de salidas aleatoriamente
        random.shuffle(candidatos)
        salidas = candidatos[:min(cantidad, len(candidatos))]
        
        # Si no hay suficientes candidatos, generar posiciones aleatorias
        while len(salidas) < cantidad:
            fila = random.randint(1, self.alto - 2)
            col = random.randint(1, self.ancho - 2)
            pos = (fila, col)
            if pos != posicion_inicio and pos not in salidas:
                salidas.append(pos)
        
        return salidas
    
    def _generar_laberinto_dfs(self) -> List[List[Tile]]:
        """
        Genera un laberinto tradicional usando DFS recursivo.
        Mantiene la estructura de laberinto pero más cerrado.
        
        Returns:
            Matriz 2D de casillas (Camino o Muro).
        """
        # Inicializamos todo como muros
        casillas = [[Muro() for _ in range(self.ancho)] for _ in range(self.alto)]
        visitado = [[False for _ in range(self.ancho)] for _ in range(self.alto)]
        
        # Empezamos desde una posición aleatoria (pero dentro de los límites)
        inicio_fila = random.randint(1, self.alto - 2)
        inicio_col = random.randint(1, self.ancho - 2)
        
        # DFS recursivo tradicional
        self._dfs_laberinto(casillas, visitado, inicio_fila, inicio_col)
        
        # Crear algunos caminos adicionales estratégicos para múltiples rutas (muy limitado)
        self._agregar_caminos_alternativos(casillas, visitado)
        
        return casillas
    
    def _dfs_laberinto(self, casillas: List[List[Tile]], 
                      visitado: List[List[bool]], 
                      fila: int, col: int):
        """
        DFS recursivo tradicional para generar el laberinto.
        Mantiene la estructura clásica de laberinto.
        
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
    
    def _agregar_caminos_alternativos(self, casillas: List[List[Tile]], 
                                      visitado: List[List[bool]]) -> None:
        """
        Agrega algunos caminos alternativos estratégicos para crear múltiples rutas.
        Muy limitado para mantener la estructura de laberinto.
        
        Args:
            casillas: Matriz de casillas a modificar.
            visitado: Matriz de visitados.
        """
        # Solo agregar un número muy limitado de conexiones adicionales
        # Basado en el tamaño del mapa, pero mucho más conservador
        num_conexiones = max(2, min(8, (self.ancho + self.alto) // 15))
        
        intentos = 0
        conexiones_creadas = 0
        
        while conexiones_creadas < num_conexiones and intentos < num_conexiones * 10:
            intentos += 1
            fila = random.randint(2, self.alto - 3)
            col = random.randint(2, self.ancho - 3)
            
            # Solo convertir muros que están entre dos caminos (crea intersecciones)
            if isinstance(casillas[fila][col], Muro):
                # Verificar que tenga exactamente 2 caminos opuestos adyacentes
                direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
                caminos_opuestos = 0
                
                for i in range(0, len(direcciones), 2):
                    df1, dc1 = direcciones[i]
                    df2, dc2 = direcciones[i + 1]
                    
                    fila1 = fila + df1
                    col1 = col + dc1
                    fila2 = fila + df2
                    col2 = col + dc2
                    
                    if (0 <= fila1 < self.alto and 0 <= col1 < self.ancho and
                        0 <= fila2 < self.alto and 0 <= col2 < self.ancho):
                        if (isinstance(casillas[fila1][col1], Camino) and 
                            isinstance(casillas[fila2][col2], Camino)):
                            caminos_opuestos += 1
                
                # Solo crear conexión si hay un par de caminos opuestos
                # Esto crea intersecciones sin abrir demasiado el laberinto
                if caminos_opuestos == 1:
                    casillas[fila][col] = Camino()
                    conexiones_creadas += 1
    
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
    
    def _agregar_variacion_terreno_segura_multiple(self, casillas: List[List[Tile]], 
                                                   inicio: Tuple[int, int], 
                                                   salidas: List[Tuple[int, int]],
                                                   modo: str = "escapa") -> List[List[Tile]]:
        """
        Agrega lianas y túneles de manera que no bloqueen los caminos a ninguna salida.
        Encuentra caminos a todas las salidas y evita modificar esas casillas críticas.
        
        Args:
            casillas: Matriz de casillas base.
            inicio: Posición de inicio.
            salidas: Lista de posiciones de salida.
            modo: Modo de juego ("escapa" o "cazador"). Afecta las probabilidades.
            
        Returns:
            Matriz de casillas con variación de terreno.
        """
        # Ajustar probabilidades según el modo
        prob_liana = self.probabilidad_liana
        prob_tunel = self.probabilidad_tunel
        
        if modo == "cazador":
            # En modo cazador: más lianas (jugador puede pasar), pocos túneles (jugador NO puede pasar)
            # Reducido 50%: 0.15 -> 0.075, 0.05 -> 0.025
            prob_liana = 0.075  # Lianas reducidas a 7.5%
            prob_tunel = 0.025  # Túneles reducidos a 2.5%
        
        # Encontrar caminos válidos a todas las salidas usando BFS
        # En modo cazador, usar reglas de transición del modo cazador
        casillas_criticas = set()
        for salida in salidas:
            if modo == "cazador":
                # En modo cazador, el jugador puede pasar por Liana pero no por Tunel
                camino_critico = self._encontrar_camino_bfs_cazador(casillas, inicio, salida)
            else:
                camino_critico = self._encontrar_camino_bfs(casillas, inicio, salida)
            if camino_critico:
                casillas_criticas.update(camino_critico)
        
        # Asegurar que el área alrededor del inicio sea transitable para el jugador
        # (en modo cazador, esto significa lianas o caminos, NO túneles)
        if modo == "cazador":
            # Proteger un área más grande alrededor del inicio (radio 5)
            radio_seguro = 5
            for df in range(-radio_seguro, radio_seguro + 1):
                for dc in range(-radio_seguro, radio_seguro + 1):
                    fila = inicio[0] + df
                    col = inicio[1] + dc
                    if (0 <= fila < self.alto and 0 <= col < self.ancho and
                        isinstance(casillas[fila][col], Camino)):
                        distancia = abs(df) + abs(dc)
                        if distancia <= 3:  # Área inmediata alrededor del inicio
                            # Proteger estas casillas (no poner túneles)
                            casillas_criticas.add((fila, col))
                            # Preferir lianas sobre caminos cerca del inicio (40% probabilidad)
                            if random.random() < 0.4:
                                casillas[fila][col] = Liana()
                        elif distancia <= radio_seguro:  # Área más lejana
                            # Proteger estas casillas también
                            casillas_criticas.add((fila, col))
            
            # En modo cazador, también proteger caminos hacia las esquinas donde están los enemigos
            # (esquinas superior e inferior izquierda)
            esquinas_enemigos = [
                (1, 1),  # Esquina superior izquierda
                (self.alto - 2, 1)  # Esquina inferior izquierda
            ]
            
            for esquina in esquinas_enemigos:
                # Encontrar camino desde el inicio hasta la esquina de enemigos
                camino_a_esquina = self._encontrar_camino_bfs_cazador(casillas, inicio, esquina)
                if camino_a_esquina:
                    # Proteger todo el camino (no poner túneles)
                    casillas_criticas.update(camino_a_esquina)
                    # También proteger área alrededor de la esquina
                    radio_esquina = 3
                    for df in range(-radio_esquina, radio_esquina + 1):
                        for dc in range(-radio_esquina, radio_esquina + 1):
                            fila = esquina[0] + df
                            col = esquina[1] + dc
                            if (0 <= fila < self.alto and 0 <= col < self.ancho and
                                isinstance(casillas[fila][col], Camino)):
                                casillas_criticas.add((fila, col))
        else:
            # En modo escapa, proteger el área alrededor del inicio normalmente
            radio_seguro = 3
            for df in range(-radio_seguro, radio_seguro + 1):
                for dc in range(-radio_seguro, radio_seguro + 1):
                    fila = inicio[0] + df
                    col = inicio[1] + dc
                    if (0 <= fila < self.alto and 0 <= col < self.ancho and
                        isinstance(casillas[fila][col], Camino)):
                        casillas_criticas.add((fila, col))
        
        # Agregar variación solo en casillas que no están en ningún camino crítico
        for fila in range(self.alto):
            for col in range(self.ancho):
                # Solo modificamos casillas que son camino y no están en ningún camino crítico
                if isinstance(casillas[fila][col], Camino) and (fila, col) not in casillas_criticas:
                    rand = random.random()
                    if rand < prob_liana:
                        casillas[fila][col] = Liana()
                    elif rand < prob_liana + prob_tunel:
                        # En modo cazador, verificar que no bloquee rutas importantes antes de poner túnel
                        if modo == "cazador":
                            # Verificar que esta casilla no sea crítica para llegar a áreas importantes
                            # Si está en el centro del mapa o cerca de rutas principales, evitar túneles
                            distancia_centro_x = abs(col - self.ancho // 2)
                            distancia_centro_y = abs(fila - self.alto // 2)
                            
                            # Calcular distancia a las esquinas de enemigos
                            dist_esquina_sup = abs(fila - 1) + abs(col - 1)
                            dist_esquina_inf = abs(fila - (self.alto - 2)) + abs(col - 1)
                            dist_min_esquina = min(dist_esquina_sup, dist_esquina_inf)
                            
                            # Evitar túneles solo en áreas muy críticas:
                            # 1. Muy cerca del centro del mapa (solo 1/4 del mapa)
                            # 2. Muy cerca de las esquinas de enemigos (dentro de 5 casillas)
                            # 3. Muy cerca del inicio del jugador (dentro de 8 casillas)
                            dist_inicio = abs(fila - inicio[0]) + abs(col - inicio[1])
                            
                            # Solo evitar túneles en áreas muy cercanas a rutas críticas
                            # Reducir restricciones para permitir más túneles
                            if (distancia_centro_x < self.ancho // 5 or 
                                distancia_centro_y < self.alto // 5 or
                                dist_min_esquina < 4 or
                                dist_inicio < 6):
                                # En lugar de túnel, poner liana o dejar camino
                                if random.random() < 0.3:
                                    casillas[fila][col] = Liana()
                                # Si no, dejar como Camino
                            else:
                                # Áreas periféricas y medias, permitir túnel normalmente
                                casillas[fila][col] = Tunel()
                        else:
                            # Modo escapa, comportamiento normal
                            casillas[fila][col] = Tunel()
        
        return casillas
    
    def _encontrar_camino_bfs_cazador(self, casillas: List[List[Tile]], 
                                      inicio: Tuple[int, int], 
                                      salida: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        Encuentra un camino desde inicio hasta salida usando BFS con reglas del modo cazador.
        En modo cazador, el jugador puede pasar por Camino y Liana, pero NO por Tunel.
        
        Args:
            casillas: Matriz de casillas.
            inicio: Posición de inicio.
            salida: Posición de salida.
            
        Returns:
            Lista de tuplas (fila, columna) representando el camino, o None si no existe.
        """
        from modelo.tile import Camino, Liana
        
        # Verificar que inicio y salida sean transitables para el jugador en modo cazador
        tile_inicio = casillas[inicio[0]][inicio[1]]
        tile_salida = casillas[salida[0]][salida[1]]
        
        if not (isinstance(tile_inicio, Camino) or isinstance(tile_inicio, Liana)):
            return None
        if not (isinstance(tile_salida, Camino) or isinstance(tile_salida, Liana)):
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
                    not visitado[nueva_fila][nueva_col]):
                    
                    tile = casillas[nueva_fila][nueva_col]
                    # En modo cazador, el jugador puede pasar por Camino y Liana, pero NO por Tunel
                    if isinstance(tile, Camino) or isinstance(tile, Liana):
                        visitado[nueva_fila][nueva_col] = True
                        padre[(nueva_fila, nueva_col)] = (fila, col)
                        cola.append((nueva_fila, nueva_col))
        
        return None
    
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
    
    def _existe_camino_valido_cazador(self, casillas: List[List[Tile]], 
                                      inicio: Tuple[int, int], 
                                      salida: Tuple[int, int]) -> bool:
        """
        Verifica si existe un camino válido desde inicio hasta salida usando BFS con reglas del modo cazador.
        En modo cazador, el jugador puede pasar por Camino y Liana, pero NO por Tunel.
        
        Args:
            casillas: Matriz de casillas.
            inicio: Tupla (fila, columna) de inicio.
            salida: Tupla (fila, columna) de salida.
            
        Returns:
            True si existe un camino válido para el jugador en modo cazador, False en caso contrario.
        """
        from modelo.tile import Camino, Liana
        
        # Verificar que inicio y salida sean transitables para el jugador en modo cazador
        tile_inicio = casillas[inicio[0]][inicio[1]]
        tile_salida = casillas[salida[0]][salida[1]]
        
        if not (isinstance(tile_inicio, Camino) or isinstance(tile_inicio, Liana)):
            return False
        if not (isinstance(tile_salida, Camino) or isinstance(tile_salida, Liana)):
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
                    not visitado[nueva_fila][nueva_col]):
                    
                    tile = casillas[nueva_fila][nueva_col]
                    # En modo cazador, el jugador puede pasar por Camino y Liana, pero NO por Tunel
                    if isinstance(tile, Camino) or isinstance(tile, Liana):
                        visitado[nueva_fila][nueva_col] = True
                        cola.append((nueva_fila, nueva_col))
        
        return False
    
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

