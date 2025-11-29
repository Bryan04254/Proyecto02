"""
Módulo dificultad: Define el sistema de dificultad del juego.
"""

from enum import Enum
from typing import Dict, Any


class Dificultad(Enum):
    """Niveles de dificultad del juego."""
    FACIL = "facil"
    NORMAL = "normal"
    DIFICIL = "dificil"


class ConfiguracionDificultad:
    """
    Configuración de parámetros para cada nivel de dificultad.
    
    Esta clase centraliza todos los parámetros de balance del juego
    para cada nivel de dificultad. Permite ajustar fácilmente:
    - Cantidad y velocidad de enemigos
    - Energía inicial del jugador
    - Sistema de puntuación
    - Tiempos de respawn
    """
    
    # ============================================
    # CONFIGURACIONES POR DIFICULTAD
    # ============================================
    # Cada dificultad tiene un diccionario con todos los parámetros
    # que afectan el balance del juego
    CONFIGURACIONES: Dict[Dificultad, Dict[str, Any]] = {
        Dificultad.FACIL: {
            # Enemigos: pocos y lentos
            "cantidad_enemigos": 4,  # Aumentado de 2 a 4 para mejor balance
            "velocidad_enemigos": 0.5,  # movimientos por segundo (lento)
            # Jugador: mucha energía inicial
            "energia_inicial_jugador": 200,  # Aumentado de 150 a 200 para mejor balance
            # Sistema de puntuación (modo escapa)
            "puntos_base_escapa": 100,  # Puntos base al completar el modo
            # Sistema de puntuación (modo cazador)
            "puntos_base_cazador": 50,  # Puntos iniciales en modo cazador
            "puntos_por_enemigo_eliminado": 15,  # Bono por eliminar enemigo con trampa
            "puntos_perdidos_por_escape": 5,  # Puntos perdidos si enemigo escapa
            "puntos_ganados_por_captura": 10,  # Puntos ganados al capturar enemigo
            # Sistema de respawn
            "tiempo_respawn_enemigo": 10.0,  # segundos (según especificación)
        },
        Dificultad.NORMAL: {
            # Enemigos: cantidad y velocidad moderadas
            "cantidad_enemigos": 8,  # Aumentado de 4 a 8 para mejor balance
            "velocidad_enemigos": 1.0,  # movimientos por segundo (normal)
            # Jugador: energía moderada
            "energia_inicial_jugador": 150,  # Aumentado de 100 a 150 para mejor balance
            # Sistema de puntuación (modo escapa)
            "puntos_base_escapa": 200,  # Puntos base al completar el modo
            # Sistema de puntuación (modo cazador)
            "puntos_base_cazador": 100,  # Puntos iniciales en modo cazador
            "puntos_por_enemigo_eliminado": 20,  # Bono por eliminar enemigo con trampa
            "puntos_perdidos_por_escape": 10,  # Puntos perdidos si enemigo escapa
            "puntos_ganados_por_captura": 20,  # Puntos ganados al capturar enemigo
            # Sistema de respawn
            "tiempo_respawn_enemigo": 10.0,  # segundos (según especificación)
        },
        Dificultad.DIFICIL: {
            # Enemigos: muchos y rápidos
            "cantidad_enemigos": 12,  # Aumentado de 6 a 12 para mejor balance
            "velocidad_enemigos": 1.5,  # movimientos por segundo (rápido)
            # Jugador: poca energía inicial
            "energia_inicial_jugador": 120,  # Aumentado de 75 a 120 para mejor balance
            # Sistema de puntuación (modo escapa)
            "puntos_base_escapa": 300,  # Puntos base al completar el modo (más recompensa)
            # Sistema de puntuación (modo cazador)
            "puntos_base_cazador": 150,  # Puntos iniciales en modo cazador
            "puntos_por_enemigo_eliminado": 30,  # Bono por eliminar enemigo con trampa (más recompensa)
            "puntos_perdidos_por_escape": 20,  # Puntos perdidos si enemigo escapa (más penalización)
            "puntos_ganados_por_captura": 40,  # Puntos ganados al capturar enemigo (más recompensa)
            # Sistema de respawn
            "tiempo_respawn_enemigo": 10.0,  # segundos (según especificación)
        }
    }
    
    @classmethod
    def obtener_configuracion(cls, dificultad: Dificultad) -> Dict[str, Any]:
        """
        Obtiene la configuración para un nivel de dificultad.
        
        Args:
            dificultad: Nivel de dificultad.
            
        Returns:
            Diccionario con los parámetros de configuración.
        """
        return cls.CONFIGURACIONES.get(dificultad, cls.CONFIGURACIONES[Dificultad.NORMAL]).copy()
    
    @classmethod
    def obtener_cantidad_enemigos(cls, dificultad: Dificultad) -> int:
        """
        Obtiene la cantidad de enemigos para una dificultad.
        
        Args:
            dificultad: Nivel de dificultad.
            
        Returns:
            Cantidad de enemigos.
        """
        return cls.obtener_configuracion(dificultad)["cantidad_enemigos"]
    
    @classmethod
    def obtener_velocidad_enemigos(cls, dificultad: Dificultad) -> float:
        """
        Obtiene la velocidad de los enemigos para una dificultad.
        
        Args:
            dificultad: Nivel de dificultad.
            
        Returns:
            Velocidad de los enemigos.
        """
        return cls.obtener_configuracion(dificultad)["velocidad_enemigos"]
    
    @classmethod
    def obtener_energia_inicial(cls, dificultad: Dificultad) -> int:
        """
        Obtiene la energía inicial del jugador para una dificultad.
        
        Args:
            dificultad: Nivel de dificultad.
            
        Returns:
            Energía inicial.
        """
        return cls.obtener_configuracion(dificultad)["energia_inicial_jugador"]
    
    @classmethod
    def obtener_puntos_base_escapa(cls, dificultad: Dificultad) -> int:
        """
        Obtiene los puntos base para el modo escapa.
        
        Args:
            dificultad: Nivel de dificultad.
            
        Returns:
            Puntos base.
        """
        return cls.obtener_configuracion(dificultad)["puntos_base_escapa"]
    
    @classmethod
    def obtener_puntos_base_cazador(cls, dificultad: Dificultad) -> int:
        """
        Obtiene los puntos base para el modo cazador.
        
        Args:
            dificultad: Nivel de dificultad.
            
        Returns:
            Puntos base.
        """
        return cls.obtener_configuracion(dificultad)["puntos_base_cazador"]
    
    @classmethod
    def obtener_puntos_por_enemigo_eliminado(cls, dificultad: Dificultad) -> int:
        """
        Obtiene los puntos por enemigo eliminado.
        
        Args:
            dificultad: Nivel de dificultad.
            
        Returns:
            Puntos por enemigo eliminado.
        """
        return cls.obtener_configuracion(dificultad)["puntos_por_enemigo_eliminado"]
    
    @classmethod
    def obtener_puntos_perdidos_por_escape(cls, dificultad: Dificultad) -> int:
        """
        Obtiene los puntos perdidos cuando un enemigo escapa (modo cazador).
        
        Args:
            dificultad: Nivel de dificultad.
            
        Returns:
            Puntos perdidos.
        """
        return cls.obtener_configuracion(dificultad)["puntos_perdidos_por_escape"]
    
    @classmethod
    def obtener_puntos_ganados_por_captura(cls, dificultad: Dificultad) -> int:
        """
        Obtiene los puntos ganados al capturar un enemigo (modo cazador).
        
        Args:
            dificultad: Nivel de dificultad.
            
        Returns:
            Puntos ganados.
        """
        return cls.obtener_configuracion(dificultad)["puntos_ganados_por_captura"]
    
    @classmethod
    def obtener_tiempo_respawn(cls, dificultad: Dificultad) -> float:
        """
        Obtiene el tiempo de respawn de los enemigos.
        
        Args:
            dificultad: Nivel de dificultad.
            
        Returns:
            Tiempo de respawn en segundos.
        """
        return cls.obtener_configuracion(dificultad)["tiempo_respawn_enemigo"]

