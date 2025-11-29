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
        
        # Crear jugador siempre en la esquina superior izquierda (1, 1)
        pos_inicio = (1, 1)
        # Asegurar que la posición de inicio del mapa sea (1, 1)
        if self.mapa.obtener_posicion_inicio_jugador() != pos_inicio:
            # Si el mapa no tiene el inicio en (1, 1), forzarlo
            # Asegurar que (1, 1) sea transitable
            if not self.mapa.es_transitable_por_jugador(1, 1):
                # Si no es transitable, buscar una posición cercana
                for df in range(0, 3):
                    for dc in range(0, 3):
                        fila = 1 + df
                        col = 1 + dc
                        if self.mapa.es_posicion_valida(fila, col) and self.mapa.es_transitable_por_jugador(fila, col):
                            pos_inicio = (fila, col)
                            break
                    if pos_inicio != (1, 1):
                        break
        
        energia_inicial = self.config["energia_inicial_jugador"]
        self.jugador = Jugador(pos_inicio[0], pos_inicio[1], energia_maxima=energia_inicial)
        
        # Gestor de trampas con límite de 3 trampas activas (según especificación)
        # Sistema de regeneración: empieza con 3 trampas disponibles
        self.gestor_trampas = GestorTrampas(max_trampas_activas=3)
        self.trampas_disponibles = 3  # Trampas que el jugador puede usar (se regeneran)
        self.tiempo_ultima_regeneracion = 0.0
        
        # Crear enemigos: 3 cazadores por cada trampa disponible (3 trampas = 9 cazadores)
        self.enemigos: List[Enemigo] = []
        self._crear_enemigos()
        
        # Estado del juego
        self.tiempo_juego = 0.0
        self.puntos = 0
        self.juego_terminado = False
        self.victoria = False
        self.movimientos = 0
        self.enemigos_eliminados = 0
        
        # ScoreBoard
        self.scoreboard = ScoreBoard()
    
    def _obtener_esquinas_enemigos(self) -> List[Tuple[int, int]]:
        """
        Obtiene las esquinas donde pueden aparecer los enemigos.
        El jugador está en la esquina superior izquierda (1, 1).
        Los enemigos aparecen en:
        - Esquina superior derecha: (1, ancho - 2)
        - Esquina inferior izquierda: (alto - 2, 1)
        
        Returns:
            Lista de tuplas (fila, columna) con las posiciones de las esquinas válidas.
        """
        posiciones_salida = self.mapa.obtener_posiciones_salida()
        esquinas = []
        
        # Esquinas objetivo donde aparecen los enemigos
        esquina_superior_derecha = (1, self.mapa.ancho - 2)
        esquina_inferior_izquierda = (self.mapa.alto - 2, 1)
        
        candidatos_esquinas = [esquina_superior_derecha, esquina_inferior_izquierda]
        
        # Para cada esquina objetivo, buscar la posición válida más cercana
        for esquina_objetivo in candidatos_esquinas:
            fila_obj, col_obj = esquina_objetivo
            mejor_posicion = None
            mejor_distancia = float('inf')
            
            # Buscar en un radio alrededor de la esquina objetivo
            for radio in range(0, 8):  # Radio más amplio para encontrar posición válida
                for df in range(-radio, radio + 1):
                    for dc in range(-radio, radio + 1):
                        fila = fila_obj + df
                        col = col_obj + dc
                        pos = (fila, col)
                        
                        # Calcular distancia a la esquina objetivo
                        distancia = abs(df) + abs(dc)
                        
                        if (self.mapa.es_posicion_valida(fila, col) and
                            self.mapa.es_transitable_por_enemigo(fila, col) and
                            pos not in posiciones_salida and
                            distancia < mejor_distancia):
                            mejor_posicion = pos
                            mejor_distancia = distancia
                
                # Si encontramos una posición válida, agregarla y continuar con la siguiente esquina
                if mejor_posicion is not None:
                    esquinas.append(mejor_posicion)
                    break
        
        return esquinas
    
    def _crear_enemigos(self) -> None:
        """Crea los enemigos en las esquinas superior derecha e inferior izquierda."""
        # 3 cazadores por cada trampa disponible (3 trampas = 9 cazadores)
        cantidad = self.trampas_disponibles * 3
        # Aumentar velocidad de los cazadores
        velocidad_base = self.config["velocidad_enemigos"]
        velocidad = velocidad_base * 1.5  # Aumentar 50% la velocidad
        # Tiempo de respawn siempre 10 segundos según especificación
        tiempo_respawn = 10.0
        
        # Aumentar velocidad de los cazadores (pero limitar para que no se salten casillas)
        velocidad_controlada = min(velocidad, 2.5)  # Máximo 2.5 mov/s
        
        # Obtener esquinas donde aparecen los enemigos
        esquinas = self._obtener_esquinas_enemigos()
        
        # Crear enemigos en las esquinas
        pos_jugador = self.jugador.obtener_posicion()
        posiciones_salida = self.mapa.obtener_posiciones_salida()
        posiciones_ocupadas = set()
        posiciones_ocupadas.add(pos_jugador)
        for salida in posiciones_salida:
            posiciones_ocupadas.add(salida)
        
        # Distribuir enemigos entre las dos esquinas
        # Alternar entre las esquinas disponibles para distribuir uniformemente
        for i in range(cantidad):
            if esquinas:
                # Alternar entre las esquinas disponibles
                esquina_idx = i % len(esquinas)
                posicion = esquinas[esquina_idx]
                
                # Si la posición ya está ocupada, buscar una cercana a esa esquina
                if posicion in posiciones_ocupadas:
                    posicion = self._buscar_posicion_cercana_esquina(esquinas[esquina_idx], posiciones_ocupadas)
            else:
                # Si no hay esquinas válidas, buscar posición alternativa
                posicion = self._obtener_posicion_alternativa_enemigo(posiciones_ocupadas)
            
            # Verificación final antes de crear el enemigo
            if posicion and posicion != pos_jugador and posicion not in posiciones_ocupadas:
                enemigo = Enemigo(
                    posicion[0],
                    posicion[1],
                    velocidad=velocidad_controlada,
                    tiempo_respawn=tiempo_respawn,
                    en_spawn=False  # No usar sistema de spawn, aparecen directamente
                )
                self.enemigos.append(enemigo)
                posiciones_ocupadas.add(posicion)
            else:
                # Fallback: usar posición aleatoria válida con distancia mínima
                posicion = self._obtener_posicion_valida_aleatoria(posiciones_ocupadas)
                # Verificación final: asegurar que no sea la posición del jugador
                if posicion and posicion != pos_jugador and posicion not in posiciones_ocupadas:
                    enemigo = Enemigo(
                        posicion[0],
                        posicion[1],
                        velocidad=velocidad_controlada,
                        tiempo_respawn=tiempo_respawn
                    )
                    self.enemigos.append(enemigo)
                    posiciones_ocupadas.add(posicion)
    
    def _buscar_posicion_cercana_esquina(self, esquina: Tuple[int, int], 
                                         posiciones_ocupadas: set) -> Optional[Tuple[int, int]]:
        """
        Busca una posición válida cercana a una esquina objetivo.
        
        Args:
            esquina: Tupla (fila, columna) de la esquina objetivo.
            posiciones_ocupadas: Conjunto de posiciones ya ocupadas.
        
        Returns:
            Tupla (fila, columna) o None si no se encuentra.
        """
        fila_obj, col_obj = esquina
        pos_jugador = self.jugador.obtener_posicion()
        posiciones_salida = self.mapa.obtener_posiciones_salida()
        
        # Buscar en un radio alrededor de la esquina
        for radio in range(1, 10):
            for df in range(-radio, radio + 1):
                for dc in range(-radio, radio + 1):
                    fila = fila_obj + df
                    col = col_obj + dc
                    pos = (fila, col)
                    
                    if (self.mapa.es_posicion_valida(fila, col) and
                        self.mapa.es_transitable_por_enemigo(fila, col) and
                        pos != pos_jugador and
                        pos not in posiciones_salida and
                        pos not in posiciones_ocupadas):
                        return pos
        
        return None
    
    def _obtener_posicion_alternativa_enemigo(self, posiciones_ocupadas: set) -> Optional[Tuple[int, int]]:
        """
        Obtiene una posición alternativa para un enemigo cerca de las esquinas objetivo.
        
        Args:
            posiciones_ocupadas: Conjunto de posiciones ya ocupadas.
        
        Returns:
            Tupla (fila, columna) o None si no se encuentra.
        """
        pos_jugador = self.jugador.obtener_posicion()
        posiciones_salida = self.mapa.obtener_posiciones_salida()
        
        # Áreas objetivo: superior derecha e inferior izquierda
        areas_objetivo = [
            # Superior derecha: fila 1-5, columna ancho-6 a ancho-2
            (1, min(5, self.mapa.alto - 2), max(1, self.mapa.ancho - 6), self.mapa.ancho - 2),
            # Inferior izquierda: fila alto-6 a alto-2, columna 1-5
            (max(1, self.mapa.alto - 6), self.mapa.alto - 2, 1, min(5, self.mapa.ancho - 2)),
        ]
        
        for fila_min, fila_max, col_min, col_max in areas_objetivo:
            intentos = 0
            max_intentos = 50
            
            while intentos < max_intentos:
                intentos += 1
                fila = random.randint(fila_min, fila_max)
                col = random.randint(col_min, col_max)
                posicion = (fila, col)
                
                if (self.mapa.es_posicion_valida(fila, col) and
                    self.mapa.es_transitable_por_enemigo(fila, col) and
                    posicion != pos_jugador and
                    posicion not in posiciones_salida and
                    posicion not in posiciones_ocupadas):
                    return posicion
        
        return None
    
    def _obtener_posiciones_opuestas_aleatorias(self, cantidad: int) -> List[Tuple[int, int]]:
        """
        Obtiene posiciones aleatorias en el lado opuesto del jugador.
        
        Args:
            cantidad: Cantidad de posiciones a obtener.
        
        Returns:
            Lista de tuplas (fila, columna) con posiciones opuestas.
        """
        pos_jugador = self.jugador.obtener_posicion()
        pos_jug_fila, pos_jug_col = pos_jugador
        
        # Determinar el lado opuesto
        # Si el jugador está en la mitad superior, buscar en la mitad inferior
        # Si está en la mitad izquierda, buscar en la mitad derecha
        mitad_fila = self.mapa.alto // 2
        mitad_col = self.mapa.ancho // 2
        
        # Calcular área opuesta
        if pos_jug_fila < mitad_fila:
            # Jugador en mitad superior, buscar en mitad inferior
            fila_min, fila_max = mitad_fila, self.mapa.alto - 2
        else:
            # Jugador en mitad inferior, buscar en mitad superior
            fila_min, fila_max = 1, mitad_fila
        
        if pos_jug_col < mitad_col:
            # Jugador en mitad izquierda, buscar en mitad derecha
            col_min, col_max = mitad_col, self.mapa.ancho - 2
        else:
            # Jugador en mitad derecha, buscar en mitad izquierda
            col_min, col_max = 1, mitad_col
        
        posiciones = []
        pos_jugador = self.jugador.obtener_posicion()
        posiciones_salida = self.mapa.obtener_posiciones_salida()
        posiciones_ocupadas = set([pos_jugador] + posiciones_salida)
        
        intentos = 0
        max_intentos = cantidad * 50
        
        while len(posiciones) < cantidad and intentos < max_intentos:
            intentos += 1
            fila = random.randint(fila_min, fila_max)
            col = random.randint(col_min, col_max)
            posicion = (fila, col)
            
            if (self.mapa.es_posicion_valida(fila, col) and
                self.mapa.es_transitable_por_enemigo(fila, col) and
                posicion not in posiciones_ocupadas and
                posicion not in posiciones):
                posiciones.append(posicion)
                posiciones_ocupadas.add(posicion)
        
        return posiciones
    
    def _obtener_posicion_opuesta_aleatoria(self, posiciones_ocupadas: set) -> Optional[Tuple[int, int]]:
        """
        Obtiene una posición aleatoria en el lado opuesto del jugador.
        Asegura distancia mínima del jugador.
        
        Args:
            posiciones_ocupadas: Conjunto de posiciones ya ocupadas.
        
        Returns:
            Tupla (fila, columna) o None si no se encuentra.
        """
        pos_jugador = self.jugador.obtener_posicion()
        pos_jug_fila, pos_jug_col = pos_jugador
        
        # Determinar el lado opuesto
        mitad_fila = self.mapa.alto // 2
        mitad_col = self.mapa.ancho // 2
        
        # Calcular área opuesta
        if pos_jug_fila < mitad_fila:
            fila_min, fila_max = mitad_fila, self.mapa.alto - 2
        else:
            fila_min, fila_max = 1, mitad_fila
        
        if pos_jug_col < mitad_col:
            col_min, col_max = mitad_col, self.mapa.ancho - 2
        else:
            col_min, col_max = 1, mitad_col
        
        intentos = 0
        max_intentos = 200
        distancia_minima = 3  # Distancia mínima del jugador
        
        while intentos < max_intentos:
            intentos += 1
            fila = random.randint(fila_min, fila_max)
            col = random.randint(col_min, col_max)
            posicion = (fila, col)
            
            # Calcular distancia de Manhattan al jugador
            distancia = abs(fila - pos_jug_fila) + abs(col - pos_jug_col)
            
            if (self.mapa.es_posicion_valida(fila, col) and
                self.mapa.es_transitable_por_enemigo(fila, col) and
                posicion != pos_jugador and
                distancia >= distancia_minima and
                posicion not in posiciones_ocupadas):
                return posicion
        
        return None
    
    def _obtener_posicion_valida_aleatoria(self, posiciones_ocupadas: set) -> Optional[Tuple[int, int]]:
        """
        Obtiene una posición válida aleatoria para un enemigo.
        Asegura que no sea la posición del jugador y mantiene distancia mínima.
        
        Args:
            posiciones_ocupadas: Conjunto de posiciones ya ocupadas (jugador, salida, otros enemigos).
        
        Returns:
            Tupla (fila, columna) o None si no se encuentra.
        """
        intentos = 0
        max_intentos = 200
        pos_jugador = self.jugador.obtener_posicion()
        distancia_minima = 3  # Distancia mínima del jugador
        
        while intentos < max_intentos:
            fila = random.randint(0, self.mapa.alto - 1)
            columna = random.randint(0, self.mapa.ancho - 1)
            posicion = (fila, columna)
            
            # Verificar que no sea la posición del jugador
            if posicion == pos_jugador:
                intentos += 1
                continue
            
            # Verificar que sea transitable por enemigos
            if not self.mapa.es_transitable_por_enemigo(fila, columna):
                intentos += 1
                continue
            
            # Verificar que no esté ocupada
            if posicion in posiciones_ocupadas:
                intentos += 1
                continue
            
            # Verificar distancia mínima del jugador
            distancia_manhattan = abs(fila - pos_jugador[0]) + abs(columna - pos_jugador[1])
            if distancia_manhattan < distancia_minima:
                intentos += 1
                continue
            
            return posicion
        
        # Si no se encuentra con distancia mínima, intentar sin restricción de distancia
        # pero SIEMPRE asegurando que no sea la posición del jugador
        intentos = 0
        while intentos < max_intentos:
            fila = random.randint(0, self.mapa.alto - 1)
            columna = random.randint(0, self.mapa.ancho - 1)
            posicion = (fila, columna)
            
            # Verificación crítica: nunca en la posición del jugador
            if posicion == pos_jugador:
                intentos += 1
                continue
            
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
        
        # Recuperar energía del jugador gradualmente (1 punto por segundo)
        self.jugador.actualizar_energia(delta_tiempo, tasa_recuperacion=1.0)
        
        # Regenerar trampas cada 5 segundos si hay menos de 3
        # Solo regenerar si hay menos de 3 trampas disponibles
        if self.trampas_disponibles < 3:
            tiempo_desde_regeneracion = self.tiempo_juego - self.tiempo_ultima_regeneracion
            if tiempo_desde_regeneracion >= 5.0:
                # Regenerar una trampa
                self.trampas_disponibles = min(3, self.trampas_disponibles + 1)
                # Reiniciar el contador de regeneración
                self.tiempo_ultima_regeneracion = self.tiempo_juego
        
        # Actualizar enemigos primero
        for enemigo in self.enemigos:
            enemigo.actualizar(self.mapa, self.jugador, delta_tiempo, "escapa", None)
        
        # Verificar colisiones con trampas DESPUÉS de actualizar enemigos
        # Esto captura enemigos que se mueven sobre trampas o que están sobre trampas
        enemigos_eliminados = self.gestor_trampas.verificar_colisiones_enemigos(self.enemigos)
        if enemigos_eliminados > 0:
            self.enemigos_eliminados += enemigos_eliminados
            # Bono de puntos por cada cazador eliminado
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
        Usa el sistema de trampas disponibles (se regeneran cada 5 segundos).
        
        Args:
            fila: Fila donde colocar la trampa. Si es None, usa la posición del jugador.
            columna: Columna donde colocar la trampa. Si es None, usa la posición del jugador.
            
        Returns:
            True si se colocó exitosamente, False en caso contrario.
        """
        if self.juego_terminado:
            return False
        
        # Verificar que haya trampas disponibles
        if self.trampas_disponibles <= 0:
            return False
        
        if fila is None or columna is None:
            pos = self.jugador.obtener_posicion()
            fila, columna = pos
        
        # Verificar límite de trampas activas en el mapa (máximo 3)
        trampas_activas = len(self.gestor_trampas.obtener_trampas_activas())
        if trampas_activas >= 3:
            return False
        
        # Intentar colocar la trampa
        if self.gestor_trampas.colocar_trampa(fila, columna, self.tiempo_juego):
            # Si se colocó exitosamente, reducir trampas disponibles
            self.trampas_disponibles -= 1
            self.tiempo_ultima_regeneracion = self.tiempo_juego
            return True
        
        return False
    
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
            
            # Bono por tiempo mejorado (menos tiempo = más puntos)
            # Máximo 150 puntos extra, escala mejor
            if self.tiempo_juego <= 30:
                bono_tiempo = 150  # Terminar en menos de 30 segundos
            elif self.tiempo_juego <= 60:
                bono_tiempo = 120 - int(self.tiempo_juego)  # Entre 30-60 segundos
            elif self.tiempo_juego <= 90:
                bono_tiempo = 90 - int(self.tiempo_juego * 0.5)  # Entre 60-90 segundos
            else:
                bono_tiempo = max(0, 60 - int(self.tiempo_juego * 0.33))  # Más de 90 segundos
            
            # Bono por enemigos eliminados
            bono_enemigos = self.enemigos_eliminados * self.config["puntos_por_enemigo_eliminado"]
            
            # Bono por energía restante (0.5 puntos por punto de energía)
            energia_restante = self.jugador.obtener_energia_actual()
            bono_energia = int(energia_restante * 0.5)
            
            # Bono por eficiencia (menos movimientos = más puntos)
            # Si terminas rápido con pocos movimientos, bono adicional
            if self.tiempo_juego > 0 and self.movimientos > 0:
                eficiencia = self.tiempo_juego / self.movimientos  # Tiempo por movimiento
                if eficiencia < 0.5:  # Muy eficiente (menos de 0.5 segundos por movimiento)
                    bono_eficiencia = 30
                elif eficiencia < 1.0:
                    bono_eficiencia = 20
                elif eficiencia < 1.5:
                    bono_eficiencia = 10
                else:
                    bono_eficiencia = 0
            else:
                bono_eficiencia = 0
            
            # Bono por trampas usadas eficientemente
            trampas_activas = len(self.gestor_trampas.obtener_trampas_activas())
            trampas_usadas = 3 - self.trampas_disponibles  # Trampas que se usaron
            if trampas_usadas > 0 and self.enemigos_eliminados > 0:
                # Eficiencia: enemigos eliminados / trampas usadas
                eficiencia_trampas = self.enemigos_eliminados / trampas_usadas
                if eficiencia_trampas >= 1.0:  # Al menos 1 enemigo por trampa
                    bono_trampas = int(eficiencia_trampas * 5)  # Hasta 15 puntos extra
                else:
                    bono_trampas = 0
            else:
                bono_trampas = 0
            
            self.puntos = puntos_base + bono_tiempo + bono_enemigos + bono_energia + bono_eficiencia + bono_trampas
            
            # Puntos mínimos garantizados
            self.puntos = max(50, int(self.puntos))
            
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
            "trampas_disponibles": self.trampas_disponibles,
            "cooldown_trampa": self.gestor_trampas.obtener_tiempo_restante_cooldown(self.tiempo_juego)
        }
    
    def __repr__(self) -> str:
        """Representación del modo de juego."""
        estado = "terminado" if self.juego_terminado else "activo"
        resultado = "victoria" if self.victoria else "derrota" if self.juego_terminado else "en curso"
        return f"GameModeEscapa(jugador='{self.nombre_jugador}', estado={estado}, resultado={resultado}, puntos={self.puntos})"

