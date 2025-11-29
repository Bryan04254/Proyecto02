"""
Configuración y paleta de colores para la GUI del juego.
Estilo: Pixel art retro con colores neón sobre fondo oscuro.
"""

import os


class Colores:
    """
    Paleta de colores del juego - tema cyberpunk/retro.
    
    Define todos los colores utilizados en la interfaz gráfica del juego.
    Los colores están en formato RGB (Red, Green, Blue) como tuplas de 3 enteros.
    El estilo general es oscuro con acentos neón para crear un ambiente cyberpunk.
    """
    
    # ============================================
    # COLORES DE FONDO
    # ============================================
    # Fondos oscuros para crear contraste con elementos neón
    FONDO_OSCURO = (13, 17, 23)  # Fondo principal (muy oscuro, casi negro)
    FONDO_MENU = (22, 27, 34)  # Fondo del menú principal (ligeramente más claro)
    FONDO_PANEL = (33, 38, 45)  # Fondo de paneles y ventanas (gris oscuro)
    
    # ============================================
    # COLORES NEÓN PRINCIPALES
    # ============================================
    # Colores brillantes y saturados para elementos destacados
    CYAN_NEON = (0, 255, 255)  # Cyan brillante (usado en modo escapa)
    MAGENTA_NEON = (255, 0, 128)  # Magenta brillante (usado en modo cazador)
    VERDE_NEON = (57, 255, 20)  # Verde neón (usado para efectos positivos)
    AMARILLO_NEON = (255, 255, 0)  # Amarillo neón (usado para advertencias)
    NARANJA_NEON = (255, 165, 0)  # Naranja neón (usado para efectos especiales)
    ROJO_NEON = (255, 50, 50)  # Rojo neón (usado para peligros y advertencias)
    
    # ============================================
    # COLORES SUAVES
    # ============================================
    # Colores más apagados para fondos de elementos UI
    CYAN_SUAVE = (0, 100, 100)  # Cyan suave (fondo de botones)
    MAGENTA_SUAVE = (100, 0, 50)  # Magenta suave (fondo de botones)
    VERDE_SUAVE = (20, 80, 20)  # Verde suave (fondo de elementos)
    
    # ============================================
    # COLORES DE TILES DEL MAPA
    # ============================================
    # Colores para los diferentes tipos de casillas del laberinto
    CAMINO = (45, 55, 72)  # Color del camino (gris oscuro)
    CAMINO_ILUMINADO = (60, 70, 90)  # Camino iluminado (gris más claro)
    MURO = (88, 28, 135)  # Color del muro (púrpura oscuro)
    MURO_BORDE = (139, 92, 246)  # Borde del muro (púrpura claro)
    LIANA = (34, 197, 94)  # Color de liana (verde)
    LIANA_BORDE = (74, 222, 128)  # Borde de liana (verde claro)
    TUNEL = (59, 130, 246)  # Color de túnel (azul)
    TUNEL_BORDE = (147, 197, 253)  # Borde de túnel (azul claro)
    
    # ============================================
    # COLORES DEL JUGADOR
    # ============================================
    # Colores para representar al jugador en el mapa
    JUGADOR = (250, 204, 21)  # Color principal del jugador (amarillo dorado)
    JUGADOR_GLOW = (253, 224, 71)  # Efecto de brillo alrededor del jugador
    
    # ============================================
    # COLORES DE POSICIONES ESPECIALES
    # ============================================
    # Colores para marcar inicio y salidas del mapa
    INICIO = (34, 197, 94)  # Color de la posición inicial (verde)
    SALIDA = (239, 68, 68)  # Color de las salidas (rojo)
    SALIDA_GLOW = (248, 113, 113)  # Efecto de brillo en las salidas (rojo claro)
    
    # ============================================
    # COLORES DE TEXTO
    # ============================================
    # Colores para texto en la interfaz
    TEXTO = (248, 250, 252)  # Texto principal (blanco casi puro)
    TEXTO_SECUNDARIO = (148, 163, 184)  # Texto secundario (gris claro)
    TEXTO_DESHABILITADO = (71, 85, 105)  # Texto deshabilitado (gris oscuro)
    
    # ============================================
    # COLORES DE ENERGÍA
    # ============================================
    # Colores para la barra de energía del jugador
    ENERGIA_LLENA = (34, 197, 94)  # Energía alta (verde)
    ENERGIA_MEDIA = (250, 204, 21)  # Energía media (amarillo)
    ENERGIA_BAJA = (239, 68, 68)  # Energía baja (rojo)
    ENERGIA_FONDO = (30, 41, 59)  # Fondo de la barra de energía (gris oscuro)
    
    # ============================================
    # COLORES DE PUNTAJES
    # ============================================
    # Colores para destacar los mejores puntajes (aunque ya no se usan en el formato actual)
    ORO = (255, 215, 0)  # Color dorado (primer lugar)
    PLATA = (192, 192, 192)  # Color plateado (segundo lugar)
    BRONCE = (205, 127, 50)  # Color bronce (tercer lugar)


