# Escapa del Laberinto - Núcleo Lógico

Este proyecto contiene el núcleo lógico del juego "Escapa del Laberinto", implementado para la Persona 1 del equipo. Incluye las clases fundamentales del mundo del juego, sistema de movimiento, energía y puntajes.

## Estructura del Proyecto

```
Proyecto02/
├── modelo/              # Clases del mundo del juego
│   ├── __init__.py
│   ├── tile.py          # Clases de terreno (Casillas)
│   ├── mapa.py          # Clase Mapa
│   └── jugador.py       # Clase Jugador
├── core/                # Lógica adicional
│   ├── __init__.py
│   └── generador_mapa.py # Generación aleatoria de mapas
├── sistema/             # Sistemas auxiliares
│   ├── __init__.py
│   ├── jugador_info.py  # Registro de jugadores
│   └── puntajes.py      # Sistema de puntajes y top 5
├── puntajes/            # Directorio de archivos JSON (se crea automáticamente)
│   ├── puntajes_escapa.json
│   └── puntajes_cazador.json
├── main.py              # Ejemplos de uso
└── README.md            # Este archivo
```

## Componentes Principales

### 1. Clases de Terreno (modelo/tile.py)

Clases base y especializadas para representar las casillas del mapa:

- **Tile**: Clase base abstracta
  - `permite_paso_jugador() -> bool`
  - `permite_paso_enemigo() -> bool`

- **Camino**: Jugador y enemigos pueden pasar
- **Muro**: Nadie puede pasar
- **Liana**: Solo enemigos pueden pasar (obstáculo para jugador)
- **Tunel**: Solo jugador puede pasar (enemigos no)

### 2. Clase Mapa (modelo/mapa.py)

Representa el mapa como una matriz 2D de casillas.

**Atributos:**
- `ancho`, `alto`: Dimensiones del mapa
- `casillas`: Matriz 2D de objetos Tile
- `posicion_inicio`: Posición inicial del jugador
- `posicion_salida`: Posición de la salida

**Métodos principales:**
- `es_posicion_valida(fila, columna) -> bool`
- `es_transitable_por_jugador(fila, columna) -> bool`
- `es_transitable_por_enemigo(fila, columna) -> bool`
- `obtener_casilla(fila, columna) -> Tile`
- `obtener_posicion_salida() -> Tuple[int, int]`
- `obtener_posicion_inicio_jugador() -> Tuple[int, int]`
- `existe_camino_valido(desde, hasta) -> bool`: Verifica si existe un camino válido entre dos posiciones

### 3. Generación de Mapas (core/generador_mapa.py)

Genera mapas aleatorios con garantía de camino válido.

**Clase GeneradorMapa:**

```python
generador = GeneradorMapa(
    ancho=15,
    alto=15,
    densidad_muros=0.3,
    probabilidad_liana=0.1,
    probabilidad_tunel=0.1
)
mapa = generador.generar_mapa()
```

**Características:**
- Usa algoritmo DFS recursivo para generar laberintos
- Garantiza siempre un camino válido desde inicio hasta salida
- Agrega lianas y túneles sin bloquear el camino principal
- Verifica existencia de camino usando BFS

### 4. Clase Jugador (modelo/jugador.py)

Representa al jugador con posición y sistema de energía.

**Atributos:**
- `fila`, `columna`: Posición actual
- `energia_actual`: Energía actual
- `energia_maxima`: Energía máxima

**Métodos de movimiento:**
- `mover_arriba(mapa, corriendo=False) -> bool`
- `mover_abajo(mapa, corriendo=False) -> bool`
- `mover_izquierda(mapa, corriendo=False) -> bool`
- `mover_derecha(mapa, corriendo=False) -> bool`

**Sistema de energía:**
- `puede_correr() -> bool`: Verifica si tiene energía suficiente
- `consumir_energia(cantidad) -> bool`: Consume energía
- `recuperar_energia(cantidad)`: Recupera energía
- `actualizar_energia(delta_tiempo, tasa_recuperacion)`: Recuperación gradual
- `obtener_porcentaje_energia() -> float`: Porcentaje (0.0 a 1.0)
- `ha_llegado_a_salida(mapa) -> bool`: Verifica si el jugador llegó a la salida

