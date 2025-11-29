"""
Pantallas del juego: Menú principal, juego, puntajes, fin de juego.
"""

import pygame
import math
import random
from typing import Tuple, Optional, List, Callable
from datetime import datetime

from modelo.mapa import Mapa
from modelo.jugador import Jugador
from logica.generador_mapa import GeneradorMapa
from logica import Dificultad
from sistema.puntajes import ScoreBoard, Puntaje, ModoJuego
from modos import GameModeEscapa, GameModeCazador

from .config import Colores, Config
from .componentes import Boton, BarraEnergia, SistemaParticulas, CuadroTexto
from .renderizador import RenderizadorMapa


class PantallaBase:
    """Clase base para todas las pantallas."""
    
    def __init__(self, ancho: int, alto: int):
        self.ancho = ancho
        self.alto = alto
        self.siguiente_pantalla = None
        self.datos_retorno = {}
        
    def manejar_evento(self, evento: pygame.event.Event):
        """Maneja eventos de la pantalla."""
        pass
    
    def actualizar(self, dt: float):
        """Actualiza la lógica de la pantalla."""
        pass
    
    def dibujar(self, superficie: pygame.Surface):
        """Dibuja la pantalla."""
        pass


class MenuPrincipal(PantallaBase):
    """Menú principal del juego con animaciones y estilo retro."""
    
    def __init__(self, ancho: int, alto: int):
        super().__init__(ancho, alto)
        
        # Fuentes
        self.fuente_titulo = None
        self.fuente_subtitulo = None
        self.fuente_boton = None
        self.fuente_info = None
        
        # Estado
        self.tiempo = 0
        self.particulas = SistemaParticulas()
        self.estrellas = self._generar_estrellas(100)
        
        # Input del nombre
        self.cuadro_nombre = CuadroTexto(
            ancho // 2 - 200, 320, 400, 50,
            placeholder="Tu nombre..."
        )
        self.nombre_jugador = ""
        
        # Botones
        self.botones = []
        self._inicializar_botones()
        
    def _generar_estrellas(self, cantidad: int) -> List[dict]:
        """Genera estrellas de fondo."""
        estrellas = []
        for _ in range(cantidad):
            estrellas.append({
                'x': random.randint(0, self.ancho),
                'y': random.randint(0, self.alto),
                'tamano': random.uniform(1, 3),
                'velocidad': random.uniform(0.5, 2),
                'parpadeo_offset': random.uniform(0, math.pi * 2)
            })
        return estrellas
    
    def _inicializar_botones(self):
        """Inicializa los botones del menú."""
        centro_x = self.ancho // 2
        
        self.botones = [
            Boton(centro_x - 150, 410, 300, 55, "MODO ESCAPA",
                  color=Colores.CYAN_NEON,
                  accion=lambda: self._seleccionar_modo("escapa")),
            Boton(centro_x - 150, 485, 300, 55, "MODO CAZADOR",
                  color=Colores.MAGENTA_NEON,
                  accion=lambda: self._seleccionar_modo("cazador")),
            Boton(centro_x - 150, 560, 300, 55, "PUNTAJES",
                  color=Colores.AMARILLO_NEON,
                  accion=self._ver_puntajes),
            Boton(centro_x - 150, 635, 300, 55, "INFORMACION",
                  color=Colores.VERDE_NEON,
                  accion=self._ver_informacion),
            Boton(centro_x - 150, 710, 300, 55, "SALIR",
                  color=Colores.ROJO_NEON,
                  accion=self._salir),
        ]
    
    def _seleccionar_modo(self, modo: str):
        """Selecciona un modo de juego."""
        nombre = self.cuadro_nombre.obtener_texto()
        if not nombre:
            nombre = "Jugador"
        
        self.nombre_jugador = nombre
        self.siguiente_pantalla = "juego"
        self.datos_retorno = {
            "modo": modo,
            "nombre": nombre
        }
    
    def _ver_puntajes(self):
        """Navega a la pantalla de puntajes."""
        self.siguiente_pantalla = "puntajes"
    
    def _ver_informacion(self):
        """Navega a la pantalla de información."""
        self.siguiente_pantalla = "informacion"
    
    def _salir(self):
        """Sale del juego."""
        self.siguiente_pantalla = "salir"
    
    def inicializar_fuentes(self):
        """Inicializa las fuentes después de iniciar pygame."""
        pygame.font.init()
        self.fuente_titulo = pygame.font.Font(None, 86)
        self.fuente_subtitulo = pygame.font.Font(None, 36)
        self.fuente_boton = pygame.font.Font(None, 32)
        self.fuente_info = pygame.font.Font(None, 24)
    
    def manejar_evento(self, evento: pygame.event.Event):
        """Maneja eventos del menú."""
        self.cuadro_nombre.manejar_evento(evento)
        
        for boton in self.botones:
            boton.manejar_evento(evento)
    
    def actualizar(self, dt: float):
        """Actualiza animaciones del menú."""
        self.tiempo += dt
        
        # Actualizar cuadro de texto
        self.cuadro_nombre.actualizar(dt)
        
        # Actualizar botones
        pos_mouse = pygame.mouse.get_pos()
        for boton in self.botones:
            boton.actualizar(pos_mouse, dt)
        
        # Actualizar estrellas
        for estrella in self.estrellas:
            estrella['y'] += estrella['velocidad']
            if estrella['y'] > self.alto:
                estrella['y'] = 0
                estrella['x'] = random.randint(0, self.ancho)
        
        # Actualizar partículas
        self.particulas.actualizar(dt)
        
        # Emitir partículas ocasionalmente
        if random.random() < 0.1:
            x = random.randint(0, self.ancho)
            self.particulas.emitir(x, 0, Colores.CYAN_NEON, 1)
    
    def dibujar(self, superficie: pygame.Surface):
        """Dibuja el menú principal."""
        # Fondo con gradiente
        superficie.fill(Colores.FONDO_OSCURO)
        
        # Dibujar estrellas
        for estrella in self.estrellas:
            alpha = int(100 + 100 * math.sin(self.tiempo * 2 + estrella['parpadeo_offset']))
            color = (*Colores.TEXTO_SECUNDARIO[:3],)
            tamano = int(estrella['tamano'])
            pygame.draw.circle(superficie, color, 
                             (int(estrella['x']), int(estrella['y'])), tamano)
        
        # Dibujar partículas
        self.particulas.dibujar(superficie)
        
        # Título con efecto de glow
        self._dibujar_titulo(superficie)
        
        # Subtítulo
        subtitulo = self.fuente_subtitulo.render(
            "Un juego de laberinto con emoción", True, Colores.TEXTO_SECUNDARIO
        )
        subtitulo_rect = subtitulo.get_rect(center=(self.ancho // 2, 200))
        superficie.blit(subtitulo, subtitulo_rect)
        
        # Instrucción para el nombre
        instruccion = self.fuente_info.render(
            "Ingresa tu nombre para guardar tus puntajes:", True, Colores.TEXTO
        )
        instruccion_rect = instruccion.get_rect(center=(self.ancho // 2, 285))
        superficie.blit(instruccion, instruccion_rect)
        
        # Cuadro de nombre
        self.cuadro_nombre.dibujar(superficie, self.fuente_boton)
        
        # Botones
        for boton in self.botones:
            boton.dibujar(superficie, self.fuente_boton)
    
    def _dibujar_titulo(self, superficie: pygame.Surface):
        """Dibuja el título con efectos."""
        titulo_texto = "ESCAPA DEL LABERINTO"
        
        # Efecto de onda en el color
        offset_color = int(50 * math.sin(self.tiempo * 2))
        color_titulo = (
            max(0, min(255, Colores.CYAN_NEON[0] + offset_color)),
            Colores.CYAN_NEON[1],
            max(0, min(255, Colores.CYAN_NEON[2] - offset_color))
        )
        
        # Sombra
        sombra = self.fuente_titulo.render(titulo_texto, True, Colores.FONDO_PANEL)
        sombra_rect = sombra.get_rect(center=(self.ancho // 2 + 3, 103))
        superficie.blit(sombra, sombra_rect)
        
        # Título principal
        titulo = self.fuente_titulo.render(titulo_texto, True, color_titulo)
        titulo_rect = titulo.get_rect(center=(self.ancho // 2, 100))
        superficie.blit(titulo, titulo_rect)
    
class PantallaJuego(PantallaBase):
    """Pantalla principal del juego."""
    
    def __init__(self, ancho: int, alto: int, modo: str, nombre_jugador: str):
        super().__init__(ancho, alto)
        
        self.modo = modo
        self.nombre_jugador = nombre_jugador
        
        # Modo de juego (GameModeEscapa o GameModeCazador)
        self.modo_juego = None
        
        # Componentes del juego (para compatibilidad con código existente)
        self.mapa = None
        self.jugador = None
        self.renderizador = RenderizadorMapa()
        self.barra_energia = None
        self.particulas = SistemaParticulas()
        
        # Dimensiones dinámicas del mapa
        self.mapa_offset_x = 20
        self.mapa_offset_y = 20
        self.widget_x = 0
        self.widget_y = 0
        
        # Estado del juego
        self.tiempo_juego = 0
        self.tiempo_limite = Config.TIEMPO_PARTIDA_ESCAPA if modo == "escapa" else Config.TIEMPO_PARTIDA_CAZADOR
        self.puntos = 0
        self.pausado = False
        self.juego_terminado = False
        self.victoria = False
        self.movimientos = 0
        
        # Fuentes
        self.fuente_ui = None
        self.fuente_titulo = None
        self.fuente_grande = None
        
        # Botones de pausa
        self.botones_pausa = []
        
        # Inicializar juego
        self._inicializar_juego()
    
    def _calcular_dimensiones_mapa(self) -> Tuple[int, int, int]:
        """
        Calcula las dimensiones del mapa y tamaño de celda basado en el tamaño de la pantalla.
        El mapa ahora ocupa casi toda la pantalla.
        
        Returns:
            Tupla (ancho_mapa, alto_mapa, tamano_celda)
        """
        # Calcular espacio disponible para el mapa (casi toda la pantalla)
        # Solo dejamos un pequeño margen y espacio para el widget de info en esquina
        margen_x = 20
        margen_y = 20
        espacio_widget = 200  # Espacio para el widget pequeño en esquina
        
        espacio_ancho = self.ancho - margen_x * 2
        espacio_alto = self.alto - margen_y * 2
        
        # Calcular tamaño de celda basado en el espacio disponible
        # Usamos un tamaño base y lo ajustamos según la pantalla
        tamano_celda_base = 40  # Tamaño base más grande
        factor_escala_ancho = espacio_ancho / (Config.MAPA_ANCHO * tamano_celda_base)
        factor_escala_alto = espacio_alto / (Config.MAPA_ALTO * tamano_celda_base)
        factor_escala = min(factor_escala_ancho, factor_escala_alto)
        
        # Asegurar un tamaño mínimo y máximo razonable (más grande)
        tamano_celda = max(30, min(80, int(tamano_celda_base * factor_escala)))
        
        # Calcular dimensiones del mapa basadas en el tamaño de celda
        # Usar todo el espacio disponible
        ancho_mapa = min(Config.MAPA_ANCHO, espacio_ancho // tamano_celda)
        alto_mapa = min(Config.MAPA_ALTO, espacio_alto // tamano_celda)
        
        # Asegurar un mínimo razonable
        ancho_mapa = max(15, ancho_mapa)
        alto_mapa = max(10, alto_mapa)
        
        return ancho_mapa, alto_mapa, tamano_celda
    
    def _inicializar_juego(self):
        """Inicializa los componentes del juego."""
        # Calcular dimensiones del mapa dinámicamente
        ancho_mapa, alto_mapa, tamano_celda = self._calcular_dimensiones_mapa()
        
        # Actualizar renderizador con el nuevo tamaño de celda
        self.renderizador = RenderizadorMapa(tamano_celda=tamano_celda)
        
        # Crear modo de juego según el modo seleccionado
        if self.modo == "escapa":
            self.modo_juego = GameModeEscapa(
                nombre_jugador=self.nombre_jugador,
                dificultad=Dificultad.NORMAL,
                ancho_mapa=ancho_mapa,
                alto_mapa=alto_mapa
            )
        else:  # cazador
            self.modo_juego = GameModeCazador(
                nombre_jugador=self.nombre_jugador,
                dificultad=Dificultad.NORMAL,
                tiempo_limite=Config.TIEMPO_PARTIDA_CAZADOR,
                ancho_mapa=ancho_mapa,
                alto_mapa=alto_mapa
            )
        
        # Obtener referencias del modo de juego
        self.mapa = self.modo_juego.mapa
        self.jugador = self.modo_juego.jugador
        
        # Calcular posición del mapa (centrado, usando casi toda la pantalla)
        mapa_ancho_px = ancho_mapa * tamano_celda
        mapa_alto_px = alto_mapa * tamano_celda
        
        # Centrar el mapa
        self.mapa_offset_x = (self.ancho - mapa_ancho_px) // 2
        self.mapa_offset_y = (self.alto - mapa_alto_px) // 2
        
        # Widget pequeño en esquina superior derecha
        widget_ancho = 200
        widget_alto = 120
        self.widget_x = self.ancho - widget_ancho - 20
        self.widget_y = 20
        
        # Barra de energía (más pequeña para el widget)
        self.barra_energia = BarraEnergia(self.widget_x + 10, self.widget_y + 60, widget_ancho - 20, 20)
        
        # Resetear renderizador
        self.renderizador.resetear_posicion_jugador(self.jugador)
    
    def inicializar_fuentes(self):
        """Inicializa las fuentes."""
        self.fuente_ui = pygame.font.Font(None, 28)
        self.fuente_titulo = pygame.font.Font(None, 42)
        self.fuente_grande = pygame.font.Font(None, 72)
        
        # Crear botones de pausa
        centro_x = self.ancho // 2
        self.botones_pausa = [
            Boton(centro_x - 120, 350, 240, 50, "▶ CONTINUAR",
                  color=Colores.VERDE_NEON,
                  accion=self._continuar),
            Boton(centro_x - 120, 420, 240, 50, "REINICIAR",
                  color=Colores.AMARILLO_NEON,
                  accion=self._reiniciar),
            Boton(centro_x - 120, 490, 240, 50, "MENU",
                  color=Colores.ROJO_NEON,
                  accion=self._ir_menu),
        ]
    
    def _continuar(self):
        """Continúa el juego."""
        self.pausado = False
    
    def _reiniciar(self):
        """Reinicia la partida."""
        self._inicializar_juego()
        self.tiempo_juego = 0
        self.puntos = 0
        self.movimientos = 0
        self.pausado = False
        self.juego_terminado = False
        self.victoria = False
        # El modo_juego ya tiene su estado reseteado al inicializarse
    
    def _ir_menu(self):
        """Vuelve al menú principal."""
        self.siguiente_pantalla = "menu"
    
    def manejar_evento(self, evento: pygame.event.Event):
        """Maneja eventos del juego."""
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                if self.juego_terminado:
                    self._ir_menu()
                else:
                    self.pausado = not self.pausado
                return
            
            if self.pausado or self.juego_terminado:
                return
            
            # Colocar trampa (solo en modo Escapa)
            if self.modo == "escapa" and (evento.key == pygame.K_t or evento.key == pygame.K_SPACE):
                if self.modo_juego.colocar_trampa():
                    # Partículas al colocar trampa
                    pos = self.jugador.obtener_posicion()
                    tamano_celda = self.renderizador.tamano_celda
                    x = self.mapa_offset_x + pos[1] * tamano_celda + tamano_celda // 2
                    y = self.mapa_offset_y + pos[0] * tamano_celda + tamano_celda // 2
                    self.particulas.emitir(x, y, Colores.ROJO_NEON, 5)
                return
            
            # Movimiento del jugador
            corriendo = pygame.key.get_mods() & pygame.KMOD_SHIFT
            movio = False
            direccion = None
            
            if evento.key == pygame.K_UP or evento.key == pygame.K_w:
                direccion = "arriba"
                movio = self.modo_juego.mover_jugador("arriba", corriendo)
            elif evento.key == pygame.K_DOWN or evento.key == pygame.K_s:
                direccion = "abajo"
                movio = self.modo_juego.mover_jugador("abajo", corriendo)
            elif evento.key == pygame.K_LEFT or evento.key == pygame.K_a:
                direccion = "izquierda"
                movio = self.modo_juego.mover_jugador("izquierda", corriendo)
            elif evento.key == pygame.K_RIGHT or evento.key == pygame.K_d:
                direccion = "derecha"
                movio = self.modo_juego.mover_jugador("derecha", corriendo)
            
            if movio:
                # Partículas al moverse
                pos = self.jugador.obtener_posicion()
                tamano_celda = self.renderizador.tamano_celda
                x = self.mapa_offset_x + pos[1] * tamano_celda + tamano_celda // 2
                y = self.mapa_offset_y + pos[0] * tamano_celda + tamano_celda // 2
                color = Colores.NARANJA_NEON if corriendo else Colores.CYAN_NEON
                self.particulas.emitir(x, y, color, 3)
        
        # Eventos de botones en pausa
        if self.pausado:
            for boton in self.botones_pausa:
                boton.manejar_evento(evento)
    
    def _terminar_juego(self, victoria: bool):
        """Termina el juego."""
        # El modo_juego ya maneja la terminación y cálculo de puntos
        # Solo sincronizamos el estado visual
        if self.modo_juego:
            self.juego_terminado = self.modo_juego.juego_terminado
            self.victoria = self.modo_juego.victoria if hasattr(self.modo_juego, 'victoria') else victoria
            estado = self.modo_juego.obtener_estado()
            self.puntos = estado.get('puntos', 0)
            self.movimientos = estado.get('movimientos', 0)
            self.tiempo_juego = estado.get('tiempo_juego', 0)
        else:
            self.juego_terminado = True
            self.victoria = victoria
    
    def actualizar(self, dt: float):
        """Actualiza la lógica del juego."""
        if self.pausado or self.juego_terminado:
            # Actualizar botones de pausa
            if self.pausado:
                pos_mouse = pygame.mouse.get_pos()
                for boton in self.botones_pausa:
                    boton.actualizar(pos_mouse, dt)
            return
        
        # Actualizar el modo de juego (esto actualiza enemigos, trampas, etc.)
        if self.modo_juego:
            # Guardar estado anterior para detectar cambios
            estado_anterior = self.modo_juego.obtener_estado()
            enemigos_capturados_antes = estado_anterior.get('enemigos_capturados', 0)
            enemigos_escapados_antes = estado_anterior.get('enemigos_escapados', 0)
            
            self.modo_juego.actualizar(dt)
            
            # Sincronizar estado
            estado = self.modo_juego.obtener_estado()
            self.tiempo_juego = estado.get('tiempo_juego', 0)
            self.puntos = estado.get('puntos', 0)
            self.movimientos = estado.get('movimientos', 0)
            self.juego_terminado = estado.get('juego_terminado', False)
            self.victoria = estado.get('victoria', False) if 'victoria' in estado else False
            
            # Feedback visual: enemigo capturado
            if self.modo == "cazador":
                enemigos_capturados_ahora = estado.get('enemigos_capturados', 0)
                if enemigos_capturados_ahora > enemigos_capturados_antes:
                    # Partículas verdes al capturar
                    pos = self.jugador.obtener_posicion()
                    tamano_celda = self.renderizador.tamano_celda
                    x = self.mapa_offset_x + pos[1] * tamano_celda + tamano_celda // 2
                    y = self.mapa_offset_y + pos[0] * tamano_celda + tamano_celda // 2
                    self.particulas.emitir(x, y, Colores.VERDE_NEON, 8)
                
                # Feedback visual: enemigo escapó
                enemigos_escapados_ahora = estado.get('enemigos_escapados', 0)
                if enemigos_escapados_ahora > enemigos_escapados_antes:
                    # Partículas rojas al escapar
                    posiciones_salida = self.mapa.obtener_posiciones_salida()
                    for salida in posiciones_salida:
                        tamano_celda = self.renderizador.tamano_celda
                        x = self.mapa_offset_x + salida[1] * tamano_celda + tamano_celda // 2
                        y = self.mapa_offset_y + salida[0] * tamano_celda + tamano_celda // 2
                        self.particulas.emitir(x, y, Colores.ROJO_NEON, 10)
            
            # Verificar si el juego terminó
            if self.juego_terminado:
                return
        else:
            # Fallback al sistema antiguo si no hay modo_juego
            self.tiempo_juego += dt
            if self.tiempo_juego >= self.tiempo_limite:
                self._terminar_juego(False)
                return
            self.jugador.actualizar_energia(dt, tasa_recuperacion=2)
        
        # Actualizar componentes visuales
        self.renderizador.actualizar(dt, self.jugador)
        self.barra_energia.actualizar(self.jugador.obtener_porcentaje_energia(), dt)
        self.particulas.actualizar(dt)
    
    def dibujar(self, superficie: pygame.Surface):
        """Dibuja la pantalla del juego."""
        superficie.fill(Colores.FONDO_OSCURO)
        
        # Dibujar mapa con trampas y enemigos si están disponibles
        trampas = None
        enemigos = None
        if self.modo_juego and self.modo == "escapa":
            trampas = self.modo_juego.gestor_trampas.obtener_trampas_activas()
            enemigos = self.modo_juego.enemigos
        elif self.modo_juego and self.modo == "cazador":
            enemigos = self.modo_juego.enemigos
        
        self.renderizador.dibujar(
            superficie, self.mapa, self.jugador,
            offset=(self.mapa_offset_x, self.mapa_offset_y),
            trampas=trampas,
            enemigos=enemigos,
            modo=self.modo
        )
        
        # Dibujar partículas
        self.particulas.dibujar(superficie)
        
        # Panel lateral
        self._dibujar_panel_lateral(superficie)
        
        # Overlay de pausa
        if self.pausado:
            self._dibujar_pausa(superficie)
        
        # Overlay de fin de juego
        if self.juego_terminado:
            self._dibujar_fin_juego(superficie)
    
    def _dibujar_panel_lateral(self, superficie: pygame.Surface):
        """Dibuja un widget pequeño en la esquina superior derecha con tiempo, energía y trampas."""
        widget_ancho = 200
        # Aumentar altura si hay información de trampas
        widget_alto = 180 if self.modo == "escapa" else 120
        
        # Fondo del widget con transparencia
        widget_surface = pygame.Surface((widget_ancho, widget_alto), pygame.SRCALPHA)
        pygame.draw.rect(widget_surface, (*Colores.FONDO_PANEL, 220), 
                        (0, 0, widget_ancho, widget_alto), border_radius=10)
        pygame.draw.rect(widget_surface, Colores.CYAN_NEON, 
                        (0, 0, widget_ancho, widget_alto), width=2, border_radius=10)
        superficie.blit(widget_surface, (self.widget_x, self.widget_y))
        
        # Tiempo (más grande y destacado)
        tiempo_restante = max(0, self.tiempo_limite - self.tiempo_juego)
        minutos = int(tiempo_restante) // 60
        segundos = int(tiempo_restante) % 60
        color_tiempo = Colores.TEXTO if tiempo_restante > 30 else Colores.ROJO_NEON
        
        tiempo_texto = f"{minutos:02d}:{segundos:02d}"
        tiempo = self.fuente_ui.render(tiempo_texto, True, color_tiempo)
        tiempo_rect = tiempo.get_rect(center=(self.widget_x + widget_ancho // 2, self.widget_y + 30))
        superficie.blit(tiempo, tiempo_rect)
        
        # Etiqueta "Tiempo"
        tiempo_label = pygame.font.Font(None, 20).render("Tiempo", True, Colores.TEXTO_SECUNDARIO)
        label_rect = tiempo_label.get_rect(center=(self.widget_x + widget_ancho // 2, self.widget_y + 10))
        superficie.blit(tiempo_label, label_rect)
        
        # Energía
        energia_label = pygame.font.Font(None, 20).render("Energia", True, Colores.TEXTO_SECUNDARIO)
        superficie.blit(energia_label, (self.widget_x + 10, self.widget_y + 50))
        self.barra_energia.dibujar(superficie, self.fuente_ui)
        
        # Información de trampas (solo en modo Escapa)
        if self.modo == "escapa" and self.modo_juego:
            estado = self.modo_juego.obtener_estado()
            trampas_activas = estado.get("trampas_activas", 0)
            trampas_disponibles = estado.get("trampas_disponibles", 0)
            
            trampas_label = pygame.font.Font(None, 20).render("Trampas", True, Colores.TEXTO_SECUNDARIO)
            superficie.blit(trampas_label, (self.widget_x + 10, self.widget_y + 100))
            
            # Mostrar trampas disponibles (se regeneran cada 5 segundos)
            trampas_texto = f"Disponibles: {trampas_disponibles}/3"
            color_trampas = Colores.VERDE_NEON if trampas_disponibles > 0 else Colores.ROJO_NEON
            trampas_valor = self.fuente_ui.render(trampas_texto, True, color_trampas)
            superficie.blit(trampas_valor, (self.widget_x + 10, self.widget_y + 120))
            
            # Mostrar trampas activas en el mapa
            trampas_activas_texto = f"En mapa: {trampas_activas}"
            trampas_activas_valor = pygame.font.Font(None, 16).render(trampas_activas_texto, True, Colores.TEXTO_SECUNDARIO)
            superficie.blit(trampas_activas_valor, (self.widget_x + 10, self.widget_y + 140))
        
        # Información de enemigos (solo en modo Cazador)
        elif self.modo == "cazador" and self.modo_juego:
            estado = self.modo_juego.obtener_estado()
            enemigos_vivos = estado.get("enemigos_vivos", 0)
            enemigos_capturados = estado.get("enemigos_capturados", 0)
            enemigos_escapados = estado.get("enemigos_escapados", 0)
            
            enemigos_label = pygame.font.Font(None, 20).render("Enemigos", True, Colores.TEXTO_SECUNDARIO)
            superficie.blit(enemigos_label, (self.widget_x + 10, self.widget_y + 100))
            
            # Mostrar enemigos vivos
            vivos_texto = f"Vivos: {enemigos_vivos}/3"
            color_vivos = Colores.VERDE_NEON if enemigos_vivos > 0 else Colores.ROJO_NEON
            vivos_valor = self.fuente_ui.render(vivos_texto, True, color_vivos)
            superficie.blit(vivos_valor, (self.widget_x + 10, self.widget_y + 120))
            
            # Mostrar capturados y escapados
            capturados_texto = f"Capturados: {enemigos_capturados}"
            capturados_valor = pygame.font.Font(None, 16).render(capturados_texto, True, Colores.VERDE_NEON)
            superficie.blit(capturados_valor, (self.widget_x + 10, self.widget_y + 140))
            
            escapados_texto = f"Escapados: {enemigos_escapados}"
            escapados_valor = pygame.font.Font(None, 16).render(escapados_texto, True, Colores.ROJO_NEON)
            superficie.blit(escapados_valor, (self.widget_x + 10, self.widget_y + 160))
    
    def _calcular_puntos_estimados(self) -> int:
        """Calcula los puntos estimados actuales."""
        if self.modo_juego:
            estado = self.modo_juego.obtener_estado()
            return estado.get('puntos', 0)
        # Fallback al cálculo antiguo
        tiempo_restante = max(0, self.tiempo_limite - self.tiempo_juego)
        energia = self.jugador.obtener_energia_actual()
        puntos = 1000 + int(tiempo_restante * 10) + energia * 5 - self.movimientos * 2
        return max(100, puntos)
    
    def _dibujar_leyenda(self, superficie: pygame.Surface, x: int, y: int):
        """Dibuja la leyenda de tipos de tile."""
        titulo = self.fuente_ui.render("LEYENDA:", True, Colores.TEXTO)
        superficie.blit(titulo, (x, y))
        
        items = [
            (Colores.CAMINO, "Camino - Puedes pasar"),
            (Colores.MURO, "Muro - Bloqueado"),
            (Colores.TUNEL, "Túnel - Solo tú puedes"),
            (Colores.LIANA, "Liana - Solo enemigos"),
            (Colores.INICIO, "Inicio"),
            (Colores.SALIDA, "Salida"),
        ]
        
        for i, (color, texto) in enumerate(items):
            rect_y = y + 30 + i * 28
            pygame.draw.rect(superficie, color, (x, rect_y, 18, 18), border_radius=3)
            label = self.fuente_ui.render(texto, True, Colores.TEXTO_SECUNDARIO)
            superficie.blit(label, (x + 26, rect_y))
    
    def _obtener_altura_leyenda(self) -> int:
        """Calcula la altura total de la leyenda."""
        # Título: ~28 píxeles + 10 de espacio
        # 6 items * 28 píxeles cada uno
        return 28 + 10 + 6 * 28
    
    def _dibujar_controles_mini(self, superficie: pygame.Surface, x: int, y: int):
        """Dibuja los controles en formato compacto."""
        titulo = self.fuente_ui.render("CONTROLES:", True, Colores.TEXTO)
        superficie.blit(titulo, (x, y))
        
        controles = [
            "Flechas / WASD - Mover",
            "SHIFT - Correr",
            "ESC - Pausar"
        ]
        
        # Agregar control de trampas solo en modo Escapa
        if self.modo == "escapa":
            controles.insert(2, "T / ESPACIO - Colocar trampa")
        
        for i, ctrl in enumerate(controles):
            texto = self.fuente_ui.render(ctrl, True, Colores.TEXTO_DESHABILITADO)
            superficie.blit(texto, (x, y + 28 + i * 24))
    
    def _dibujar_pausa(self, superficie: pygame.Surface):
        """Dibuja el overlay de pausa."""
        # Fondo semi-transparente
        overlay = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        superficie.blit(overlay, (0, 0))
        
        # Título
        titulo = self.fuente_grande.render("⏸ PAUSA", True, Colores.AMARILLO_NEON)
        titulo_rect = titulo.get_rect(center=(self.ancho // 2, 250))
        superficie.blit(titulo, titulo_rect)
        
        # Botones
        for boton in self.botones_pausa:
            boton.dibujar(superficie, self.fuente_ui)
    
    def _dibujar_fin_juego(self, superficie: pygame.Surface):
        """Dibuja el overlay de fin de juego."""
        # Fondo semi-transparente
        overlay = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        superficie.blit(overlay, (0, 0))
        
        # Título según resultado
        if self.victoria:
            titulo_texto = "🎉 ¡VICTORIA! 🎉"
            color_titulo = Colores.VERDE_NEON
        else:
            titulo_texto = "💀 TIEMPO AGOTADO 💀"
            color_titulo = Colores.ROJO_NEON
        
        titulo = self.fuente_grande.render(titulo_texto, True, color_titulo)
        titulo_rect = titulo.get_rect(center=(self.ancho // 2, 200))
        superficie.blit(titulo, titulo_rect)
        
        # Estadísticas finales
        if self.victoria:
            stats = [
                f"Puntos: {self.puntos}",
                f"Tiempo: {int(self.tiempo_juego)}s",
                f"Movimientos: {self.movimientos}",
                f"Energía final: {self.jugador.obtener_energia_actual()}%"
            ]
            
            for i, stat in enumerate(stats):
                texto = self.fuente_titulo.render(stat, True, Colores.TEXTO)
                rect = texto.get_rect(center=(self.ancho // 2, 300 + i * 45))
                superficie.blit(texto, rect)
        
        # Instrucción
        instruccion = self.fuente_ui.render(
            "Presiona ESC para volver al menú", True, Colores.TEXTO_SECUNDARIO
        )
        instruccion_rect = instruccion.get_rect(center=(self.ancho // 2, 550))
        superficie.blit(instruccion, instruccion_rect)


class PantallaInformacion(PantallaBase):
    """Pantalla de información del juego con controles y detalles."""
    
    def __init__(self, ancho: int, alto: int):
        super().__init__(ancho, alto)
        
        self.tiempo = 0
        
        # Fuentes
        self.fuente_titulo = None
        self.fuente_subtitulo = None
        self.fuente_info = None
        self.fuente_boton = None
        
        # Botones
        self.botones = []
    
    def inicializar_fuentes(self):
        """Inicializa las fuentes."""
        self.fuente_titulo = pygame.font.Font(None, 72)
        self.fuente_subtitulo = pygame.font.Font(None, 42)
        self.fuente_info = pygame.font.Font(None, 28)
        self.fuente_boton = pygame.font.Font(None, 32)
        
        # Crear botón volver (posicionado fuera del panel)
        centro_x = self.ancho // 2
        self.botones = [
            Boton(centro_x - 100, self.alto - 70, 200, 50, "VOLVER",
                  color=Colores.AMARILLO_NEON,
                  accion=self._volver),
        ]
        
        # Crear botón de detalles de modos (se posicionará dinámicamente en dibujar)
        self.boton_detalles_modos = Boton(
            0, 0, 300, 45, "VER DETALLES DE MODOS",
            color=Colores.MAGENTA_NEON,
            accion=self._ver_detalles_modos
        )
    
    def _volver(self):
        """Vuelve al menú principal."""
        self.siguiente_pantalla = "menu"
    
    def _ver_detalles_modos(self):
        """Navega a la pantalla de detalles de modos."""
        self.siguiente_pantalla = "detalles_modos"
    
    def manejar_evento(self, evento: pygame.event.Event):
        """Maneja eventos."""
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            self._volver()
            return
        
        for boton in self.botones:
            boton.manejar_evento(evento)
        
        # Manejar botón de detalles de modos
        if self.boton_detalles_modos:
            self.boton_detalles_modos.manejar_evento(evento)
    
    def actualizar(self, dt: float):
        """Actualiza la pantalla."""
        self.tiempo += dt
        
        pos_mouse = pygame.mouse.get_pos()
        for boton in self.botones:
            boton.actualizar(pos_mouse, dt)
        
        # Actualizar botón de detalles de modos
        if self.boton_detalles_modos:
            self.boton_detalles_modos.actualizar(pos_mouse, dt)
    
    def dibujar(self, superficie: pygame.Surface):
        """Dibuja la pantalla de información."""
        superficie.fill(Colores.FONDO_OSCURO)
        
        # Título
        titulo = self.fuente_titulo.render("INFORMACION DEL JUEGO", True, Colores.CYAN_NEON)
        titulo_rect = titulo.get_rect(center=(self.ancho // 2, 60))
        superficie.blit(titulo, titulo_rect)
        
        # Panel principal con scroll si es necesario
        panel_ancho = min(1000, self.ancho - 80)
        panel_alto = self.alto - 180  # Más espacio para el botón
        panel_x = (self.ancho - panel_ancho) // 2
        panel_y = 100
        
        # Fondo del panel
        panel_rect = pygame.Rect(panel_x, panel_y, panel_ancho, panel_alto)
        pygame.draw.rect(superficie, Colores.FONDO_PANEL, panel_rect, border_radius=15)
        pygame.draw.rect(superficie, Colores.CYAN_NEON, panel_rect, width=2, border_radius=15)
        
        y_pos = panel_y + 25
        margen_x = panel_x + 40
        espacio_entre_secciones = 25
        espacio_entre_items = 28
        
        # CONTROLES
        seccion_titulo = self.fuente_subtitulo.render("CONTROLES", True, Colores.CYAN_NEON)
        superficie.blit(seccion_titulo, (margen_x, y_pos))
        y_pos += 45
        
        controles = [
            "Flechas / WASD - Mover al jugador",
            "SHIFT - Correr (consume más energía)",
            "T / ESPACIO - Colocar trampa (solo modo Escapa)",
            "ESC - Pausar / Volver al menú",
            "F11 - Alternar pantalla completa"
        ]
        
        for ctrl in controles:
            texto = self.fuente_info.render(ctrl, True, Colores.TEXTO_SECUNDARIO)
            superficie.blit(texto, (margen_x + 20, y_pos))
            y_pos += espacio_entre_items
        
        y_pos += espacio_entre_secciones
        
        # TIPOS DE CASILLAS
        seccion_titulo = self.fuente_subtitulo.render("TIPOS DE CASILLAS", True, Colores.VERDE_NEON)
        superficie.blit(seccion_titulo, (margen_x, y_pos))
        y_pos += 45
        
        tipos_casillas = [
            (Colores.CAMINO, "Camino", "Transitable por jugador y enemigos"),
            (Colores.MURO, "Muro", "Bloquea el paso a todos"),
            (Colores.LIANA, "Liana", "Solo los enemigos pueden pasar"),
            (Colores.TUNEL, "Túnel", "Solo el jugador puede pasar"),
            (Colores.INICIO, "Inicio", "Posición inicial del jugador"),
            (Colores.SALIDA, "Salida", "Llega aquí para ganar")
        ]
        
        for color, nombre, descripcion in tipos_casillas:
            # Dibujar muestra de color
            pygame.draw.rect(superficie, color, (margen_x + 20, y_pos, 22, 22), border_radius=4)
            # Nombre y descripción
            nombre_texto = self.fuente_info.render(f"{nombre}: {descripcion}", True, Colores.TEXTO_SECUNDARIO)
            superficie.blit(nombre_texto, (margen_x + 50, y_pos + 1))
            y_pos += espacio_entre_items
        
        y_pos += espacio_entre_secciones
        
        # MODOS DE JUEGO (con botón para ver detalles)
        seccion_titulo = self.fuente_subtitulo.render("MODOS DE JUEGO", True, Colores.MAGENTA_NEON)
        superficie.blit(seccion_titulo, (margen_x, y_pos))
        y_pos += 45
        
        # Descripción breve
        descripcion = self.fuente_info.render(
            "El juego tiene dos modos: Escapa y Cazador. Cada uno tiene mecánicas únicas.",
            True, Colores.TEXTO_SECUNDARIO
        )
        superficie.blit(descripcion, (margen_x + 20, y_pos))
        y_pos += espacio_entre_items + 10
        
        # Botón para ver detalles de modos (actualizar posición)
        if self.boton_detalles_modos:
            self.boton_detalles_modos.rect.x = margen_x + 20
            self.boton_detalles_modos.rect.y = y_pos
            self.boton_detalles_modos.dibujar(superficie, self.fuente_info)
        y_pos += 60
        
        y_pos += espacio_entre_secciones
        
        # MULTIPLES SALIDAS
        seccion_titulo = self.fuente_subtitulo.render("MULTIPLES SALIDAS", True, Colores.AMARILLO_NEON)
        superficie.blit(seccion_titulo, (margen_x, y_pos))
        y_pos += 45
        
        salidas_info = [
            "• Cada mapa tiene 3 salidas diferentes",
            "• Puedes llegar a cualquiera de ellas para ganar",
            "• Planifica tu ruta estratégicamente",
            "• Las salidas están marcadas en rojo"
        ]
        
        for info in salidas_info:
            texto = self.fuente_info.render(info, True, Colores.TEXTO_SECUNDARIO)
            superficie.blit(texto, (margen_x + 20, y_pos))
            y_pos += espacio_entre_items
        
        # Botón volver
        for boton in self.botones:
            boton.dibujar(superficie, self.fuente_boton)


class PantallaDetallesModos(PantallaBase):
    """Pantalla con detalles detallados de los modos de juego."""
    
    def __init__(self, ancho: int, alto: int):
        super().__init__(ancho, alto)
        
        self.tiempo = 0
        
        # Fuentes
        self.fuente_titulo = None
        self.fuente_subtitulo = None
        self.fuente_info = None
        self.fuente_boton = None
        
        # Botones
        self.botones = []
    
    def inicializar_fuentes(self):
        """Inicializa las fuentes."""
        self.fuente_titulo = pygame.font.Font(None, 72)
        self.fuente_subtitulo = pygame.font.Font(None, 42)
        self.fuente_info = pygame.font.Font(None, 28)
        self.fuente_boton = pygame.font.Font(None, 32)
        
        # Crear botón volver
        centro_x = self.ancho // 2
        self.botones = [
            Boton(centro_x - 100, self.alto - 70, 200, 50, "VOLVER",
                  color=Colores.AMARILLO_NEON,
                  accion=self._volver),
        ]
    
    def _volver(self):
        """Vuelve a la pantalla de información."""
        self.siguiente_pantalla = "informacion"
    
    def manejar_evento(self, evento: pygame.event.Event):
        """Maneja eventos."""
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            self._volver()
            return
        
        for boton in self.botones:
            boton.manejar_evento(evento)
    
    def actualizar(self, dt: float):
        """Actualiza la pantalla."""
        self.tiempo += dt
        
        pos_mouse = pygame.mouse.get_pos()
        for boton in self.botones:
            boton.actualizar(pos_mouse, dt)
    
    def dibujar(self, superficie: pygame.Surface):
        """Dibuja la pantalla de detalles de modos."""
        superficie.fill(Colores.FONDO_OSCURO)
        
        # Título
        titulo = self.fuente_titulo.render("DETALLES DE MODOS", True, Colores.MAGENTA_NEON)
        titulo_rect = titulo.get_rect(center=(self.ancho // 2, 60))
        superficie.blit(titulo, titulo_rect)
        
        # Panel principal
        panel_ancho = min(1000, self.ancho - 80)
        panel_alto = self.alto - 180
        panel_x = (self.ancho - panel_ancho) // 2
        panel_y = 100
        
        # Fondo del panel
        panel_rect = pygame.Rect(panel_x, panel_y, panel_ancho, panel_alto)
        pygame.draw.rect(superficie, Colores.FONDO_PANEL, panel_rect, border_radius=15)
        pygame.draw.rect(superficie, Colores.MAGENTA_NEON, panel_rect, width=2, border_radius=15)
        
        y_pos = panel_y + 25
        margen_x = panel_x + 40
        espacio_entre_items = 28
        espacio_entre_secciones = 30
        
        # MODO ESCAPA
        modo_escapa_titulo = self.fuente_subtitulo.render("MODO ESCAPA", True, Colores.CYAN_NEON)
        superficie.blit(modo_escapa_titulo, (margen_x, y_pos))
        y_pos += 45
        
        escapa_info = [
            "• Los enemigos te persiguen constantemente",
            "• Tu objetivo es llegar a cualquiera de las 3 salidas para ganar",
            "• Puedes colocar hasta 3 trampas simultáneamente en el mapa",
            "• Las trampas tienen un cooldown de 5 segundos entre colocaciones",
            "• Si un enemigo pasa sobre una trampa, muere inmediatamente",
            "• Cada enemigo eliminado con trampas te da puntos extra",
            "• Los enemigos eliminados reaparecen después de 10 segundos",
            "• Si un enemigo te alcanza (misma casilla), pierdes la partida",
            "• Gana puntos basados en el tiempo, dificultad y enemigos eliminados"
        ]
        
        for info in escapa_info:
            texto = self.fuente_info.render(info, True, Colores.TEXTO_SECUNDARIO)
            superficie.blit(texto, (margen_x + 20, y_pos))
            y_pos += espacio_entre_items
        
        y_pos += espacio_entre_secciones
        
        # MODO CAZADOR
        modo_cazador_titulo = self.fuente_subtitulo.render("MODO CAZADOR", True, Colores.MAGENTA_NEON)
        superficie.blit(modo_cazador_titulo, (margen_x, y_pos))
        y_pos += 45
        
        cazador_info = [
            "• Los enemigos huyen de ti constantemente",
            "• Tu objetivo es atrapar a los enemigos antes de que escapen",
            "• Si un enemigo llega a una salida, pierdes puntos",
            "• Si atrapas a un enemigo (misma casilla), ganas puntos",
            "• Los puntos ganados por atrapar son el doble de los que perderías si escapara",
            "• Los enemigos atrapados reaparecen después de un tiempo",
            "• Tienes un tiempo límite para atrapar la mayor cantidad de enemigos",
            "• Gana puntos basados en la cantidad de enemigos capturados"
        ]
        
        for info in cazador_info:
            texto = self.fuente_info.render(info, True, Colores.TEXTO_SECUNDARIO)
            superficie.blit(texto, (margen_x + 20, y_pos))
            y_pos += espacio_entre_items
        
        # Botón volver
        for boton in self.botones:
            boton.dibujar(superficie, self.fuente_boton)


class PantallaPuntajes(PantallaBase):
    """Pantalla de tabla de clasificación."""
    
    def __init__(self, ancho: int, alto: int):
        super().__init__(ancho, alto)
        
        self.scoreboard = ScoreBoard(Config.obtener_ruta_puntajes())
        self.modo_actual = "escapa"
        self.tiempo = 0
        
        # Fuentes
        self.fuente_titulo = None
        self.fuente_subtitulo = None
        self.fuente_tabla = None
        self.fuente_boton = None
        
        # Botones
        self.botones = []
    
    def inicializar_fuentes(self):
        """Inicializa las fuentes."""
        self.fuente_titulo = pygame.font.Font(None, 72)
        self.fuente_subtitulo = pygame.font.Font(None, 42)
        self.fuente_tabla = pygame.font.Font(None, 32)
        self.fuente_boton = pygame.font.Font(None, 28)
        
        # Crear botones
        centro_x = self.ancho // 2
        self.botones = [
            Boton(centro_x - 250, 180, 200, 45, "ESCAPA",
                  color=Colores.CYAN_NEON,
                  accion=lambda: self._cambiar_modo("escapa")),
            Boton(centro_x + 50, 180, 200, 45, "CAZADOR",
                  color=Colores.MAGENTA_NEON,
                  accion=lambda: self._cambiar_modo("cazador")),
            Boton(centro_x - 100, 620, 200, 45, "VOLVER",
                  color=Colores.AMARILLO_NEON,
                  accion=self._volver),
        ]
    
    def _cambiar_modo(self, modo: str):
        """Cambia el modo de puntajes mostrado."""
        self.modo_actual = modo
    
    def _volver(self):
        """Vuelve al menú principal."""
        self.siguiente_pantalla = "menu"
    
    def manejar_evento(self, evento: pygame.event.Event):
        """Maneja eventos."""
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            self._volver()
            return
        
        for boton in self.botones:
            boton.manejar_evento(evento)
    
    def actualizar(self, dt: float):
        """Actualiza la pantalla."""
        self.tiempo += dt
        
        pos_mouse = pygame.mouse.get_pos()
        for boton in self.botones:
            boton.actualizar(pos_mouse, dt)
    
    def dibujar(self, superficie: pygame.Surface):
        """Dibuja la pantalla de puntajes."""
        superficie.fill(Colores.FONDO_OSCURO)
        
        # Título
        titulo = self.fuente_titulo.render("TABLA DE PUNTAJES", True, Colores.ORO)
        titulo_rect = titulo.get_rect(center=(self.ancho // 2, 80))
        superficie.blit(titulo, titulo_rect)
        
        # Subtítulo del modo actual
        modo_texto = "Modo Escapa" if self.modo_actual == "escapa" else "Modo Cazador"
        color_modo = Colores.CYAN_NEON if self.modo_actual == "escapa" else Colores.MAGENTA_NEON
        subtitulo = self.fuente_subtitulo.render(modo_texto, True, color_modo)
        subtitulo_rect = subtitulo.get_rect(center=(self.ancho // 2, 140))
        superficie.blit(subtitulo, subtitulo_rect)
        
        # Botones de modo
        for boton in self.botones[:2]:
            boton.dibujar(superficie, self.fuente_boton)
        
        # Tabla de puntajes
        self._dibujar_tabla(superficie)
        
        # Botón volver
        self.botones[2].dibujar(superficie, self.fuente_boton)
    
    def _dibujar_tabla(self, superficie: pygame.Surface):
        """Dibuja la tabla de puntajes."""
        top5 = self.scoreboard.obtener_top5(self.modo_actual)
        
        # Fondo de la tabla
        tabla_rect = pygame.Rect(self.ancho // 2 - 350, 250, 700, 340)
        pygame.draw.rect(superficie, Colores.FONDO_PANEL, tabla_rect, border_radius=15)
        pygame.draw.rect(superficie, Colores.TEXTO_SECUNDARIO, tabla_rect, width=2, border_radius=15)
        
        # Encabezados
        headers = ["#", "JUGADOR", "PUNTOS"]
        header_x = [tabla_rect.x + 50, tabla_rect.x + 180, tabla_rect.x + 500]
        
        for i, header in enumerate(headers):
            texto = self.fuente_tabla.render(header, True, Colores.TEXTO)
            superficie.blit(texto, (header_x[i], tabla_rect.y + 20))
        
        # Línea separadora
        pygame.draw.line(superficie, Colores.TEXTO_SECUNDARIO,
                        (tabla_rect.x + 20, tabla_rect.y + 55),
                        (tabla_rect.x + tabla_rect.width - 20, tabla_rect.y + 55), 1)
        
        if not top5:
            # Mensaje de no hay puntajes
            mensaje = self.fuente_tabla.render("No hay puntajes registrados", True, Colores.TEXTO_DESHABILITADO)
            mensaje_rect = mensaje.get_rect(center=(self.ancho // 2, tabla_rect.y + 180))
            superficie.blit(mensaje, mensaje_rect)
            return
        
        # Filas de puntajes
        colores_medalla = [Colores.ORO, Colores.PLATA, Colores.BRONCE, Colores.TEXTO, Colores.TEXTO]
        
        for i, puntaje in enumerate(top5):
            y = tabla_rect.y + 75 + i * 50
            color = colores_medalla[i]
            
            # Fondo de fila con hover effect
            fila_rect = pygame.Rect(tabla_rect.x + 10, y - 5, tabla_rect.width - 20, 45)
            
            # Medalla/Número
            if i < 3:
                medallas = ["🥇", "🥈", "🥉"]
                num_texto = medallas[i]
            else:
                num_texto = str(i + 1)
            
            num = self.fuente_tabla.render(num_texto, True, color)
            superficie.blit(num, (header_x[0], y))
            
            # Nombre
            nombre = self.fuente_tabla.render(puntaje.nombre_jugador, True, color)
            superficie.blit(nombre, (header_x[1], y))
            
            # Puntos
            puntos = self.fuente_tabla.render(f"{int(puntaje.puntos):,}", True, color)
            superficie.blit(puntos, (header_x[2], y))


class PantallaFinJuego(PantallaBase):
    """Pantalla de fin de juego (alternativa standalone)."""
    
    def __init__(self, ancho: int, alto: int, victoria: bool, puntos: int, 
                 tiempo: float, movimientos: int, modo: str):
        super().__init__(ancho, alto)
        
        self.victoria = victoria
        self.puntos = puntos
        self.tiempo = tiempo
        self.movimientos = movimientos
        self.modo = modo
        self.tiempo_animacion = 0
        
        # Fuentes
        self.fuente_titulo = None
        self.fuente_stats = None
        self.fuente_boton = None
        
        # Botones
        self.botones = []
        self.particulas = SistemaParticulas()
    
    def inicializar_fuentes(self):
        """Inicializa las fuentes."""
        self.fuente_titulo = pygame.font.Font(None, 86)
        self.fuente_stats = pygame.font.Font(None, 42)
        self.fuente_boton = pygame.font.Font(None, 32)
        
        centro_x = self.ancho // 2
        self.botones = [
            Boton(centro_x - 150, 500, 300, 55, "JUGAR DE NUEVO",
                  color=Colores.VERDE_NEON,
                  accion=self._jugar_nuevo),
            Boton(centro_x - 150, 570, 300, 55, "MENU PRINCIPAL",
                  color=Colores.CYAN_NEON,
                  accion=self._ir_menu),
        ]
    
    def _jugar_nuevo(self):
        """Inicia una nueva partida."""
        self.siguiente_pantalla = "juego_nuevo"
        self.datos_retorno = {"modo": self.modo}
    
    def _ir_menu(self):
        """Vuelve al menú."""
        self.siguiente_pantalla = "menu"
    
    def manejar_evento(self, evento: pygame.event.Event):
        """Maneja eventos."""
        for boton in self.botones:
            boton.manejar_evento(evento)
    
    def actualizar(self, dt: float):
        """Actualiza la pantalla."""
        self.tiempo_animacion += dt
        
        pos_mouse = pygame.mouse.get_pos()
        for boton in self.botones:
            boton.actualizar(pos_mouse, dt)
        
        # Partículas de celebración
        if self.victoria and random.random() < 0.3:
            x = random.randint(100, self.ancho - 100)
            color = random.choice([Colores.ORO, Colores.CYAN_NEON, Colores.MAGENTA_NEON])
            self.particulas.emitir(x, 50, color, 2)
        
        self.particulas.actualizar(dt)
    
    def dibujar(self, superficie: pygame.Surface):
        """Dibuja la pantalla de fin."""
        superficie.fill(Colores.FONDO_OSCURO)
        
        # Partículas
        self.particulas.dibujar(superficie)
        
        # Título
        if self.victoria:
            titulo_texto = "🎉 ¡VICTORIA! 🎉"
            color = Colores.VERDE_NEON
        else:
            titulo_texto = "💀 GAME OVER 💀"
            color = Colores.ROJO_NEON
        
        titulo = self.fuente_titulo.render(titulo_texto, True, color)
        titulo_rect = titulo.get_rect(center=(self.ancho // 2, 120))
        superficie.blit(titulo, titulo_rect)
        
        # Estadísticas
        if self.victoria:
            stats = [
                f"Puntos: {self.puntos:,}",
                f"Tiempo: {int(self.tiempo)}s",
                f"Movimientos: {self.movimientos}"
            ]
            
            for i, stat in enumerate(stats):
                texto = self.fuente_stats.render(stat, True, Colores.TEXTO)
                rect = texto.get_rect(center=(self.ancho // 2, 250 + i * 60))
                superficie.blit(texto, rect)
        
        # Botones
        for boton in self.botones:
            boton.dibujar(superficie, self.fuente_boton)

