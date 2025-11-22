"""
Archivo principal con ejemplos de uso del núcleo lógico del juego.
"""

from modelo import Tile, Camino, Muro, Liana, Tunel, Mapa, Jugador
from core import GeneradorMapa
from sistema import JugadorInfo, registrar_jugador, Puntaje, ScoreBoard, ModoJuego


def ejemplo_clases_terreno():
    """Ejemplo de uso de las clases de terreno."""
    print("=" * 60)
    print("EJEMPLO 1: Clases de Terreno")
    print("=" * 60)
    
    camino = Camino()
    muro = Muro()
    liana = Liana()
    tunel = Tunel()
    
    print(f"Camino - Jugador: {camino.permite_paso_jugador()}, Enemigo: {camino.permite_paso_enemigo()}")
    print(f"Muro - Jugador: {muro.permite_paso_jugador()}, Enemigo: {muro.permite_paso_enemigo()}")
    print(f"Liana - Jugador: {liana.permite_paso_jugador()}, Enemigo: {liana.permite_paso_enemigo()}")
    print(f"Tunel - Jugador: {tunel.permite_paso_jugador()}, Enemigo: {tunel.permite_paso_enemigo()}")
    print()


def ejemplo_generacion_mapa():
    """Ejemplo de generación de mapa."""
    print("=" * 60)
    print("EJEMPLO 2: Generación de Mapa")
    print("=" * 60)
    
    generador = GeneradorMapa(ancho=10, alto=10)
    mapa = generador.generar_mapa()
    
    print(f"Mapa generado: {mapa}")
    print(f"Tamaño: {mapa.ancho}x{mapa.alto}")
    print(f"Posición inicio: {mapa.obtener_posicion_inicio_jugador()}")
    print(f"Posición salida: {mapa.obtener_posicion_salida()}")
    
    # Verificar que existe camino válido (usando método interno del generador)
    generador_verif = GeneradorMapa(ancho=mapa.ancho, alto=mapa.alto)
    existe_camino = generador_verif._existe_camino_valido(
        mapa.casillas,
        mapa.obtener_posicion_inicio_jugador(),
        mapa.obtener_posicion_salida()
    )
    print(f"¿Existe camino valido? {existe_camino}")
    print()


def ejemplo_movimiento_jugador():
    """Ejemplo de movimiento del jugador."""
    print("=" * 60)
    print("EJEMPLO 3: Movimiento del Jugador")
    print("=" * 60)
    
    # Crear un mapa simple
    casillas = [[Camino() if (i + j) % 2 == 0 else Muro() for j in range(5)] for i in range(5)]
    # Asegurar que inicio y salida sean camino
    casillas[0][0] = Camino()
    casillas[4][4] = Camino()
    
    mapa = Mapa(5, 5, casillas, (0, 0), (4, 4))
    
    # Crear jugador
    jugador = Jugador(0, 0, energia_maxima=100)
    print(f"Jugador inicial: {jugador}")
    print(f"Posición: {jugador.obtener_posicion()}")
    print(f"Energía: {jugador.obtener_energia_actual()}/{jugador.obtener_energia_maxima()}")
    
    # Intentar movimientos
    print("\nIntentando mover a la derecha (caminando)...")
    if jugador.mover_derecha(mapa, corriendo=False):
        print(f"[OK] Movimiento exitoso. Nueva posicion: {jugador.obtener_posicion()}")
        print(f"  Energia restante: {jugador.obtener_energia_actual()}")
    else:
        print("[X] Movimiento fallido")
    
    print("\nIntentando mover hacia abajo (corriendo)...")
    if jugador.mover_abajo(mapa, corriendo=True):
        print(f"[OK] Movimiento exitoso. Nueva posicion: {jugador.obtener_posicion()}")
        print(f"  Energia restante: {jugador.obtener_energia_actual()}")
    else:
        print("[X] Movimiento fallido")
    
    print("\nIntentando mover hacia un muro...")
    if jugador.mover_derecha(mapa, corriendo=False):
        print(f"[OK] Movimiento exitoso")
    else:
        print("[X] Movimiento fallido (esperado, hay un muro)")
    
    print(f"\nEstado final del jugador: {jugador}")
    print(f"Porcentaje de energía: {jugador.obtener_porcentaje_energia() * 100:.1f}%")
    print()


def ejemplo_sistema_energia():
    """Ejemplo del sistema de energía."""
    print("=" * 60)
    print("EJEMPLO 4: Sistema de Energía")
    print("=" * 60)
    
    jugador = Jugador(0, 0, energia_maxima=100)
    print(f"Energía inicial: {jugador.obtener_energia_actual()}/{jugador.obtener_energia_maxima()}")
    
    # Consumir energía corriendo
    print("\nConsumiendo energía corriendo (3 puntos)...")
    jugador.consumir_energia(3)
    print(f"Energía después de correr: {jugador.obtener_energia_actual()}")
    
    # Verificar si puede correr
    print(f"\n¿Puede correr? {jugador.puede_correr()}")
    
    # Recuperar energía
    print("\nRecuperando 10 puntos de energía...")
    jugador.recuperar_energia(10)
    print(f"Energía después de recuperar: {jugador.obtener_energia_actual()}")
    
    # Actualizar energía con tiempo
    print("\nActualizando energía (simulando 5 segundos con tasa 0.5)...")
    jugador.actualizar_energia(5.0, tasa_recuperacion=0.5)
    print(f"Energía después de actualizar: {jugador.obtener_energia_actual()}")
    
    print(f"\nPorcentaje de energía: {jugador.obtener_porcentaje_energia() * 100:.1f}%")
    print()


