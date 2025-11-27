"""
Interfaz mínima de texto para probar los modos de juego.
"""

import sys
import time
from modos import GameModeEscapa, GameModeCazador
from logica import Dificultad
from sistema import ScoreBoard


def mostrar_menu_principal():
    """Muestra el menú principal y obtiene la selección del usuario."""
    print("\n" + "=" * 60)
    print("   ESCAPA DEL LABERINTO - Modos de Juego")
    print("=" * 60)
    print("\n1. Modo Escapa")
    print("2. Modo Cazador")
    print("3. Ver Top 5 Puntajes")
    print("4. Salir")
    print("\n" + "-" * 60)
    
    opcion = input("Selecciona una opción (1-4): ").strip()
    return opcion


def seleccionar_dificultad():
    """Permite al usuario seleccionar la dificultad."""
    print("\n" + "-" * 60)
    print("Dificultades disponibles:")
    print("1. Fácil")
    print("2. Normal")
    print("3. Difícil")
    print("-" * 60)
    
    opcion = input("Selecciona dificultad (1-3, por defecto Normal): ").strip()
    
    if opcion == "1":
        return Dificultad.FACIL
    elif opcion == "3":
        return Dificultad.DIFICIL
    else:
        return Dificultad.NORMAL


def obtener_nombre_jugador():
    """Obtiene el nombre del jugador."""
    nombre = input("\nIngresa tu nombre (por defecto 'Jugador'): ").strip()
    return nombre if nombre else "Jugador"


def simular_modo_escapa():
    """Simula una partida del modo Escapa."""
    print("\n" + "=" * 60)
    print("   MODO ESCAPA")
    print("=" * 60)
    print("\nObjetivo: Llega a la salida antes de que los enemigos te alcancen.")
    print("Puedes colocar trampas (máximo 3, cooldown 5 segundos) para eliminar enemigos.")
    print("\nControles simulados:")
    print("  - w/a/s/d: Mover (arriba/izquierda/abajo/derecha)")
    print("  - t: Colocar trampa")
    print("  - q: Terminar partida")
    print("\n" + "-" * 60)
    
    nombre = obtener_nombre_jugador()
    dificultad = seleccionar_dificultad()
    
    # Crear modo de juego
    modo = GameModeEscapa(
        nombre_jugador=nombre,
        dificultad=dificultad,
        ancho_mapa=12,
        alto_mapa=12
    )
    
    print(f"\n¡Partida iniciada! Dificultad: {dificultad.value}")
    print(f"Mapa: {modo.mapa.ancho}x{modo.mapa.alto}")
    print(f"Enemigos: {len(modo.enemigos)}")
    print(f"Posición inicial: {modo.jugador.obtener_posicion()}")
    print(f"Salida: {modo.mapa.obtener_posicion_salida()}")
    
    # Simular partida
    ultima_actualizacion = time.time()
    
    while not modo.juego_terminado:
        tiempo_actual = time.time()
        delta_tiempo = tiempo_actual - ultima_actualizacion
        ultima_actualizacion = tiempo_actual
        
        # Actualizar juego
        modo.actualizar(delta_tiempo)
        
        # Mostrar estado cada segundo aproximadamente
        if int(modo.tiempo_juego) != int(modo.tiempo_juego - delta_tiempo):
            estado = modo.obtener_estado()
            print(f"\n[Tiempo: {estado['tiempo_juego']:.1f}s] "
                  f"Puntos: {estado['puntos']} | "
                  f"Energía: {estado['energia_jugador']}/{estado['energia_maxima']} | "
                  f"Trampas: {estado['trampas_activas']}/3 | "
                  f"Enemigos eliminados: {estado['enemigos_eliminados']}")
        
        # Simular entrada del usuario (simplificado)
        # En una implementación real, esto sería un bucle de eventos
        time.sleep(0.1)  # Pequeña pausa para no saturar
        
        # Simular algunos movimientos automáticos hacia la salida
        if modo.movimientos < 50:  # Limitar movimientos para la demo
            salida = modo.mapa.obtener_posicion_salida()
            jugador_pos = modo.jugador.obtener_posicion()
            
            # Movimiento simple hacia la salida
            if jugador_pos[0] < salida[0]:
                modo.mover_jugador("abajo", corriendo=False)
            elif jugador_pos[0] > salida[0]:
                modo.mover_jugador("arriba", corriendo=False)
            elif jugador_pos[1] < salida[1]:
                modo.mover_jugador("derecha", corriendo=False)
            elif jugador_pos[1] > salida[1]:
                modo.mover_jugador("izquierda", corriendo=False)
        
        # Verificar si llegó a la salida
        if modo.jugador.ha_llegado_a_salida(modo.mapa):
            break
    
    # Mostrar resultado final
    estado_final = modo.obtener_estado()
    print("\n" + "=" * 60)
    if estado_final["victoria"]:
        print("¡VICTORIA! Has llegado a la salida.")
    else:
        print("DERROTA. Un enemigo te alcanzó.")
    
    print(f"\nPuntos finales: {estado_final['puntos']}")
    print(f"Tiempo: {estado_final['tiempo_juego']:.2f} segundos")
    print(f"Movimientos: {estado_final['movimientos']}")
    print(f"Enemigos eliminados: {estado_final['enemigos_eliminados']}")
    print("=" * 60)


