# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Notebooks de la Actividad 2 del curso de Inteligencia Artificial: **Simulated Annealing** y **Algoritmos Genéticos**. Repo git raíz: `C:\Users\diego\Intro_IA`; esta carpeta es una actividad dentro de él. Ver también `../Actividad1/CLAUDE.md`, cuyas convenciones se heredan aquí.

## Los cuatro notebooks

Dos pares. Los `0X_*.ipynb` son los notebooks base del profesor sobre un problema de juguete; los `0X_*_hospitales.ipynb` son la adaptación al problema de casas/hospitales heredado de `Actividad1/01_hill_climbing.ipynb`.

- `02_simulated_annealing.ipynb` — maximiza `f(x)=sin(3x)+0.35·sin(9x)-0.03(x-2)²` en `[-4, 7]`. `SEED = 21`.
- `02_simulated_annealing_hospitales.ipynb` — minimiza `total_cost`. Compara Hill Climbing vs SA.
- `03_algoritmos_geneticos.ipynb` — OneMax (maximizar unos en una cadena binaria). `SEED = 14`.
- `03_algoritmos_geneticos_hospitales.ipynb` — GA sobre hospitales; `fitness = -total_cost` para convertir la minimización en maximización.

## Contrato compartido de los notebooks de hospitales

`manhattan`, `total_cost(houses, hospitals)`, `plot_state` y las constantes `SEED = 8`, `HEIGHT, WIDTH = 10, 16`, `NUM_HOUSES = 18`, `NUM_HOSPITALS = 3` están **duplicados textualmente** entre `02_simulated_annealing_hospitales.ipynb` y `03_algoritmos_geneticos_hospitales.ipynb`. Cualquier cambio ahí debe replicarse en ambos, o las comparaciones entre algoritmos dejan de ser válidas.

Ojo: SA-hospitales muestrea las casas con `random.sample` global y GA-hospitales con `rng.sample` sobre un `random.Random(SEED)`, así que **los conjuntos de casas no son idénticos** pese al mismo `SEED`. Antes de comparar costos entre notebooks hay que unificar el muestreo.

Signo de la aceptación: `exp(delta/T)` en el notebook base (maximiza) y `exp(-delta/T)` en el de hospitales (minimiza). No copiar uno sobre otro sin ajustar el signo.

Cada algoritmo devuelve un `records`/`history` de dicts con llaves en inglés (`iteration`, `temperature`, `best_cost`, `accepted`, `generation`, `diversity`, …). Las celdas de gráficas y tablas dependen de esas llaves.

## Idioma

Prosa markdown, comentarios, `print`, mensajes de excepción y etiquetas de gráficas: **español**. Identificadores (funciones, variables, clases): **inglés** (`houses`, `total_cost`, `best_individual`).

## Ejercicios y stubs

Son actividades de curso, no código de producción. Cada notebook termina con `## Actividades` (con `# TODO` + `pass`) y `## Preguntas de cierre`, todo sin resolver.

- No resolver ni borrar un stub que no se haya pedido explícitamente.
- Al resolver un ejercicio: **primero explicar el razonamiento y el enfoque, después el código**. El objetivo es aprender el algoritmo.
- No hay tests, ni pytest, ni CI. La verificación es ejecutar la celda.

## Estilo

Sin docstrings ni type hints. 4 espacios, `snake_case`, constantes de módulo en `UPPER_CASE`. Reproducibilidad intencional: `SEED` a nivel de módulo y objetos `random.Random(seed)` explícitos pasados por `rng=`.

Comillas: **simples** y formato compacto en los dos notebooks base; **dobles** y formato vertical (un argumento por línea) en los dos `_hospitales`. Seguir el archivo que se esté editando.

## Entorno y gotchas

- **No hay manifiesto de dependencias.** Se usan `numpy` y `matplotlib` además de `math`/`random` de stdlib. Nada más.
- Los notebooks se ejecutan en **VS Code contra el kernel de `../Actividad_cl2/.venv`** (único entorno con `ipykernel`, numpy y matplotlib). El Python global `C:\Python313` **no** tiene `ipykernel`. No hay servidor `jupyter` ni `gh` en el PATH.
- **Los outputs guardados no son confiables**: se generaron en un sandbox Linux ajeno (`/home/oai`, `/tmp/ipykernel_*`) y varios `execution_count` están en `null`. Verificar ejecutando, no leyendo el output almacenado.
- El entorno local tiene **matplotlib 3.11**, que ya eliminó el parámetro `labels=` de `boxplot()`. `02_simulated_annealing_hospitales.ipynb` todavía lo usa y esa celda falla al reejecutarse: cambiar a `tick_labels=` (como ya hace el notebook base).
- **No reserializar los `.ipynb`.** Tres de los cuatro están guardados como JSON minificado en una sola línea; editarlos con una herramienta que reindente produce un diff inútil de ~200 KB. Preservar el formato de cada archivo tal como está.
- Commits: minúscula, sin prefijo ni scope, mensaje corto en español.
