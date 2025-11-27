"""
Configuración y paleta de colores para la GUI del juego.
Estilo: Pixel art retro con colores neón sobre fondo oscuro.
"""

import os


class Colores:
    """Paleta de colores del juego - tema cyberpunk/retro."""
    
    # Fondos
    FONDO_OSCURO = (13, 17, 23)
    FONDO_MENU = (22, 27, 34)
    FONDO_PANEL = (33, 38, 45)
    
    # Colores principales (neón)
    CYAN_NEON = (0, 255, 255)
    MAGENTA_NEON = (255, 0, 128)
    VERDE_NEON = (57, 255, 20)
    AMARILLO_NEON = (255, 255, 0)
    NARANJA_NEON = (255, 165, 0)
    ROJO_NEON = (255, 50, 50)
    
    # Colores suaves (para fondos de elementos)
    CYAN_SUAVE = (0, 100, 100)
    MAGENTA_SUAVE = (100, 0, 50)
    VERDE_SUAVE = (20, 80, 20)
    
    # Tiles del mapa
    CAMINO = (45, 55, 72)
    CAMINO_ILUMINADO = (60, 70, 90)
    MURO = (88, 28, 135)
    MURO_BORDE = (139, 92, 246)
    LIANA = (34, 197, 94)
    LIANA_BORDE = (74, 222, 128)
    TUNEL = (59, 130, 246)
    TUNEL_BORDE = (147, 197, 253)
    
    # Jugador
    JUGADOR = (250, 204, 21)
    JUGADOR_GLOW = (253, 224, 71)
    
    # Posiciones especiales
    INICIO = (34, 197, 94)
    SALIDA = (239, 68, 68)
    SALIDA_GLOW = (248, 113, 113)
    
    # UI
    TEXTO = (248, 250, 252)
    TEXTO_SECUNDARIO = (148, 163, 184)
    TEXTO_DESHABILITADO = (71, 85, 105)
    
    # Energía
    ENERGIA_LLENA = (34, 197, 94)
    ENERGIA_MEDIA = (250, 204, 21)
    ENERGIA_BAJA = (239, 68, 68)
    ENERGIA_FONDO = (30, 41, 59)
    
    # Puntajes
    ORO = (255, 215, 0)
    PLATA = (192, 192, 192)
    BRONCE = (205, 127, 50)


class Config:
    """Configuración general del juego."""
    
    # Ventana
    ANCHO_VENTANA = 1280
    ALTO_VENTANA = 720
    FPS = 60
    TITULO = "Escapa del Laberinto"
    
    # Mapa
    TAMANO_CELDA = 32
    MAPA_ANCHO = 20
    MAPA_ALTO = 15
    
    # Offset del mapa en la pantalla (para centrar)
    MAPA_OFFSET_X = 50
    MAPA_OFFSET_Y = 80
    
    # Panel lateral
    PANEL_X = 720
    PANEL_ANCHO = 540
    
    # Jugador
    ENERGIA_INICIAL = 100
    
    # Tiempos
    TIEMPO_PARTIDA_ESCAPA = 120  # segundos
    TIEMPO_PARTIDA_CAZADOR = 180  # segundos
    
    # Animaciones
    VELOCIDAD_PARPADEO = 0.5
    VELOCIDAD_PARTICULAS = 2
    
    # Rutas
    @staticmethod
    def obtener_ruta_base():
        """Obtiene la ruta base del proyecto."""
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    @staticmethod
    def obtener_ruta_puntajes():
        """Obtiene la ruta de la carpeta de puntajes."""
        return os.path.join(Config.obtener_ruta_base(), "puntajes")

