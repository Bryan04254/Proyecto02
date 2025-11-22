"""
Módulo puntajes: Define las clases para el sistema de puntajes y top 5.
"""

import json
import os
from typing import List, Optional
from enum import Enum


class ModoJuego(Enum):
    """Enum para los modos de juego."""
    ESCAPA = "escapa"
    CAZADOR = "cazador"


class Puntaje:
    """
    Clase que representa un puntaje de un jugador.
    """
    
    def __init__(self, nombre_jugador: str, modo: str, puntos: float):
        """
        Inicializa un puntaje.
        
        Args:
            nombre_jugador: Nombre del jugador.
            modo: Modo de juego ("escapa" o "cazador").
            puntos: Puntos obtenidos.
        """
        self.nombre_jugador = nombre_jugador
        self.modo = modo
        self.puntos = puntos
    
    def to_dict(self) -> dict:
        """
        Convierte el puntaje a un diccionario.
        
        Returns:
            Diccionario con los datos del puntaje.
        """
        return {
            "nombre_jugador": self.nombre_jugador,
            "modo": self.modo,
            "puntos": self.puntos
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Puntaje':
        """
        Crea un Puntaje desde un diccionario.
        
        Args:
            data: Diccionario con los datos del puntaje.
            
        Returns:
            Objeto Puntaje.
        """
        return cls(
            nombre_jugador=data["nombre_jugador"],
            modo=data["modo"],
            puntos=data["puntos"]
        )
    
    def __repr__(self) -> str:
        """Representación del puntaje."""
        return f"Puntaje(nombre='{self.nombre_jugador}', modo='{self.modo}', puntos={self.puntos})"


class ScoreBoard:
    """
    Clase que gestiona los puntajes y el top 5 por modo de juego.
    """
    
    def __init__(self, directorio_puntajes: str = "puntajes"):
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
    
    def registrar_puntaje(self, modo: str, nombre_jugador: str, puntos: float) -> None:
        """
        Registra un nuevo puntaje.
        
        Args:
            modo: Modo de juego ("escapa" o "cazador").
            nombre_jugador: Nombre del jugador.
            puntos: Puntos obtenidos.
        """
        # Validar modo
        if modo not in [ModoJuego.ESCAPA.value, ModoJuego.CAZADOR.value]:
            raise ValueError(f"Modo inválido: {modo}. Debe ser 'escapa' o 'cazador'.")
        
        # Crear nuevo puntaje
        nuevo_puntaje = Puntaje(nombre_jugador, modo, puntos)
        
        # Agregar a la lista
        self._puntajes[modo].append(nuevo_puntaje)
        
        # Ordenar de mayor a menor
        self._puntajes[modo].sort(key=lambda p: p.puntos, reverse=True)
        
        # Mantener solo los mejores (opcional: podemos mantener todos y solo mostrar top 5)
        # Por ahora mantenemos todos, pero podemos limitar si es necesario
        
        # Guardar en archivo
        self._guardar_puntajes(modo)
    
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

