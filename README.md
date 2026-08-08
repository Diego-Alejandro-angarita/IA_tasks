# Algoritmos de Búsqueda en Inteligencia Artificial
### Búsqueda en grafos, búsqueda en laberintos e Hill Climbing

**Curso:** Inteligencia Artificial S2666-0343

**Integrantes:**
1. Daniel Mauricio Giraldo Moreno
2. Esteban Alvarez
3. Diego Angarita
4. Ismael Garcia

---

## Tabla de contenido

1. [Introducción](#introducción)
2. [Repaso: ¿qué es un problema de búsqueda?](#repaso-qué-es-un-problema-de-búsqueda)
3. [Contenido del repositorio](#contenido-del-repositorio)
4. [Algoritmos de búsqueda en grafos](#algoritmos-de-búsqueda-en-grafos)
5. [De grafos a laberintos: qué cambia en el código](#de-grafos-a-laberintos-qué-cambia-en-el-código)
6. [¿Qué tipo de grafos/problemas resuelve mejor cada algoritmo?](#qué-tipo-de-grafosproblemas-resuelve-mejor-cada-algoritmo)
7. [Complejidad algorítmica](#complejidad-algorítmica)
8. [Hill Climbing y Random Restart](#hill-climbing-y-random-restart)
9. [Búsqueda en grafos vs. Hill Climbing](#búsqueda-en-grafos-vs-hill-climbing)
10. [Cómo ejecutar los notebooks](#cómo-ejecutar-los-notebooks)
11. [Conclusiones](#conclusiones)

---

## Introducción

Este repositorio reúne las actividades desarrolladas para la unidad de **búsqueda** de la materia de Inteligencia Artificial. El trabajo se organiza en tres notebooks que comparten una misma idea central: **la estructura general de un algoritmo de búsqueda casi no cambia entre problemas distintos; lo que cambia es cómo se representa el problema y cómo se organiza la frontera (frontier) de nodos por explorar.**

Se trabajaron dos grandes familias de algoritmos:

- **Búsqueda en espacio de estados con frontier explícita:** DFS, BFS, UCS (Uniform Cost Search), Greedy Best-First Search (GBF) y A\*. Estos algoritmos construyen y recorren un árbol/grafo de búsqueda, reconstruyen un camino y garantizan (bajo ciertas condiciones) encontrar una solución óptima.
- **Búsqueda local u optimización:** Hill Climbing y Random Restart. Aquí no se busca un *camino* hacia una meta, sino el mejor *estado* posible según una función de costo/objetivo, moviéndose únicamente entre estados vecinos y sin recordar el historial de estados visitados.

## Repaso: ¿qué es un problema de búsqueda?

Antes de entrar en cada algoritmo, es útil recordar los elementos comunes que definen cualquier problema de búsqueda, porque son exactamente los que se implementan en el código:

- **Estado inicial:** de dónde parte el agente (`start`).
- **Estado(s) meta:** condición que determina si se llegó a la solución (`goal`).
- **Función de vecinos / sucesores:** qué estados son alcanzables desde el estado actual y con qué costo. En el notebook de grafos es un diccionario (`graph[state]`); en el de laberintos es un método (`maze.neighbors(state)`).
- **Nodo de búsqueda (`Node`):** estructura auxiliar que guarda el estado, el nodo padre (para reconstruir el camino) y el costo acumulado `g(n)`.
- **Frontier (frontera):** conjunto de nodos generados pero aún no expandidos. **Es la pieza que distingue a cada algoritmo entre sí.**
- **Conjunto de explorados:** estados ya expandidos, para no reprocesarlos.

Con estas piezas fijas, los cinco algoritmos de búsqueda en grafo (DFS, BFS, UCS, GBF, A\*) comparten literalmente el mismo esqueleto de código (`while not frontier.empty(): ...`) y solo cambian **el tipo de frontier** y **el criterio de prioridad** con el que se decide qué nodo expandir a continuación.

## Contenido del repositorio

| Notebook | Problema | Algoritmos trabajados |
|---|---|---|
| `02_algoritmos_busqueda_grafo.ipynb` | Grafo pequeño y fijo (`A` → `H`), estados = letras, vecinos escritos a mano con costos | DFS, BFS, UCS, GBF, A\* |
| `02_busqueda_en_laberintos.ipynb` | Laberintos leídos desde archivo de texto, estados = coordenadas `(fila, columna)` | DFS, BFS, UCS, GBF, A\* (+ heurística ponderada no admisible) |
| `01_hill_climbing.ipynb` | Ubicación óptima de $k$ hospitales en una cuadrícula, minimizando distancia a las casas | Hill Climbing, Random Restart |

## Algoritmos de búsqueda en grafos

### DFS (Depth-First Search)

- **Frontier:** pila (LIFO), implementada en `StackFrontier`.
- **Criterio de expansión:** el último nodo agregado es el primero en explorarse.
- **Usa los costos de las aristas?** No. Los costos existen en el problema, pero DFS no los consulta para decidir a quién expandir; solo los acumula para reportar el costo final del camino encontrado.
- **Comportamiento observado:** en el laberinto `maze1`, DFS encontró un camino de costo **64**, muy por encima del óptimo (**28**). Se profundiza en una rama hasta el final antes de retroceder, así que puede encontrar caminos innecesariamente largos.

### BFS (Breadth-First Search)

- **Frontier:** cola (FIFO), implementada en `QueueFrontier` (una `StackFrontier` a la que solo se le cambia el método `remove` para hacer `pop(0)` en vez de `pop()`).
- **Criterio de expansión:** se exploran los nodos por niveles de profundidad.
- **Garantía:** encuentra el camino con **menor número de aristas**. Si todos los costos son iguales (como en el laberinto, donde cada paso cuesta 1), esto coincide con el camino de menor costo — por eso en `maze1` BFS también alcanza el óptimo de 28.

### UCS (Uniform Cost Search)

- **Frontier:** cola de prioridad (`PriorityFrontier`, basada en `heapq`).
- **Prioridad:** costo acumulado $g(n)$.
- **Diferencia clave en el código respecto a DFS/BFS:** aparece un diccionario `best_cost` que guarda el mejor costo conocido a cada estado, y si se encuentra un camino más barato a un estado ya visto, se vuelve a insertar en la frontier (las entradas "viejas" se descartan al extraerlas).
- **Garantía:** siempre encuentra el camino de **menor costo total**, incluso con costos de arista distintos.

### Greedy Best-First Search (GBF)

- **Frontier:** también `PriorityFrontier`.
- **Prioridad:** heurística $h(n)$ — la estimación del costo restante hasta la meta. En el grafo es una tabla fija (`heuristic["A"] = 4`); en el laberinto es una función de la coordenada, la distancia Manhattan a la meta.
- **Diferencia clave:** ignora completamente $g(n)$ al decidir qué expandir. Esto lo hace muy rápido (en `maze1` exploró solo 33 estados frente a los 106 de BFS/UCS) pero **no garantiza optimalidad**: encontró un camino de costo 32 en vez de 28, porque siguió un pasillo que "parecía" prometedor según la heurística.

### A\*

- **Frontier:** `PriorityFrontier`, igual que UCS.
- **Prioridad:** $f(n) = g(n) + h(n)$, combinando el costo ya recorrido con la estimación heurística.
- **Diferencia clave en el código respecto a UCS:** es literalmente UCS sumándole la heurística al priorizar (`priority=new_cost + heuristic(child_state, goal)`), conservando el mismo mecanismo de `best_cost` para permitir mejorar rutas.
- **Garantía:** óptimo cuando la heurística es **admisible** (nunca sobreestima el costo real). La distancia Manhattan lo es en una grilla donde solo se permiten movimientos ortogonales de costo 1.
- **Caso límite importante:** si $h(n) = 0$ para todos los nodos, A\* se comporta exactamente igual que UCS.
- **Heurística no admisible (experimento del notebook):** al ponderar la heurística ($h'(n) = w \cdot h(n)$, con $w=3$), A\* exploró muchos menos estados (52 vs. 141) pero perdió la garantía de optimalidad (costo 40 en vez de 36). Esto ilustra el espectro entre A\* puro ($w=1$) y Greedy puro ($w \to \infty$).

### Tabla comparativa (grafo `A → H`)

| Algoritmo | Frontier | Prioridad | Camino | Costo | ¿Óptimo? |
|---|---|---|---|---:|---:|
| DFS | Pila | LIFO | A→C→E→H | 6 | No |
| BFS | Cola | FIFO | A→B→D→H | 5 | Sí (aristas uniformes) |
| UCS | Cola de prioridad | $g(n)$ | A→B→E→H | 5 | Sí |
| GBF | Cola de prioridad | $h(n)$ | A→C→E→H | 6 | No |
| A\* | Cola de prioridad | $g(n)+h(n)$ | A→B→E→H | 5 | Sí (heurística admisible) |

### Tabla comparativa (laberinto `maze1`)

| Algoritmo | Estados explorados | Costo | ¿Óptimo? |
|---|---:|---:|---:|
| DFS | 69 | 64 | No |
| BFS | 106 | 28 | Sí |
| UCS | 106 | 28 | Sí |
| Greedy | 33 | 32 | No |
| A\* | 59 | 28 | Sí |

## De grafos a laberintos: qué cambia en el código

El notebook de laberintos está diseñado explícitamente para mostrar que **el algoritmo no cambia**; solo cambian dos piezas del problema:

1. **La representación de vecinos.** En el grafo era un diccionario fijo escrito a mano (`graph[state]` → lista de tuplas `(vecino, costo)`). En el laberinto es un método que calcula los vecinos dinámicamente a partir de una matriz de muros (`maze.neighbors(state)`), pero **devuelve exactamente el mismo formato** `(estado_vecino, costo)`. Gracias a eso, cualquier función de búsqueda escrita para el grafo funciona sin tocar una sola línea de su lógica interna, solo cambiando `graph[node.state]` por `maze.neighbors(node.state)`.
2. **La heurística.** En el grafo era una tabla fija por estado (`heuristic["A"]`). En el laberinto es una función `heuristic(state, goal)` (distancia Manhattan), porque los estados ahora son coordenadas y no se pueden enumerar de antemano.

Las clases `Node`, `StackFrontier`, `QueueFrontier`, `PriorityFrontier` y la función `reconstruct_path` se copian **sin ningún cambio** entre ambos notebooks. Esa es la evidencia más clara de que la arquitectura de búsqueda es independiente del problema concreto.

## ¿Qué tipo de grafos/problemas resuelve mejor cada algoritmo?

| Algoritmo | Funciona mejor cuando... | Se desempeña mal cuando... |
|---|---|---|
| **DFS** | El espacio de estados es profundo pero con soluciones conocidas cerca del fondo, o cuando solo importa *encontrar alguna* solución con poca memoria. Útil en grafos tipo árbol sin ciclos largos. | Grafos con caminos muy largos o ciclos: puede explorar ramas irrelevantes muy profundas antes de encontrar la meta, y no garantiza el camino más corto ni el más barato. |
| **BFS** | Grafos con **costos uniformes** (todas las aristas cuestan igual) donde interesa el camino con menos pasos, como laberintos con movimientos de costo 1. | Grafos con costos heterogéneos: puede reportar como "primera solución" un camino con más aristas pero de menor costo total, es decir, se vuelve subóptimo en costo. También es costoso en memoria en grafos muy anchos. |
| **UCS** | Grafos **ponderados con costos distintos** por arista, cuando se necesita garantía de camino de costo mínimo y no se dispone de una heurística. | Espacios de estados muy grandes: al no usar información adicional sobre la meta, explora en todas direcciones por igual y puede ser lento. |
| **Greedy (GBF)** | Problemas donde se prioriza la **velocidad** sobre la garantía de optimalidad y se cuenta con una heurística razonablemente buena (p. ej. laberintos simples y bien "guiados" hacia la meta). | Grafos con heurísticas engañosas (pasillos que "parecen" cercanos a la meta pero llevan a rodeos), donde puede quedar atrapado en soluciones notablemente subóptimas. |
| **A\*** | Es, en general, el mejor balance: grafos ponderados o laberintos donde se dispone de una **heurística admisible** (como la distancia Manhattan en grillas). Combina la garantía de UCS con la eficiencia de Greedy. | Si la heurística es mala, cara de calcular, o no admisible, pierde parte de su ventaja (menos estados explorados) o su garantía de optimalidad, respectivamente. |

## Complejidad algorítmica

Con factor de ramificación $b$, profundidad de la solución $d$, profundidad máxima del árbol $m$ y costo de la solución óptima $C^*$ (con aristas de costo mínimo $\varepsilon$):

| Algoritmo | Tiempo | Espacio | Completo | Óptimo |
|---|---|---|---:|---:|
| DFS | $O(b^m)$ | $O(bm)$ | No en espacios infinitos | No |
| BFS | $O(b^d)$ | $O(b^d)$ | Sí (ramificación finita) | Sí, con costos uniformes |
| UCS | $O(b^{1+\lfloor C^*/\varepsilon \rfloor})$ | $O(b^{1+\lfloor C^*/\varepsilon \rfloor})$ | Sí (costos positivos) | Sí |
| Greedy | $O(b^m)$ peor caso | $O(b^m)$ | No siempre | No |
| A\* | $O(b^d)$, mejora con mejor heurística | $O(b^d)$ | Sí, bajo condiciones estándar | Sí, con heurística admisible |

BFS y UCS son, en la práctica, muy parecidos en costo computacional a lo observado en `maze1` (106 estados explorados ambos); la diferencia entre ellos aparece solo cuando los costos de arista no son uniformes. A\* reduce claramente el número de estados explorados frente a BFS/UCS (59 vs. 106) gracias a la heurística, sin perder optimalidad.

## Hill Climbing y Random Restart

El segundo bloque del curso cambia de familia de algoritmos: en vez de *búsqueda de caminos* se trabaja *búsqueda local/optimización*, usando como problema la ubicación de $k$ hospitales en una cuadrícula para minimizar la distancia total a un conjunto de casas.

- **Representación del estado:** un conjunto de coordenadas de hospitales (no una secuencia de pasos desde un inicio).
- **Función objetivo:** costo total = suma de la distancia (Manhattan, o euclídea en la actividad de extensión) de cada casa al hospital más cercano.
- **Vecindario:** mover **un hospital a la vez** una celda en una de las cuatro direcciones (o hasta dos celdas, en la variante de la Actividad 3).
- **Hill Climbing:** en cada iteración se generan todos los vecinos, se calculan sus costos y el algoritmo se mueve al mejor vecino **solo si mejora estrictamente** el costo actual; si ningún vecino mejora, el algoritmo se detiene (óptimo local).
- **Random Restart:** ejecuta Hill Climbing varias veces desde distintos estados iniciales aleatorios y conserva la mejor solución de todas las corridas, como forma de escapar de óptimos locales sin garantizar el óptimo global.
- **Actividades resueltas:** comparación entre distancia Manhattan y euclídea, efecto de variar el número de hospitales $k$, y ampliación del vecindario a movimientos de hasta dos celdas (mejoró el costo de 62 a 60 a cambio de evaluar más vecinos: de 12 a 31).

## Búsqueda en grafos vs. Hill Climbing

| Aspecto | DFS / BFS / UCS / Greedy / A\* | Hill Climbing / Random Restart |
|---|---|---|
| Qué se busca | Un **camino** desde un inicio hasta una meta | El **mejor estado** según una función objetivo |
| Estructura de datos clave | Frontier (pila, cola o cola de prioridad) + conjunto de explorados | Ninguna: solo el estado actual y su vecindario |
| Memoria del historial | Sí, se reconstruye el camino completo (`parent`) | No, no se recuerda cómo se llegó al estado actual |
| Garantía de optimalidad | Sí, según el algoritmo (BFS/UCS/A\*) | No, puede quedar atrapado en óptimos locales |
| Espacio de búsqueda | Se construye explícitamente el árbol/grafo de búsqueda | Nunca se construye todo el espacio; solo se evalúan vecinos inmediatos |
| Costo computacional | Depende de $b$, $d$ o $m$ (ver tabla de complejidad) | Depende del tamaño del vecindario y del número de iteraciones/reinicios, mucho más barato por corrida |


## Conclusiones

- Los cinco algoritmos de búsqueda en grafo comparten **el mismo esqueleto de código**; la diferencia real está en el tipo de frontier y en el criterio de prioridad usado para decidir qué nodo expandir.
- **BFS, UCS y A\*** (con heurística admisible) garantizan encontrar una solución óptima; **DFS y Greedy**, no.
- Pasar de un grafo pequeño escrito a mano a un laberinto representado como matriz solo exige cambiar **cómo se calculan los vecinos** y **cómo se calcula la heurística** — el resto del código de búsqueda permanece intacto, lo que demuestra la generalidad de esta arquitectura.
- Hill Climbing pertenece a una familia distinta de algoritmos (búsqueda local): es mucho más económico en memoria y tiempo porque no explora ni recuerda todo el espacio de estados, pero a cambio pierde la garantía de optimalidad, lo que Random Restart intenta mitigar (sin garantizarlo del todo) probando múltiples puntos de partida.
- La elección del algoritmo adecuado en un problema real depende de: si se necesita una solución óptima, si los costos son uniformes, cuánta memoria hay disponible, qué tan buena es la heurística disponible, y qué tan grande es el espacio de estados.
