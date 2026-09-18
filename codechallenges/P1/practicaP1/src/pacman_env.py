"""Ambiente de Pac-Man usado en la Parte 0 (conocer el ambiente).

Interfaz tipo Gym, minima y sin dependencias externas:

    state = env.reset(seed=7)
    legal_actions = env.get_legal_actions()
    next_state, reward, done, info = env.step(action)
    frame = env.render()

Recompensas
-----------
    -1    por cada paso (incluido 'Stop'),
   +10    al comer una comida,
   -100   si el fantasma atrapa a Pac-Man,
   +50    al comer toda la comida del tablero.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, FrozenSet, List, Optional, Tuple

from pacman_render import draw_frame, parse_maze

ACTIONS: Dict[int, str] = {
    0: "North",
    1: "South",
    2: "East",
    3: "West",
    4: "Stop",
}

MOVES: Dict[int, Tuple[int, int]] = {
    0: (-1, 0),
    1: (1, 0),
    2: (0, 1),
    3: (0, -1),
    4: (0, 0),
}

MAZE: Tuple[str, ...] = (
    "#########",
    "#P..#...#",
    "#.#.#.#.#",
    "#.......#",
    "###.#.###",
    "#...#..G#",
    "#.......#",
    "#########",
)

STEP_PENALTY = -1
FOOD_REWARD = 10
GHOST_PENALTY = -100
WIN_REWARD = 50


@dataclass(frozen=True)
class PacmanState:
    pacman: Tuple[int, int]
    ghost: Tuple[int, int]
    food: FrozenSet[Tuple[int, int]]

    def __repr__(self) -> str:  # se muestra el conteo, no el conjunto completo
        return (
            f"PacmanState(pacman={self.pacman}, "
            f"ghost={self.ghost}, food={len(self.food)})"
        )


class PacmanEnv:
    """Pac-Man en un laberinto pequeño con un fantasma de movimiento aleatorio."""

    def __init__(self, maze: Tuple[str, ...] = MAZE, seed: Optional[int] = None):
        self.walls, self._initial_food, self._start_pacman, self._start_ghost = parse_maze(maze)
        self.n_rows, self.n_cols = self.walls.shape
        self.free_cells = [
            (r, c)
            for r in range(self.n_rows)
            for c in range(self.n_cols)
            if not self.walls[r, c]
        ]
        self.max_food = len(self._initial_food)
        self.n_actions = len(ACTIONS)

        self._rng = random.Random(seed)
        self.reset(seed=seed)

    # ------------------------------------------------------------------ API

    def reset(self, seed: Optional[int] = None) -> PacmanState:
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
    def state(self) -> PacmanState:
        return PacmanState(self.pacman, self.ghost, frozenset(self.food))

    def get_legal_actions(self, position: Optional[Tuple[int, int]] = None) -> List[int]:
        position = self.pacman if position is None else position
        legal = []
        for action, (dr, dc) in MOVES.items():
            row, col = position[0] + dr, position[1] + dc
            if not self.walls[row, col]:
                legal.append(action)
        return legal

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
            if (dr, dc) != (0, 0):
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
            for action, (dr, dc) in MOVES.items()
            if action != 4 and not self.walls[self.ghost[0] + dr, self.ghost[1] + dc]
        ]
        return self._rng.choice(options) if options else self.ghost

    def _info(self) -> dict:
        return {
            "score": self.score,
            "steps": self.steps,
            "food_remaining": len(self.food),
            "won": self.won,
            "lost": self.lost,
        }
