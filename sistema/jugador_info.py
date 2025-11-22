"""
Módulo jugador_info: Define la clase para información del jugador.
"""

from typing import Optional
from datetime import datetime


class JugadorInfo:
    """
    Clase que almacena información del jugador.
    """
    
    def __init__(self, nombre: str, fecha_registro: Optional[datetime] = None):
        """
        Inicializa la información del jugador.
        
        Args:
            nombre: Nombre del jugador.
            fecha_registro: Fecha de registro (opcional, por defecto usa la fecha actual).
        """
        self.nombre = nombre
        self.fecha_registro = fecha_registro if fecha_registro else datetime.now()
    
    def __repr__(self) -> str:
        """Representación de la información del jugador."""
        return f"JugadorInfo(nombre='{self.nombre}', fecha_registro={self.fecha_registro})"


def registrar_jugador(nombre: str) -> JugadorInfo:
    """
    Función auxiliar para registrar un nuevo jugador.
    
    Args:
        nombre: Nombre del jugador a registrar.
        
    Returns:
        Objeto JugadorInfo con la información del jugador.
    """
    return JugadorInfo(nombre)

