"""Utilidades de dibujo para los ambientes de Pac-Man.

Genera los frames como arreglos RGB (uint8) listos para `plt.imshow`,
sin dependencias externas mas alla de NumPy.
"""

from __future__ import annotations

import numpy as np

CELL = 40

COLOR_BG = (0, 0, 0)
COLOR_WALL = (23, 58, 143)
COLOR_WALL_EDGE = (93, 125, 255)
COLOR_FOOD = (255, 255, 255)
COLOR_PACMAN = (255, 210, 31)
COLOR_GHOST = (255, 75, 75)
COLOR_EYE = (255, 255, 255)

# Angulo hacia el que apunta la boca de Pac-Man, en radianes.
_DIRECTION_ANGLE = {
    (0, 1): 0.0,               # derecha
    (0, -1): np.pi,            # izquierda
    (-1, 0): np.pi / 2,        # arriba
    (1, 0): -np.pi / 2,        # abajo
}


def _cell_grid(size=CELL):
    """Coordenadas (y, x) normalizadas al centro de una celda."""
    axis = np.arange(size) + 0.5
    yy, xx = np.meshgrid(axis, axis, indexing="ij")
    return yy - size / 2, xx - size / 2


def _paint(frame, row, col, mask, color, size=CELL):
    y0, x0 = row * size, col * size
    block = frame[y0:y0 + size, x0:x0 + size]
    block[mask] = color


def draw_frame(walls, food, pacman, ghost, direction=(0, 1), size=CELL):
    """Dibuja un estado completo del tablero.

    Parameters
    ----------
    walls : np.ndarray booleano (n_rows, n_cols), True donde hay pared.
    food : iterable de posiciones (row, col) con comida.
    pacman : posicion (row, col) de Pac-Man.
    ghost : posicion (row, col) del fantasma (o None).
    direction : (dr, dc) hacia donde mira Pac-Man.
    """
    n_rows, n_cols = walls.shape
    frame = np.zeros((n_rows * size, n_cols * size, 3), dtype=np.uint8)
    frame[:, :] = COLOR_BG

    yy, xx = _cell_grid(size)
    radius = np.sqrt(yy ** 2 + xx ** 2)

    edge = size * 0.06
    border = (np.abs(yy) > size / 2 - edge) | (np.abs(xx) > size / 2 - edge)

    for row in range(n_rows):
        for col in range(n_cols):
            if walls[row, col]:
                _paint(frame, row, col, np.ones_like(border), COLOR_WALL, size)
                _paint(frame, row, col, border, COLOR_WALL_EDGE, size)

    dot = radius <= size * 0.09
    for row, col in food:
        _paint(frame, row, col, dot, COLOR_FOOD, size)

    if ghost is not None:
        _paint(frame, ghost[0], ghost[1], _ghost_mask(yy, xx, size), COLOR_GHOST, size)
        _paint(frame, ghost[0], ghost[1], _eyes_mask(yy, xx, size), COLOR_EYE, size)

    if pacman is not None:
        _paint(frame, pacman[0], pacman[1], _pacman_mask(yy, xx, size, direction), COLOR_PACMAN, size)

    return frame


def _pacman_mask(yy, xx, size, direction):
    radius = np.sqrt(yy ** 2 + xx ** 2)
    body = radius <= size * 0.40

    angle = np.arctan2(-yy, xx)
    target = _DIRECTION_ANGLE.get(tuple(direction), 0.0)
    delta = np.abs(np.arctan2(np.sin(angle - target), np.cos(angle - target)))
    mouth = delta < 0.55

    return body & ~mouth


def _ghost_mask(yy, xx, size):
    half = size * 0.32
    head_center = -size * 0.06

    head = (yy <= head_center) & (np.sqrt((yy - head_center) ** 2 + xx ** 2) <= half)

    # Falda con tres ondas en la parte inferior.
    t = (xx + half) / (2 * half)
    wave = size * 0.28 - size * 0.07 * (1 - np.cos(6 * np.pi * t)) / 2
    skirt = (yy > head_center) & (yy <= wave) & (np.abs(xx) <= half)

    return head | skirt


def _eyes_mask(yy, xx, size):
    left = np.sqrt((yy + size * 0.08) ** 2 + (xx + size * 0.12) ** 2) <= size * 0.07
    right = np.sqrt((yy + size * 0.08) ** 2 + (xx - size * 0.12) ** 2) <= size * 0.07
    return left | right


def parse_maze(rows):
    """Convierte un mapa ASCII en (walls, food, pacman, ghost).

    '#' pared, '.' comida, 'P' Pac-Man, 'G' fantasma, ' ' celda vacia.
    """
    walls = np.array([[char == "#" for char in row] for row in rows], dtype=bool)

    food, pacman, ghost = set(), None, None
    for r, row in enumerate(rows):
        for c, char in enumerate(row):
            if char == ".":
                food.add((r, c))
            elif char == "P":
                pacman = (r, c)
            elif char == "G":
                ghost = (r, c)

    return walls, food, pacman, ghost