class Config:
    """
    Configuración general del juego.
    
    Contiene todas las constantes de configuración del juego:
    - Dimensiones de ventana y pantalla
    - Configuración del mapa
    - Parámetros de animación
    - Rutas de archivos
    """
    
    # ============================================
    # CONFIGURACIÓN DE VENTANA
    # ============================================
    PANTALLA_COMPLETA = True  # Activar pantalla completa por defecto
    ANCHO_VENTANA = 1280  # Ancho en modo ventana (si no está en pantalla completa)
    ALTO_VENTANA = 720   # Alto en modo ventana (si no está en pantalla completa)
    FPS = 60  # Frames por segundo (velocidad de actualización)
    TITULO = "Escapa del Laberinto"  # Título de la ventana
    
    # ============================================
    # CONFIGURACIÓN DEL MAPA
    # ============================================
    TAMANO_CELDA = 32  # Tamaño en píxeles de cada celda del mapa
    MAPA_ANCHO = 40  # Ancho del mapa en celdas (aumentado para mapas más grandes)
    MAPA_ALTO = 30   # Alto del mapa en celdas (aumentado para mapas más grandes)
    
    # Offset del mapa en la pantalla (para centrar y posicionar)
    MAPA_OFFSET_X = 50  # Desplazamiento horizontal del mapa
    MAPA_OFFSET_Y = 80  # Desplazamiento vertical del mapa
    
    # ============================================
    # CONFIGURACIÓN DE UI
    # ============================================
    # Panel lateral (ya no se usa en el diseño actual, pero se mantiene por compatibilidad)
    PANEL_X = 720  # Posición X del panel lateral
    PANEL_ANCHO = 540  # Ancho del panel lateral
    
    # ============================================
    # CONFIGURACIÓN DEL JUGADOR
    # ============================================
    ENERGIA_INICIAL = 100  # Energía inicial por defecto (se puede sobrescribir por dificultad)
    
    # ============================================
    # CONFIGURACIÓN DE TIEMPOS
    # ============================================
    TIEMPO_PARTIDA_ESCAPA = 120  # Tiempo límite para modo escapa (segundos)
    TIEMPO_PARTIDA_CAZADOR = 180  # Tiempo límite para modo cazador (segundos)
    
    # ============================================
    # CONFIGURACIÓN DE ANIMACIONES
    # ============================================
    VELOCIDAD_PARPADEO = 0.5  # Velocidad de parpadeo de elementos (ciclos por segundo)
    VELOCIDAD_PARTICULAS = 2  # Velocidad de partículas de efectos visuales
    
    # ============================================
    # MÉTODOS DE RUTAS
    # ============================================
    @staticmethod
    def obtener_ruta_base():
        """
        Obtiene la ruta base del proyecto.
        
        Returns:
            Ruta absoluta del directorio raíz del proyecto.
        """
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    @staticmethod
    def obtener_ruta_puntajes():
        """
        Obtiene la ruta de la carpeta de puntajes.
        
        Returns:
            Ruta absoluta del directorio donde se guardan los archivos de puntajes.
        """
        return os.path.join(Config.obtener_ruta_base(), "data", "puntajes")

