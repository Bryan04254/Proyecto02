"""
Componentes de UI reutilizables para el juego.
"""

import pygame
import random
import math
from typing import Tuple, Optional, Callable, List
from .config import Colores, Config


class Boton:
    """
    Botón interactivo con efectos hover y glow.
    
    Componente de UI reutilizable que muestra un botón con:
    - Efecto hover (cambio de color y escala)
    - Efecto glow (brillo pulsante cuando hay hover)
    - Animación suave de escala
    - Callback al hacer clic
    """
    
    def __init__(self, x: int, y: int, ancho: int, alto: int, 
                 texto: str, color: Tuple[int, int, int] = Colores.CYAN_NEON,
                 color_hover: Tuple[int, int, int] = None,
                 accion: Callable = None):
        """
        Inicializa un botón.
        
        Args:
            x: Posición X en píxeles.
            y: Posición Y en píxeles.
            ancho: Ancho del botón en píxeles.
            alto: Alto del botón en píxeles.
            texto: Texto a mostrar en el botón.
            color: Color base del botón (RGB).
            color_hover: Color cuando el mouse está sobre el botón (si es None, se aclara automáticamente).
            accion: Función a llamar cuando se hace clic en el botón.
        """
        self.rect = pygame.Rect(x, y, ancho, alto)  # Rectángulo del botón
        self.texto = texto  # Texto a mostrar
        self.color_base = color  # Color base (normal)
        self.color_hover = color_hover or self._aclarar_color(color)  # Color cuando hay hover
        self.color_actual = color  # Color actual (cambia según hover)
        self.accion = accion  # Callback al hacer clic
        self.hover = False  # Estado de hover
        self.presionado = False  # Estado de presionado
        self.tiempo_animacion = 0  # Tiempo acumulado para animaciones
        self.escala = 1.0  # Escala del botón (para efecto de crecimiento)
        
    def _aclarar_color(self, color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """
        Aclara un color para el efecto hover.
        
        Suma 40 a cada componente RGB, limitando a 255.
        
        Args:
            color: Color RGB original.
            
        Returns:
            Color RGB aclarado.
        """
        return tuple(min(255, c + 40) for c in color)
    
    def actualizar(self, pos_mouse: Tuple[int, int], dt: float):
        """
        Actualiza el estado del botón.
        
        Detecta hover y actualiza animaciones de escala y color.
        
        Args:
            pos_mouse: Posición actual del mouse (x, y).
            dt: Tiempo transcurrido desde el último frame (segundos).
        """
        # Detectar si el mouse está sobre el botón
        self.hover = self.rect.collidepoint(pos_mouse)
        
        if self.hover:
            # Efecto hover: cambiar color y aumentar escala
            self.color_actual = self.color_hover
            self.escala = min(1.05, self.escala + dt * 2)  # Crecer hasta 5% más
        else:
            # Sin hover: volver al color base y escala normal
            self.color_actual = self.color_base
            self.escala = max(1.0, self.escala - dt * 2)  # Reducir hasta escala 1.0
        
        # Actualizar tiempo para animaciones basadas en tiempo
        self.tiempo_animacion += dt
    
    def manejar_evento(self, evento: pygame.event.Event) -> bool:
        """Maneja eventos del mouse. Retorna True si se hizo clic."""
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.hover:
                self.presionado = True
        elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            if self.presionado and self.hover:
                self.presionado = False
                if self.accion:
                    self.accion()
                return True
            self.presionado = False
        return False
    
    def dibujar(self, superficie: pygame.Surface, fuente: pygame.font.Font):
        """Dibuja el botón con efectos."""
        # Calcular rect escalado
        ancho_escalado = int(self.rect.width * self.escala)
        alto_escalado = int(self.rect.height * self.escala)
        x_escalado = self.rect.centerx - ancho_escalado // 2
        y_escalado = self.rect.centery - alto_escalado // 2
        rect_dibujado = pygame.Rect(x_escalado, y_escalado, ancho_escalado, alto_escalado)
        
        # Glow exterior (cuando hay hover)
        if self.hover:
            glow_rect = rect_dibujado.inflate(8, 8)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            alpha = int(100 + 50 * math.sin(self.tiempo_animacion * 4))
            pygame.draw.rect(glow_surface, (*self.color_actual[:3], alpha), 
                           glow_surface.get_rect(), border_radius=12)
            superficie.blit(glow_surface, glow_rect.topleft)
        
        # Fondo del botón
        pygame.draw.rect(superficie, Colores.FONDO_PANEL, rect_dibujado, border_radius=8)
        
        # Borde del botón
        grosor_borde = 3 if self.hover else 2
        pygame.draw.rect(superficie, self.color_actual, rect_dibujado, 
                        width=grosor_borde, border_radius=8)
        
        # Texto
        texto_render = fuente.render(self.texto, True, self.color_actual)
        texto_rect = texto_render.get_rect(center=rect_dibujado.center)
        superficie.blit(texto_render, texto_rect)


class BarraEnergia:
    """
    Barra de energía animada con gradiente y efectos visuales.
    
    Muestra el nivel de energía del jugador con:
    - Animación suave de cambio de nivel
    - Cambio de color según el nivel (verde/amarillo/rojo)
    - Efecto de brillo cuando la energía está baja
    - Porcentaje visible
    """
    
    def __init__(self, x: int, y: int, ancho: int, alto: int):
        """
        Inicializa una barra de energía.
        
        Args:
            x: Posición X en píxeles.
            y: Posición Y en píxeles.
            ancho: Ancho de la barra en píxeles.
            alto: Alto de la barra en píxeles.
        """
        self.rect = pygame.Rect(x, y, ancho, alto)  # Rectángulo de la barra
        self.porcentaje = 1.0  # Porcentaje real de energía (0.0 a 1.0)
        self.porcentaje_visual = 1.0  # Porcentaje visual (para animación suave/interpolación)
        self.tiempo = 0  # Tiempo acumulado para animaciones
        
    def actualizar(self, porcentaje: float, dt: float):
        """
        Actualiza el porcentaje de energía con animación suave.
        
        Args:
            porcentaje: Nuevo porcentaje de energía (0.0 a 1.0).
            dt: Tiempo transcurrido desde el último frame (segundos).
        """
        # Limitar porcentaje entre 0 y 1
        self.porcentaje = max(0, min(1, porcentaje))
        
        # Interpolación suave hacia el porcentaje objetivo
        # Esto crea un efecto de movimiento fluido en lugar de saltos
        diferencia = self.porcentaje - self.porcentaje_visual
        self.porcentaje_visual += diferencia * dt * 5  # Velocidad de interpolación
        
        # Actualizar tiempo para animaciones
        self.tiempo += dt
    
    def _obtener_color_energia(self) -> Tuple[int, int, int]:
        """
        Obtiene el color según el nivel de energía.
        
        El color cambia según el porcentaje:
        - > 60%: Verde (energía llena)
        - 30-60%: Amarillo (energía media)
        - < 30%: Rojo (energía baja)
        
        Returns:
            Color RGB según el nivel de energía.
        """
        if self.porcentaje > 0.6:
            return Colores.ENERGIA_LLENA  # Verde
        elif self.porcentaje > 0.3:
            return Colores.ENERGIA_MEDIA  # Amarillo
        else:
            return Colores.ENERGIA_BAJA  # Rojo
    
    def dibujar(self, superficie: pygame.Surface, fuente: pygame.font.Font = None):
        """Dibuja la barra de energía."""
        # Fondo
        pygame.draw.rect(superficie, Colores.ENERGIA_FONDO, self.rect, border_radius=4)
        
        # Barra de energía
        if self.porcentaje_visual > 0:
            ancho_barra = int((self.rect.width - 4) * self.porcentaje_visual)
            barra_rect = pygame.Rect(
                self.rect.x + 2, 
                self.rect.y + 2, 
                ancho_barra, 
                self.rect.height - 4
            )
            
            color = self._obtener_color_energia()
            pygame.draw.rect(superficie, color, barra_rect, border_radius=3)
            
            # Efecto de brillo
            if self.porcentaje < 0.3:
                alpha = int(128 + 64 * math.sin(self.tiempo * 6))
                brillo = pygame.Surface((barra_rect.width, barra_rect.height), pygame.SRCALPHA)
                brillo.fill((*Colores.ROJO_NEON, alpha))
                superficie.blit(brillo, barra_rect.topleft)
        
        # Borde
        pygame.draw.rect(superficie, Colores.TEXTO_SECUNDARIO, self.rect, width=2, border_radius=4)
        
        # Texto de porcentaje
        if fuente:
            texto = f"{int(self.porcentaje * 100)}%"
            texto_render = fuente.render(texto, True, Colores.TEXTO)
            texto_rect = texto_render.get_rect(center=self.rect.center)
            superficie.blit(texto_render, texto_rect)


class Particula:
    """
    Partícula para efectos visuales.
    
    Representa una partícula individual con física simple:
    - Movimiento con velocidad
    - Gravedad
    - Desvanecimiento gradual
    - Tamaño variable
    """
    
    def __init__(self, x: float, y: float, color: Tuple[int, int, int]):
        """
        Inicializa una partícula.
        
        Args:
            x: Posición X inicial.
            y: Posición Y inicial.
            color: Color RGB de la partícula.
        """
        self.x = x  # Posición X
        self.y = y  # Posición Y
        self.color = color  # Color RGB
        self.velocidad_x = random.uniform(-2, 2)  # Velocidad horizontal aleatoria
        self.velocidad_y = random.uniform(-3, -1)  # Velocidad vertical aleatoria (hacia arriba)
        self.vida = 1.0  # Vida restante (1.0 = 100%, 0.0 = muerta)
        self.tamano = random.randint(3, 6)  # Tamaño aleatorio en píxeles
        
    def actualizar(self, dt: float) -> bool:
        """Actualiza la partícula. Retorna False si debe eliminarse."""
        self.x += self.velocidad_x * 60 * dt
        self.y += self.velocidad_y * 60 * dt
        self.velocidad_y += 5 * dt  # Gravedad
        self.vida -= dt * 2
        return self.vida > 0
    
    def dibujar(self, superficie: pygame.Surface):
        """Dibuja la partícula."""
        alpha = int(255 * self.vida)
        tamano = int(self.tamano * self.vida)
        if tamano > 0:
            s = pygame.Surface((tamano * 2, tamano * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (tamano, tamano), tamano)
            superficie.blit(s, (int(self.x) - tamano, int(self.y) - tamano))


class SistemaParticulas:
    """
    Sistema para manejar múltiples partículas.
    
    Gestiona un conjunto de partículas, permitiendo:
    - Emitir nuevas partículas
    - Actualizar todas las partículas
    - Dibujar todas las partículas
    - Eliminar automáticamente partículas muertas
    """
    
    def __init__(self):
        """Inicializa el sistema de partículas."""
        self.particulas: List[Particula] = []  # Lista de partículas activas
    
    def emitir(self, x: float, y: float, color: Tuple[int, int, int], cantidad: int = 5):
        """
        Emite nuevas partículas en una posición.
        
        Args:
            x: Posición X donde emitir las partículas.
            y: Posición Y donde emitir las partículas.
            color: Color RGB de las partículas.
            cantidad: Número de partículas a emitir.
        """
        for _ in range(cantidad):
            self.particulas.append(Particula(x, y, color))
    
    def actualizar(self, dt: float):
        """
        Actualiza todas las partículas y elimina las muertas.
        
        Args:
            dt: Tiempo transcurrido desde el último frame (segundos).
        """
        # Actualizar todas las partículas y filtrar las que murieron
        self.particulas = [p for p in self.particulas if p.actualizar(dt)]
    
    def dibujar(self, superficie: pygame.Surface):
        """
        Dibuja todas las partículas activas.
        
        Args:
            superficie: Superficie de pygame donde dibujar.
        """
        for p in self.particulas:
            p.dibujar(superficie)


class CuadroTexto:
    """
    Cuadro de texto para ingresar el nombre del jugador.
    
    Componente de UI que permite al usuario ingresar texto con:
    - Placeholder cuando está vacío
    - Cursor parpadeante cuando está activo
    - Límite de caracteres
    - Cambio visual cuando está activo
    """
    
    def __init__(self, x: int, y: int, ancho: int, alto: int, 
                 placeholder: str = "Ingresa tu nombre..."):
        """
        Inicializa un cuadro de texto.
        
        Args:
            x: Posición X en píxeles.
            y: Posición Y en píxeles.
            ancho: Ancho del cuadro en píxeles.
            alto: Alto del cuadro en píxeles.
            placeholder: Texto a mostrar cuando está vacío.
        """
        self.rect = pygame.Rect(x, y, ancho, alto)  # Rectángulo del cuadro
        self.texto = ""  # Texto ingresado
        self.placeholder = placeholder  # Texto de placeholder
        self.activo = False  # Si el cuadro está activo (recibiendo input)
        self.cursor_visible = True  # Si el cursor está visible
        self.tiempo_cursor = 0  # Tiempo acumulado para parpadeo del cursor
        self.max_caracteres = 15  # Límite máximo de caracteres
        
    def manejar_evento(self, evento: pygame.event.Event):
        """Maneja eventos de teclado y mouse."""
        if evento.type == pygame.MOUSEBUTTONDOWN:
            self.activo = self.rect.collidepoint(evento.pos)
        
        if evento.type == pygame.KEYDOWN and self.activo:
            if evento.key == pygame.K_BACKSPACE:
                self.texto = self.texto[:-1]
            elif evento.key == pygame.K_RETURN:
                self.activo = False
            elif len(self.texto) < self.max_caracteres:
                if evento.unicode.isprintable() and evento.unicode:
                    self.texto += evento.unicode
    
    def actualizar(self, dt: float):
        """Actualiza la animación del cursor."""
        if self.activo:
            self.tiempo_cursor += dt
            if self.tiempo_cursor >= 0.5:
                self.tiempo_cursor = 0
                self.cursor_visible = not self.cursor_visible
        else:
            self.cursor_visible = False
    
    def dibujar(self, superficie: pygame.Surface, fuente: pygame.font.Font):
        """Dibuja el cuadro de texto."""
        # Fondo
        color_fondo = Colores.FONDO_PANEL if not self.activo else Colores.FONDO_MENU
        pygame.draw.rect(superficie, color_fondo, self.rect, border_radius=8)
        
        # Borde
        color_borde = Colores.CYAN_NEON if self.activo else Colores.TEXTO_SECUNDARIO
        pygame.draw.rect(superficie, color_borde, self.rect, width=2, border_radius=8)
        
        # Texto
        if self.texto:
            texto_mostrar = self.texto
            color_texto = Colores.TEXTO
        else:
            texto_mostrar = self.placeholder
            color_texto = Colores.TEXTO_DESHABILITADO
        
        if self.cursor_visible and self.activo:
            texto_mostrar += "|"
        
        texto_render = fuente.render(texto_mostrar, True, color_texto)
        texto_rect = texto_render.get_rect(midleft=(self.rect.x + 15, self.rect.centery))
        superficie.blit(texto_render, texto_rect)
    
    def obtener_texto(self) -> str:
        """Retorna el texto ingresado."""
        return self.texto.strip()

