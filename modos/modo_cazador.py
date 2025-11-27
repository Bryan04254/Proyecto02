"""
Módulo modo_cazador: Implementa el modo de juego "Cazador".
"""

import random
from typing import List, Optional, Tuple
from modelo import Mapa, Jugador
from modelo.enemigo import Enemigo
from sistema.puntajes import ScoreBoard
from logica import Dificultad, ConfiguracionDificultad, GeneradorMapa


class GameModeCazador:
    """
    Modo de juego "Cazador": el jugador debe atrapar enemigos
    que intentan escapar por la salida.
    """
    
    def __init__(self, mapa: Optional[Mapa] = None,
                 nombre_jugador: str = "Jugador",
                 dificultad: Dificultad = Dificultad.NORMAL,
                 tiempo_limite: float = 120.0,  # 2 minutos
                 ancho_mapa: int = 15,
                 alto_mapa: int = 15):
        """
        Inicializa el modo Cazador.
        
        Args:
            mapa: Mapa del juego. Si es None, se genera uno nuevo.
            nombre_jugador: Nombre del jugador.
            dificultad: Nivel de dificultad.
            tiempo_limite: Tiempo límite de la partida en segundos.
            ancho_mapa: Ancho del mapa si se genera uno nuevo.
            alto_mapa: Alto del mapa si se genera uno nuevo.
        """
        self.nombre_jugador = nombre_jugador
        self.dificultad = dificultad
        self.config = ConfiguracionDificultad.obtener_configuracion(dificultad)
        self.tiempo_limite = tiempo_limite
        
        # Generar o usar mapa existente
        if mapa is None:
            generador = GeneradorMapa(ancho=ancho_mapa, alto=alto_mapa)
            self.mapa = generador.generar_mapa()
        else:
            self.mapa = mapa
        
        # Crear jugador
        pos_inicio = self.mapa.obtener_posicion_inicio_jugador()
        energia_inicial = self.config["energia_inicial_jugador"]
        self.jugador = Jugador(pos_inicio[0], pos_inicio[1], energia_maxima=energia_inicial)
        
        # Crear enemigos
        self.enemigos: List[Enemigo] = []
        self._crear_enemigos()
        
        # Estado del juego
        self.tiempo_juego = 0.0
        self.puntos = self.config["puntos_base_cazador"]  # Puntos iniciales
        self.juego_terminado = False
        self.enemigos_capturados = 0
        self.enemigos_escapados = 0
        self.movimientos = 0
    
    def _crear_enemigos(self) -> None:
        """Crea los enemigos según la dificultad."""
        cantidad = self.config["cantidad_enemigos"]
        velocidad = self.config["velocidad_enemigos"]
        tiempo_respawn = self.config["tiempo_respawn_enemigo"]
        
        # Obtener posiciones ya ocupadas
        posiciones_ocupadas = set()
        pos_jugador = self.jugador.obtener_posicion()
        pos_salida = self.mapa.obtener_posicion_salida()
        posiciones_ocupadas.add(pos_jugador)
        # En modo cazador, los enemigos pueden estar cerca de la salida, pero no encima
        
        for _ in range(cantidad):
            # Buscar posición válida aleatoria
            posicion = self._obtener_posicion_valida_aleatoria(posiciones_ocupadas)
            if posicion:
                enemigo = Enemigo(
                    posicion[0],
                    posicion[1],
                    velocidad=velocidad,
                    tiempo_respawn=tiempo_respawn
                )
                self.enemigos.append(enemigo)
                posiciones_ocupadas.add(posicion)
    
    def _obtener_posicion_valida_aleatoria(self, posiciones_ocupadas: set) -> Optional[Tuple[int, int]]:
        """
        Obtiene una posición válida aleatoria para un enemigo.
        
        Args:
            posiciones_ocupadas: Conjunto de posiciones ya ocupadas (jugador, otros enemigos).
        
        Returns:
            Tupla (fila, columna) o None si no se encuentra.
        """
        intentos = 0
        max_intentos = 200
        pos_jugador = self.jugador.obtener_posicion()
        distancia_minima = 2  # Distancia mínima del jugador al inicio
        
        while intentos < max_intentos:
            fila = random.randint(0, self.mapa.alto - 1)
            columna = random.randint(0, self.mapa.ancho - 1)
            posicion = (fila, columna)
            
            # Verificar que sea transitable por enemigos
            if not self.mapa.es_transitable_por_enemigo(fila, columna):
                intentos += 1
                continue
            
            # Verificar que no esté ocupada
            if posicion in posiciones_ocupadas:
                intentos += 1
                continue
            
            # Verificar distancia mínima del jugador (solo al inicio)
            distancia_manhattan = abs(fila - pos_jugador[0]) + abs(columna - pos_jugador[1])
            if distancia_manhattan < distancia_minima:
                intentos += 1
                continue
            
            return posicion
        
        # Si no se encuentra con distancia mínima, intentar sin restricción de distancia
        intentos = 0
        while intentos < max_intentos:
            fila = random.randint(0, self.mapa.alto - 1)
            columna = random.randint(0, self.mapa.ancho - 1)
            posicion = (fila, columna)
            
            if (self.mapa.es_transitable_por_enemigo(fila, columna) and
                posicion not in posiciones_ocupadas):
                return posicion
            
            intentos += 1
        
        return None
    
    def actualizar(self, delta_tiempo: float) -> None:
        """
        Actualiza el estado del juego.
        
        Args:
            delta_tiempo: Tiempo transcurrido desde la última actualización (segundos).
        """
        if self.juego_terminado:
            return
        
        self.tiempo_juego += delta_tiempo
        
        # Verificar tiempo límite
        if self.tiempo_juego >= self.tiempo_limite:
            self._terminar_juego()
            return
        
        # Actualizar energía del jugador
        self.jugador.actualizar_energia(delta_tiempo)
        
        # Actualizar enemigos (modo cazador no usa spawn)
        for enemigo in self.enemigos:
            enemigo.actualizar(self.mapa, self.jugador, delta_tiempo, "cazador", None)
            
            # Verificar si un enemigo llegó a la salida
            if enemigo.esta_vivo() and enemigo.ha_llegado_a_salida(self.mapa):
                self._enemigo_escapo(enemigo)
            
            # Verificar si el jugador capturó a un enemigo
            if enemigo.esta_vivo() and enemigo.obtener_posicion() == self.jugador.obtener_posicion():
                self._capturar_enemigo(enemigo)
    
    def _enemigo_escapo(self, enemigo: Enemigo) -> None:
        """
        Maneja cuando un enemigo escapa por la salida.
        
        Args:
            enemigo: Enemigo que escapó.
        """
        puntos_perdidos = self.config["puntos_perdidos_por_escape"]
        self.puntos = max(0, self.puntos - puntos_perdidos)
        self.enemigos_escapados += 1
        
        # Respawnear el enemigo
        enemigo.matar()
    
    def _capturar_enemigo(self, enemigo: Enemigo) -> None:
        """
        Maneja cuando el jugador captura a un enemigo.
        
        Args:
            enemigo: Enemigo capturado.
        """
        puntos_ganados = self.config["puntos_ganados_por_captura"]
        self.puntos += puntos_ganados
        self.enemigos_capturados += 1
        
        # Respawnear el enemigo
        enemigo.matar()
    
    def mover_jugador(self, direccion: str, corriendo: bool = False) -> bool:
        """
        Mueve al jugador en la dirección especificada.
        
        Args:
            direccion: Dirección ("arriba", "abajo", "izquierda", "derecha").
            corriendo: Si True, el jugador corre.
            
        Returns:
            True si el movimiento fue exitoso, False en caso contrario.
        """
        if self.juego_terminado:
            return False
        
        movimiento_exitoso = False
        
        if direccion == "arriba":
            movimiento_exitoso = self.jugador.mover_arriba(self.mapa, corriendo)
        elif direccion == "abajo":
            movimiento_exitoso = self.jugador.mover_abajo(self.mapa, corriendo)
        elif direccion == "izquierda":
            movimiento_exitoso = self.jugador.mover_izquierda(self.mapa, corriendo)
        elif direccion == "derecha":
            movimiento_exitoso = self.jugador.mover_derecha(self.mapa, corriendo)
        
        if movimiento_exitoso:
            self.movimientos += 1
        
        return movimiento_exitoso
    
    def _terminar_juego(self) -> None:
        """Termina el juego y registra el puntaje."""
        self.juego_terminado = True
        
        # Registrar puntaje
        scoreboard = ScoreBoard()
        scoreboard.registrar_puntaje(
            "cazador",
            self.nombre_jugador,
            self.puntos,
            tiempo_juego=self.tiempo_juego,
            movimientos=self.movimientos
        )
    
    def obtener_estado(self) -> dict:
        """
        Obtiene el estado actual del juego.
        
        Returns:
            Diccionario con el estado del juego.
        """
        tiempo_restante = max(0.0, self.tiempo_limite - self.tiempo_juego)
        
        return {
            "tiempo_juego": self.tiempo_juego,
            "tiempo_restante": tiempo_restante,
            "puntos": self.puntos,
            "movimientos": self.movimientos,
            "enemigos_capturados": self.enemigos_capturados,
            "enemigos_escapados": self.enemigos_escapados,
            "energia_jugador": self.jugador.obtener_energia_actual(),
            "energia_maxima": self.jugador.obtener_energia_maxima(),
            "juego_terminado": self.juego_terminado
        }
    
    def __repr__(self) -> str:
        """Representación del modo de juego."""
        estado = "terminado" if self.juego_terminado else "activo"
        return f"GameModeCazador(jugador='{self.nombre_jugador}', estado={estado}, puntos={self.puntos}, capturados={self.enemigos_capturados})"

