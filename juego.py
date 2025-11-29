
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
    """
    Clase principal que controla el flujo del juego.
    
    Esta clase gestiona:
    - La inicialización de pygame y la ventana
    - El bucle principal del juego
    - La navegación entre diferentes pantallas
    - El manejo de eventos y actualización del estado
    """
    
    def __init__(self):
        """
        Inicializa pygame y los componentes del juego.
        
        Configura la ventana (pantalla completa o ventana normal),
        inicializa el reloj de pygame y establece el estado inicial
        del juego en el menú principal.
        """
        # Inicializar pygame
        pygame.init()
        pygame.display.set_caption(Config.TITULO)
        
        # Configurar ventana (pantalla completa o ventana)
        if Config.PANTALLA_COMPLETA:
            # Modo pantalla completa: usar toda la pantalla disponible
            self.ventana = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            # Obtener dimensiones reales de la pantalla
            self.ancho_pantalla, self.alto_pantalla = self.ventana.get_size()
        else:
            # Modo ventana: usar dimensiones predefinidas
            self.ventana = pygame.display.set_mode(
                (Config.ANCHO_VENTANA, Config.ALTO_VENTANA)
            )
            self.ancho_pantalla = Config.ANCHO_VENTANA
            self.alto_pantalla = Config.ALTO_VENTANA
        
        # Reloj para controlar FPS
        self.reloj = pygame.time.Clock()
        # Flag para controlar si el juego sigue corriendo
        self.corriendo = True
        
        # Pantalla actual que se está mostrando
        self.pantalla_actual = None
        # Nombre del jugador (se actualiza cuando inicia una partida)
        self.nombre_jugador = "Jugador"
        
        # Iniciar en el menú principal
        self._ir_a_menu()
    
    def _alternar_pantalla_completa(self):
        """
        Alterna entre pantalla completa y ventana.
        
        Cambia el modo de visualización y recrea la pantalla actual
        con las nuevas dimensiones para mantener la consistencia visual.
        """
        # Cambiar el estado de pantalla completa
        Config.PANTALLA_COMPLETA = not Config.PANTALLA_COMPLETA
        
        # Aplicar el nuevo modo de visualización
        if Config.PANTALLA_COMPLETA:
            # Cambiar a pantalla completa
            self.ventana = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            # Cambiar a ventana con dimensiones predefinidas
            self.ventana = pygame.display.set_mode(
                (Config.ANCHO_VENTANA, Config.ALTO_VENTANA)
            )
        
        # Actualizar dimensiones
        self.ancho_pantalla, self.alto_pantalla = self.ventana.get_size()
        
        # Recrear la pantalla actual con las nuevas dimensiones
        # para que se ajuste correctamente al nuevo tamaño
        if isinstance(self.pantalla_actual, MenuPrincipal):
            self._ir_a_menu()
        elif isinstance(self.pantalla_actual, PantallaJuego):
            # Obtener datos del juego actual para recrearlo
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
        """
        Navega al menú principal.
        
        Crea una nueva instancia de MenuPrincipal y la establece
        como la pantalla actual del juego.
        """
        self.pantalla_actual = MenuPrincipal(self.ancho_pantalla, self.alto_pantalla)
        self.pantalla_actual.inicializar_fuentes()
    
    def _ir_a_juego(self, modo: str, nombre: str):
        """
        Navega a la pantalla de juego.
        
        Args:
            modo: Modo de juego a iniciar ("escapa" o "cazador").
            nombre: Nombre del jugador para la partida.
        """
        # Guardar el nombre del jugador
        self.nombre_jugador = nombre
        # Crear nueva pantalla de juego
        self.pantalla_actual = PantallaJuego(
            self.ancho_pantalla, self.alto_pantalla, 
            modo, nombre
        )
        self.pantalla_actual.inicializar_fuentes()
    
    def _ir_a_puntajes(self):
        """
        Navega a la pantalla de puntajes.
        
        Muestra la tabla de clasificación con los mejores puntajes
        de ambos modos de juego.
        """
        self.pantalla_actual = PantallaPuntajes(self.ancho_pantalla, self.alto_pantalla)
        self.pantalla_actual.inicializar_fuentes()
    
    def _ir_a_informacion(self):
        """
        Navega a la pantalla de información.
        
        Muestra información general del juego, controles y mecánicas.
        """
        self.pantalla_actual = PantallaInformacion(self.ancho_pantalla, self.alto_pantalla)
        self.pantalla_actual.inicializar_fuentes()
    
    def _ir_a_detalles_modos(self):
        """
        Navega a la pantalla de detalles de modos.
        
        Muestra información detallada sobre los modos de juego
        "Escapa" y "Cazador".
        """
        self.pantalla_actual = PantallaDetallesModos(self.ancho_pantalla, self.alto_pantalla)
        self.pantalla_actual.inicializar_fuentes()
    
    def _manejar_navegacion(self):
        """
        Maneja la navegación entre pantallas.
        
        Verifica si la pantalla actual ha solicitado un cambio de pantalla
        y ejecuta la transición correspondiente. Las pantallas indican su
        destino mediante el atributo `siguiente_pantalla`.
        """
        # Verificar si hay una solicitud de cambio de pantalla
        if self.pantalla_actual.siguiente_pantalla:
            destino = self.pantalla_actual.siguiente_pantalla
            # Obtener datos adicionales si los hay (ej: modo de juego, nombre)
            datos = self.pantalla_actual.datos_retorno
            
            # Ejecutar la transición según el destino
            if destino == "salir":
                # Salir del juego
                self.corriendo = False
            elif destino == "menu":
                # Ir al menú principal
                self._ir_a_menu()
            elif destino == "juego":
                # Iniciar nueva partida
                self._ir_a_juego(datos.get("modo", "escapa"), datos.get("nombre", "Jugador"))
            elif destino == "juego_nuevo":
                # Reiniciar partida con el mismo modo
                self._ir_a_juego(datos.get("modo", "escapa"), self.nombre_jugador)
            elif destino == "puntajes":
                # Ir a la pantalla de puntajes
                self._ir_a_puntajes()
            elif destino == "informacion":
                # Ir a la pantalla de información
                self._ir_a_informacion()
            elif destino == "detalles_modos":
                # Ir a la pantalla de detalles de modos
                self._ir_a_detalles_modos()
    
    def ejecutar(self):
        """
        Bucle principal del juego.
        
        Este método contiene el ciclo principal del juego que se ejecuta
        continuamente hasta que el usuario cierra el juego. En cada iteración:
        1. Calcula el tiempo transcurrido (delta time)
        2. Procesa eventos de entrada (teclado, mouse, etc.)
        3. Actualiza el estado del juego
        4. Maneja la navegación entre pantallas
        5. Dibuja el contenido en la pantalla
        """
        while self.corriendo:
            # Calcular delta time en segundos (tiempo transcurrido desde el último frame)
            # tick() limita el FPS y devuelve milisegundos, convertimos a segundos
            dt = self.reloj.tick(Config.FPS) / 1000.0
            
            # Manejar eventos de pygame
            for evento in pygame.event.get():
                # Evento de cierre de ventana
                if evento.type == pygame.QUIT:
                    self.corriendo = False
                elif evento.type == pygame.KEYDOWN:
                    # F11 para alternar entre pantalla completa y ventana
                    if evento.key == pygame.K_F11:
                        self._alternar_pantalla_completa()
                    else:
                        # Pasar otros eventos a la pantalla actual
                        self.pantalla_actual.manejar_evento(evento)
                else:
                    # Pasar todos los demás eventos a la pantalla actual
                    self.pantalla_actual.manejar_evento(evento)
            
            # Actualizar el estado del juego (lógica, animaciones, etc.)
            self.pantalla_actual.actualizar(dt)
            
            # Verificar si hay solicitud de cambio de pantalla
            self._manejar_navegacion()
            
            # Dibujar el contenido de la pantalla actual
            self.pantalla_actual.dibujar(self.ventana)
            # Actualizar la pantalla (mostrar el frame dibujado)
            pygame.display.flip()
        
        # Limpiar recursos de pygame y salir
        pygame.quit()
        sys.exit()


def main():
    """
    Función principal del programa.
    
    Punto de entrada del juego. Inicializa el juego, muestra información
    de inicio y maneja errores durante la ejecución.
    """
    # Mostrar información de inicio en la consola
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
        # Crear e iniciar el juego
        juego = JuegoLaberinto()
        juego.ejecutar()
    except Exception as e:
        # Manejar errores y mostrar información de depuración
        print(f"\n[ERROR] Error al ejecutar el juego: {e}")
        # Mostrar el traceback completo para depuración
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

