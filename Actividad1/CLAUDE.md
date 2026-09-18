# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Notebooks del curso **SI3003 — Inteligencia Artificial**. Repo git raíz: `C:\Users\diego\Intro_IA`; esta carpeta es una actividad dentro de él.

## Idioma

Prosa markdown, comentarios, `print`, mensajes de excepción y etiquetas de gráficas: **español**. Identificadores (funciones, variables, clases): **inglés** (`houses`, `total_cost`, `expansion_order`). Términos como `frontier`, `state`, `goal` se dejan sin traducir a propósito. La única excepción son las llaves de `summarize_results` en `02_busqueda_en_laberintos.ipynb`, que sí van en español.

## Contrato compartido de los algoritmos de búsqueda

Toda función de búsqueda devuelve exactamente:

```python
{"path": reconstruct_path(node), "expansion_order": expansion_order, "cost": node.cost}
```

y devuelve `None` si no hay solución. Las que aceptan `verbose=True` imprimen `f"Expandiendo: {node.state}"`, `f"Frontier antes de agregar vecinos: {frontier.states()}"` y separadores `print("-" * 45)`. Mantener este formato: las celdas de prueba y las tablas comparativas dependen de él.

`Node`, `reconstruct_path`, `StackFrontier`, `QueueFrontier` y `PriorityFrontier` están **duplicados textualmente** entre `02_algoritmos_busqueda_grafo.ipynb` y `02_busqueda_en_laberintos.ipynb`. Cualquier cambio a esa arquitectura compartida debe replicarse en ambos notebooks.

`PriorityFrontier.remove()` devuelve la tupla `(node, priority)`, no solo el nodo.

## Ejercicios y stubs

Son actividades de curso, no código de producción:

- `# YOUR CODE HERE` + `raise NotImplementedError` (notebook de grafos) y `# TODO: ...` + `pass` (hill climbing) marcan ejercicios pendientes.
- No resolver ni borrar un stub que no se haya pedido explícitamente; al resolver uno, conservar el marcador `# YOUR CODE HERE` encima de la solución (es el patrón que ya usa el notebook).
- Las celdas `assert` son la única forma de prueba del repo. No hay pytest ni CI.

## Estilo

Sin docstrings ni type hints, salvo la clase `Maze`. 4 espacios, `snake_case`, constantes de módulo en `UPPER_CASE`. Comillas: **simples** en `01_hill_climbing.ipynb`, **dobles** en los dos notebooks `02_*`; seguir el archivo que se esté editando. `Node(...)` se construye con argumentos nombrados, uno por línea.

`01_hill_climbing.ipynb` fija `SEED = 8` y pasa objetos `random.Random(seed)` explícitos por el parámetro `rng=`. Preservar ese patrón: la reproducibilidad es intencional.

## Entorno y gotchas

- **No hay manifiesto de dependencias.** Se usan `numpy` y `matplotlib` además de stdlib. El venv en `../Actividad_cl2/.venv` **no** tiene numpy ni matplotlib, así que solo `02_algoritmos_busqueda_grafo.ipynb` (stdlib puro) corre ahí.
- **Los outputs guardados no son confiables.** Los notebooks se commitean con outputs, y los `execution_count` están desordenados; hay tracebacks viejos guardados. Verificar ejecutando, no leyendo el output almacenado.
- `02_busqueda_en_laberintos.ipynb` es **solo para Colab**: hace `drive.mount('/content/drive')` y `cd` a una ruta de Drive. Además lee `maze1.txt`/`maze2.txt`/`maze3.txt` y la imagen `heuristica_busqueda.png`, que **no están en el repo**.
- Commits: minúscula, sin prefijo ni scope, mensaje corto en español.
