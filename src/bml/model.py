"""Simultaneous updates with open North/East boundaries, North first."""
import numpy as np


def validate(grid):
    grid = np.asarray(grid)
    if grid.ndim != 2 or not grid.size or grid.shape[0] != grid.shape[1]:
        raise ValueError("grid must be a nonempty square matrix")
    if not np.isin(grid, [0, 1, 3]).all():
        raise ValueError("grid entries must be 0, 1 or 3")
    return grid.astype(np.int8, copy=True)


def _step(grid, time):
    # Masks are computed from the old state: a car cannot follow into a site
    # vacated during this same update. Boundary cars leave the grid.
    result = grid.copy()
    if time % 2:
        moving = grid == 3
        moving[1:] &= grid[:-1] == 0
        result[moving] = 0
        result[:-1][moving[1:]] = 3
    else:
        moving = grid == 1
        moving[:, :-1] &= grid[:, 1:] == 0
        result[moving] = 0
        result[:, 1:][moving[:, :-1]] = 1
    return result


def step(grid, time):
    """Return the state after positive absolute time `time` (odd = North)."""
    if not isinstance(time, (int, np.integer)) or time < 1:
        raise ValueError("time must be a positive integer")
    return _step(validate(grid), time)


def evolve(grid, steps, first_update="north"):
    """Return the state at time `steps`, starting at time zero."""
    if not isinstance(steps, (int, np.integer)) or steps < 0:
        raise ValueError("steps must be a nonnegative integer")
    if first_update not in {"north", "east"}:
        raise ValueError("first_update must be north or east")
    grid = validate(grid)
    for time in range(1, steps + 1):
        grid = _step(grid, time + (first_update == "east"))
    return grid


def states_at(grid, times, first_update="north"):
    """Yield selected (time, state) pairs in increasing order in a single run."""
    times = sorted(set(times))
    if any(not isinstance(t, (int, np.integer)) or t < 0 for t in times):
        raise ValueError("snapshot times must be nonnegative integers")
    if first_update not in {"north", "east"}:
        raise ValueError("first_update must be north or east")
    grid = validate(grid)
    previous = 0
    for time in times:
        for t in range(previous + 1, time + 1):
            grid = _step(grid, t + (first_update == "east"))
        previous = time
        yield time, grid.copy()


def clearing_time(grid, max_steps=None, first_update="north"):
    """Count half-steps until empty; raise if the step budget is exceeded."""
    grid = validate(grid)
    if max_steps is not None and (not isinstance(max_steps, (int, np.integer)) or max_steps < 0):
        raise ValueError("max_steps must be a nonnegative integer")
    if first_update not in {"north", "east"}:
        raise ValueError("first_update must be north or east")
    n = len(grid)
    limit = 5 * n * n - n if max_steps is None else max_steps
    time = 0
    while np.any(grid):
        if time >= limit:
            raise TimeoutError(f"grid did not clear within {limit} steps")
        time += 1
        grid = _step(grid, time + (first_update == "east"))
    return time
