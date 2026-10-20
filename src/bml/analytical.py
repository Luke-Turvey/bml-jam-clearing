"""Explicit two-column evolution used in Figure 3."""
import numpy as np


def linear_state(n, time):
    """Evaluate the archived piecewise formula for the Figure 3 column phase.

    Arrays are indexed from the top left. At time zero each row is 1,3,1,3,...;
    the first update moves North cars. The formula applies to even grid sizes.
    """
    if not isinstance(n, (int, np.integer)) or n < 2 or n % 2:
        raise ValueError("the explicit formula requires a positive even grid size")
    if not isinstance(time, (int, np.integer)) or time < 0:
        raise ValueError("time must be a nonnegative integer")
    i = np.arange(1, n + 1)[:, None]
    column = np.arange(n)[None, :]
    boundary = n - (time - 4*n + 4)//2
    central = i <= boundary
    unchanged = central & (4*i >= time + 6)
    tail = central & (4*i <= time + 5)
    odd = column % 2 == 1
    north = tail & odd & ((i + (time-1)//2) % 3 == 0)
    east = tail & (4*i + 3*(column-1) >= time-1) & (
        (odd & ((i + time//2) % 3 == 2)) |
        (~odd & ((i + time//2) % 3 != 2))
    ) & ~north
    outer = (i > boundary) & (i + column + 1 > n + (time-4*n+4)//2)
    outer = outer & ((i + column - time//2) % 2 == 0)
    grid = np.zeros((n, n), dtype=np.uint8)
    grid[np.broadcast_to(unchanged, grid.shape)] = np.broadcast_to(
        np.where(odd, 3, 1), grid.shape
    )[np.broadcast_to(unchanged, grid.shape)]
    grid[north] = 3
    grid[east | outer] = 1
    return grid
