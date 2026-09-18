# Justificación — Examen práctico: Q-Learning tabular con Pac-Man

Documento de acompañamiento de [`04_qlearning_pacman_examen.ipynb`](04_qlearning_pacman_examen.ipynb).
Explica **qué se implementó**, **por qué se tomó cada decisión** y **en qué
evidencia se apoya cada respuesta**. Todos los números citados aquí salen de
ejecutar el notebook completo de arriba abajo.

---

## 1. El problema

`TabularPacmanEnv` es un laberinto 6×7 con 18 celdas libres:

```
#######
#P . .#      P = Pac-Man (1,1)      G = fantasma (2,5)
# # #G#      comidas: (1,3) (1,5) (3,1) (3,5) (4,3)
#.   .#
#  .  #
#######
```

| Elemento | Valor |
|---|---|
| Estados | $18 \times 18 \times 6 = 1944$ |
| Acciones | 4 (`up`, `right`, `down`, `left`) |
| Valores a aprender | $1944 \times 4 = 7776$ |
| Recompensas | $-1$ paso, $+10$ comida, $-100$ fantasma, $+50$ tablero limpio |

El fantasma se mueve **aleatoriamente** entre celdas vecinas, sembrado por
`env.reset(seed=...)`. El entorno es por tanto **estocástico**: la misma
política produce retornos distintos en episodios distintos. Esto condiciona
toda la lectura de resultados más abajo.

---

## 2. Implementación

### TODO 1 — Q-table

```python
Q = np.zeros((env.n_states, env.n_actions))   # (1944, 4)
```

**Por qué ceros y no valores aleatorios.** Inicializar en cero significa "no
tengo ninguna preferencia todavía". Es además la elección neutra para este
ambiente: como casi todas las recompensas son negativas al principio
($-1$ por paso, $-100$ al morir), un cero funciona de hecho como
*inicialización optimista* — cualquier par $(s,a)$ nunca visitado parece
mejor que uno ya castigado, lo que empuja al agente a probar acciones nuevas
incluso cuando explota.

### TODO 2 — Política ε-greedy

```python
def choose_action(Q, state, epsilon, env):
    legal_actions = env.get_legal_actions()

    if random.random() < epsilon:
        return random.choice(legal_actions)

    values = np.array([Q[state, action] for action in legal_actions])
    best_value = values.max()

    best_actions = [a for a, v in zip(legal_actions, values) if v == best_value]
    return int(random.choice(best_actions))
```

Dos decisiones deliberadas:

1. **El `argmax` se calcula solo sobre `env.get_legal_actions()`**, no sobre
   la fila completa `Q[state]`. Si se usara `np.argmax(Q[state])` el agente
   elegiría acciones que chocan contra paredes; el ambiente las absorbe sin
   moverse, pero el agente gastaría un paso ($-1$) y —peor— aprendería
   Q-values para transiciones que no existen. Se añadió un `assert` en el
   notebook que verifica sobre 400 llamadas ($\epsilon=1$ y $\epsilon=0$) que
   la acción devuelta siempre es legal.

2. **Desempate aleatorio.** En el primer episodio toda la Q-table vale 0 y
   *todas* las acciones empatan. Con `np.argmax` se devolvería siempre el
   primer índice, así que el agente arrancaría marchando siempre en la misma
   dirección y exploraría muy mal el laberinto. `random.choice` sobre el
   conjunto de máximos convierte ese empate en una caminata aleatoria
   uniforme, que es el comportamiento correcto cuando no hay información.
   (Es la misma corrección que se aplicó en la actividad de Taxi-v4.)

### TODO 3 — Actualización Q-Learning

```python
def update_q(Q, state, action, reward, next_state, done, alpha, gamma):
    best_next_q = 0.0 if done else float(np.max(Q[next_state]))
    td_target = reward + gamma * best_next_q
    td_error  = td_target - Q[state, action]
    Q[state, action] += alpha * td_error
    return td_target, td_error
```

El punto crítico es **`0.0 if done else ...`**. Si $S_{t+1}$ es terminal no
hay futuro que estimar y $\max_{a'}Q(S_{t+1},a')$ debe valer 0 por definición.
Omitir esa guarda es el error clásico: la fila del estado terminal se sigue
actualizando y **filtra valor hacia atrás desde un estado del que nunca se
sale**, lo que infla los Q-values y puede hacer que morir junto a una comida
parezca rentable.

Aquí importa el doble: el estado terminal de *victoria* y el de *muerte* son
estados distintos pero ambos deben cortar el bootstrapping.

La función devuelve `td_target` y `td_error` como pide el enunciado, lo que
permite la comprobación manual de la celda 25.

### TODO 4 — Entrenamiento

