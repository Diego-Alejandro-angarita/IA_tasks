"""Versión tabular de Pac-Man para Q-Learning.

El estado se simplifica a

    s = (p, g, n)

donde p es la posición de Pac-Man, g la del fantasma y n la cantidad de
comidas restantes, de modo que

    n_states = n_p * n_g * (max_food + 1).

El ambiente conserva internamente la posición exacta de cada comida (para
simular y visualizar), pero esa información no forma parte del estado.

Interfaz:

    state = env.reset(seed=7)          # entero
    legal_actions = env.get_legal_actions()
    next_state, reward, done, info = env.step(action)
    env.decode_state(state)            # PacmanState(pacman, ghost, food_remaining)
    frame = env.render()

Recompensas
-----------
    -1    por cada paso,
   +10    al comer una comida,
   -100   si el fantasma atrapa a Pac-Man,
   +50    al comer toda la comida del tablero.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from pacman_render import draw_frame, parse_maze

ACTIONS: Dict[int, str] = {
    0: "up",
    1: "right",
    2: "down",
    3: "left",
}

MOVES: Dict[int, Tuple[int, int]] = {
    0: (-1, 0),
    1: (0, 1),
    2: (1, 0),
    3: (0, -1),
}

MAZE: Tuple[str, ...] = (
    "#######",
    "#P . .#",
    "# # #G#",
    "#.   .#",
    "#  .  #",
    "#######",
)

STEP_PENALTY = -1
FOOD_REWARD = 10
GHOST_PENALTY = -100
WIN_REWARD = 50


@dataclass(frozen=True)
class PacmanState:
    pacman: Tuple[int, int]
    ghost: Tuple[int, int]
    food_remaining: int


class TabularPacmanEnv:
    """Pac-Man discreto, pensado para una Q-table de tamaño manejable."""

    def __init__(self, maze: Tuple[str, ...] = MAZE, seed: Optional[int] = None):
        self.walls, self._initial_food, self._start_pacman, self._start_ghost = parse_maze(maze)
        self.n_rows, self.n_cols = self.walls.shape

        self.free_cells: List[Tuple[int, int]] = [
            (r, c)
            for r in range(self.n_rows)
            for c in range(self.n_cols)
            if not self.walls[r, c]
        ]
        self._cell_index = {cell: i for i, cell in enumerate(self.free_cells)}

        self.max_food = len(self._initial_food)
        self.n_actions = len(ACTIONS)
        self.n_states = len(self.free_cells) ** 2 * (self.max_food + 1)

        self._rng = random.Random(seed)
        self.reset(seed=seed)

    # ------------------------------------------------------------------ API

    def reset(self, seed: Optional[int] = None) -> int:
        if seed is not None:
            self._rng = random.Random(seed)

        self.pacman = self._start_pacman
        self.ghost = self._start_ghost
        self.food = set(self._initial_food)
        self.direction = (0, 1)

        self.steps = 0
        self.score = 0
        self.done = False
        self.won = False
        self.lost = False

        return self.state

    @property
    def state(self) -> int:
        return self.encode_state(self.pacman, self.ghost, len(self.food))

    def encode_state(self, pacman, ghost, food_remaining: int) -> int:
        p = self._cell_index[tuple(pacman)]
        g = self._cell_index[tuple(ghost)]
        return (p * len(self.free_cells) + g) * (self.max_food + 1) + food_remaining

    def decode_state(self, state: int) -> PacmanState:
        n_cells = len(self.free_cells)
        state, food_remaining = divmod(int(state), self.max_food + 1)
        p, g = divmod(state, n_cells)
        return PacmanState(self.free_cells[p], self.free_cells[g], food_remaining)

    def get_legal_actions(self, position: Optional[Tuple[int, int]] = None) -> List[int]:
        position = self.pacman if position is None else position
        return [
            action
            for action, (dr, dc) in MOVES.items()
            if not self.walls[position[0] + dr, position[1] + dc]
        ]

    def step(self, action: int):
        if self.done:
            raise RuntimeError("El episodio terminó: llame a env.reset() antes de continuar.")
        if action not in ACTIONS:
            raise ValueError(f"Acción inválida: {action}. Use una de {sorted(ACTIONS)}.")

        reward = STEP_PENALTY
        self.steps += 1

        dr, dc = MOVES[action]
        target = (self.pacman[0] + dr, self.pacman[1] + dc)
        if not self.walls[target]:
            self.pacman = target
            self.direction = (dr, dc)

        if self.pacman in self.food:
            self.food.discard(self.pacman)
            reward += FOOD_REWARD

        if self.pacman == self.ghost:
            reward += GHOST_PENALTY
            self.lost = True
            self.done = True
        elif not self.food:
            reward += WIN_REWARD
            self.won = True
            self.done = True
        else:
            self.ghost = self._move_ghost()
            if self.ghost == self.pacman:
                reward += GHOST_PENALTY
                self.lost = True
                self.done = True

        self.score += reward
        return self.state, reward, self.done, self._info()

    def render(self):
        return draw_frame(self.walls, self.food, self.pacman, self.ghost, self.direction)

    # -------------------------------------------------------------- internos

    def _move_ghost(self) -> Tuple[int, int]:
        options = [
            (self.ghost[0] + dr, self.ghost[1] + dc)
            for dr, dc in MOVES.values()
            if not self.walls[self.ghost[0] + dr, self.ghost[1] + dc]
        ]
        return self._rng.choice(options) if options else self.ghost

    def _info(self) -> dict:
        return {
            "score": self.score,
            "steps": self.steps,
            "food_remaining": len(self.food),
            "food_eaten": self.max_food - len(self.food),
            "won": self.won,
            "lost": self.lost,
        }
