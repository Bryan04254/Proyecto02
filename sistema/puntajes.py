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
        # Información básica del puntaje
        self.nombre_jugador = nombre_jugador
        self.modo = modo  # "escapa" o "cazador"
        self.puntos = puntos  # Puntos obtenidos (puede ser float)
        # Fecha y hora cuando se obtuvo el puntaje
        self.fecha = fecha if fecha else datetime.now()
        # Estadísticas opcionales
        self.tiempo_juego = tiempo_juego  # Tiempo de juego en segundos
        self.movimientos = movimientos  # Número de movimientos realizados
    
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
        # Normalizar la ruta a absoluta si es relativa
        if not os.path.isabs(directorio_puntajes):
            # Obtener el directorio raíz del proyecto (asumiendo que este archivo está en sistema/)
            ruta_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            directorio_puntajes = os.path.join(ruta_base, directorio_puntajes)
        
        # Directorio donde se guardan los archivos JSON de puntajes (ruta absoluta)
        self.directorio_puntajes = os.path.normpath(directorio_puntajes)
        
        # Diccionario que almacena los puntajes en memoria
        # Separado por modo de juego
        self._puntajes: dict = {
            ModoJuego.ESCAPA.value: [],  # Lista de puntajes del modo escapa
            ModoJuego.CAZADOR.value: []  # Lista de puntajes del modo cazador
        }
        
        # Crear directorio si no existe
        # Esto asegura que el directorio esté disponible para guardar puntajes
        if not os.path.exists(self.directorio_puntajes):
            os.makedirs(self.directorio_puntajes, exist_ok=True)
            print(f"[DEBUG] Directorio de puntajes creado: {self.directorio_puntajes}")
        
        # Cargar puntajes existentes desde archivos JSON
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
        # ============================================
        # VALIDACIÓN
        # ============================================
        # Validar que el modo sea válido
        if modo not in [ModoJuego.ESCAPA.value, ModoJuego.CAZADOR.value]:
            raise ValueError(f"Modo inválido: {modo}. Debe ser 'escapa' o 'cazador'.")
        
        # ============================================
        # CREAR NUEVO PUNTAJE
        # ============================================
        # Crear nuevo puntaje con fecha actual
        nuevo_puntaje = Puntaje(
            nombre_jugador=nombre_jugador,
            modo=modo,
            puntos=puntos,
            tiempo_juego=tiempo_juego,
            movimientos=movimientos
        )
        
        # ============================================
        # AGREGAR Y ORDENAR
        # ============================================
        # Agregar el nuevo puntaje a la lista del modo correspondiente
        self._puntajes[modo].append(nuevo_puntaje)
        
        # Ordenar de mayor a menor (mejores puntajes primero)
        self._puntajes[modo].sort(key=lambda p: p.puntos, reverse=True)
        
        # Mantener solo los 10 mejores para evitar que la lista crezca demasiado
        # Esto optimiza el rendimiento y el tamaño de los archivos JSON
        self._puntajes[modo] = self._puntajes[modo][:10]
        
        # ============================================
        # PERSISTENCIA
        # ============================================
        # Guardar los puntajes actualizados en el archivo JSON
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
        """
        Carga los puntajes desde los archivos JSON.
        
        Lee los archivos JSON de puntajes para ambos modos y los carga
        en memoria. Si un archivo no existe o hay un error, se inicializa
        una lista vacía para ese modo.
        """
        # Cargar puntajes para ambos modos
        for modo in [ModoJuego.ESCAPA.value, ModoJuego.CAZADOR.value]:
            archivo = self._obtener_archivo_puntajes(modo)
            print(f"[DEBUG _cargar_puntajes] Cargando {modo} desde: {archivo}")
            if os.path.exists(archivo):
                try:
                    # Leer archivo JSON y convertir a objetos Puntaje
                    with open(archivo, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Convertir cada diccionario a un objeto Puntaje
                        self._puntajes[modo] = [Puntaje.from_dict(p) for p in data]
                        print(f"[DEBUG _cargar_puntajes] {modo}: {len(self._puntajes[modo])} puntajes cargados")
                except (json.JSONDecodeError, KeyError, IOError) as e:
                    # Si hay error al cargar, inicializar lista vacía
                    print(f"[ERROR] Error al cargar puntajes de {archivo}: {e}")
                    self._puntajes[modo] = []
            else:
                # Si el archivo no existe, inicializar lista vacía
                print(f"[DEBUG _cargar_puntajes] Archivo no existe: {archivo}")
                self._puntajes[modo] = []
    
    def recargar_puntajes(self) -> None:
        """
        Recarga los puntajes desde los archivos JSON.
        
        Útil para actualizar la lista de puntajes después de que se hayan
        guardado nuevos puntajes en los archivos.
        """
        self._cargar_puntajes()
    
    def _guardar_puntajes(self, modo: str) -> None:
        """
        Guarda los puntajes en el archivo JSON correspondiente.
        
        Convierte los objetos Puntaje a diccionarios y los guarda
        en formato JSON con indentación para legibilidad.
        
        Args:
            modo: Modo de juego ("escapa" o "cazador").
        """
        archivo = self._obtener_archivo_puntajes(modo)
        print(f"[DEBUG] Intentando guardar puntajes en: {archivo}")
        print(f"[DEBUG] Directorio base: {self.directorio_puntajes}")
        print(f"[DEBUG] Total de puntajes a guardar: {len(self._puntajes[modo])}")
        
        try:
            # Asegurar que el directorio existe antes de guardar
            directorio = os.path.dirname(archivo)
            if not os.path.exists(directorio):
                os.makedirs(directorio, exist_ok=True)
                print(f"[DEBUG] Directorio creado: {directorio}")
            
            # Convertir objetos Puntaje a diccionarios
            data = [p.to_dict() for p in self._puntajes[modo]]
            print(f"[DEBUG] Datos a guardar: {len(data)} puntajes")
            
            # Guardar en archivo JSON con formato legible (indentación)
            with open(archivo, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                # Forzar escritura al disco antes de cerrar
                f.flush()
                os.fsync(f.fileno())
            
            # Verificar que el archivo se guardó correctamente
            if os.path.exists(archivo):
                tamanio = os.path.getsize(archivo)
                print(f"[DEBUG] ✓ Puntajes guardados exitosamente en {archivo} (tamaño: {tamanio} bytes)")
            else:
                print(f"[ERROR] ✗ ADVERTENCIA: El archivo {archivo} no se creó después de guardar")
        except Exception as e:
            # Capturar cualquier error y mostrarlo
            print(f"[ERROR] ✗ ERROR al guardar puntajes en {archivo}: {e}")
            import traceback
            traceback.print_exc()

