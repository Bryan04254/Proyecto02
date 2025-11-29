"""
Módulo modo_cazador: Implementa el modo de juego "Cazador".
En este modo, el jugador es el cazador y debe atrapar a 3 enemigos
que intentan escapar por la salida.
"""

import random
from typing import List, Optional, Tuple
from modelo import Mapa, Jugador
from modelo.enemigo import Enemigo, EstadoEnemigo
from sistema.puntajes import ScoreBoard
from logica import Dificultad, ConfiguracionDificultad, GeneradorMapa


class GameModeCazador:
    """
    Modo de juego "Cazador": el jugador es el cazador y debe atrapar
    a 3 enemigos que intentan escapar por la salida.
    """
    
    def __init__(self, mapa: Optional[Mapa] = None,
                 nombre_jugador: str = "Jugador",
                 dificultad: Dificultad = Dificultad.NORMAL,
                 tiempo_limite: float = 120.0,  # 2 minutos
                 ancho_mapa: int = 40,
                 alto_mapa: int = 30):
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
            # Generar mapa con modo cazador (más lianas, menos túneles)
            self.mapa = generador.generar_mapa(modo="cazador")
        else:
            self.mapa = mapa
        
        # Crear jugador (siempre en esquina inferior derecha)
        pos_inicio = (self.mapa.alto - 2, self.mapa.ancho - 2)
        if not self.mapa.es_transitable_por_jugador(pos_inicio[0], pos_inicio[1]):
            # Buscar posición cercana válida
            pos_inicio = self._buscar_posicion_cercana(pos_inicio)
        energia_inicial = self.config["energia_inicial_jugador"]
        self.jugador = Jugador(pos_inicio[0], pos_inicio[1], energia_maxima=energia_inicial)
        
        # Crear exactamente 3 enemigos que buscan la salida
        self.enemigos: List[Enemigo] = []
        self._crear_enemigos()
        
        # Estado del juego
        self.tiempo_juego = 0.0
        self.puntos = self.config["puntos_base_cazador"]  # Puntos iniciales
        self.juego_terminado = False
        self.victoria = False
        self.enemigos_capturados = 0
        self.enemigos_escapados = 0
        self.movimientos = 0
        self.ultima_captura_tiempo = 0.0  # Para sistema de combos
        self.combo_actual = 0  # Contador de combos
        self.puntos_ganados_ultima_captura = 0  # Para mostrar feedback visual
        self.tiempo_mostrar_puntos = 0.0  # Tiempo para mostrar puntos ganados
        self.enemigos_cerca_salida = []  # Lista de enemigos cerca de salida
    
    def _buscar_posicion_cercana(self, posicion: Tuple[int, int]) -> Tuple[int, int]:
        """Busca una posición transitable cercana a la posición dada."""
        fila, col = posicion
        for radio in range(1, 10):
            for df in range(-radio, radio + 1):
                for dc in range(-radio, radio + 1):
                    nueva_fila = fila + df
                    nueva_col = col + dc
                    if (self.mapa.es_posicion_valida(nueva_fila, nueva_col) and
                        self.mapa.es_transitable_por_jugador(nueva_fila, nueva_col)):
                        return (nueva_fila, nueva_col)
        return posicion
    
    def _crear_enemigos(self) -> None:
        """Crea exactamente 3 enemigos en esquinas superior e inferior izquierda."""
        cantidad = 3  # Siempre 3 enemigos en modo cazador
        velocidad_base = self.config["velocidad_enemigos"]
        # Aumentar velocidad según dificultad
        velocidad = velocidad_base * 1.3  # 30% más rápido
        tiempo_respawn = 10.0  # No se usa en este modo, pero necesario para Enemigo
        
        # Obtener posiciones ya ocupadas
        posiciones_ocupadas = set()
        pos_jugador = self.jugador.obtener_posicion()
        posiciones_salida = self.mapa.obtener_posiciones_salida()
        posiciones_ocupadas.add(pos_jugador)
        for salida in posiciones_salida:
            posiciones_ocupadas.add(salida)
        
        # Esquinas objetivo: superior izquierda e inferior izquierda
        esquinas_objetivo = [
            (1, 1),  # Esquina superior izquierda
            (self.mapa.alto - 2, 1)  # Esquina inferior izquierda
        ]
        
        # Crear enemigos en las esquinas
        for i in range(cantidad):
            # Alternar entre las dos esquinas
            esquina_target = esquinas_objetivo[i % len(esquinas_objetivo)]
            
            # Buscar posición válida cerca de la esquina objetivo
            posicion = self._buscar_posicion_cercana_esquina(esquina_target, posiciones_ocupadas)
            
            if posicion:
                enemigo = Enemigo(
                    posicion[0],
                    posicion[1],
                    velocidad=velocidad,
                    tiempo_respawn=tiempo_respawn
                )
                self.enemigos.append(enemigo)
                posiciones_ocupadas.add(posicion)
            else:
                # Fallback: posición aleatoria
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
    
    def _buscar_posicion_cercana_esquina(self, esquina: Tuple[int, int], posiciones_ocupadas: set) -> Optional[Tuple[int, int]]:
        """
        Busca una posición válida cerca de una esquina objetivo.
        
        Args:
            esquina: Tupla (fila, columna) de la esquina objetivo.
            posiciones_ocupadas: Conjunto de posiciones ya ocupadas.
        
        Returns:
            Tupla (fila, columna) o None si no se encuentra.
        """
        fila_target, col_target = esquina
        
        # Buscar en un radio alrededor de la esquina
        for radio in range(0, 10):
            for df in range(-radio, radio + 1):
                for dc in range(-radio, radio + 1):
                    fila = fila_target + df
                    col = col_target + dc
                    posicion = (fila, col)
                    
                    # Verificar que sea válida y transitable
                    if (self.mapa.es_posicion_valida(fila, col) and
                        self.mapa.es_transitable_por_enemigo(fila, col) and
                        posicion not in posiciones_ocupadas):
                        return posicion
        
        return None
    
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
        distancia_minima = 5  # Distancia mínima del jugador
        
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
            
            # Verificar distancia mínima del jugador
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
        
        # Recuperar energía del jugador gradualmente (1 punto por segundo)
        self.jugador.actualizar_energia(delta_tiempo, tasa_recuperacion=1.0)
        
        # Verificar tiempo límite
        if self.tiempo_juego >= self.tiempo_limite:
            self._terminar_juego()
            return
        
        # Verificar victoria: todos los enemigos capturados
        enemigos_vivos = [e for e in self.enemigos if e.esta_vivo()]
        if len(enemigos_vivos) == 0:
            self.victoria = True
            self._terminar_juego()
            return
        
        # Actualizar tiempo para mostrar puntos ganados
        if self.tiempo_mostrar_puntos > 0:
            self.tiempo_mostrar_puntos -= delta_tiempo
        
        # Actualizar enemigos (buscan la salida)
        self.enemigos_cerca_salida = []  # Resetear lista
        for enemigo in self.enemigos:
            if enemigo.esta_vivo():
                # Enemigos buscan la salida más cercana
                enemigo.actualizar(self.mapa, self.jugador, delta_tiempo, "cazador", None)
                
                # Verificar proximidad a salida (para advertencia visual)
                pos_enemigo = enemigo.obtener_posicion()
                posiciones_salida = self.mapa.obtener_posiciones_salida()
                for salida in posiciones_salida:
                    distancia = abs(pos_enemigo[0] - salida[0]) + abs(pos_enemigo[1] - salida[1])
                    if distancia <= 3:  # Enemigo está a 3 casillas o menos de una salida
                        self.enemigos_cerca_salida.append((enemigo, distancia))
                        break
                
                # Verificar si un enemigo llegó a la salida (el jugador pierde)
                if enemigo.ha_llegado_a_salida(self.mapa):
                    self._enemigo_escapo(enemigo)
                    # El juego termina inmediatamente si un enemigo escapa
                    return
                # Verificar si el jugador capturó a un enemigo (solo contacto)
                elif enemigo.obtener_posicion() == self.jugador.obtener_posicion():
                    self._capturar_enemigo(enemigo)
    
    def _enemigo_escapo(self, enemigo: Enemigo) -> None:
        """
        Maneja cuando un enemigo escapa por la salida.
        El jugador pierde puntos y el juego termina inmediatamente.
        
        Args:
            enemigo: Enemigo que escapó.
        """
        puntos_perdidos = self.config["puntos_perdidos_por_escape"]
        self.puntos = max(0, self.puntos - puntos_perdidos)
        self.enemigos_escapados += 1
        
        # El enemigo desaparece (no respawnea)
        enemigo.matar()
        
        # Si un enemigo escapa, el jugador pierde inmediatamente
        self.victoria = False
        self.juego_terminado = True
    
    def _capturar_enemigo(self, enemigo: Enemigo) -> None:
        """
        Maneja cuando el jugador captura a un enemigo (solo contacto).
        El jugador gana el doble de puntos que perdería si el enemigo escapara.
        Incluye sistema de combos por capturas rápidas.
        
        Args:
            enemigo: Enemigo capturado.
        """
        # El jugador gana el doble de puntos que perdería si escapara
        puntos_perdidos_por_escape = self.config["puntos_perdidos_por_escape"]
        puntos_ganados = puntos_perdidos_por_escape * 2
        
        # Sistema de combos: si capturas rápido, bono adicional
        tiempo_desde_ultima_captura = self.tiempo_juego - self.ultima_captura_tiempo
        if tiempo_desde_ultima_captura <= 5.0 and self.ultima_captura_tiempo > 0:
            # Captura rápida (menos de 5 segundos desde la última)
            self.combo_actual += 1
            bono_combo = min(20, self.combo_actual * 5)  # Hasta 20 puntos extra por combo
            puntos_ganados += bono_combo
        else:
            # Resetear combo si pasó mucho tiempo
            self.combo_actual = 1
        
        self.puntos += puntos_ganados
        self.enemigos_capturados += 1
        self.ultima_captura_tiempo = self.tiempo_juego
        
        # Guardar puntos ganados para feedback visual
        self.puntos_ganados_ultima_captura = puntos_ganados
        self.tiempo_mostrar_puntos = 2.0  # Mostrar por 2 segundos
        
        # El enemigo desaparece (no respawnea)
        enemigo.matar()
    
    def mover_jugador(self, direccion: str, corriendo: bool = False) -> bool:
        """
        Mueve al jugador en la dirección especificada.
        En modo cazador, el jugador puede pasar por Liana pero no por Tunel.
        
        Args:
            direccion: Dirección ("arriba", "abajo", "izquierda", "derecha").
            corriendo: Si True, el jugador corre.
            
        Returns:
            True si el movimiento fue exitoso, False en caso contrario.
        """
        if self.juego_terminado:
            return False
        
        movimiento_exitoso = False
        
        # Obtener posición actual
        pos_actual = self.jugador.obtener_posicion()
        nueva_fila, nueva_col = pos_actual[0], pos_actual[1]
        
        # Calcular nueva posición
        if direccion == "arriba":
            nueva_fila -= 1
        elif direccion == "abajo":
            nueva_fila += 1
        elif direccion == "izquierda":
            nueva_col -= 1
        elif direccion == "derecha":
            nueva_col += 1
        
        # Verificar transición con reglas del modo cazador
        if (self.mapa.es_posicion_valida(nueva_fila, nueva_col) and
            self.mapa.es_transitable_por_jugador(nueva_fila, nueva_col, modo="cazador")):
            # Verificar energía antes de mover
            if corriendo:
                if not self.jugador.puede_correr():
                    return False
                self.jugador.consumir_energia(self.jugador.ENERGIA_CORRER)
            else:
                self.jugador.consumir_energia(self.jugador.ENERGIA_CAMINAR)
            
            # Realizar el movimiento
            self.jugador.fila = nueva_fila
            self.jugador.columna = nueva_col
            
            # Perder 1% de energía cada 3 movimientos
            self.jugador.movimientos_desde_ultima_perdida += 1
            if self.jugador.movimientos_desde_ultima_perdida >= 3:
                porcentaje_perdida = self.jugador.energia_maxima * 0.01
                self.jugador.consumir_energia(int(porcentaje_perdida))
                self.jugador.movimientos_desde_ultima_perdida = 0
            
            movimiento_exitoso = True
        
        if movimiento_exitoso:
            self.movimientos += 1
        
        return movimiento_exitoso
    
    def _terminar_juego(self) -> None:
        """Termina el juego y registra el puntaje."""
        self.juego_terminado = True
        
        # Calcular puntos finales
        # Bonus por tiempo restante
        tiempo_restante = max(0.0, self.tiempo_limite - self.tiempo_juego)
        bonus_tiempo = int(tiempo_restante * 2)  # 2 puntos por segundo restante
        self.puntos += bonus_tiempo
        
        # Bono por energía restante (0.3 puntos por punto de energía)
        energia_restante = self.jugador.obtener_energia_actual()
        bono_energia = int(energia_restante * 0.3)
        self.puntos += bono_energia
        
        # Bono por velocidad de captura (si capturaste todos rápido)
        if self.enemigos_capturados == 3 and self.tiempo_juego < self.tiempo_limite * 0.5:
            # Capturaste todos en menos de la mitad del tiempo
            bono_velocidad = 50
            self.puntos += bono_velocidad
        elif self.enemigos_capturados == 3 and self.tiempo_juego < self.tiempo_limite * 0.75:
            # Capturaste todos en menos de 3/4 del tiempo
            bono_velocidad = 25
            self.puntos += bono_velocidad
        
        # Bonus por dificultad (ahora incluye Fácil)
        if self.dificultad == Dificultad.DIFICIL:
            self.puntos = int(self.puntos * 1.5)
        elif self.dificultad == Dificultad.NORMAL:
            self.puntos = int(self.puntos * 1.2)
        elif self.dificultad == Dificultad.FACIL:
            self.puntos = int(self.puntos * 1.1)
        
        # Puntos mínimos garantizados
        self.puntos = max(50, int(self.puntos))
        
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
        enemigos_vivos = len([e for e in self.enemigos if e.esta_vivo()])
        
        return {
            "tiempo_juego": self.tiempo_juego,
            "tiempo_restante": tiempo_restante,
            "puntos": self.puntos,
            "movimientos": self.movimientos,
            "enemigos_capturados": self.enemigos_capturados,
            "enemigos_escapados": self.enemigos_escapados,
            "enemigos_vivos": enemigos_vivos,
            "energia_jugador": self.jugador.obtener_energia_actual(),
            "energia_maxima": self.jugador.obtener_energia_maxima(),
            "juego_terminado": self.juego_terminado,
            "victoria": self.victoria,
            "combo_actual": self.combo_actual,
            "puntos_ganados_ultima_captura": self.puntos_ganados_ultima_captura if self.tiempo_mostrar_puntos > 0 else 0,
            "enemigos_cerca_salida": len(self.enemigos_cerca_salida)
        }
    
    def __repr__(self) -> str:
        """Representación del modo de juego."""
        estado = "terminado" if self.juego_terminado else "activo"
        return f"GameModeCazador(jugador='{self.nombre_jugador}', estado={estado}, puntos={self.puntos}, capturados={self.enemigos_capturados})"
