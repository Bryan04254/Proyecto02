"""
Componentes de UI reutilizables para el juego.
"""

import pygame
import random
import math
from typing import Tuple, Optional, Callable, List
from .config import Colores, Config


class Boton:
    """Botón interactivo con efectos hover y glow."""
    
    def __init__(self, x: int, y: int, ancho: int, alto: int, 
                 texto: str, color: Tuple[int, int, int] = Colores.CYAN_NEON,
                 color_hover: Tuple[int, int, int] = None,
                 accion: Callable = None):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.color_base = color
        self.color_hover = color_hover or self._aclarar_color(color)
        self.color_actual = color
        self.accion = accion
        self.hover = False
        self.presionado = False
        self.tiempo_animacion = 0
        self.escala = 1.0
        
    def _aclarar_color(self, color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Aclara un color para el efecto hover."""
        return tuple(min(255, c + 40) for c in color)
    
    def actualizar(self, pos_mouse: Tuple[int, int], dt: float):
        """Actualiza el estado del botón."""
        self.hover = self.rect.collidepoint(pos_mouse)
        
        if self.hover:
            self.color_actual = self.color_hover
            self.escala = min(1.05, self.escala + dt * 2)
        else:
            self.color_actual = self.color_base
            self.escala = max(1.0, self.escala - dt * 2)
        
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
    """Barra de energía animada con gradiente."""
    
    def __init__(self, x: int, y: int, ancho: int, alto: int):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.porcentaje = 1.0
        self.porcentaje_visual = 1.0  # Para animación suave
        self.tiempo = 0
        
    def actualizar(self, porcentaje: float, dt: float):
        """Actualiza el porcentaje de energía con animación."""
        self.porcentaje = max(0, min(1, porcentaje))
        
        # Interpolación suave
        diferencia = self.porcentaje - self.porcentaje_visual
        self.porcentaje_visual += diferencia * dt * 5
        
        self.tiempo += dt
    
    def _obtener_color_energia(self) -> Tuple[int, int, int]:
        """Obtiene el color según el nivel de energía."""
        if self.porcentaje > 0.6:
            return Colores.ENERGIA_LLENA
        elif self.porcentaje > 0.3:
            return Colores.ENERGIA_MEDIA
        else:
            return Colores.ENERGIA_BAJA
    
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
    """Partícula para efectos visuales."""
    
    def __init__(self, x: float, y: float, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.color = color
        self.velocidad_x = random.uniform(-2, 2)
        self.velocidad_y = random.uniform(-3, -1)
        self.vida = 1.0
        self.tamano = random.randint(3, 6)
        
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
    """Sistema para manejar múltiples partículas."""
    
    def __init__(self):
        self.particulas: List[Particula] = []
    
    def emitir(self, x: float, y: float, color: Tuple[int, int, int], cantidad: int = 5):
        """Emite partículas en una posición."""
        for _ in range(cantidad):
            self.particulas.append(Particula(x, y, color))
    
    def actualizar(self, dt: float):
        """Actualiza todas las partículas."""
        self.particulas = [p for p in self.particulas if p.actualizar(dt)]
    
    def dibujar(self, superficie: pygame.Surface):
        """Dibuja todas las partículas."""
        for p in self.particulas:
            p.dibujar(superficie)


class CuadroTexto:
    """Cuadro de texto para ingresar el nombre del jugador."""
    
    def __init__(self, x: int, y: int, ancho: int, alto: int, 
                 placeholder: str = "Ingresa tu nombre..."):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = ""
        self.placeholder = placeholder
        self.activo = False
        self.cursor_visible = True
        self.tiempo_cursor = 0
        self.max_caracteres = 15
        
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