```python
def train_q_learning(env, episodes=5000, alpha=0.1, gamma=0.95, epsilon=0.15,
                     max_steps=100, seed=100,
                     epsilon_min=0.02, epsilon_decay=0.9995):
    random.seed(seed)
    np.random.seed(seed)
    Q = np.zeros((env.n_states, env.n_actions))
    ...
        epsilon = max(epsilon_min, epsilon * epsilon_decay)
```

Cuatro decisiones:

- **`epsilon_min` y `epsilon_decay` como parámetros con valor por defecto.**
  El enunciado del TODO 4 los menciona explícitamente, pero la firma dada y la
  llamada de la celda 31 no los pasan. Se añadieron *con default* para no
  romper la llamada provista: `train_q_learning(env, episodes=5000, alpha=0.1,
  gamma=0.95, epsilon=0.15, max_steps=100, seed=100)` sigue funcionando tal
  cual está escrita en el notebook.
- **Decaimiento de ε.** Al principio conviene explorar (la Q-table no vale
  nada); al final conviene explotar (cada acción aleatoria arriesga un $-100$).
  El decaimiento multiplicativo con piso hace esa transición gradual.
- **Semilla por episodio, `env.reset(seed=seed + episode)`.** El laberinto y
  la posición inicial son fijos; lo único que cambia entre episodios es la
  trayectoria del fantasma. Variar la semilla garantiza que el agente vea
  muchos comportamientos distintos del fantasma en vez de memorizar uno solo.
  La evaluación usa semillas `10000+` — **disjuntas** de las de entrenamiento
  (`100..5099`) — para que sea una prueba de generalización real.
- **`random.seed(seed)` / `np.random.seed(seed)` al entrar.** `choose_action`
  usa el módulo `random` para explorar y desempatar, así que sin fijar la
  semilla el entrenamiento no es reproducible. Con esto, dos ejecuciones
  completas del notebook dan cifras idénticas (verificado).

---

## 3. Elección de la política de exploración

`alpha`, `gamma`, `episodes`, `epsilon` inicial y `max_steps` vienen fijados
por la celda 31 del notebook y **no se modificaron**. Lo único elegido fue el
*schedule* de ε. Se compararon offline varias combinaciones, midiendo siempre
con `evaluate_policy` (200 episodios greedy, semillas 10000+):

| ε inicial | decay | mínimo | Reward | Pasos | Victorias |
|---:|---:|---:|---:|---:|---:|
| 0.15 | 0.999 | 0.01 | 40.40 | 43.41 | 0.730 |
| 0.15 | 1.0 (sin decay) | 0.15 | 31.64 | 49.46 | 0.685 |
| 0.15 | 0.9995 | 0.05 | 47.54 | 38.81 | 0.775 |
| **0.15** | **0.9995** | **0.02** | **54.42** | **35.53** | **0.835** |

Se adoptó la última fila. Dos lecturas:

- **Sin decaimiento el resultado es el peor de todos** (0.685). Mantener
  $\epsilon=0.15$ hasta el final impide que la política se afine.
- Bajar demasiado el piso (0.01) tampoco es mejor que 0.02: corta la
  exploración antes de que la Q-table cubra los estados poco frecuentes.

La sección 14 del notebook reproduce el experimento complementario —variar
**solo** el ε inicial— y muestra que, una vez fijado el decaimiento, subirlo
**no** ayuda:

```
epsilon inicial = 0.15 -> reward =  54.42 | pasos = 35.53 | victorias = 0.835
epsilon inicial = 0.30 -> reward =  52.21 | pasos = 37.19 | victorias = 0.825
epsilon inicial = 0.50 -> reward =  49.04 | pasos = 39.51 | victorias = 0.810
```

Es decir: con 5000 episodios, **el schedule pesa más que el valor inicial**, y
explorar de más simplemente gasta episodios en trayectorias que ya se sabían
malas.

---

## 4. Resultados

**Entrenamiento** (medias móviles de 100 episodios):

| | Primeros 100 | Últimos 100 |
|---|---:|---:|
| Recompensa | $-81.89$ | $+35.16$ |
| Victorias | 0.08 | 0.71 |

**Evaluación greedy**, 200 episodios con semillas no vistas:

| Métrica | Valor |
|---|---:|
| Recompensa promedio | **54.42** |
| Pasos promedio | 35.53 |
| Tasa de victoria | **0.835** |
| Muertes | **0 / 200** |
| Episodios agotados (`max_steps`) | 33 / 200 |

**Episodio de demostración** (`seed=20`):

| | Aleatoria | Aprendida |
|---|---:|---:|
| Recompensa | $-94$ | $+80$ |
| Pasos | 14 | 20 |
| Comidas | 2/5 | 5/5 |
| Desenlace | atrapada por el fantasma | tablero limpio |

---

## 5. Justificación de las respuestas

