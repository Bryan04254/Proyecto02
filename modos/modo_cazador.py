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
        # ============================================
        # CONFIGURACIÓN BÁSICA
        # ============================================
        self.nombre_jugador = nombre_jugador
        self.dificultad = dificultad
        # Obtener configuración según la dificultad (energía, velocidad enemigos, etc.)
        self.config = ConfiguracionDificultad.obtener_configuracion(dificultad)
        self.tiempo_limite = tiempo_limite  # Tiempo límite para capturar a los 3 enemigos
        
        # ============================================
        # GENERACIÓN O USO DE MAPA
        # ============================================
        # Generar o usar mapa existente
        if mapa is None:
            # Crear nuevo mapa con modo cazador
            # En modo cazador: menos lianas y túneles (50% menos que modo escapa)
            generador = GeneradorMapa(ancho=ancho_mapa, alto=alto_mapa)
            self.mapa = generador.generar_mapa(modo="cazador")
        else:
            # Usar mapa proporcionado
            self.mapa = mapa
        
        # ============================================
        # POSICIÓN INICIAL DEL JUGADOR
        # ============================================
        # El jugador siempre empieza en la esquina inferior derecha
        pos_inicio = (self.mapa.alto - 2, self.mapa.ancho - 2)
        # Verificar que la posición sea transitable
        if not self.mapa.es_transitable_por_jugador(pos_inicio[0], pos_inicio[1], modo="cazador"):
            # Buscar posición cercana válida si la esquina no es transitable
            pos_inicio = self._buscar_posicion_cercana(pos_inicio)
        
        # Crear jugador con energía inicial según dificultad
        energia_inicial = self.config["energia_inicial_jugador"]
        self.jugador = Jugador(pos_inicio[0], pos_inicio[1], energia_maxima=energia_inicial)
        
        # ============================================
        # CREACIÓN DE ENEMIGOS
        # ============================================
        # Crear exactamente 3 enemigos que intentan escapar por la salida
        # Los enemigos aparecen en esquinas superior e inferior izquierda
        self.enemigos: List[Enemigo] = []
        self._crear_enemigos()
        
        # ============================================
        # ESTADO DEL JUEGO
        # ============================================
        self.tiempo_juego = 0.0  # Tiempo transcurrido en segundos
        self.puntos = self.config["puntos_base_cazador"]  # Puntos iniciales
        self.juego_terminado = False  # Flag de fin de juego
        self.victoria = False  # True si capturó a los 3 enemigos, False si uno escapó
        self.enemigos_capturados = 0  # Contador de enemigos capturados
        self.enemigos_escapados = 0  # Contador de enemigos que escaparon
        self.movimientos = 0  # Contador de movimientos del jugador
        
        # ============================================
        # SISTEMA DE COMBOS Y FEEDBACK VISUAL
        # ============================================
        self.ultima_captura_tiempo = 0.0  # Tiempo de la última captura (para combos)
        self.combo_actual = 0  # Contador de combos (capturas rápidas consecutivas)
        self.puntos_ganados_ultima_captura = 0  # Puntos ganados en última captura (para feedback visual)
        self.tiempo_mostrar_puntos = 0.0  # Tiempo restante para mostrar puntos ganados
        self.enemigos_cerca_salida = []  # Lista de enemigos cerca de salida (para advertencia visual)
    
    def _buscar_posicion_cercana(self, posicion: Tuple[int, int]) -> Tuple[int, int]:
        """
        Busca una posición transitable cercana a la posición dada.
        
        Utiliza búsqueda en espiral desde la posición objetivo hasta encontrar
        una casilla transitable para el jugador en modo cazador.
        
        Args:
            posicion: Tupla (fila, columna) de la posición objetivo.
            
        Returns:
            Tupla (fila, columna) de la posición válida más cercana.
            Si no se encuentra, retorna la posición original.
        """
        fila, col = posicion
        # Buscar en espiral desde la posición objetivo
        for radio in range(1, 10):
            for df in range(-radio, radio + 1):
                for dc in range(-radio, radio + 1):
                    nueva_fila = fila + df
                    nueva_col = col + dc
                    # Verificar que sea válida y transitable para el jugador en modo cazador
                    if (self.mapa.es_posicion_valida(nueva_fila, nueva_col) and
                        self.mapa.es_transitable_por_jugador(nueva_fila, nueva_col, modo="cazador")):
                        return (nueva_fila, nueva_col)
        # Si no se encuentra, retornar posición original
        return posicion
    
    def _crear_enemigos(self) -> None:
        """
        Crea exactamente 3 enemigos en esquinas superior e inferior izquierda.
        
        Los enemigos se distribuyen entre las dos esquinas izquierdas del mapa.
        Cada enemigo tiene velocidad aumentada según la dificultad y busca
        activamente la salida más cercana usando pathfinding BFS.
        """
        cantidad = 3  # Siempre 3 enemigos en modo cazador (especificación)
        velocidad_base = self.config["velocidad_enemigos"]
        # Aumentar velocidad según dificultad (30% más rápido que la base)
        velocidad = velocidad_base * 1.3
        tiempo_respawn = 10.0  # No se usa en este modo (enemigos no respawnean), pero necesario para Enemigo
        
        # ============================================
        # PREPARAR POSICIONES OCUPADAS
        # ============================================
        # Obtener posiciones ya ocupadas (jugador, salidas)
        posiciones_ocupadas = set()
        pos_jugador = self.jugador.obtener_posicion()
        posiciones_salida = self.mapa.obtener_posiciones_salida()
        posiciones_ocupadas.add(pos_jugador)
        for salida in posiciones_salida:
            posiciones_ocupadas.add(salida)
        
        # ============================================
        # ESQUINAS OBJETIVO PARA ENEMIGOS
        # ============================================
        # Los enemigos aparecen en esquinas opuestas al jugador:
        # - Esquina superior izquierda: (1, 1)
        # - Esquina inferior izquierda: (alto - 2, 1)
        esquinas_objetivo = [
            (1, 1),  # Esquina superior izquierda
            (self.mapa.alto - 2, 1)  # Esquina inferior izquierda
        ]
        
        # ============================================
        # CREAR ENEMIGOS
        # ============================================
        # Crear enemigos distribuyéndolos entre las dos esquinas
        for i in range(cantidad):
            # Alternar entre las dos esquinas disponibles
            esquina_target = esquinas_objetivo[i % len(esquinas_objetivo)]
            
            # Buscar posición válida cerca de la esquina objetivo
            posicion = self._buscar_posicion_cercana_esquina(esquina_target, posiciones_ocupadas)
            
            if posicion:
                # Crear enemigo en la posición encontrada
                enemigo = Enemigo(
                    posicion[0],
                    posicion[1],
                    velocidad=velocidad,
                    tiempo_respawn=tiempo_respawn
                )
                self.enemigos.append(enemigo)
                posiciones_ocupadas.add(posicion)
            else:
                # Fallback: si no se encuentra posición cerca de la esquina, usar posición aleatoria
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
        Actualiza el estado del juego en cada frame.
        
        Este método se llama continuamente durante el juego para:
        - Actualizar el tiempo transcurrido
        - Recuperar energía del jugador
        - Mover enemigos (IA de búsqueda de salida)
        - Verificar condiciones de victoria/derrota
        - Detectar capturas y escapes
        
        Args:
            delta_tiempo: Tiempo transcurrido desde la última actualización (segundos).
        """
        # Si el juego ya terminó, no actualizar nada más
        if self.juego_terminado:
            return
        
        # Actualizar tiempo de juego
        self.tiempo_juego += delta_tiempo
        
        # ============================================
        # ACTUALIZACIÓN DEL JUGADOR
        # ============================================
        # Recuperar energía del jugador gradualmente (1 punto por segundo)
        self.jugador.actualizar_energia(delta_tiempo, tasa_recuperacion=1.0)
        
        # ============================================
        # VERIFICACIÓN DE TIEMPO LÍMITE
        # ============================================
        # Si se agotó el tiempo, terminar el juego
        if self.tiempo_juego >= self.tiempo_limite:
            self._terminar_juego()
            return
        
        # ============================================
        # VERIFICACIÓN DE VICTORIA
        # ============================================
        # Victoria: todos los enemigos fueron capturados
        enemigos_vivos = [e for e in self.enemigos if e.esta_vivo()]
        if len(enemigos_vivos) == 0:
            self.victoria = True
            self._terminar_juego()
            return
        
        # ============================================
        # ACTUALIZACIÓN DE FEEDBACK VISUAL
        # ============================================
        # Actualizar tiempo para mostrar puntos ganados (feedback visual)
        if self.tiempo_mostrar_puntos > 0:
            self.tiempo_mostrar_puntos -= delta_tiempo
        
        # ============================================
        # ACTUALIZACIÓN DE ENEMIGOS (IA)
        # ============================================
        # Resetear lista de enemigos cerca de salida
        self.enemigos_cerca_salida = []
        
        # Actualizar cada enemigo vivo
        for enemigo in self.enemigos:
            if enemigo.esta_vivo():
                # Enemigos buscan la salida más cercana usando pathfinding BFS
                # En modo cazador, los enemigos pueden pasar por Túneles pero no por Lianas
                enemigo.actualizar(self.mapa, self.jugador, delta_tiempo, "cazador", None)
                
                # ============================================
                # DETECCIÓN DE PROXIMIDAD A SALIDA
                # ============================================
                # Verificar si el enemigo está cerca de una salida (para advertencia visual)
                pos_enemigo = enemigo.obtener_posicion()
                posiciones_salida = self.mapa.obtener_posiciones_salida()
                for salida in posiciones_salida:
                    distancia = abs(pos_enemigo[0] - salida[0]) + abs(pos_enemigo[1] - salida[1])
                    if distancia <= 3:  # Enemigo está a 3 casillas o menos de una salida
                        self.enemigos_cerca_salida.append((enemigo, distancia))
                        break
                
                # ============================================
                # DETECCIÓN DE ESCAPE (DERROTA)
                # ============================================
                # Si un enemigo llegó a la salida, el jugador pierde inmediatamente
                if enemigo.ha_llegado_a_salida(self.mapa):
                    self._enemigo_escapo(enemigo)
                    # El juego termina inmediatamente si un enemigo escapa
                    return
                
                # ============================================
                # DETECCIÓN DE CAPTURA (VICTORIA PARCIAL)
                # ============================================
                # Si el jugador está en la misma posición que un enemigo, lo captura
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
        """
        Termina el juego y calcula el puntaje final.
        
        Calcula los puntos finales basándose en:
        - Tiempo restante
        - Energía restante
        - Velocidad de captura
        - Dificultad
        
        Luego registra el puntaje en el ScoreBoard.
        """
        self.juego_terminado = True
        
        # ============================================
        # CÁLCULO DE PUNTAJE FINAL
        # ============================================
        
        # Bonus por tiempo restante (2 puntos por segundo restante)
        tiempo_restante = max(0.0, self.tiempo_limite - self.tiempo_juego)
        bonus_tiempo = int(tiempo_restante * 2)
        self.puntos += bonus_tiempo
        
        # Bono por energía restante (0.3 puntos por punto de energía)
        energia_restante = self.jugador.obtener_energia_actual()
        bono_energia = int(energia_restante * 0.3)
        self.puntos += bono_energia
        
        # ============================================
        # BONO POR VELOCIDAD DE CAPTURA
        # ============================================
        # Recompensa por capturar a todos los enemigos rápidamente
        if self.enemigos_capturados == 3 and self.tiempo_juego < self.tiempo_limite * 0.5:
            # Capturaste todos en menos de la mitad del tiempo (máximo bono)
            bono_velocidad = 50
            self.puntos += bono_velocidad
        elif self.enemigos_capturados == 3 and self.tiempo_juego < self.tiempo_limite * 0.75:
            # Capturaste todos en menos de 3/4 del tiempo (bono medio)
            bono_velocidad = 25
            self.puntos += bono_velocidad
        
        # ============================================
        # MULTIPLICADOR POR DIFICULTAD
        # ============================================
        # Aplica multiplicador según la dificultad
        if self.dificultad == Dificultad.DIFICIL:
            self.puntos = int(self.puntos * 1.5)  # 50% más puntos
        elif self.dificultad == Dificultad.NORMAL:
            self.puntos = int(self.puntos * 1.2)  # 20% más puntos
        elif self.dificultad == Dificultad.FACIL:
            self.puntos = int(self.puntos * 1.1)  # 10% más puntos
        
        # Puntos mínimos garantizados (50 puntos mínimo)
        self.puntos = max(50, int(self.puntos))
        
        # ============================================
        # REGISTRO DE PUNTAJE
        # ============================================
        # Registrar el puntaje en el ScoreBoard
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