**Consumo de energía:**
- Caminar: 1 punto
- Correr: 3 puntos

### 5. Registro de Jugador (sistema/jugador_info.py)

**Clase JugadorInfo:**
- `nombre`: Nombre del jugador
- `fecha_registro`: Fecha de registro

**Función auxiliar:**
```python
jugador_info = registrar_jugador("Juan")
```

### 6. Sistema de Puntajes (sistema/puntajes.py)

**Clase Puntaje:**
- `nombre_jugador`: Nombre del jugador
- `modo`: Modo de juego ("escapa" o "cazador")
- `puntos`: Puntos obtenidos

**Clase ScoreBoard:**
- Almacena puntajes por modo de juego
- Guarda en archivos JSON (puntajes_escapa.json, puntajes_cazador.json)
- Mantiene top 5 ordenados

**Uso:**
```python
scoreboard = ScoreBoard()
scoreboard.registrar_puntaje("escapa", "Juan", 1500)
top5 = scoreboard.obtener_top5("escapa")
```

## Ejemplos de Uso

Ejecuta `main.py` para ver ejemplos completos de uso:

```bash
python main.py
```

Los ejemplos demuestran:
1. Uso de clases de terreno
2. Generación de mapas
3. Movimiento del jugador
4. Sistema de energía
5. Registro de jugadores
6. Sistema de puntajes
7. Ejemplo completo integrado

## Requisitos

- Python 3.7 o superior
- No se requieren dependencias externas (solo biblioteca estándar)

## Uso Básico

### Crear un mapa manualmente

```python
from modelo import Mapa, Camino, Muro

# Crear matriz de casillas
casillas = [[Camino() for j in range(5)] for i in range(5)]
casillas[2][2] = Muro()  # Agregar un muro

# Crear mapa
mapa = Mapa(5, 5, casillas, (0, 0), (4, 4))
```

### Generar un mapa aleatorio

```python
from core import GeneradorMapa

generador = GeneradorMapa(ancho=10, alto=10)
mapa = generador.generar_mapa()
```

### Crear y mover un jugador

```python
from modelo import Jugador

# Crear jugador en la posición inicial del mapa
inicio = mapa.obtener_posicion_inicio_jugador()
jugador = Jugador(inicio[0], inicio[1], energia_maxima=100)

# Mover el jugador
jugador.mover_derecha(mapa, corriendo=False)  # Caminar
jugador.mover_abajo(mapa, corriendo=True)    # Correr

# Verificar si llegó a la salida
if jugador.ha_llegado_a_salida(mapa):
    print("¡Ganaste!")
```

### Registrar puntajes

```python
from sistema import ScoreBoard

scoreboard = ScoreBoard()
scoreboard.registrar_puntaje("escapa", "Juan", 1500)
top5 = scoreboard.obtener_top5("escapa")
```

## Notas de Implementación

- Sin interfaz gráfica: Este núcleo lógico está diseñado para ser independiente de la UI
- Modular: Cada componente está en su propio módulo para facilitar la integración
- Type hints: El código incluye anotaciones de tipo para mejor documentación
- Docstrings: Todas las clases y métodos están documentados
- Validaciones: El código incluye validaciones básicas para prevenir errores

## Próximos Pasos

Este núcleo lógico está listo para integrarse con:
- Lógica de enemigos e IA
- Sistema de trampas
- Modos de juego (Escapa y Cazador)
- Interfaz gráfica
- Sistema de sonido

## Estructura Modular

El proyecto está organizado en módulos independientes:

- **modelo/**: Contiene las clases fundamentales del juego (Tile, Mapa, Jugador)
- **core/**: Contiene algoritmos y lógica de generación (GeneradorMapa)
- **sistema/**: Contiene sistemas auxiliares (registro de jugadores, puntajes)

Cada módulo puede usarse independientemente, facilitando el trabajo en equipo y la mantenibilidad del código.

## Autor

##Iniciado por Bryan Charpentier

