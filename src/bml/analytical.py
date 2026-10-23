"""Explicit two-column evolution used in Figure 3."""
import numpy as np


def linear_state(n, time):
    """Evaluate the complete alternating-column evolution in Figure 3.

    The theorem uses Cartesian coordinates, with (1, 1) at the bottom left.
    The returned array is indexed from the top left: ``grid[row, column]``
    equals ``F_n(column + 1, n - row, time)``. Entries are 0 (empty),
    1 (East), or 3 (North). At time zero, every row is 1,3,1,3,...;
    North moves on odd updates. The formula applies to every positive size.
    """
    if not isinstance(n, (int, np.integer)) or n < 1:
        raise ValueError("n must be a positive integer")
    if not isinstance(time, (int, np.integer)) or time < 0:
        raise ValueError("time must be a nonnegative integer")
    x = np.arange(1, n + 1)[None, :]
    y = np.arange(n, 0, -1)[:, None]
    q, r = (time - 1) // 2, time // 2
    boundary = r - 2*n + 3
    central = y >= boundary
    unchanged = central & (4*y + time <= 4*n - 2)
    periodic = central & (4*y + time >= 4*n - 1)
    even = x % 2 == 0
    north = (unchanged & even) | (
        periodic & even & ((y - n - q - 1) % 3 == 0)
    )
    east = (unchanged & ~even) | (
        periodic & (3*x - 4*y >= time - 4*n + 1) & (
            (even & ((y - n - r + 1) % 3 == 0)) |
            (~even & ((y - n - r + 1) % 3 != 0))
        ) & ~north
    )
    outer = (y < boundary) & (x - y > r - 2*n + 1)
    outer &= (x - y - r) % 2 == 0
    grid = np.zeros((n, n), dtype=np.uint8)
    grid[north] = 3
    grid[east | outer] = 1
    if n % 2 and r >= 1:
        boundary_exit = (x == n) & central & (
            (r < 2*n - 2*y + 1) | ((y - n - r) % 3 == 0)
        )
        grid[boundary_exit] = 0
    return grid