def ejemplo_registro_jugador():
    """Ejemplo de registro de jugador."""
    print("=" * 60)
    print("EJEMPLO 5: Registro de Jugador")
    print("=" * 60)
    
    jugador_info = registrar_jugador("Juan")
    print(f"Jugador registrado: {jugador_info}")
    print(f"Nombre: {jugador_info.nombre}")
    print(f"Fecha de registro: {jugador_info.fecha_registro}")
    print()


def ejemplo_sistema_puntajes():
    """Ejemplo del sistema de puntajes."""
    print("=" * 60)
    print("EJEMPLO 6: Sistema de Puntajes")
    print("=" * 60)
    
    scoreboard = ScoreBoard()
    
    # Registrar algunos puntajes
    print("Registrando puntajes...")
    scoreboard.registrar_puntaje("escapa", "Juan", 1500)
    scoreboard.registrar_puntaje("escapa", "María", 2000)
    scoreboard.registrar_puntaje("escapa", "Pedro", 1200)
    scoreboard.registrar_puntaje("escapa", "Ana", 1800)
    scoreboard.registrar_puntaje("escapa", "Luis", 2500)
    scoreboard.registrar_puntaje("escapa", "Sofía", 1000)
    
    scoreboard.registrar_puntaje("cazador", "Juan", 3000)
    scoreboard.registrar_puntaje("cazador", "María", 3500)
    scoreboard.registrar_puntaje("cazador", "Pedro", 2800)
    
    # Obtener top 5
    print("\nTop 5 - Modo Escapa:")
    top5_escapa = scoreboard.obtener_top5("escapa")
    for i, puntaje in enumerate(top5_escapa, 1):
        print(f"  {i}. {puntaje.nombre_jugador}: {puntaje.puntos} puntos")
    
    print("\nTop 5 - Modo Cazador:")
    top5_cazador = scoreboard.obtener_top5("cazador")
    for i, puntaje in enumerate(top5_cazador, 1):
        print(f"  {i}. {puntaje.nombre_jugador}: {puntaje.puntos} puntos")
    print()


def ejemplo_completo():
    """Ejemplo completo integrando varios componentes."""
    print("=" * 60)
    print("EJEMPLO 7: Ejemplo Completo")
    print("=" * 60)
    
    # 1. Generar mapa
    generador = GeneradorMapa(ancho=8, alto=8)
    mapa = generador.generar_mapa()
    print(f"Mapa generado: {mapa.ancho}x{mapa.alto}")
    
    # 2. Crear jugador en la posición inicial
    inicio = mapa.obtener_posicion_inicio_jugador()
    jugador = Jugador(inicio[0], inicio[1], energia_maxima=100)
    print(f"Jugador creado en: {jugador.obtener_posicion()}")
    
    # 3. Intentar llegar a la salida
    salida = mapa.obtener_posicion_salida()
    print(f"Objetivo: llegar a la salida en {salida}")
    
    # Simular algunos movimientos
    movimientos = 0
    max_movimientos = 20
    
    while movimientos < max_movimientos and jugador.obtener_posicion() != salida:
        # Estrategia simple: moverse hacia la salida
        fila_actual, col_actual = jugador.obtener_posicion()
        fila_salida, col_salida = salida
        
        corriendo = jugador.puede_correr() and movimientos % 3 == 0
        
        if fila_actual < fila_salida:
            if jugador.mover_abajo(mapa, corriendo=corriendo):
                movimientos += 1
        elif fila_actual > fila_salida:
            if jugador.mover_arriba(mapa, corriendo=corriendo):
                movimientos += 1
        
        if col_actual < col_salida:
            if jugador.mover_derecha(mapa, corriendo=corriendo):
                movimientos += 1
        elif col_actual > col_salida:
            if jugador.mover_izquierda(mapa, corriendo=corriendo):
                movimientos += 1
        
        if movimientos >= max_movimientos:
            break
    
    print(f"\nMovimientos realizados: {movimientos}")
    print(f"Posición final: {jugador.obtener_posicion()}")
    print(f"Energía restante: {jugador.obtener_energia_actual()}/{jugador.obtener_energia_maxima()}")
    
    if jugador.obtener_posicion() == salida:
        print("[OK] ¡Llegaste a la salida!")
    else:
        print("[X] No se llego a la salida en el limite de movimientos")
    
    print()


def main():
    """Función principal que ejecuta todos los ejemplos."""
    print("\n" + "=" * 60)
    print("DEMOSTRACIÓN DEL NÚCLEO LÓGICO - ESCAPA DEL LABERINTO")
    print("=" * 60 + "\n")
    
    ejemplo_clases_terreno()
    ejemplo_generacion_mapa()
    ejemplo_movimiento_jugador()
    ejemplo_sistema_energia()
    ejemplo_registro_jugador()
    ejemplo_sistema_puntajes()
    ejemplo_completo()
    
    print("=" * 60)
    print("FIN DE LA DEMOSTRACIÓN")
    print("=" * 60)


if __name__ == "__main__":
    main()