def simular_modo_cazador():
    """Simula una partida del modo Cazador."""
    print("\n" + "=" * 60)
    print("   MODO CAZADOR")
    print("=" * 60)
    print("\nObjetivo: Atrapa a los enemigos antes de que escapen por la salida.")
    print("Gana puntos por cada captura, pierde puntos si un enemigo escapa.")
    print("\nControles simulados:")
    print("  - w/a/s/d: Mover (arriba/izquierda/abajo/derecha)")
    print("  - q: Terminar partida")
    print("\n" + "-" * 60)
    
    nombre = obtener_nombre_jugador()
    dificultad = seleccionar_dificultad()
    
    # Crear modo de juego
    modo = GameModeCazador(
        nombre_jugador=nombre,
        dificultad=dificultad,
        tiempo_limite=60.0,  # 1 minuto para la demo
        ancho_mapa=12,
        alto_mapa=12
    )
    
    print(f"\n¡Partida iniciada! Dificultad: {dificultad.value}")
    print(f"Mapa: {modo.mapa.ancho}x{modo.mapa.alto}")
    print(f"Enemigos: {len(modo.enemigos)}")
    print(f"Tiempo límite: {modo.tiempo_limite} segundos")
    print(f"Puntos iniciales: {modo.puntos}")
    
    # Simular partida
    ultima_actualizacion = time.time()
    
    while not modo.juego_terminado:
        tiempo_actual = time.time()
        delta_tiempo = tiempo_actual - ultima_actualizacion
        ultima_actualizacion = tiempo_actual
        
        # Actualizar juego
        modo.actualizar(delta_tiempo)
        
        # Mostrar estado cada segundo aproximadamente
        if int(modo.tiempo_juego) != int(modo.tiempo_juego - delta_tiempo):
            estado = modo.obtener_estado()
            print(f"\n[Tiempo: {estado['tiempo_restante']:.1f}s restantes] "
                  f"Puntos: {estado['puntos']} | "
                  f"Energía: {estado['energia_jugador']}/{estado['energia_maxima']} | "
                  f"Capturados: {estado['enemigos_capturados']} | "
                  f"Escapados: {estado['enemigos_escapados']}")
        
        # Simular entrada del usuario (simplificado)
        time.sleep(0.1)
        
        # Simular algunos movimientos automáticos
        if modo.movimientos < 30:  # Limitar movimientos para la demo
            # Movimiento aleatorio simple
            import random
            direcciones = ["arriba", "abajo", "izquierda", "derecha"]
            if random.random() < 0.3:  # 30% de probabilidad de moverse
                direccion = random.choice(direcciones)
                modo.mover_jugador(direccion, corriendo=False)
    
    # Mostrar resultado final
    estado_final = modo.obtener_estado()
    print("\n" + "=" * 60)
    print("¡Partida terminada!")
    print(f"\nPuntos finales: {estado_final['puntos']}")
    print(f"Tiempo: {estado_final['tiempo_juego']:.2f} segundos")
    print(f"Movimientos: {estado_final['movimientos']}")
    print(f"Enemigos capturados: {estado_final['enemigos_capturados']}")
    print(f"Enemigos escapados: {estado_final['enemigos_escapados']}")
    print("=" * 60)


def mostrar_top5_puntajes():
    """Muestra el top 5 de puntajes para ambos modos."""
    print("\n" + "=" * 60)
    print("   TOP 5 PUNTAJES")
    print("=" * 60)
    
    scoreboard = ScoreBoard()
    
    print("\n--- MODO ESCAPA ---")
    top5_escapa = scoreboard.obtener_top5("escapa")
    if top5_escapa:
        for i, puntaje in enumerate(top5_escapa, 1):
            fecha_str = puntaje.obtener_fecha_formateada()
            print(f"  {i}. {puntaje.nombre_jugador}: {puntaje.puntos} puntos ({fecha_str})")
    else:
        print("  No hay puntajes registrados aún.")
    
    print("\n--- MODO CAZADOR ---")
    top5_cazador = scoreboard.obtener_top5("cazador")
    if top5_cazador:
        for i, puntaje in enumerate(top5_cazador, 1):
            fecha_str = puntaje.obtener_fecha_formateada()
            print(f"  {i}. {puntaje.nombre_jugador}: {puntaje.puntos} puntos ({fecha_str})")
    else:
        print("  No hay puntajes registrados aún.")
    
    print("\n" + "=" * 60)
    input("\nPresiona Enter para continuar...")


def main():
    """Función principal."""
    print("\n" + "=" * 60)
    print("   ESCAPA DEL LABERINTO - Interfaz de Texto")
    print("=" * 60)
    print("\nEsta es una interfaz mínima para probar los modos de juego.")
    print("En una implementación completa, esto sería una GUI interactiva.")
    
    while True:
        opcion = mostrar_menu_principal()
        
        if opcion == "1":
            simular_modo_escapa()
        elif opcion == "2":
            simular_modo_cazador()
        elif opcion == "3":
            mostrar_top5_puntajes()
        elif opcion == "4":
            print("\n¡Hasta luego!")
            break
        else:
            print("\nOpción inválida. Por favor selecciona 1-4.")
        
        input("\nPresiona Enter para continuar...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrumpido por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

