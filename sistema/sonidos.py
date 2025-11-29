"""
Módulo sonidos: Sistema de gestión de sonidos para el juego.
Incluye sonidos programáticos y soporte para archivos de audio.
"""

import pygame
import numpy as np
import os
from typing import Optional, Dict
from enum import Enum


class TipoSonido(Enum):
    """Tipos de sonidos disponibles en el juego."""
    PASO_NORMAL = "paso_normal"
    PASO_CORRIENDO = "paso_corriendo"
    CHOQUE_MURO = "choque_muro"
    PASO_LIANA = "paso_liana"
    PASO_TUNEL = "paso_tunel"
    TRAMPA_COLOCAR = "trampa_colocar"
    TRAMPA_ACTIVAR = "trampa_activar"
    ENEMIGO_CAPTURADO = "enemigo_capturado"
    VICTORIA = "victoria"
    DERROTA = "derrota"
    MUSICA_AMBIENTE = "musica_ambiente"


class GestorSonidos:
    """
    Gestor de sonidos del juego.
    
    Genera sonidos programáticamente y también puede cargar archivos de audio.
    Maneja música de fondo y efectos de sonido.
    """
    
    def __init__(self):
        """Inicializa el gestor de sonidos."""
        # Inicializar mixer de pygame si no está inicializado
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Volumen por defecto
        self.volumen_efectos = 0.5
        self.volumen_musica = 0.3
        
        # Cache de sonidos generados
        self.sonidos_cache: Dict[str, pygame.mixer.Sound] = {}
        
        # Música de fondo
        self.musica_actual: Optional[pygame.mixer.Sound] = None
        self.musica_reproduciendo = False
        
        # Generar todos los sonidos programáticos
        self._generar_sonidos()
    
    def _generar_sonidos(self):
        """Genera todos los sonidos programáticos."""
        # Sonidos de pasos (caminar)
        self.sonidos_cache[TipoSonido.PASO_NORMAL.value] = self._generar_paso_normal()
        self.sonidos_cache[TipoSonido.PASO_CORRIENDO.value] = self._generar_paso_corriendo()
        
        # Sonido de choque
        self.sonidos_cache[TipoSonido.CHOQUE_MURO.value] = self._generar_choque_muro()
        
        # Sonidos de tiles especiales
        self.sonidos_cache[TipoSonido.PASO_LIANA.value] = self._generar_paso_liana()
        self.sonidos_cache[TipoSonido.PASO_TUNEL.value] = self._generar_paso_tunel()
        
        # Sonidos de acciones
        self.sonidos_cache[TipoSonido.TRAMPA_COLOCAR.value] = self._generar_trampa_colocar()
        self.sonidos_cache[TipoSonido.TRAMPA_ACTIVAR.value] = self._generar_trampa_activar()
        self.sonidos_cache[TipoSonido.ENEMIGO_CAPTURADO.value] = self._generar_enemigo_capturado()
        
        # Sonidos de resultado
        self.sonidos_cache[TipoSonido.VICTORIA.value] = self._generar_victoria()
        self.sonidos_cache[TipoSonido.DERROTA.value] = self._generar_derrota()
        
        # Música ambiente
        self.sonidos_cache[TipoSonido.MUSICA_AMBIENTE.value] = self._generar_musica_ambiente()
    
    def _generar_tono(self, frecuencia: float, duracion: float = 0.1, 
                     tipo_onda: str = "sin", volumen: float = 1.0) -> pygame.mixer.Sound:
        """
        Genera un tono sintético.
        
        Args:
            frecuencia: Frecuencia en Hz.
            duracion: Duración en segundos.
            tipo_onda: Tipo de onda ("sin", "cuadrada", "sierra", "triangular").
            volumen: Volumen (0.0 a 1.0).
        """
        sample_rate = 22050
        frames = int(duracion * sample_rate)
        arr = np.zeros((frames, 2), dtype=np.int16)
        max_sample = 2**(16 - 1) - 1
        
        for i in range(frames):
            t = float(i) / sample_rate
            if tipo_onda == "sin":
                sample = np.sin(2 * np.pi * frecuencia * t)
            elif tipo_onda == "cuadrada":
                sample = np.sign(np.sin(2 * np.pi * frecuencia * t))
            elif tipo_onda == "sierra":
                sample = 2 * (t * frecuencia % 1.0) - 1
            elif tipo_onda == "triangular":
                sample = 2 * abs(2 * (t * frecuencia % 1.0) - 1) - 1
            else:
                sample = np.sin(2 * np.pi * frecuencia * t)
            
            val = int(max_sample * volumen * sample)
            arr[i][0] = val
            arr[i][1] = val
        
        return pygame.sndarray.make_sound(arr)
    
    def _generar_paso_normal(self) -> pygame.mixer.Sound:
        """Genera sonido de paso normal (caminar)."""
        # Sonido suave de pasos (baja frecuencia con ruido)
        duracion = 0.15
        sample_rate = 22050
        frames = int(duracion * sample_rate)
        arr = np.zeros((frames, 2), dtype=np.int16)
        max_sample = 2**(16 - 1) - 1
        
        for i in range(frames):
            t = float(i) / sample_rate
            # Mezcla de tono bajo con ruido suave
            tono = np.sin(2 * np.pi * 80 * t) * 0.3
            ruido = np.random.normal(0, 0.2)
            # Envelope exponencial
            envelope = np.exp(-t * 8)
            sample = (tono + ruido) * envelope
            val = int(max_sample * 0.4 * sample)
            arr[i][0] = val
            arr[i][1] = val
        
        return pygame.sndarray.make_sound(arr)
    
    def _generar_paso_corriendo(self) -> pygame.mixer.Sound:
        """Genera sonido de paso corriendo."""
        # Sonido más rápido y agudo que el paso normal
        duracion = 0.1
        sample_rate = 22050
        frames = int(duracion * sample_rate)
        arr = np.zeros((frames, 2), dtype=np.int16)
        max_sample = 2**(16 - 1) - 1
        
        for i in range(frames):
            t = float(i) / sample_rate
            # Tono más agudo con más ruido
            tono = np.sin(2 * np.pi * 120 * t) * 0.3
            ruido = np.random.normal(0, 0.3)
            envelope = np.exp(-t * 12)
            sample = (tono + ruido) * envelope
            val = int(max_sample * 0.5 * sample)
            arr[i][0] = val
            arr[i][1] = val
        
        return pygame.sndarray.make_sound(arr)
    
    def _generar_choque_muro(self) -> pygame.mixer.Sound:
        """Genera sonido de choque con muro."""
        # Sonido de impacto seco
        duracion = 0.2
        sample_rate = 22050
        frames = int(duracion * sample_rate)
        arr = np.zeros((frames, 2), dtype=np.int16)
        max_sample = 2**(16 - 1) - 1
        
        for i in range(frames):
            t = float(i) / sample_rate
            # Tono descendente con ruido
            frecuencia = 300 * (1 - t * 2)  # Desciende rápidamente
            tono = np.sin(2 * np.pi * frecuencia * t) * 0.5
            ruido = np.random.normal(0, 0.2) * (1 - t * 3)
            envelope = np.exp(-t * 15)
            sample = (tono + ruido) * envelope
            val = int(max_sample * 0.6 * sample)
            arr[i][0] = val
            arr[i][1] = val
        
        return pygame.sndarray.make_sound(arr)
    
    def _generar_paso_liana(self) -> pygame.mixer.Sound:
        """Genera sonido de pisar liana."""
        # Sonido suave y crujiente
        duracion = 0.25
        sample_rate = 22050
        frames = int(duracion * sample_rate)
        arr = np.zeros((frames, 2), dtype=np.int16)
        max_sample = 2**(16 - 1) - 1
        
        for i in range(frames):
            t = float(i) / sample_rate
            # Sonido crujiente con frecuencias múltiples
            tono1 = np.sin(2 * np.pi * 150 * t) * 0.2
            tono2 = np.sin(2 * np.pi * 200 * t) * 0.15
            ruido = np.random.normal(0, 0.15) * np.sin(2 * np.pi * 400 * t)
            envelope = np.exp(-t * 6)
            sample = (tono1 + tono2 + ruido) * envelope
            val = int(max_sample * 0.4 * sample)
            arr[i][0] = val
            arr[i][1] = val
        
        return pygame.sndarray.make_sound(arr)
    
    def _generar_paso_tunel(self) -> pygame.mixer.Sound:
        """Genera sonido de entrar en túnel."""
        # Sonido hueco y eco
        duracion = 0.3
        sample_rate = 22050
        frames = int(duracion * sample_rate)
        arr = np.zeros((frames, 2), dtype=np.int16)
        max_sample = 2**(16 - 1) - 1
        
        for i in range(frames):
            t = float(i) / sample_rate
            # Tono bajo con eco simulado
            tono_base = np.sin(2 * np.pi * 60 * t) * 0.3
            eco = np.sin(2 * np.pi * 60 * (t - 0.1)) * 0.15 if t > 0.1 else 0
            envelope = np.exp(-t * 4)
            sample = (tono_base + eco) * envelope
            val = int(max_sample * 0.5 * sample)
            arr[i][0] = val
            arr[i][1] = val
        
        return pygame.sndarray.make_sound(arr)
    
    def _generar_trampa_colocar(self) -> pygame.mixer.Sound:
        """Genera sonido de colocar trampa."""
        # Sonido de "clic" mecánico
        duracion = 0.15
        sample_rate = 22050
        frames = int(duracion * sample_rate)
        arr = np.zeros((frames, 2), dtype=np.int16)
        max_sample = 2**(16 - 1) - 1
        
        for i in range(frames):
            t = float(i) / sample_rate
            # Sonido agudo de clic
            frecuencia = 400 + 200 * (1 - t * 5)
            tono = np.sin(2 * np.pi * frecuencia * t) * 0.4
            envelope = np.exp(-t * 20)
            sample = tono * envelope
            val = int(max_sample * 0.5 * sample)
            arr[i][0] = val
            arr[i][1] = val
        
        return pygame.sndarray.make_sound(arr)
    
    def _generar_trampa_activar(self) -> pygame.mixer.Sound:
        """Genera sonido de activar trampa."""
        # Sonido más fuerte y explosivo
        duracion = 0.3
        sample_rate = 22050
        frames = int(duracion * sample_rate)
        arr = np.zeros((frames, 2), dtype=np.int16)
        max_sample = 2**(16 - 1) - 1
        
        for i in range(frames):
            t = float(i) / sample_rate
            # Explosión corta con frecuencias múltiples
            tono1 = np.sin(2 * np.pi * 300 * t) * 0.3
            tono2 = np.sin(2 * np.pi * 600 * t) * 0.2
            ruido = np.random.normal(0, 0.25) * (1 - t * 2)
            envelope = np.exp(-t * 8)
            sample = (tono1 + tono2 + ruido) * envelope
            val = int(max_sample * 0.7 * sample)
            arr[i][0] = val
            arr[i][1] = val
        
        return pygame.sndarray.make_sound(arr)
    
    def _generar_enemigo_capturado(self) -> pygame.mixer.Sound:
        """Genera sonido de enemigo capturado."""
        # Sonido ascendente de éxito
        duracion = 0.4
        sample_rate = 22050
        frames = int(duracion * sample_rate)
        arr = np.zeros((frames, 2), dtype=np.int16)
        max_sample = 2**(16 - 1) - 1
        
        for i in range(frames):
            t = float(i) / sample_rate
            # Melodía ascendente
            frecuencia = 200 + 300 * t
            tono = np.sin(2 * np.pi * frecuencia * t) * 0.5
            armonico = np.sin(2 * np.pi * frecuencia * 2 * t) * 0.2
            envelope = 1 - abs(t * 2.5 - 1)  # Envelope triangular
            sample = (tono + armonico) * envelope
            val = int(max_sample * 0.6 * sample)
            arr[i][0] = val
            arr[i][1] = val
        
        return pygame.sndarray.make_sound(arr)
    
    def _generar_victoria(self) -> pygame.mixer.Sound:
        """Genera sonido de victoria."""
        # Fanfarria ascendente
        duracion = 1.0
        sample_rate = 22050
        frames = int(duracion * sample_rate)
        arr = np.zeros((frames, 2), dtype=np.int16)
        max_sample = 2**(16 - 1) - 1
        
        notas = [261.63, 329.63, 392.00, 523.25]  # C, E, G, C (acorde mayor)
        
        for i in range(frames):
            t = float(i) / sample_rate
            sample = 0
            # Reproducir cada nota en secuencia
            nota_index = int(t * 2)  # 2 notas por segundo
            if nota_index < len(notas):
                frecuencia = notas[nota_index]
                tono = np.sin(2 * np.pi * frecuencia * (t % 0.5)) * 0.4
                envelope = np.exp(-((t % 0.5) * 4))
                sample += tono * envelope
            
            val = int(max_sample * 0.7 * sample)
            arr[i][0] = val
            arr[i][1] = val
        
        return pygame.sndarray.make_sound(arr)
    
    def _generar_derrota(self) -> pygame.mixer.Sound:
        """Genera sonido de derrota."""
        # Sonido descendente y triste
        duracion = 0.8
        sample_rate = 22050
        frames = int(duracion * sample_rate)
        arr = np.zeros((frames, 2), dtype=np.int16)
        max_sample = 2**(16 - 1) - 1
        
        for i in range(frames):
            t = float(i) / sample_rate
            # Tono descendente
            frecuencia = 300 * (1 - t * 0.5)
            tono = np.sin(2 * np.pi * frecuencia * t) * 0.5
            envelope = np.exp(-t * 2)
            sample = tono * envelope
            val = int(max_sample * 0.6 * sample)
            arr[i][0] = val
            arr[i][1] = val
        
        return pygame.sndarray.make_sound(arr)
    
    def _generar_musica_ambiente(self) -> pygame.mixer.Sound:
        """Genera música ambiente de fondo."""
        # Música ambiente repetitiva y atmosférica
        duracion = 4.0  # Loop de 4 segundos
        sample_rate = 22050
        frames = int(duracion * sample_rate)
        arr = np.zeros((frames, 2), dtype=np.int16)
        max_sample = 2**(16 - 1) - 1
        
        # Frecuencias bajas para ambiente
        frecuencia_base = 65.41  # C2
        
        for i in range(frames):
            t = float(i) / sample_rate
            # Base suave y repetitiva
            tono1 = np.sin(2 * np.pi * frecuencia_base * t) * 0.1
            tono2 = np.sin(2 * np.pi * frecuencia_base * 2 * t) * 0.08
            tono3 = np.sin(2 * np.pi * frecuencia_base * 3 * t) * 0.05
            # Modulación lenta
            modulacion = np.sin(2 * np.pi * 0.5 * t) * 0.5 + 0.5
            sample = (tono1 + tono2 + tono3) * modulacion
            val = int(max_sample * 0.3 * sample)
            arr[i][0] = val
            arr[i][1] = val
        
        return pygame.sndarray.make_sound(arr)
    
    def reproducir(self, tipo: TipoSonido, volumen: Optional[float] = None):
        """
        Reproduce un efecto de sonido.
        
        Args:
            tipo: Tipo de sonido a reproducir.
            volumen: Volumen (0.0 a 1.0). Si es None, usa el volumen por defecto.
        """
        if tipo.value not in self.sonidos_cache:
            return
        
        sonido = self.sonidos_cache[tipo.value]
        vol = volumen if volumen is not None else self.volumen_efectos
        sonido.set_volume(vol)
        sonido.play()
    
    def reproducir_musica(self, loop: bool = True, volumen: Optional[float] = None):
        """
        Reproduce la música de fondo.
        
        Args:
            loop: Si True, la música se repite indefinidamente.
            volumen: Volumen (0.0 a 1.0). Si es None, usa el volumen por defecto.
        """
        if TipoSonido.MUSICA_AMBIENTE.value not in self.sonidos_cache:
            return
        
        if self.musica_reproduciendo:
            self.detener_musica()
        
        self.musica_actual = self.sonidos_cache[TipoSonido.MUSICA_AMBIENTE.value]
        vol = volumen if volumen is not None else self.volumen_musica
        self.musica_actual.set_volume(vol)
        
        if loop:
            # Repetir infinitamente
            self.musica_actual.play(loops=-1)
        else:
            self.musica_actual.play()
        
        self.musica_reproduciendo = True
    
    def detener_musica(self):
        """Detiene la reproducción de música."""
        if self.musica_actual and self.musica_reproduciendo:
            self.musica_actual.stop()
            self.musica_reproduciendo = False
    
    def pausar_musica(self):
        """Pausa la música de fondo."""
        if self.musica_actual and self.musica_reproduciendo:
            pygame.mixer.pause()
    
    def reanudar_musica(self):
        """Reanuda la música de fondo."""
        if self.musica_reproduciendo:
            pygame.mixer.unpause()
    
    def establecer_volumen_efectos(self, volumen: float):
        """
        Establece el volumen de los efectos de sonido.
        
        Args:
            volumen: Volumen (0.0 a 1.0).
        """
        self.volumen_efectos = max(0.0, min(1.0, volumen))
    
    def establecer_volumen_musica(self, volumen: float):
        """
        Establece el volumen de la música.
        
        Args:
            volumen: Volumen (0.0 a 1.0).
        """
        self.volumen_musica = max(0.0, min(1.0, volumen))
        if self.musica_actual:
            self.musica_actual.set_volume(self.volumen_musica)

