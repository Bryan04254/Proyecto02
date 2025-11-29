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
    """
    
    # Configuraciones por dificultad
    CONFIGURACIONES: Dict[Dificultad, Dict[str, Any]] = {
        Dificultad.FACIL: {
            "cantidad_enemigos": 4,  # Aumentado de 2 a 4
            "velocidad_enemigos": 0.5,  # movimientos por segundo
            "energia_inicial_jugador": 200,  # Aumentado de 150 a 200
            "puntos_base_escapa": 100,
            "puntos_base_cazador": 50,
            "puntos_por_enemigo_eliminado": 15,
            "puntos_perdidos_por_escape": 5,
            "puntos_ganados_por_captura": 10,
            "tiempo_respawn_enemigo": 10.0,  # segundos (según especificación)
        },
        Dificultad.NORMAL: {
            "cantidad_enemigos": 8,  # Aumentado de 4 a 8
            "velocidad_enemigos": 1.0,
            "energia_inicial_jugador": 150,  # Aumentado de 100 a 150
            "puntos_base_escapa": 200,
            "puntos_base_cazador": 100,
            "puntos_por_enemigo_eliminado": 20,
            "puntos_perdidos_por_escape": 10,
            "puntos_ganados_por_captura": 20,
            "tiempo_respawn_enemigo": 10.0,  # segundos (según especificación)
        },
        Dificultad.DIFICIL: {
            "cantidad_enemigos": 12,  # Aumentado de 6 a 12
            "velocidad_enemigos": 1.5,
            "energia_inicial_jugador": 120,  # Aumentado de 75 a 120
            "puntos_base_escapa": 300,
            "puntos_base_cazador": 150,
            "puntos_por_enemigo_eliminado": 30,
            "puntos_perdidos_por_escape": 20,
            "puntos_ganados_por_captura": 40,
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

