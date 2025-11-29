
"""
Escapa del Laberinto - Juego con Interfaz Gráfica
=================================================

Un emocionante juego de laberinto donde debes escapar antes de que
se acabe el tiempo. ¡Cuidado con tu energía al correr!

Ejecuta este archivo para iniciar el juego con GUI:
    python juego.py

Controles:
    - Flechas / WASD: Mover
    - SHIFT: Correr (consume energía)
    - ESC: Pausar / Menú
"""

import pygame
import sys
import os
import traceback
# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.config import Config, Colores
from gui.pantallas import MenuPrincipal, PantallaJuego, PantallaPuntajes, PantallaInformacion, PantallaDetallesModos


class JuegoLaberinto:
    """Clase principal que controla el flujo del juego."""
    
    def __init__(self):
        """Inicializa pygame y los componentes del juego."""
        pygame.init()
        pygame.display.set_caption(Config.TITULO)
        
        # Configurar ventana (pantalla completa o ventana)
        if Config.PANTALLA_COMPLETA:
            self.ventana = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            # Obtener dimensiones reales de la pantalla
            self.ancho_pantalla, self.alto_pantalla = self.ventana.get_size()
        else:
            self.ventana = pygame.display.set_mode(
                (Config.ANCHO_VENTANA, Config.ALTO_VENTANA)
            )
            self.ancho_pantalla = Config.ANCHO_VENTANA
            self.alto_pantalla = Config.ALTO_VENTANA
        
        self.reloj = pygame.time.Clock()
        self.corriendo = True
        
        # Pantalla actual
        self.pantalla_actual = None
        self.nombre_jugador = "Jugador"
        
        # Iniciar en el menú
        self._ir_a_menu()
    
    def _alternar_pantalla_completa(self):
        """Alterna entre pantalla completa y ventana."""
        Config.PANTALLA_COMPLETA = not Config.PANTALLA_COMPLETA
        
        if Config.PANTALLA_COMPLETA:
            self.ventana = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.ventana = pygame.display.set_mode(
                (Config.ANCHO_VENTANA, Config.ALTO_VENTANA)
            )
        
        self.ancho_pantalla, self.alto_pantalla = self.ventana.get_size()
        
        # Recrear la pantalla actual con las nuevas dimensiones
        if isinstance(self.pantalla_actual, MenuPrincipal):
            self._ir_a_menu()
        elif isinstance(self.pantalla_actual, PantallaJuego):
            modo = getattr(self.pantalla_actual, 'modo', 'escapa')
            nombre = getattr(self.pantalla_actual, 'nombre_jugador', 'Jugador')
            self._ir_a_juego(modo, nombre)
        elif isinstance(self.pantalla_actual, PantallaPuntajes):
            self._ir_a_puntajes()
        elif isinstance(self.pantalla_actual, PantallaInformacion):
            self._ir_a_informacion()
        elif isinstance(self.pantalla_actual, PantallaDetallesModos):
            self._ir_a_detalles_modos()
    
    def _alternar_pantalla_completa(self):
        """Alterna entre pantalla completa y ventana."""
        Config.PANTALLA_COMPLETA = not Config.PANTALLA_COMPLETA
        
        if Config.PANTALLA_COMPLETA:
            self.ventana = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.ventana = pygame.display.set_mode(
                (Config.ANCHO_VENTANA, Config.ALTO_VENTANA)
            )
        
        self.ancho_pantalla, self.alto_pantalla = self.ventana.get_size()
        
        # Recrear la pantalla actual con las nuevas dimensiones
        if isinstance(self.pantalla_actual, MenuPrincipal):
            self._ir_a_menu()
        elif isinstance(self.pantalla_actual, PantallaJuego):
            datos = self.pantalla_actual.datos_retorno if hasattr(self.pantalla_actual, 'datos_retorno') else {}
            self.pantalla_actual = PantallaJuego(
                self.ancho_pantalla, self.alto_pantalla,
                datos.get("modo", "escapa"),
                datos.get("nombre_jugador", "Jugador")
            )
        elif isinstance(self.pantalla_actual, PantallaPuntajes):
            self.pantalla_actual = PantallaPuntajes(
                self.ancho_pantalla, self.alto_pantalla
            )
    
    def _ir_a_menu(self):
        """Navega al menú principal."""
        self.pantalla_actual = MenuPrincipal(self.ancho_pantalla, self.alto_pantalla)
        self.pantalla_actual.inicializar_fuentes()
    
    def _ir_a_juego(self, modo: str, nombre: str):
        """Navega a la pantalla de juego."""
        self.nombre_jugador = nombre
        self.pantalla_actual = PantallaJuego(
            self.ancho_pantalla, self.alto_pantalla, 
            modo, nombre
        )
        self.pantalla_actual.inicializar_fuentes()
    
    def _ir_a_puntajes(self):
        """Navega a la pantalla de puntajes."""
        self.pantalla_actual = PantallaPuntajes(self.ancho_pantalla, self.alto_pantalla)
        self.pantalla_actual.inicializar_fuentes()
    
    def _ir_a_informacion(self):
        """Navega a la pantalla de información."""
        self.pantalla_actual = PantallaInformacion(self.ancho_pantalla, self.alto_pantalla)
        self.pantalla_actual.inicializar_fuentes()
    
    def _ir_a_detalles_modos(self):
        """Navega a la pantalla de detalles de modos."""
        self.pantalla_actual = PantallaDetallesModos(self.ancho_pantalla, self.alto_pantalla)
        self.pantalla_actual.inicializar_fuentes()
    
    def _manejar_navegacion(self):
        """Maneja la navegación entre pantallas."""
        if self.pantalla_actual.siguiente_pantalla:
            destino = self.pantalla_actual.siguiente_pantalla
            datos = self.pantalla_actual.datos_retorno
            
            if destino == "salir":
                self.corriendo = False
            elif destino == "menu":
                self._ir_a_menu()
            elif destino == "juego":
                self._ir_a_juego(datos.get("modo", "escapa"), datos.get("nombre", "Jugador"))
            elif destino == "juego_nuevo":
                # Reiniciar con el mismo modo
                self._ir_a_juego(datos.get("modo", "escapa"), self.nombre_jugador)
            elif destino == "puntajes":
                self._ir_a_puntajes()
            elif destino == "informacion":
                self._ir_a_informacion()
            elif destino == "detalles_modos":
                self._ir_a_detalles_modos()
    
    def ejecutar(self):
        """Bucle principal del juego."""
        while self.corriendo:
            # Delta time en segundos
            dt = self.reloj.tick(Config.FPS) / 1000.0
            
            # Manejar eventos
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.corriendo = False
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_F11:
                        # F11 para alternar pantalla completa
                        self._alternar_pantalla_completa()
                    else:
                        self.pantalla_actual.manejar_evento(evento)
                else:
                    self.pantalla_actual.manejar_evento(evento)
            
            # Actualizar
            self.pantalla_actual.actualizar(dt)
            
            # Verificar navegación
            self._manejar_navegacion()
            
            # Dibujar
            self.pantalla_actual.dibujar(self.ventana)
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()


def main():
    """Función principal."""
    print("\n" + "=" * 60)
    print("   ESCAPA DEL LABERINTO - Edicion Grafica")
    print("=" * 60)
    print("\nIniciando el juego...\n")
    print("Controles:")
    print("  - Flechas / WASD: Mover al jugador")
    print("  - SHIFT + Direccion: Correr (gasta energia)")
    print("  - ESC: Pausar / Volver al menu")
    print("\n" + "=" * 60 + "\n")
    
    try:
        juego = JuegoLaberinto()
        juego.ejecutar()
    except Exception as e:
        print(f"\n[ERROR] Error al ejecutar el juego: {e}")
        
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

