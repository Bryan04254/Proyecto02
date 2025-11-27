"""
Módulo puntajes: Define las clases para el sistema de puntajes y top 5.
Incluye soporte para fechas y estadísticas detalladas.
"""

import json
import os
from typing import List, Optional
from enum import Enum
from datetime import datetime


class ModoJuego(Enum):
    """Enum para los modos de juego."""
    ESCAPA = "escapa"
    CAZADOR = "cazador"


class Puntaje:
    """
    Clase que representa un puntaje de un jugador.
    Incluye fecha, tiempo de juego y movimientos para estadísticas detalladas.
    """
    
    def __init__(self, nombre_jugador: str, modo: str, puntos: float,
                 fecha: Optional[datetime] = None, 
                 tiempo_juego: Optional[float] = None,
                 movimientos: Optional[int] = None):
        """
        Inicializa un puntaje.
        
        Args:
            nombre_jugador: Nombre del jugador.
            modo: Modo de juego ("escapa" o "cazador").
            puntos: Puntos obtenidos.
            fecha: Fecha y hora cuando se obtuvo el puntaje.
            tiempo_juego: Tiempo de juego en segundos.
            movimientos: Número de movimientos realizados.
        """
        self.nombre_jugador = nombre_jugador
        self.modo = modo
        self.puntos = puntos
        self.fecha = fecha if fecha else datetime.now()
        self.tiempo_juego = tiempo_juego
        self.movimientos = movimientos
    
    def to_dict(self) -> dict:
        """
        Convierte el puntaje a un diccionario.
        
        Returns:
            Diccionario con los datos del puntaje.
        """
        data = {
            "nombre_jugador": self.nombre_jugador,
            "modo": self.modo,
            "puntos": self.puntos,
            "fecha": self.fecha.isoformat() if self.fecha else None
        }
        
        if self.tiempo_juego is not None:
            data["tiempo_juego"] = self.tiempo_juego
        if self.movimientos is not None:
            data["movimientos"] = self.movimientos
        
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Puntaje':
        """
        Crea un Puntaje desde un diccionario.
        
        Args:
            data: Diccionario con los datos del puntaje.
            
        Returns:
            Objeto Puntaje.
        """
        fecha = None
        if "fecha" in data and data["fecha"]:
            try:
                fecha = datetime.fromisoformat(data["fecha"])
            except (ValueError, TypeError):
                fecha = datetime.now()
        
        return cls(
            nombre_jugador=data["nombre_jugador"],
            modo=data["modo"],
            puntos=data["puntos"],
            fecha=fecha,
            tiempo_juego=data.get("tiempo_juego"),
            movimientos=data.get("movimientos")
        )
    
    def obtener_fecha_formateada(self) -> str:
        """
        Obtiene la fecha en formato legible.
        
        Returns:
            String con la fecha formateada.
        """
        if self.fecha:
            return self.fecha.strftime("%d/%m/%Y %H:%M")
        return "Sin fecha"
    
    def __repr__(self) -> str:
        """Representación del puntaje."""
        fecha_str = self.obtener_fecha_formateada()
        return f"Puntaje(nombre='{self.nombre_jugador}', modo='{self.modo}', puntos={self.puntos}, fecha='{fecha_str}')"


class ScoreBoard:
    """
    Clase que gestiona los puntajes y el top 5 por modo de juego.
    """
    
    def __init__(self, directorio_puntajes: str = "data/puntajes"):
        """
        Inicializa el ScoreBoard.
        
        Args:
            directorio_puntajes: Directorio donde se guardan los archivos de puntajes.
        """
        self.directorio_puntajes = directorio_puntajes
        self._puntajes: dict = {
            ModoJuego.ESCAPA.value: [],
            ModoJuego.CAZADOR.value: []
        }
        
        # Crear directorio si no existe
        if not os.path.exists(self.directorio_puntajes):
            os.makedirs(self.directorio_puntajes)
        
        # Cargar puntajes existentes
        self._cargar_puntajes()
    
    def registrar_puntaje(self, modo: str, nombre_jugador: str, puntos: float,
                          tiempo_juego: float = None, movimientos: int = None) -> Puntaje:
        """
        Registra un nuevo puntaje.
        
        Args:
            modo: Modo de juego ("escapa" o "cazador").
            nombre_jugador: Nombre del jugador.
            puntos: Puntos obtenidos.
            tiempo_juego: Tiempo de juego en segundos (opcional).
            movimientos: Número de movimientos (opcional).
            
        Returns:
            El puntaje registrado.
        """
        # Validar modo
        if modo not in [ModoJuego.ESCAPA.value, ModoJuego.CAZADOR.value]:
            raise ValueError(f"Modo inválido: {modo}. Debe ser 'escapa' o 'cazador'.")
        
        # Crear nuevo puntaje con fecha actual
        nuevo_puntaje = Puntaje(
            nombre_jugador=nombre_jugador,
            modo=modo,
            puntos=puntos,
            tiempo_juego=tiempo_juego,
            movimientos=movimientos
        )
        
        # Agregar a la lista
        self._puntajes[modo].append(nuevo_puntaje)
        
        # Ordenar de mayor a menor
        self._puntajes[modo].sort(key=lambda p: p.puntos, reverse=True)
        
        # Mantener solo los 10 mejores para evitar que crezca demasiado
        self._puntajes[modo] = self._puntajes[modo][:10]
        
        # Guardar en archivo
        self._guardar_puntajes(modo)
        
        return nuevo_puntaje
    
    def obtener_top5(self, modo: str) -> List[Puntaje]:
        """
        Obtiene el top 5 de puntajes para un modo específico.
        
        Args:
            modo: Modo de juego ("escapa" o "cazador").
            
        Returns:
            Lista de los 5 mejores puntajes ordenados de mayor a menor.
        """
        # Validar modo
        if modo not in [ModoJuego.ESCAPA.value, ModoJuego.CAZADOR.value]:
            raise ValueError(f"Modo inválido: {modo}. Debe ser 'escapa' o 'cazador'.")
        
        # Ordenar y devolver top 5
        puntajes_ordenados = sorted(
            self._puntajes[modo], 
            key=lambda p: p.puntos, 
            reverse=True
        )
        
        return puntajes_ordenados[:5]
    
    def _obtener_archivo_puntajes(self, modo: str) -> str:
        """
        Obtiene la ruta del archivo de puntajes para un modo.
        
        Args:
            modo: Modo de juego.
            
        Returns:
            Ruta del archivo.
        """
        nombre_archivo = f"puntajes_{modo}.json"
        return os.path.join(self.directorio_puntajes, nombre_archivo)
    
    def _cargar_puntajes(self) -> None:
        """Carga los puntajes desde los archivos JSON."""
        for modo in [ModoJuego.ESCAPA.value, ModoJuego.CAZADOR.value]:
            archivo = self._obtener_archivo_puntajes(modo)
            if os.path.exists(archivo):
                try:
                    with open(archivo, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self._puntajes[modo] = [Puntaje.from_dict(p) for p in data]
                except (json.JSONDecodeError, KeyError, IOError) as e:
                    print(f"Error al cargar puntajes de {archivo}: {e}")
                    self._puntajes[modo] = []
            else:
                self._puntajes[modo] = []
    
    def _guardar_puntajes(self, modo: str) -> None:
        """
        Guarda los puntajes en el archivo JSON correspondiente.
        
        Args:
            modo: Modo de juego.
        """
        archivo = self._obtener_archivo_puntajes(modo)
        try:
            data = [p.to_dict() for p in self._puntajes[modo]]
            with open(archivo, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error al guardar puntajes en {archivo}: {e}")

