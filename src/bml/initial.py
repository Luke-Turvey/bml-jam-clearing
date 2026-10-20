"""Initial states anchored at the bottom left, as in the paper."""
import math
import numpy as np
from .model import validate


def periodic(tile, n):
    """Repeat a tile written top-to-bottom; crop to n without rounding down.

    The tile's bottom-left corner stays at the grid's bottom-left corner.
    This phase convention matters for sizes not divisible by the tile period.
    """
    tile = validate(tile)
    if not isinstance(n, (int, np.integer)) or n < 1:
        raise ValueError("n must be a positive integer")
    k = math.ceil(n / len(tile))
    return np.tile(tile, (k, k))[-n:, :n].copy()


def parse_tile(text):
    """Read a row-major tile, for example 113133313 (0/1/3 encoding)."""
    if not text or any(c not in '013' for c in text):
        raise ValueError("tile must contain only 0, 1 and 3")
    side = math.isqrt(len(text))
    if side * side != len(text):
        raise ValueError("tile length must be a perfect square")
    return np.array(list(text), dtype=np.int8).reshape(side, side)


def random_grid(n, seed=0, density=1.0):
    if not isinstance(n, (int, np.integer)) or n < 1:
        raise ValueError("n must be a positive integer")
    if not 0 <= density <= 1:
        raise ValueError("density must lie between zero and one")
    return np.random.default_rng(seed).choice(
        [0, 1, 3], size=(n, n), p=[1-density, density/2, density/2]
    ).astype(np.int8)
