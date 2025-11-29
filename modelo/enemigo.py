"""
Módulo enemigo: Define la clase Enemigo con movimiento e IA.
"""

from typing import Tuple, Optional, List
from enum import Enum

# Importaciones que funcionan tanto como módulo como ejecutado directamente
try:
    from .mapa import Mapa
    from .jugador import Jugador
except ImportError:
    # Si falla la importación relativa, intentar absoluta
    from modelo.mapa import Mapa
    from modelo.jugador import Jugador


class EstadoEnemigo(Enum):
    """Estados posibles de un enemigo."""
    EN_SPAWN = "en_spawn"  # Esperando en el spawn
    SALIENDO_SPAWN = "saliendo_spawn"  # Saliendo del spawn
    ACTIVO = "activo"
    MUERTO = "muerto"
    ESPERANDO_RESPAWN = "esperando_respawn"


class Enemigo:
    """
    Clase que representa a un enemigo/cazador en el juego.
    
    Los enemigos pueden perseguir o huir del jugador según el modo de juego.
    """
    
    def __init__(self, fila: int, columna: int, velocidad: float = 1.0, 
                 tiempo_respawn: float = 10.0, en_spawn: bool = False):
        """
        Inicializa un enemigo.
        
        Args:
            fila: Fila inicial del enemigo.
            columna: Columna inicial del enemigo.
            velocidad: Velocidad de movimiento (movimientos por segundo).
            tiempo_respawn: Tiempo en segundos antes de reaparecer después de morir.
            en_spawn: Si True, el enemigo comienza en el spawn.
        """
        # Posición del enemigo en el mapa
        self.fila = fila
        self.columna = columna
        
        # Sistema de velocidad: controla qué tan rápido se mueve el enemigo
        # velocidad = movimientos por segundo (ej: 1.0 = 1 movimiento/segundo)
        self.velocidad = velocidad
        self.tiempo_respawn = tiempo_respawn  # Tiempo antes de reaparecer después de morir
        
        # Estado inicial: puede empezar en spawn o activo
        self.estado = EstadoEnemigo.EN_SPAWN if en_spawn else EstadoEnemigo.ACTIVO
        self.tiempo_restante_respawn = 0.0  # Contador para respawn
        self.mapa: Optional[Mapa] = None  # Referencia al mapa (se asigna en actualizar)
        
        # Control de velocidad de movimiento (temporizador)
        # Evita que el enemigo se mueva demasiado rápido
        self.tiempo_desde_ultimo_movimiento = 0.0  # Tiempo acumulado desde último movimiento
        # Calcular tiempo entre movimientos basado en la velocidad
        # Si velocidad = 1.0, entonces tiempo_entre_movimientos = 1.0 segundo
        self.tiempo_entre_movimientos = 1.0 / velocidad if velocidad > 0 else 1.0
        
        # Control de salida del spawn (sistema de spawn gradual)
        self.tiempo_en_spawn = 0.0  # Tiempo acumulado en el spawn
        self.tiempo_espera_spawn = 2.0  # Segundos esperando en spawn antes de salir
    
    def obtener_posicion(self) -> Tuple[int, int]:
        """
        Obtiene la posición actual del enemigo.
        
        Returns:
            Tupla (fila, columna) con la posición actual.
        """
        return (self.fila, self.columna)
    
    def mover_arriba(self, mapa: Mapa, modo: str = "escapa") -> bool:
        """
        Mueve al enemigo hacia arriba (disminuye fila).
        
        Args:
            mapa: Mapa en el que se mueve el enemigo.
            modo: Modo de juego ("escapa" o "cazador").
            
        Returns:
            True si el movimiento fue exitoso, False en caso contrario.
        """
        return self._mover(mapa, self.fila - 1, self.columna, modo)
    
    def mover_abajo(self, mapa: Mapa, modo: str = "escapa") -> bool:
        """
        Mueve al enemigo hacia abajo (aumenta fila).
        
        Args:
            mapa: Mapa en el que se mueve el enemigo.
            modo: Modo de juego ("escapa" o "cazador").
            
        Returns:
            True si el movimiento fue exitoso, False en caso contrario.
        """
        return self._mover(mapa, self.fila + 1, self.columna, modo)
    
    def mover_izquierda(self, mapa: Mapa, modo: str = "escapa") -> bool:
        """
        Mueve al enemigo hacia la izquierda (disminuye columna).
        
        Args:
            mapa: Mapa en el que se mueve el enemigo.
            modo: Modo de juego ("escapa" o "cazador").
            
        Returns:
            True si el movimiento fue exitoso, False en caso contrario.
        """
        return self._mover(mapa, self.fila, self.columna - 1, modo)
    
    def mover_derecha(self, mapa: Mapa, modo: str = "escapa") -> bool:
        """
        Mueve al enemigo hacia la derecha (aumenta columna).
        
        Args:
            mapa: Mapa en el que se mueve el enemigo.
            modo: Modo de juego ("escapa" o "cazador").
            
        Returns:
            True si el movimiento fue exitoso, False en caso contrario.
        """
        return self._mover(mapa, self.fila, self.columna + 1, modo)
    
    def _mover(self, mapa: Mapa, nueva_fila: int, nueva_col: int, modo: str = "escapa") -> bool:
        """
        Método interno que realiza el movimiento del enemigo.
        
        Valida la posición y verifica que la casilla sea transitable según
        las reglas del modo de juego (en modo cazador, las reglas son diferentes).
        
        Args:
            mapa: Mapa en el que se mueve el enemigo.
            nueva_fila: Nueva fila destino.
            nueva_col: Nueva columna destino.
            modo: Modo de juego ("escapa" o "cazador").
                  - "escapa": Enemigos pueden pasar por Camino y Liana, NO por Tunel
                  - "cazador": Enemigos pueden pasar por Camino y Tunel, NO por Liana
            
        Returns:
            True si el movimiento fue exitoso, False en caso contrario.
        """
        # Validar que la nueva posición esté dentro de los límites del mapa
        if not mapa.es_posicion_valida(nueva_fila, nueva_col):
            return False
        
        # Verificar si la casilla permite el paso del enemigo
        # Las reglas de transición varían según el modo de juego
        if not mapa.es_transitable_por_enemigo(nueva_fila, nueva_col, modo=modo):
            return False
        
        # Realizar el movimiento (actualizar posición)
        self.fila = nueva_fila
        self.columna = nueva_col
        return True
    
    def matar(self) -> None:
        """
        Mata al enemigo y lo pone en estado de respawn.
        
        Cuando un enemigo es eliminado (por ejemplo, por una trampa),
        cambia su estado a MUERTO e inicia el temporizador de respawn.
        """
        self.estado = EstadoEnemigo.MUERTO
        # Iniciar temporizador de respawn (por defecto 10 segundos)
        self.tiempo_restante_respawn = self.tiempo_respawn
    
    def esta_vivo(self) -> bool:
        """
        Verifica si el enemigo está vivo (activo, en spawn o saliendo del spawn).
        
        Returns:
            True si está vivo, False en caso contrario.
        """
        return self.estado in (EstadoEnemigo.ACTIVO, EstadoEnemigo.EN_SPAWN, EstadoEnemigo.SALIENDO_SPAWN)
    
    def esta_muerto(self) -> bool:
        """
        Verifica si el enemigo está muerto.
        
        Returns:
            True si está muerto, False en caso contrario.
        """
        return self.estado == EstadoEnemigo.MUERTO
    
    def actualizar(self, mapa: Mapa, jugador: Jugador, delta_tiempo: float, 
                   modo: str, posicion_spawn: Optional[Tuple[int, int]] = None) -> None:
        """
        Actualiza el estado del enemigo (respawn, movimiento según modo).
        
        Args:
            mapa: Mapa del juego.
            jugador: Jugador del juego.
            delta_tiempo: Tiempo transcurrido desde la última actualización (segundos).
            modo: Modo de juego ("escapa" o "cazador").
            posicion_spawn: Posición del spawn (fila, columna). Si es None, no hay spawn.
        """
        # Guardar referencia al mapa para uso en otros métodos
        self.mapa = mapa
        
        # Máquina de estados: manejar cada estado del enemigo
        # ===================================================
        
        # Estado: MUERTO - Esperando respawn
        if self.estado == EstadoEnemigo.MUERTO:
            # Decrementar temporizador de respawn
            self.tiempo_restante_respawn -= delta_tiempo
            # Si el temporizador llegó a 0, hacer respawn
            if self.tiempo_restante_respawn <= 0:
                self._respawn(mapa, posicion_spawn)
        
        # Estado: EN_SPAWN - Esperando en el punto de spawn
        elif self.estado == EstadoEnemigo.EN_SPAWN:
            if posicion_spawn:
                # Asegurar que el enemigo esté en la posición de spawn
                if self.obtener_posicion() != posicion_spawn:
                    self.fila, self.columna = posicion_spawn
                
                # Esperar un tiempo antes de salir (sistema de spawn gradual)
                self.tiempo_en_spawn += delta_tiempo
                if self.tiempo_en_spawn >= self.tiempo_espera_spawn:
                    # Cambiar a estado de salida del spawn
                    self.estado = EstadoEnemigo.SALIENDO_SPAWN
                    self.tiempo_en_spawn = 0.0
            else:
                # Si no hay spawn definido, activar directamente
                self.estado = EstadoEnemigo.ACTIVO
        
        # Estado: SALIENDO_SPAWN - Intentando salir del punto de spawn
        elif self.estado == EstadoEnemigo.SALIENDO_SPAWN:
            if posicion_spawn and self.obtener_posicion() == posicion_spawn:
                # Intentar salir del spawn moviéndose hacia una casilla adyacente válida
                self._salir_del_spawn(mapa, posicion_spawn)
            else:
                # Ya salió del spawn, cambiar a activo
                self.estado = EstadoEnemigo.ACTIVO
        
        # Estado: ACTIVO - Enemigo activo, puede moverse
        elif self.estado == EstadoEnemigo.ACTIVO:
            # Control de velocidad: acumular tiempo desde último movimiento
            self.tiempo_desde_ultimo_movimiento += delta_tiempo
            
            # Solo mover si ha pasado el tiempo suficiente según la velocidad
            # Esto evita que el enemigo se mueva demasiado rápido
            if self.tiempo_desde_ultimo_movimiento >= self.tiempo_entre_movimientos:
                # Ejecutar IA según el modo de juego
                if modo == "escapa":
                    # En modo escapa: perseguir al jugador
                    self._perseguir_jugador(mapa, jugador)
                elif modo == "cazador":
                    # En modo cazador: buscar la salida (los enemigos huyen)
                    self._buscar_salida(mapa, jugador)
                
                # Resetear temporizador de movimiento
                self.tiempo_desde_ultimo_movimiento = 0.0
    
    def _respawn(self, mapa: Mapa, posicion_spawn: Optional[Tuple[int, int]] = None) -> None:
        """
        Hace que el enemigo reaparezca en el spawn o en una posición válida.
        
        Args:
            mapa: Mapa del juego.
            posicion_spawn: Posición del spawn. Si es None, busca posición aleatoria.
        """
        if posicion_spawn:
            # Respawnear en el spawn
            self.fila, self.columna = posicion_spawn
            self.estado = EstadoEnemigo.EN_SPAWN
            self.tiempo_en_spawn = 0.0
            self.tiempo_restante_respawn = 0.0
        else:
            # Buscar una posición válida aleatoria (comportamiento antiguo)
            import random
            intentos = 0
            max_intentos = 100
            
            while intentos < max_intentos:
                fila = random.randint(0, mapa.alto - 1)
                columna = random.randint(0, mapa.ancho - 1)
                
                if mapa.es_transitable_por_enemigo(fila, columna):
                    self.fila = fila
                    self.columna = columna
                    self.estado = EstadoEnemigo.ACTIVO
                    self.tiempo_restante_respawn = 0.0
                    return
                
                intentos += 1
            
            # Si no se encuentra posición, intentar en la posición inicial del mapa
            inicio = mapa.obtener_posicion_inicio_jugador()
            if mapa.es_transitable_por_enemigo(inicio[0], inicio[1]):
                self.fila = inicio[0]
                self.columna = inicio[1]
                self.estado = EstadoEnemigo.ACTIVO
                self.tiempo_restante_respawn = 0.0
    
    def _salir_del_spawn(self, mapa: Mapa, posicion_spawn: Tuple[int, int]) -> None:
        """
        Intenta salir del spawn moviéndose a una casilla adyacente válida.
        
        Args:
            mapa: Mapa del juego.
            posicion_spawn: Posición del spawn.
        """
        spawn_fila, spawn_col = posicion_spawn
        
        # Intentar moverse en las 4 direcciones para salir del spawn
        direcciones = [
            ("arriba", -1, 0),
            ("abajo", 1, 0),
            ("izquierda", 0, -1),
            ("derecha", 0, 1)
        ]
        
        for nombre, df, dc in direcciones:
            nueva_fila = spawn_fila + df
            nueva_col = spawn_col + dc
            
            if (mapa.es_posicion_valida(nueva_fila, nueva_col) and
                mapa.es_transitable_por_enemigo(nueva_fila, nueva_col)):
                # Mover en esa dirección
                if nombre == "arriba":
                    self.mover_arriba(mapa)
                elif nombre == "abajo":
                    self.mover_abajo(mapa)
                elif nombre == "izquierda":
                    self.mover_izquierda(mapa)
                elif nombre == "derecha":
                    self.mover_derecha(mapa)
                return
    
    def _perseguir_jugador(self, mapa: Mapa, jugador: Jugador) -> None:
        """
        Mueve al enemigo hacia el jugador usando pathfinding inteligente (modo escapa).
        
        Args:
            mapa: Mapa del juego.
            jugador: Jugador a perseguir.
        """
        # Obtener posiciones actuales
        jugador_pos = jugador.obtener_posicion()
        enemigo_pos = self.obtener_posicion()
        
        # Usar pathfinding BFS (Breadth-First Search) para encontrar el camino más corto al jugador
        # Esto hace que el enemigo sea más inteligente y eficiente en la persecución
        camino = self._encontrar_camino_bfs_escapa(mapa, enemigo_pos, jugador_pos)
        
        if camino and len(camino) >= 2:
            # El camino contiene: [posición_actual, siguiente_paso, ..., destino]
            # [0] es la posición actual del enemigo
            # [1] es el siguiente paso hacia el jugador
            siguiente_paso = camino[1]
            # Convertir la posición del siguiente paso a una dirección (arriba, abajo, etc.)
            mejor_movimiento = self._obtener_direccion_hacia(enemigo_pos, siguiente_paso)
        else:
            # Si BFS no encuentra camino (fallback), usar método simple basado en distancia Manhattan
            # Esto puede pasar si hay obstáculos o el mapa está bloqueado
            mejor_movimiento = self._perseguir_jugador_simple(mapa, jugador_pos, enemigo_pos)
        
        # Aplicar el movimiento calculado
        if mejor_movimiento:
            if mejor_movimiento == "arriba":
                self.mover_arriba(mapa)
            elif mejor_movimiento == "abajo":
                self.mover_abajo(mapa)
            elif mejor_movimiento == "izquierda":
                self.mover_izquierda(mapa)
            elif mejor_movimiento == "derecha":
                self.mover_derecha(mapa)
    
    def _encontrar_camino_bfs_escapa(self, mapa: Mapa, inicio: Tuple[int, int], destino: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        Encuentra el camino más corto desde inicio hasta destino usando BFS (modo escapa).
        Los enemigos pueden pasar por Camino y Liana, pero no por Tunel.
        
        Args:
            mapa: Mapa del juego.
            inicio: Posición inicial (fila, columna).
            destino: Posición destino (fila, columna).
            
        Returns:
            Lista de posiciones desde inicio hasta destino, o None si no hay camino.
        """
        from collections import deque
        
        if inicio == destino:
            return [inicio]
        
        # Verificar que inicio y destino sean transitables para enemigos en modo escapa
        if not mapa.es_transitable_por_enemigo(inicio[0], inicio[1], modo="escapa"):
            return None
        if not mapa.es_transitable_por_enemigo(destino[0], destino[1], modo="escapa"):
            return None
        
        # Inicializar estructuras de datos para BFS
        visitado = [[False for _ in range(mapa.ancho)] for _ in range(mapa.alto)]  # Matriz de visitados
        padre = {}  # Diccionario para reconstruir el camino: {hijo: padre}
        cola = deque([inicio])  # Cola FIFO para BFS
        visitado[inicio[0]][inicio[1]] = True  # Marcar inicio como visitado
        
        # Direcciones posibles: arriba, abajo, izquierda, derecha
        direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        # BFS: explorar nivel por nivel hasta encontrar el destino
        while cola:
            fila, col = cola.popleft()  # Obtener siguiente posición de la cola
            
            # Si llegamos al destino, reconstruir y retornar el camino
            if (fila, col) == destino:
                # Reconstruir camino desde destino hasta inicio usando el diccionario padre
                camino = []
                actual = destino
                while actual is not None:
                    camino.append(actual)
                    actual = padre.get(actual)  # Obtener padre de la posición actual
                # Invertir para tener el camino desde inicio -> destino
                return camino[::-1]
            
            # Explorar vecinos (4 direcciones)
            for df, dc in direcciones:
                nueva_fila = fila + df
                nueva_col = col + dc
                
                # Verificar que la nueva posición sea válida y transitable
                if (0 <= nueva_fila < mapa.alto and 
                    0 <= nueva_col < mapa.ancho and 
                    not visitado[nueva_fila][nueva_col] and
                    mapa.es_transitable_por_enemigo(nueva_fila, nueva_col, modo="escapa")):
                    
                    # Marcar como visitado y agregar a la cola
                    visitado[nueva_fila][nueva_col] = True
                    padre[(nueva_fila, nueva_col)] = (fila, col)  # Guardar relación padre-hijo
                    cola.append((nueva_fila, nueva_col))
        
        # No se encontró camino
        return None
    
    def _perseguir_jugador_simple(self, mapa: Mapa, jugador_pos: Tuple[int, int], enemigo_pos: Tuple[int, int]) -> Optional[str]:
        """
        Método simple de persecución como fallback (usa distancia de Manhattan).
        
        Args:
            mapa: Mapa del juego.
            jugador_pos: Posición del jugador.
            enemigo_pos: Posición actual del enemigo.
            
        Returns:
            Nombre de la dirección a mover, o None si no hay movimiento válido.
        """
        # Calcular distancia de Manhattan
        distancia_actual = abs(jugador_pos[0] - enemigo_pos[0]) + abs(jugador_pos[1] - enemigo_pos[1])
        
        # Probar movimientos en las 4 direcciones y elegir el que más reduzca la distancia
        mejor_movimiento = None
        menor_distancia = distancia_actual
        
        movimientos = [
            ("arriba", self.mover_arriba),
            ("abajo", self.mover_abajo),
            ("izquierda", self.mover_izquierda),
            ("derecha", self.mover_derecha)
        ]
        
        for nombre, movimiento_func in movimientos:
            # Guardar posición actual
            fila_original = self.fila
            col_original = self.columna
            
            # Intentar movimiento
            if movimiento_func(mapa):
                # Calcular nueva distancia
                nueva_pos = self.obtener_posicion()
                nueva_distancia = abs(jugador_pos[0] - nueva_pos[0]) + abs(jugador_pos[1] - nueva_pos[1])
                
                if nueva_distancia < menor_distancia:
                    menor_distancia = nueva_distancia
                    mejor_movimiento = nombre
                
                # Revertir movimiento para probar el siguiente
                self.fila = fila_original
                self.columna = col_original
        
        return mejor_movimiento
    
    def _huir_del_jugador(self, mapa: Mapa, jugador: Jugador) -> None:
        """
        Mueve al enemigo alejándose del jugador (modo cazador).
        
        Args:
            mapa: Mapa del juego.
            jugador: Jugador del que huir.
        """
        jugador_pos = jugador.obtener_posicion()
        enemigo_pos = self.obtener_posicion()
        
        # Calcular distancia de Manhattan actual
        distancia_actual = abs(jugador_pos[0] - enemigo_pos[0]) + abs(jugador_pos[1] - enemigo_pos[1])
        
        # Probar movimientos en las 4 direcciones y elegir el que más aumente la distancia
        mejor_movimiento = None
        mayor_distancia = distancia_actual
        
        movimientos = [
            ("arriba", self.mover_arriba),
            ("abajo", self.mover_abajo),
            ("izquierda", self.mover_izquierda),
            ("derecha", self.mover_derecha)
        ]
        
        for nombre, movimiento_func in movimientos:
            # Guardar posición actual
            fila_original = self.fila
            col_original = self.columna
            
            # Intentar movimiento
            if movimiento_func(mapa):
                # Calcular nueva distancia
                nueva_pos = self.obtener_posicion()
                nueva_distancia = abs(jugador_pos[0] - nueva_pos[0]) + abs(jugador_pos[1] - nueva_pos[1])
                
                if nueva_distancia > mayor_distancia:
                    mayor_distancia = nueva_distancia
                    mejor_movimiento = nombre
                
                # Revertir movimiento para probar el siguiente
                self.fila = fila_original
                self.columna = col_original
        
        # Aplicar el mejor movimiento
        if mejor_movimiento:
            if mejor_movimiento == "arriba":
                self.mover_arriba(mapa)
            elif mejor_movimiento == "abajo":
                self.mover_abajo(mapa)
            elif mejor_movimiento == "izquierda":
                self.mover_izquierda(mapa)
            elif mejor_movimiento == "derecha":
                self.mover_derecha(mapa)
    
    def _buscar_salida(self, mapa: Mapa, jugador: Optional['Jugador'] = None) -> None:
        """
        Mueve al enemigo hacia la salida más cercana usando pathfinding inteligente (modo cazador).
        Si el jugador está cerca, intenta evitarlo mientras se dirige a la salida.
        
        Args:
            mapa: Mapa del juego.
            jugador: Jugador (opcional) para evitar si está cerca.
        """
        posiciones_salida = mapa.obtener_posiciones_salida()
        if not posiciones_salida:
            return
        
        enemigo_pos = self.obtener_posicion()
        
        # Encontrar la salida más cercana usando pathfinding
        salida_mas_cercana = None
        camino_mas_corto = None
        menor_longitud = float('inf')
        
        for salida in posiciones_salida:
            camino = self._encontrar_camino_bfs(mapa, enemigo_pos, salida)
            if camino and len(camino) < menor_longitud:
                menor_longitud = len(camino)
                salida_mas_cercana = salida
                camino_mas_corto = camino
        
        if not salida_mas_cercana or not camino_mas_corto or len(camino_mas_corto) < 2:
            # Si no hay camino, usar método simple como fallback
            self._buscar_salida_simple(mapa, posiciones_salida)
            return
        
        # El siguiente paso en el camino más corto
        siguiente_paso = camino_mas_corto[1]  # [0] es la posición actual
        
        # Si el jugador está cerca (distancia <= 3), considerar evitarlo
        if jugador:
            jugador_pos = jugador.obtener_posicion()
            distancia_al_jugador = abs(jugador_pos[0] - enemigo_pos[0]) + abs(jugador_pos[1] - enemigo_pos[1])
            
            if distancia_al_jugador <= 3:
                # El jugador está cerca, intentar evitar pero priorizar la salida
                mejor_movimiento = self._elegir_movimiento_evasivo(mapa, siguiente_paso, jugador_pos, enemigo_pos)
            else:
                # El jugador está lejos, ir directo hacia la salida
                mejor_movimiento = self._obtener_direccion_hacia(enemigo_pos, siguiente_paso)
        else:
            mejor_movimiento = self._obtener_direccion_hacia(enemigo_pos, siguiente_paso)
        
        # Aplicar el movimiento
        if mejor_movimiento:
            if mejor_movimiento == "arriba":
                self.mover_arriba(mapa, modo="cazador")
            elif mejor_movimiento == "abajo":
                self.mover_abajo(mapa, modo="cazador")
            elif mejor_movimiento == "izquierda":
                self.mover_izquierda(mapa, modo="cazador")
            elif mejor_movimiento == "derecha":
                self.mover_derecha(mapa, modo="cazador")
    
    def _encontrar_camino_bfs(self, mapa: Mapa, inicio: Tuple[int, int], destino: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        Encuentra el camino más corto desde inicio hasta destino usando BFS.
        
        Args:
            mapa: Mapa del juego.
            inicio: Posición inicial (fila, columna).
            destino: Posición destino (fila, columna).
            
        Returns:
            Lista de posiciones desde inicio hasta destino, o None si no hay camino.
        """
        from collections import deque
        
        if inicio == destino:
            return [inicio]
        
        # Verificar que inicio y destino sean transitables para enemigos en modo cazador
        if not mapa.es_transitable_por_enemigo(inicio[0], inicio[1], modo="cazador"):
            return None
        if not mapa.es_transitable_por_enemigo(destino[0], destino[1], modo="cazador"):
            return None
        
        visitado = [[False for _ in range(mapa.ancho)] for _ in range(mapa.alto)]
        padre = {}
        cola = deque([inicio])
        visitado[inicio[0]][inicio[1]] = True
        
        direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        while cola:
            fila, col = cola.popleft()
            
            if (fila, col) == destino:
                # Reconstruir camino
                camino = []
                actual = destino
                while actual is not None:
                    camino.append(actual)
                    actual = padre.get(actual)
                return camino[::-1]  # Invertir para tener inicio -> destino
            
            for df, dc in direcciones:
                nueva_fila = fila + df
                nueva_col = col + dc
                
                if (0 <= nueva_fila < mapa.alto and 
                    0 <= nueva_col < mapa.ancho and 
                    not visitado[nueva_fila][nueva_col] and
                    mapa.es_transitable_por_enemigo(nueva_fila, nueva_col, modo="cazador")):
                    
                    visitado[nueva_fila][nueva_col] = True
                    padre[(nueva_fila, nueva_col)] = (fila, col)
                    cola.append((nueva_fila, nueva_col))
        
        return None
    
    def _obtener_direccion_hacia(self, desde: Tuple[int, int], hacia: Tuple[int, int]) -> Optional[str]:
        """
        Obtiene la dirección (arriba, abajo, izquierda, derecha) para moverse de 'desde' hacia 'hacia'.
        
        Args:
            desde: Posición actual (fila, columna).
            hacia: Posición destino (fila, columna).
            
        Returns:
            Nombre de la dirección o None si ya está en el destino.
        """
        df = hacia[0] - desde[0]
        dc = hacia[1] - desde[1]
        
        if df < 0:
            return "arriba"
        elif df > 0:
            return "abajo"
        elif dc < 0:
            return "izquierda"
        elif dc > 0:
            return "derecha"
        
        return None
    
    def _elegir_movimiento_evasivo(self, mapa: Mapa, siguiente_paso_ideal: Tuple[int, int], 
                                   jugador_pos: Tuple[int, int], enemigo_pos: Tuple[int, int]) -> Optional[str]:
        """
        Elige un movimiento que evite al jugador pero se acerque a la salida.
        
        Args:
            mapa: Mapa del juego.
            siguiente_paso_ideal: El siguiente paso ideal hacia la salida.
            jugador_pos: Posición del jugador.
            enemigo_pos: Posición actual del enemigo.
            
        Returns:
            Nombre de la dirección a mover, o None si no hay movimiento válido.
        """
        # Calcular distancia al jugador desde cada posible movimiento
        movimientos = [
            ("arriba", (-1, 0)),
            ("abajo", (1, 0)),
            ("izquierda", (0, -1)),
            ("derecha", (0, 1))
        ]
        
        mejor_movimiento = None
        mejor_puntuacion = float('-inf')
        
        for nombre, (df, dc) in movimientos:
            nueva_fila = enemigo_pos[0] + df
            nueva_col = enemigo_pos[1] + dc
            
            # Verificar que el movimiento sea válido
            if not mapa.es_posicion_valida(nueva_fila, nueva_col):
                continue
            if not mapa.es_transitable_por_enemigo(nueva_fila, nueva_col, modo="cazador"):
                continue
            
            nueva_pos = (nueva_fila, nueva_col)
            
            # Calcular puntuación: priorizar acercarse a la salida, pero evitar al jugador
            distancia_a_salida = abs(siguiente_paso_ideal[0] - nueva_fila) + abs(siguiente_paso_ideal[1] - nueva_col)
            distancia_al_jugador = abs(jugador_pos[0] - nueva_fila) + abs(jugador_pos[1] - nueva_col)
            
            # Puntuación: más puntos si está más cerca de la salida ideal y más lejos del jugador
            # Pero siempre priorizar acercarse a la salida
            puntuacion = -distancia_a_salida * 2  # Prioridad alta: acercarse a la salida
            if distancia_al_jugador > 2:  # Bonus si está lejos del jugador
                puntuacion += distancia_al_jugador * 0.5
            
            if puntuacion > mejor_puntuacion:
                mejor_puntuacion = puntuacion
                mejor_movimiento = nombre
        
        return mejor_movimiento
    
    def _buscar_salida_simple(self, mapa: Mapa, posiciones_salida: List[Tuple[int, int]]) -> None:
        """
        Método simple de búsqueda de salida como fallback (usa distancia de Manhattan).
        
        Args:
            mapa: Mapa del juego.
            posiciones_salida: Lista de posiciones de salida.
        """
        enemigo_pos = self.obtener_posicion()
        
        # Encontrar la salida más cercana
        salida_mas_cercana = None
        menor_distancia = float('inf')
        
        for salida in posiciones_salida:
            distancia = abs(salida[0] - enemigo_pos[0]) + abs(salida[1] - enemigo_pos[1])
            if distancia < menor_distancia:
                menor_distancia = distancia
                salida_mas_cercana = salida
        
        if not salida_mas_cercana:
            return
        
        # Probar movimientos en las 4 direcciones y elegir el que más reduzca la distancia
        mejor_movimiento = None
        menor_distancia_nueva = menor_distancia
        
        movimientos = [
            ("arriba", self.mover_arriba),
            ("abajo", self.mover_abajo),
            ("izquierda", self.mover_izquierda),
            ("derecha", self.mover_derecha)
        ]
        
        for nombre, movimiento_func in movimientos:
            # Guardar posición actual
            fila_original = self.fila
            col_original = self.columna
            
            # Intentar movimiento con modo cazador
            if movimiento_func(mapa, modo="cazador"):
                # Calcular nueva distancia a la salida
                nueva_pos = self.obtener_posicion()
                nueva_distancia = abs(salida_mas_cercana[0] - nueva_pos[0]) + abs(salida_mas_cercana[1] - nueva_pos[1])
                
                if nueva_distancia < menor_distancia_nueva:
                    menor_distancia_nueva = nueva_distancia
                    mejor_movimiento = nombre
                
                # Revertir movimiento para probar el siguiente
                self.fila = fila_original
                self.columna = col_original
        
        # Aplicar el mejor movimiento
        if mejor_movimiento:
            if mejor_movimiento == "arriba":
                self.mover_arriba(mapa, modo="cazador")
            elif mejor_movimiento == "abajo":
                self.mover_abajo(mapa, modo="cazador")
            elif mejor_movimiento == "izquierda":
                self.mover_izquierda(mapa, modo="cazador")
            elif mejor_movimiento == "derecha":
                self.mover_derecha(mapa, modo="cazador")
    
    def ha_llegado_a_salida(self, mapa: Mapa) -> bool:
        """
        Verifica si el enemigo ha llegado a alguna salida del mapa.
        
        Args:
            mapa: Mapa del juego.
            
        Returns:
            True si el enemigo está en alguna posición de salida, False en caso contrario.
        """
        if not self.esta_vivo():
            return False
        
        posicion_actual = self.obtener_posicion()
        return mapa.es_posicion_salida(posicion_actual[0], posicion_actual[1])
    
    def __repr__(self) -> str:
        """Representación del enemigo."""
        estado_str = self.estado.value if self.estado else "desconocido"
        return f"Enemigo(pos=({self.fila}, {self.columna}), estado={estado_str}, velocidad={self.velocidad})"

