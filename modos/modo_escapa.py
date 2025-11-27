"""
Módulo modo_escapa: Implementa el modo de juego "Escapa".
"""

import random
from typing import List, Optional, Tuple
from modelo import Mapa, Jugador
from modelo.enemigo import Enemigo
from modelo.trampa import GestorTrampas
from sistema.puntajes import ScoreBoard
from logica import Dificultad, ConfiguracionDificultad, GeneradorMapa


class GameModeEscapa:
    """
    Modo de juego "Escapa": el jugador debe llegar a la salida
    mientras los enemigos lo persiguen.
    """
    
    def __init__(self, mapa: Optional[Mapa] = None, 
                 nombre_jugador: str = "Jugador",
                 dificultad: Dificultad = Dificultad.NORMAL,
                 ancho_mapa: int = 15,
                 alto_mapa: int = 15):
        """
        Inicializa el modo Escapa.
        
        Args:
            mapa: Mapa del juego. Si es None, se genera uno nuevo.
            nombre_jugador: Nombre del jugador.
            dificultad: Nivel de dificultad.
            ancho_mapa: Ancho del mapa si se genera uno nuevo.
            alto_mapa: Alto del mapa si se genera uno nuevo.
        """
        self.nombre_jugador = nombre_jugador
        self.dificultad = dificultad
        self.config = ConfiguracionDificultad.obtener_configuracion(dificultad)
        
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
        
        # Obtener posición del spawn (después de crear el jugador)
        self.posicion_spawn = self._obtener_posicion_spawn()
        
        # Crear enemigos
        self.enemigos: List[Enemigo] = []
        self._crear_enemigos()
        
        # Gestor de trampas
        self.gestor_trampas = GestorTrampas()
        
        # Estado del juego
        self.tiempo_juego = 0.0
        self.puntos = 0
        self.juego_terminado = False
        self.victoria = False
        self.movimientos = 0
        self.enemigos_eliminados = 0
        
        # ScoreBoard
        self.scoreboard = ScoreBoard()
    
    def _obtener_posicion_spawn(self) -> Optional[Tuple[int, int]]:
        """
        Obtiene la posición del spawn para los enemigos.
        El spawn está cerca del centro del mapa o en una posición estratégica.
        
        Returns:
            Tupla (fila, columna) con la posición del spawn, o None si no se encuentra.
        """
        # Buscar una posición cerca del centro del mapa que sea transitable
        centro_fila = self.mapa.alto // 2
        centro_col = self.mapa.ancho // 2
        
        # Buscar en un área alrededor del centro
        for radio in range(0, max(self.mapa.alto, self.mapa.ancho)):
            for df in range(-radio, radio + 1):
                for dc in range(-radio, radio + 1):
                    fila = centro_fila + df
                    col = centro_col + dc
                    
                    if (self.mapa.es_posicion_valida(fila, col) and
                        self.mapa.es_transitable_por_enemigo(fila, col) and
                        (fila, col) != self.jugador.obtener_posicion() and
                        (fila, col) != self.mapa.obtener_posicion_salida()):
                        return (fila, col)
        
        return None
    
    def _crear_enemigos(self) -> None:
        """Crea los enemigos según la dificultad."""
        cantidad = self.config["cantidad_enemigos"]
        velocidad = self.config["velocidad_enemigos"]
        tiempo_respawn = self.config["tiempo_respawn_enemigo"]
        
        # Reducir velocidad para que no se salten casillas (máximo 2 movimientos por segundo)
        velocidad_controlada = min(velocidad, 2.0)
        
        # Crear enemigos en el spawn con tiempos escalonados
        for i in range(cantidad):
            if self.posicion_spawn:
                # Crear enemigo en el spawn
                enemigo = Enemigo(
                    self.posicion_spawn[0],
                    self.posicion_spawn[1],
                    velocidad=velocidad_controlada,
                    tiempo_respawn=tiempo_respawn,
                    en_spawn=True
                )
                # Escalonar los tiempos de espera en spawn (cada enemigo espera un poco más)
                enemigo.tiempo_espera_spawn = 2.0 + (i * 1.5)  # 2s, 3.5s, 5s, 6.5s...
                self.enemigos.append(enemigo)
            else:
                # Si no hay spawn, usar el sistema antiguo
                posiciones_ocupadas = set()
                pos_jugador = self.jugador.obtener_posicion()
                pos_salida = self.mapa.obtener_posicion_salida()
                posiciones_ocupadas.add(pos_jugador)
                posiciones_ocupadas.add(pos_salida)
                
                posicion = self._obtener_posicion_valida_aleatoria(posiciones_ocupadas)
                if posicion:
                    enemigo = Enemigo(
                        posicion[0],
                        posicion[1],
                        velocidad=velocidad_controlada,
                        tiempo_respawn=tiempo_respawn
                    )
                    self.enemigos.append(enemigo)
                    posiciones_ocupadas.add(posicion)
    
    def _obtener_posicion_valida_aleatoria(self, posiciones_ocupadas: set) -> Optional[Tuple[int, int]]:
        """
        Obtiene una posición válida aleatoria para un enemigo.
        
        Args:
            posiciones_ocupadas: Conjunto de posiciones ya ocupadas (jugador, salida, otros enemigos).
        
        Returns:
            Tupla (fila, columna) o None si no se encuentra.
        """
        intentos = 0
        max_intentos = 200
        pos_jugador = self.jugador.obtener_posicion()
        distancia_minima = 3  # Distancia mínima del jugador al inicio
        
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
        
        # Actualizar energía del jugador
        self.jugador.actualizar_energia(delta_tiempo)
        
        # Actualizar enemigos
        for enemigo in self.enemigos:
            enemigo.actualizar(self.mapa, self.jugador, delta_tiempo, "escapa", self.posicion_spawn)
        
        # Verificar colisiones con trampas
        enemigos_eliminados = self.gestor_trampas.verificar_colisiones_enemigos(self.enemigos)
        if enemigos_eliminados > 0:
            self.enemigos_eliminados += enemigos_eliminados
            puntos_ganados = enemigos_eliminados * self.config["puntos_por_enemigo_eliminado"]
            self.puntos += puntos_ganados
        
        # Verificar si un enemigo alcanzó al jugador
        for enemigo in self.enemigos:
            if enemigo.esta_vivo() and enemigo.obtener_posicion() == self.jugador.obtener_posicion():
                self._terminar_juego(victoria=False)
                return
        
        # Verificar si el jugador llegó a la salida
        if self.jugador.ha_llegado_a_salida(self.mapa):
            self._terminar_juego(victoria=True)
            return
    
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
    
    def colocar_trampa(self, fila: Optional[int] = None, columna: Optional[int] = None) -> bool:
        """
        Coloca una trampa en la posición del jugador o en la posición especificada.
        
        Args:
            fila: Fila donde colocar la trampa. Si es None, usa la posición del jugador.
            columna: Columna donde colocar la trampa. Si es None, usa la posición del jugador.
            
        Returns:
            True si se colocó exitosamente, False en caso contrario.
        """
        if self.juego_terminado:
            return False
        
        if fila is None or columna is None:
            pos = self.jugador.obtener_posicion()
            fila, columna = pos
        
        return self.gestor_trampas.colocar_trampa(fila, columna, self.tiempo_juego)
    
    def _terminar_juego(self, victoria: bool) -> None:
        """
        Termina el juego y calcula el puntaje final.
        
        Args:
            victoria: True si el jugador ganó, False si perdió.
        """
        self.juego_terminado = True
        self.victoria = victoria
        
        if victoria:
            # Calcular puntaje final
            puntos_base = self.config["puntos_base_escapa"]
            
            # Bono por tiempo (menos tiempo = más puntos)
            # Máximo 100 puntos extra si termina en menos de 60 segundos
            bono_tiempo = max(0, 100 - int(self.tiempo_juego))
            
            # Bono por enemigos eliminados
            bono_enemigos = self.enemigos_eliminados * self.config["puntos_por_enemigo_eliminado"]
            
            # Bono por dificultad (ya está en puntos_base)
            
            self.puntos = puntos_base + bono_tiempo + bono_enemigos
            
            # Registrar puntaje
            self.scoreboard.registrar_puntaje(
                "escapa",
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
        return {
            "tiempo_juego": self.tiempo_juego,
            "puntos": self.puntos,
            "movimientos": self.movimientos,
            "enemigos_eliminados": self.enemigos_eliminados,
            "energia_jugador": self.jugador.obtener_energia_actual(),
            "energia_maxima": self.jugador.obtener_energia_maxima(),
            "juego_terminado": self.juego_terminado,
            "victoria": self.victoria,
            "trampas_activas": len(self.gestor_trampas.obtener_trampas_activas()),
            "cooldown_trampa": self.gestor_trampas.obtener_tiempo_restante_cooldown(self.tiempo_juego)
        }
    
    def __repr__(self) -> str:
        """Representación del modo de juego."""
        estado = "terminado" if self.juego_terminado else "activo"
        resultado = "victoria" if self.victoria else "derrota" if self.juego_terminado else "en curso"
        return f"GameModeEscapa(jugador='{self.nombre_jugador}', estado={estado}, resultado={resultado}, puntos={self.puntos})"

