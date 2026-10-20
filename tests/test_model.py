"""Compare vectorised dynamics with an independent literal car simulator."""
import itertools
import numpy as np
import pytest
from bml.model import step, clearing_time, evolve
from bml.initial import periodic, parse_tile, random_grid


def literal(grid, time):
    result = grid.copy()
    n = len(grid)
    species, (di, dj) = (3, (-1, 0)) if time % 2 else (1, (0, 1))
    for i, j in itertools.product(range(n), repeat=2):
        if grid[i, j] != species:
            continue
        a, b = i + di, j + dj
        if not (0 <= a < n and 0 <= b < n):
            result[i, j] = 0
        elif grid[a, b] == 0:
            result[i, j] = 0
            result[a, b] = species
    return result


def test_all_small_states():
    for values in itertools.product([0, 1, 3], repeat=4):
        grid = np.array(values).reshape(2, 2)
        for time in [1, 2]:
            np.testing.assert_array_equal(step(grid, time), literal(grid, time))


def test_random_trajectories():
    rng = np.random.default_rng(23)
    for n in [3, 5, 8]:
        grid = rng.choice([0, 1, 3], size=(n, n))
        for time in range(1, 100):
            expected = literal(grid, time)
            np.testing.assert_array_equal(step(grid, time), expected)
            assert np.count_nonzero(expected) <= np.count_nonzero(grid)
            grid = expected


@pytest.mark.parametrize('n', [1, 2, 5, 10])
def test_known_homogeneous_times(n):
    assert clearing_time(np.ones((n, n), dtype=int)) == 4*n-2
    assert clearing_time(np.full((n, n), 3)) == 4*n-3
    assert clearing_time(np.zeros((n, n))) == 0


def test_phase_and_seed():
    tile = parse_tile('133333113')
    np.testing.assert_array_equal(periodic(tile, 2), tile[-2:, :2])
    np.testing.assert_array_equal(periodic(tile, 3), tile)
    np.testing.assert_array_equal(random_grid(10, 42), random_grid(10, 42))
    assert not np.array_equal(random_grid(10, 42), random_grid(10, 43))


def test_validation_and_budget():
    for grid in [[], [[2]], np.zeros((2, 3))]:
        with pytest.raises(ValueError): clearing_time(grid)
    with pytest.raises(TimeoutError): clearing_time([[1]], max_steps=1)
    with pytest.raises(ValueError): parse_tile('113')
    with pytest.raises(ValueError): evolve([[1]], -1)
    with pytest.raises(ValueError, match='North'):
        clearing_time([[1]], first_update='east')
    with pytest.raises(ValueError, match='North'):
        evolve([[1]], 1, first_update='east')


def test_north_only_simulation_policy():
    from bml.model import states_at
    with pytest.raises(ValueError, match='North'):
        list(states_at([[1]], [1], first_update='east'))
