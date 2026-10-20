"""Checks for the complete numbered-figure workflow."""
import hashlib
import json
from pathlib import Path
import numpy as np
import pytest
from bml.analytical import linear_state
from bml.figures import plan, reproduce, _load_state, _simulate_states
from bml.initial import periodic, parse_tile
from bml.model import states_at, step

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('n', [2, 4, 10, 50])
def test_explicit_evolution(n):
    for time, grid in states_at(periodic(parse_tile('1313'), n), range(6*n)):
        np.testing.assert_array_equal(linear_state(n, time), grid)


def test_figure_catalog_and_data():
    build = plan(ROOT, range(1, 14), mode='simulate')
    assert [entry['figure'] for entry in build['figures']] == list(range(1, 14))
    states = json.loads((ROOT / 'data/figures/states.json').read_text())
    for entry in states.values():
        grid = _load_state(ROOT, entry)
        assert hashlib.sha256(grid.tobytes()).hexdigest() == entry['state_sha256']
    initial = _load_state(ROOT, states['random_initial'])
    first = step(initial, 2)
    assert hashlib.sha256(first.tobytes()).hexdigest() == states['random_initial']['first_step_sha256']
    assert np.all(initial != 0)
    for number in range(1, 14):
        recipe = json.loads((ROOT / 'figures' / f'figure{number:02d}.json').read_text())
        for panel in recipe.get('panels', []):
            if 'crop_pixels' in panel:
                top, bottom, left, right = panel['crop_pixels']
                width, height = panel['source_pixels']
                assert 0 <= top < bottom <= height
                assert 0 <= left < right <= width


def test_all_recorded_figures(tmp_path):
    output = tmp_path / 'figures'
    reports = reproduce(ROOT, range(1, 14), output, dpi=50)
    assert len(reports) == 13
    for number in range(1, 14):
        directory = output / f'figure{number:02d}'
        assert (directory / f'figure{number:02d}.png').stat().st_size > 1000
        assert (directory / f'figure{number:02d}.pdf').read_bytes().startswith(b'%PDF')
        assert json.loads((directory / 'recipe.json').read_text())['number'] == number
        assert (directory / 'provenance.json').is_file()
    six, seven, twelve = reports[5]['fits'], reports[6]['fits'], reports[11]['fits']
    assert six['all']['power'] == pytest.approx(1.2700144998)
    assert six['all']['intercept'] == pytest.approx(1.7479869617)
    assert seven['n_mod_3_equals_2']['power'] == pytest.approx(1.2134466411)
    assert seven['other_residues']['power'] == pytest.approx(1.0229250031)
    assert twelve['all']['power'] == pytest.approx(1.1562846778)
    assert reports[1]['observations'] == 43
    with pytest.raises(FileExistsError):
        reproduce(ROOT, [3], output, dpi=50)


@pytest.mark.parametrize('first', ['north', 'east'])
def test_shared_snapshot_simulation(tmp_path, first):
    states, panels = {}, []
    tile = '133131313'
    # The two initial phases give distinct trajectories for this tile.
    for time, grid in states_at(periodic(parse_tile(tile), 6), [1, 2, 5], first):
        name = f't{time}'
        path = tmp_path / f'{name}.npz'
        np.savez_compressed(path, grid=grid)
        states[name] = {'path': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                        'n': 6, 'time': time, 'tile': tile, 'first_update': first}
        panels.append({'state': name})
    actual = _simulate_states(tmp_path, [{'kind': 'states', 'panels': panels}], states)
    assert set(actual) == {'t1', 't2', 't5'}
    other = dict(states)
    other['t2'] = dict(states['t2'], first_update='east' if first == 'north' else 'north')
    with pytest.raises(ValueError, match='differs from recorded state'):
        _simulate_states(tmp_path, [{'kind': 'states', 'panels': panels}], other)


def test_analytical_figure_simulation(tmp_path):
    reports = reproduce(ROOT, [3], tmp_path / 'analytical', mode='simulate', dpi=50)
    assert reports[0]['states_match_recorded']


def test_scaling_simulation_and_random_provenance(tmp_path):
    root = tmp_path / 'companion'
    (root / 'figures').mkdir(parents=True)
    (root / 'data/figures').mkdir(parents=True)
    (root / 'data/figures/states.json').write_text('{}\n')
    (root / 'periodic.csv').write_text('3,14\n6,38\n9,62\n')
    recipe = {'number': 6, 'title': 'Small periodic sweep', 'kind': 'scaling',
              'data': 'periodic.csv', 'scale': 'log', 'simulation_kind': 'periodic',
              'tile': '113133313', 'first_update': 'east',
              'fit_groups': [{'name': 'all', 'selection': 'all'}]}
    (root / 'figures/figure06.json').write_text(json.dumps(recipe))
    report = reproduce(root, [6], tmp_path / 'periodic-replay', mode='simulate', dpi=50)
    assert report[0]['observations'] == 3
    (root / 'periodic.csv').write_text('3,999\n6,38\n9,62\n')
    with pytest.raises(ValueError, match='differ from recorded measurements'):
        reproduce(root, [6], tmp_path / 'mismatch', mode='simulate', dpi=50)
    recipe.update(number=12, title='Small random sweep', simulation_kind='random')
    (root / 'figures/figure12.json').write_text(json.dumps(recipe))
    for run in ['random-a', 'random-b']:
        report = reproduce(root, [12], tmp_path / run, mode='simulate', dpi=50, seed=9)
        assert report[0]['sample_provenance'] == 'new seeded samples'
    a = tmp_path / 'random-a/figure12/measurements.csv'
    b = tmp_path / 'random-b/figure12/measurements.csv'
    assert a.read_bytes() == b.read_bytes()
