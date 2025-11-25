# 🏃 Escapa del Laberinto

Un emocionante juego de laberinto con interfaz gráfica donde debes escapar antes de que se acabe el tiempo. ¡Cuidado con tu energía al correr!

![Modos de Juego](https://img.shields.io/badge/Modos-Escapa%20%7C%20Cazador-blue)
![Python](https://img.shields.io/badge/Python-3.7+-green)
![Pygame](https://img.shields.io/badge/GUI-Pygame-red)

## 🎮 Características

- **Dos modos de juego**: Escapa y Cazador
- **Sistema de energía**: Administra tu energía al correr
- **Laberintos procedurales**: Cada partida es diferente
- **Tabla de puntajes**: Compite por el mejor puntaje
- **Interfaz visual moderna**: Tema cyberpunk/retro con animaciones

## 📁 Estructura del Proyecto

```
Proyecto02/
├── gui/                   # 🆕 Interfaz Gráfica
│   ├── __init__.py
│   ├── config.py          # Configuración y colores
│   ├── componentes.py     # Botones, barras, partículas
│   ├── renderizador.py    # Renderizado del mapa
│   └── pantallas.py       # Menú, juego, puntajes
├── modelo/                # Clases del mundo del juego
│   ├── __init__.py
│   ├── tile.py            # Casillas (Camino, Muro, Liana, Túnel)
│   ├── mapa.py            # Clase Mapa
│   └── jugador.py         # Clase Jugador con energía
├── core/                  # Lógica del juego
│   ├── __init__.py
│   └── generador_mapa.py  # Generación de laberintos
├── sistema/               # Sistemas auxiliares
│   ├── __init__.py
│   ├── jugador_info.py    # Registro de jugadores
│   └── puntajes.py        # Sistema de puntajes con fechas
├── puntajes/              # Archivos JSON de puntajes
│   ├── puntajes_escapa.json
│   └── puntajes_cazador.json
├── main_gui.py            # 🎮 EJECUTAR JUEGO CON GUI
├── main.py                # Demo del núcleo lógico (sin GUI)
├── requirements.txt       # Dependencias
└── README.md
```

## 🚀 Instalación y Ejecución

### Requisitos

- Python 3.7 o superior
- Pygame 2.5+

### Instalación de Pygame

**Opción 1 - Ubuntu/Debian (Recomendado):**
```bash
sudo apt install python3-pygame
```

**Opción 2 - Con pip (entorno virtual):**
```bash
python3 -m venv venv
source venv/bin/activate
pip install pygame
```

**Opción 3 - Con pip directamente:**
```bash
pip install pygame
```

### Ejecutar el Juego

```bash
cd Proyecto02
python3 main_gui.py
```

## 🎯 Controles

| Tecla | Acción |
|-------|--------|
| `↑ ↓ ← →` o `W A S D` | Mover al jugador |
| `SHIFT` + Dirección | Correr (gasta más energía) |
| `ESC` | Pausar / Menú |

## 🌟 Tipos de Terreno

| Terreno | Descripción | Jugador | Enemigo |
|---------|-------------|---------|---------|
| 🟫 **Camino** | Paso libre | ✅ | ✅ |
| 🟪 **Muro** | Bloqueado | ❌ | ❌ |
| 🟦 **Túnel** | Solo jugador | ✅ | ❌ |
| 🟩 **Liana** | Solo enemigos | ❌ | ✅ |

## ⚡ Sistema de Energía

- **Caminar**: Consume 1 punto de energía
- **Correr**: Consume 3 puntos de energía
- **Recuperación**: La energía se regenera gradualmente

## 🏆 Sistema de Puntajes

Los puntajes se calculan basándose en:
- **Tiempo restante**: +10 puntos por segundo
- **Energía final**: +5 puntos por punto de energía
- **Movimientos**: -2 puntos por movimiento
- **Base**: 1000 puntos (mínimo 100)

Los puntajes se guardan con fecha y hora en archivos JSON.

## 📝 Ejemplos de Uso del Núcleo Lógico

### Generar un mapa aleatorio

```python
from core import GeneradorMapa

generador = GeneradorMapa(ancho=20, alto=15)
mapa = generador.generar_mapa()
```

### Crear y mover un jugador

```python
from modelo import Jugador

inicio = mapa.obtener_posicion_inicio_jugador()
jugador = Jugador(inicio[0], inicio[1], energia_maxima=100)

# Mover el jugador
jugador.mover_derecha(mapa, corriendo=False)  # Caminar
jugador.mover_abajo(mapa, corriendo=True)     # Correr

# Verificar victoria
if jugador.ha_llegado_a_salida(mapa):
    print("¡Ganaste!")
```

### Registrar puntajes

```python
from sistema import ScoreBoard

scoreboard = ScoreBoard()
scoreboard.registrar_puntaje(
    modo="escapa",
    nombre_jugador="Juan",
    puntos=1500,
    tiempo_juego=45.5,
    movimientos=32
)

top5 = scoreboard.obtener_top5("escapa")
for puntaje in top5:
    print(f"{puntaje.nombre_jugador}: {puntaje.puntos} pts - {puntaje.obtener_fecha_formateada()}")
```

## 🎨 Personalización

El tema visual se puede modificar en `gui/config.py`:

```python
class Colores:
    # Fondos
    FONDO_OSCURO = (13, 17, 23)
    
    # Colores neón
    CYAN_NEON = (0, 255, 255)
    MAGENTA_NEON = (255, 0, 128)
    # ...
```

## 🔧 Configuración

En `gui/config.py` puedes ajustar:

```python
class Config:
    ANCHO_VENTANA = 1280
    ALTO_VENTANA = 720
    FPS = 60
    
    # Tamaño del mapa
    MAPA_ANCHO = 20
    MAPA_ALTO = 15
    
    # Tiempo límite por modo
    TIEMPO_PARTIDA_ESCAPA = 120   # segundos
    TIEMPO_PARTIDA_CAZADOR = 180  # segundos
```

## 📚 Módulos

### GUI (`gui/`)
- **config.py**: Configuración y paleta de colores
- **componentes.py**: Botones, barras de energía, partículas, inputs
- **renderizador.py**: Renderizado visual del mapa
- **pantallas.py**: Menú principal, pantalla de juego, puntajes

### Modelo (`modelo/`)
- **tile.py**: Tipos de casillas del laberinto
- **mapa.py**: Clase que representa el mapa
- **jugador.py**: Clase del jugador con sistema de energía

### Core (`core/`)
- **generador_mapa.py**: Algoritmo DFS para generar laberintos

### Sistema (`sistema/`)
- **puntajes.py**: Sistema de puntajes con persistencia JSON
- **jugador_info.py**: Información del jugador

## 👥 Autores

Iniciado por Bryan Charpentier

---

¡Disfruta el juego! 🎮