**Pregunta 1 (aliasing).** La respuesta —"el mismo estado"— se lee
directamente de `encode_state`, que solo consume `(p, g, len(food))`. No es un
detalle teórico: es la causa demostrable de los 33 timeouts. Con $n=1$ el
agente no puede saber si la comida que falta está en $(1,3)$ o en $(3,1)$
—extremos opuestos— y la política greedy determinista oscila. Se cuantificó el
arreglo: representar el conjunto exacto de comida lleva el espacio de
$18\cdot18\cdot6 = 1944$ a $18\cdot18\cdot2^5 = 10\,368$ estados.

**Pregunta 2 (qué da el ambiente).** $R_{t+1}$ y $S_{t+1}$ son el valor de
retorno de `env.step()`; los dos Q-values se leen de `Q`, una estructura que
vive en el agente. Se destacó que el TD target mezcla ambas fuentes porque ahí
está el concepto que se evalúa: *bootstrapping*, aprender sin modelo de
transición.

**Pregunta 3 (ε = 0.10).** 10 % explorar / 90 % explotar. Se añadió el matiz
de que la probabilidad de ejecutar una acción distinta de la greedy es menor
que 10 % (la rama aleatoria puede caer sobre la greedy: con 2 acciones
legales, la mitad de las veces). El punto 3 conecta con la decisión de diseño
del TODO 2: con todos los Q-values iguales, explotar es indistinguible de
explorar, y esa es exactamente la razón del desempate aleatorio.

**Pregunta 4 (target / error / nuevo Q).** Se respondió con los números
concretos que imprime la celda 25 ($-1 + 0.9\cdot4 = 2.6$; error $2.6$; nuevo
Q $= 0 + 0.5\cdot2.6 = 1.3$) en vez de solo con definiciones, para mostrar que
$\alpha$ produce un paso *parcial* hacia el target. Ese promediado es
justamente lo que da estabilidad frente a un fantasma aleatorio.

**Pregunta 5 (curvas).** Sí hay aprendizaje, con los números de la tabla de
arriba. Se señalaron dos cosas que suelen leerse mal:

- la curva **oscila** y eso no indica un error — el fantasma es aleatorio y
  $\epsilon$ nunca llega a 0;
- la victoria en entrenamiento (0.71) es **menor** que en evaluación (0.835)
  precisamente porque durante el entrenamiento el agente sigue explorando.
  Comparar ambas cifras sin esa aclaración llevaría a la conclusión falsa de
  que el agente empeora al evaluarlo.

**Pregunta 6 (Q-values iniciales).** `right` = 23.630 vs `down` = 10.857. El
argumento clave: **las dos acciones dan la misma recompensa inmediata**
($-1$; ni $(1,2)$ ni $(2,1)$ tienen comida), así que los ~12.8 puntos de
diferencia son enteramente *futuro descontado*. Es la demostración más limpia
de que $Q(s,a) \neq$ recompensa inmediata.

**Pregunta 7 (comparación).** Además de la tabla, se apoyó la afirmación
"evita al fantasma" en el trazado paso a paso del episodio: el agente llega a
$(4,5)$ con el fantasma a distancia 1 en $(3,5)$, **retrocede** en lugar de
seguir, y vuelve a por esa comida dos pasos más tarde cuando el fantasma se ha
alejado. No es una impresión visual: en 200 episodios de evaluación hay **0
muertes**.

Sobre por qué un solo escalar optimiza tres objetivos: los cuatro términos se
suman en el mismo retorno con magnitudes jerarquizadas a propósito. El $-100$
domina (equivale a 10 comidas o 100 pasos) **y además corta el episodio**,
cancelando el $+50$ pendiente — por eso "no morir" es lo primero que se
aprende y lo que explica la subida brusca de los primeros ~600 episodios. El
$-1$ por paso penaliza los rodeos, y $\gamma=0.95$ refuerza lo mismo por otra
vía: una comida a 5 pasos vale $0.95^5 \approx 0.77$ de su valor.

---

## 6. Limitación conocida

El agente **no muere nunca** pero **falla en 33/200 episodios por agotar
`max_steps`**. Todos los fallos son del mismo tipo y tienen una única causa:
el aliasing de la Pregunta 1. Vale la pena decirlo explícitamente porque
cambia el diagnóstico — no es falta de entrenamiento ni un ε mal elegido, es
un límite de la **representación del estado**. Con esta codificación de
estado, el techo empírico ronda 0.93 de victorias incluso entrenando
20 000 episodios; para superarlo haría falta incluir en el estado *qué*
comidas quedan.

---

## 7. Reproducibilidad

- Notebook ejecutado de principio a fin sin errores; todas las celdas tienen
  salida.
- Ejecutado dos veces completas: cifras **idénticas** (la sección 14 vuelve a
  entrenar con $\epsilon=0.15$ y recupera exactamente `0.835`, la misma cifra
  de la celda de evaluación).
- No se modificó nada en `src/`, ni las funciones auxiliares de
  visualización, ni la llamada de entrenamiento de la celda 31.
- Entorno: Python 3.13, `numpy`, `matplotlib`, `ipython`.
