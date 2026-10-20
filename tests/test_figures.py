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
    states = json.loads((ROOT / 'data/figure_states/states.json').read_text())
    for entry in states.values():
        grid = _load_state(ROOT, entry)
        assert hashlib.sha256(grid.tobytes()).hexdigest() == entry['state_sha256']
        assert entry['first_update'] == 'north'
    initial = _load_state(ROOT, states['random_initial'])
    first = step(initial, 2)
    assert hashlib.sha256(first.tobytes()).hexdigest() == states['random_initial']['reconstruction_step_sha256']
    assert np.all(initial != 0)
    for number in range(1, 14):
        recipe = json.loads((ROOT / 'figures/recipes' / f'figure{number:02d}.json').read_text())
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
    assert 1 < six['all']['power'] < 2
    assert reports[5]['first_update'] == 'north'
    assert seven['n_mod_3_equals_2']['power'] == pytest.approx(1.2134466411)
    assert seven['other_residues']['power'] == pytest.approx(1.0229250031)
    assert 1 < twelve['all']['power'] < 2
    assert reports[1]['observations'] == 43
    with pytest.raises(FileExistsError):
        reproduce(ROOT, [3], output, dpi=50)


@pytest.mark.parametrize('first', ['north'])
def test_shared_snapshot_simulation(tmp_path, first):
    states, panels = {}, []
    tile = '133131313'
    # Several selected times are collected from the same simulation.
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
    with pytest.raises(ValueError, match='North'):
        _simulate_states(tmp_path, [{'kind': 'states', 'panels': panels}], other)


def test_analytical_figure_simulation(tmp_path):
    reports = reproduce(ROOT, [3], tmp_path / 'analytical', mode='simulate', dpi=50)
    assert reports[0]['states_match_recorded']


def test_scaling_simulation_and_random_provenance(tmp_path):
    root = tmp_path / 'companion'
    (root / 'figures/recipes').mkdir(parents=True)
    (root / 'data/figure_states').mkdir(parents=True)
    (root / 'data/figure_states/states.json').write_text('{}\n')
    (root / 'periodic.csv').write_text('3,13\n6,37\n9,61\n')
    recipe = {'number': 6, 'title': 'Small periodic sweep', 'kind': 'scaling',
              'data': 'periodic.csv', 'scale': 'log', 'simulation_kind': 'periodic',
              'tile': '113133313', 'first_update': 'north',
              'fit_groups': [{'name': 'all', 'selection': 'all'}]}
    (root / 'figures/recipes/figure06.json').write_text(json.dumps(recipe))
    report = reproduce(root, [6], tmp_path / 'periodic-replay', mode='simulate', dpi=50)
    assert report[0]['observations'] == 3
    (root / 'periodic.csv').write_text('3,999\n6,38\n9,62\n')
    with pytest.raises(ValueError, match='differ from recorded measurements'):
        reproduce(root, [6], tmp_path / 'mismatch', mode='simulate', dpi=50)
    recipe.update(number=12, title='Small random sweep', simulation_kind='random')
    (root / 'figures/recipes/figure12.json').write_text(json.dumps(recipe))
    for run in ['random-a', 'random-b']:
        report = reproduce(root, [12], tmp_path / run, mode='simulate', dpi=50, seed=9)
        assert report[0]['sample_provenance'] == 'North-first seeded samples'
    a = tmp_path / 'random-a/figure12/measurements.csv'
    b = tmp_path / 'random-b/figure12/measurements.csv'
    assert a.read_bytes() == b.read_bytes()


def test_paper_uses_numbered_outputs():
    import re
    manuscript = (ROOT / 'latex/main.tex').read_text()
    images = re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', manuscript)
    assert images == [f'../figures/paper/figure{n:02d}.pdf' for n in range(1, 14)]
    assert r'\input{../figures/paper/figure_statistics.tex}' in manuscript
    assert (ROOT / 'latex/preamble.sty').is_file()
    assert (ROOT / 'latex/refs.bib').is_file()
    assert (ROOT / 'latex/sections/appendix.tex').is_file()


def test_refresh_data_is_north_first_and_resumable(tmp_path):
    from bml.north_data import refresh_data
    root = tmp_path / 'companion'
    (root / 'figures/recipes').mkdir(parents=True)
    (root / 'data/figure_states').mkdir(parents=True)
    (root / 'data/figure_states/states.json').write_text('{}')
    (root / 'sizes.csv').write_text('3,999\n6,999\n3,888\n')
    for number in [6, 12]:
        recipe = {'data': f'data/clearing_times/north_first/figure{number:02d}.csv', 'size_source': 'sizes.csv',
                  'tile': '113133313', 'first_update': 'north'}
        (root / f'figures/recipes/figure{number:02d}.json').write_text(json.dumps(recipe))
    refresh_data(root, max_n=3, update_states=False)
    first = (root / 'data/clearing_times/north_first/figure06.csv').read_text()
    assert first.splitlines() == ['3,13', '3,13']
    refresh_data(root, max_n=6, update_states=False)
    full = (root / 'data/clearing_times/north_first/figure06.csv').read_text()
    assert full.splitlines() == ['3,13', '6,37', '3,13']
    refresh_data(root, max_n=6, update_states=False)
    assert (root / 'data/clearing_times/north_first/figure06.csv').read_text() == full
    for number in [6, 12]:
        metadata = json.loads((root / f'data/clearing_times/north_first/figure{number:02d}.json').read_text())
        assert metadata['first_update'] == 'north'
        assert metadata['source_rows'] == [0, 1, 2]


def test_repository_layout_and_input_paths():
    expected = {'miscellaneous', 'figures', 'tests', 'src', 'latex', 'data'}
    visible = {p.name for p in ROOT.iterdir() if p.is_dir() and not p.name.startswith('.')}
    assert expected <= visible
    assert not visible.intersection({'archive', 'configs', 'docs', 'paper', 'results', 'local_artifacts'})
    for path in (ROOT / 'figures/recipes').glob('figure*.json'):
        recipe = json.loads(path.read_text())
        for key in ['data', 'size_source']:
            if key in recipe:
                assert (ROOT / recipe[key]).is_file()
                assert recipe[key].startswith('data/')
    ledger = json.loads((ROOT / 'data/figure_states/states.json').read_text())
    for entry in ledger.values():
        assert entry['path'].startswith('data/figure_states/matrices/')
        assert (ROOT / entry['path']).is_file()


def test_paper_provenance_matches_recipes():
    from bml.experiments import read_csv
    for number in [6, 7, 12]:
        path = ROOT / f'data/provenance/figure{number:02d}-fit.json'
        summary = json.loads(path.read_text())
        recipe = json.loads((ROOT / summary['recipe']).read_text())
        selected = read_csv(ROOT / recipe['data'])[recipe.get('skip_rows', 0):]
        assert summary['first_update'] == 'north'
        assert summary['observations'] == len(selected)
        assert sum(fit['observations'] for fit in summary['fits'].values()) == len(selected)
