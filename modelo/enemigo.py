"""
Módulo enemigo: Define la clase Enemigo con movimiento e IA.
"""

from typing import Tuple, Optional
from enum import Enum
from .mapa import Mapa
from .jugador import Jugador


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
        self.fila = fila
        self.columna = columna
        self.velocidad = velocidad  # movimientos por segundo
        self.tiempo_respawn = tiempo_respawn
        self.estado = EstadoEnemigo.EN_SPAWN if en_spawn else EstadoEnemigo.ACTIVO
        self.tiempo_restante_respawn = 0.0
        self.mapa: Optional[Mapa] = None
        
        # Control de velocidad de movimiento (temporizador)
        self.tiempo_desde_ultimo_movimiento = 0.0
        self.tiempo_entre_movimientos = 1.0 / velocidad if velocidad > 0 else 1.0  # segundos entre movimientos
        
        # Control de salida del spawn
        self.tiempo_en_spawn = 0.0
        self.tiempo_espera_spawn = 2.0  # segundos esperando en spawn antes de salir
    
    def obtener_posicion(self) -> Tuple[int, int]:
        """
        Obtiene la posición actual del enemigo.
        
        Returns:
            Tupla (fila, columna) con la posición actual.
        """
        return (self.fila, self.columna)
    
    def mover_arriba(self, mapa: Mapa) -> bool:
        """
        Mueve al enemigo hacia arriba (disminuye fila).
        
        Args:
            mapa: Mapa en el que se mueve el enemigo.
            
        Returns:
            True si el movimiento fue exitoso, False en caso contrario.
        """
        return self._mover(mapa, self.fila - 1, self.columna)
    
    def mover_abajo(self, mapa: Mapa) -> bool:
        """
        Mueve al enemigo hacia abajo (aumenta fila).
        
        Args:
            mapa: Mapa en el que se mueve el enemigo.
            
        Returns:
            True si el movimiento fue exitoso, False en caso contrario.
        """
        return self._mover(mapa, self.fila + 1, self.columna)
    
    def mover_izquierda(self, mapa: Mapa) -> bool:
        """
        Mueve al enemigo hacia la izquierda (disminuye columna).
        
        Args:
            mapa: Mapa en el que se mueve el enemigo.
            
        Returns:
            True si el movimiento fue exitoso, False en caso contrario.
        """
        return self._mover(mapa, self.fila, self.columna - 1)
    
    def mover_derecha(self, mapa: Mapa) -> bool:
        """
        Mueve al enemigo hacia la derecha (aumenta columna).
        
        Args:
            mapa: Mapa en el que se mueve el enemigo.
            
        Returns:
            True si el movimiento fue exitoso, False en caso contrario.
        """
        return self._mover(mapa, self.fila, self.columna + 1)
    
    def _mover(self, mapa: Mapa, nueva_fila: int, nueva_col: int) -> bool:
        """
        Método interno que realiza el movimiento.
        
        Args:
            mapa: Mapa en el que se mueve el enemigo.
            nueva_fila: Nueva fila destino.
            nueva_col: Nueva columna destino.
            
        Returns:
            True si el movimiento fue exitoso, False en caso contrario.
        """
        # Validar posición
        if not mapa.es_posicion_valida(nueva_fila, nueva_col):
            return False
        
        # Verificar si la casilla permite el paso del enemigo
        if not mapa.es_transitable_por_enemigo(nueva_fila, nueva_col):
            return False
        
        # Realizar el movimiento
        self.fila = nueva_fila
        self.columna = nueva_col
        return True
    
    def matar(self) -> None:
        """Mata al enemigo y lo pone en estado de respawn."""
        self.estado = EstadoEnemigo.MUERTO
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
        self.mapa = mapa
        
        # Manejar respawn
        if self.estado == EstadoEnemigo.MUERTO:
            self.tiempo_restante_respawn -= delta_tiempo
            if self.tiempo_restante_respawn <= 0:
                self._respawn(mapa, posicion_spawn)
        
        # Manejar estado en spawn
        elif self.estado == EstadoEnemigo.EN_SPAWN:
            if posicion_spawn:
                # Mover al enemigo al spawn si no está ahí
                if self.obtener_posicion() != posicion_spawn:
                    self.fila, self.columna = posicion_spawn
                
                # Esperar un tiempo antes de salir
                self.tiempo_en_spawn += delta_tiempo
                if self.tiempo_en_spawn >= self.tiempo_espera_spawn:
                    self.estado = EstadoEnemigo.SALIENDO_SPAWN
                    self.tiempo_en_spawn = 0.0
            else:
                # Si no hay spawn, activar directamente
                self.estado = EstadoEnemigo.ACTIVO
        
        # Manejar salida del spawn
        elif self.estado == EstadoEnemigo.SALIENDO_SPAWN:
            if posicion_spawn and self.obtener_posicion() == posicion_spawn:
                # Intentar salir del spawn moviéndose hacia una casilla adyacente válida
                self._salir_del_spawn(mapa, posicion_spawn)
            else:
                # Ya salió del spawn
                self.estado = EstadoEnemigo.ACTIVO
        
        # Si está activo, mover según el modo (con control de velocidad)
        elif self.estado == EstadoEnemigo.ACTIVO:
            self.tiempo_desde_ultimo_movimiento += delta_tiempo
            
            # Solo mover si ha pasado el tiempo suficiente
            if self.tiempo_desde_ultimo_movimiento >= self.tiempo_entre_movimientos:
                if modo == "escapa":
                    self._perseguir_jugador(mapa, jugador)
                elif modo == "cazador":
                    self._huir_del_jugador(mapa, jugador)
                
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
        Mueve al enemigo hacia el jugador (modo escapa).
        
        Args:
            mapa: Mapa del juego.
            jugador: Jugador a perseguir.
        """
        jugador_pos = jugador.obtener_posicion()
        enemigo_pos = self.obtener_posicion()
        
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
    
    def ha_llegado_a_salida(self, mapa: Mapa) -> bool:
        """
        Verifica si el enemigo ha llegado a la salida del mapa.
        
        Args:
            mapa: Mapa del juego.
            
        Returns:
            True si el enemigo está en la posición de salida, False en caso contrario.
        """
        if not self.esta_vivo():
            return False
        
        salida = mapa.obtener_posicion_salida()
        return self.obtener_posicion() == salida
    
    def __repr__(self) -> str:
        """Representación del enemigo."""
        estado_str = self.estado.value if self.estado else "desconocido"
        return f"Enemigo(pos=({self.fila}, {self.columna}), estado={estado_str}, velocidad={self.velocidad})"

