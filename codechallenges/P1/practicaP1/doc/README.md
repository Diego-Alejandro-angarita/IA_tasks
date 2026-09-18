# Práctica P1 — Pac-Man (RL)

Los notebooks ya **no dependen de Google Colab ni de Google Drive**: el ambiente
vive en `src/` dentro de este mismo repositorio.

```
practicaP1/
├── 00_pacman_environment.ipynb   # Parte 0: conocer el ambiente
├── 04_qlearning_pacman_examen.ipynb
└── src/
    ├── pacman_env.py             # PacmanEnv  (laberinto 8x9, 5 acciones)
    ├── tabular_pacman_env.py     # TabularPacmanEnv (laberinto 6x7, 4 acciones)
    └── pacman_render.py          # dibujo de los frames (NumPy puro)
```

## Cómo ejecutar

Basta con abrir cualquiera de los notebooks desde esta carpeta (VS Code, Jupyter
o Colab). La primera celda localiza `src/` subiendo por el árbol de directorios;
si no lo encuentra y detecta Colab, monta Drive y busca allí la carpeta del curso.

Requisitos: `numpy`, `matplotlib`, `ipython`.

## Ambientes

| | `PacmanEnv` | `TabularPacmanEnv` |
|---|---|---|
| Laberinto | 8x9, 32 celdas libres | 6x7, 18 celdas libres |
| Acciones | `North, South, East, West, Stop` | `up, right, down, left` |
| Estado | `PacmanState(pacman, ghost, food)` | entero, `n_states = 18 * 18 * 6 = 1944` |
| Comida | 30 (todas las celdas libres) | 5 posiciones fijas |

Estado tabular: `s = (p * n_celdas + g) * (max_food + 1) + comida_restante`,
decodificable con `env.decode_state(s)`.

Recompensas en ambos ambientes: `-1` por paso, `+10` por comida, `-100` si el
fantasma atrapa a Pac-Man y `+50` al limpiar el tablero. El fantasma se mueve
aleatoriamente entre sus casillas vecinas usando la semilla de `env.reset(seed=...)`.

Interfaz común:

```python
state = env.reset(seed=7)
legal_actions = env.get_legal_actions()
next_state, reward, done, info = env.step(action)
frame = env.render()
```
