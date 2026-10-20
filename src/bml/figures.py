"""Reproduce the numbered figures from recorded data or simulations."""
import csv
import hashlib
import json
import platform
from collections import defaultdict
from pathlib import Path
import numpy as np
from .analytical import linear_state
from .experiments import read_csv
from .figure_rendering import save_states, save_scaling
from .initial import periodic, parse_tile, random_grid
from .model import states_at, clearing_time


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _load_state(root, entry):
    path = root / entry['path']
    if _sha(path) != entry['sha256']:
        raise ValueError(f'state integrity check failed: {path}')
    with np.load(path, allow_pickle=False) as archive:
        grid = archive['grid'].copy()
    if grid.shape != (entry['n'], entry['n']) or not np.isin(grid, [0, 1, 3]).all():
        raise ValueError(f'invalid grid state: {path}')
    return grid


def load_recipes(root, numbers):
    root = Path(root)
    recipes = []
    for number in sorted(set(numbers)):
        if number not in range(1, 14):
            raise ValueError('figure numbers must lie between 1 and 13')
        path = root / 'figures/recipes' / f'figure{number:02d}.json'
        recipe = json.loads(path.read_text())
        if recipe['number'] != number:
            raise ValueError(f'figure number does not match {path}')
        if recipe.get('first_update', 'north') != 'north':
            raise ValueError('figure recipes must use North-first updates')
        recipes.append(recipe)
    return recipes


def plan(root, numbers, mode='recorded'):
    """Describe a figure build without generating images or simulating grids."""
    root = Path(root)
    states = json.loads((root / 'data/figure_states/states.json').read_text())
    planned = []
    for recipe in load_recipes(root, numbers):
        entry = {'figure': recipe['number'], 'title': recipe['title'], 'kind': recipe['kind']}
        if recipe['kind'] == 'states':
            entry['panels'] = [dict(states[p['state']], crop_pixels=p.get('crop_pixels'))
                               for p in recipe['panels']]
            for panel in entry['panels']:
                if panel['first_update'] != 'north':
                    raise ValueError('panel data must use North-first updates; run bml refresh-data')
                if not (root / panel['path']).is_file():
                    raise FileNotFoundError(panel['path'])
        else:
            rows = read_csv(root / recipe['data'])[recipe.get('skip_rows', 0):]
            if len(rows) < 2:
                raise ValueError('scaling figures require at least two observations')
            entry.update(data=recipe['data'], observations=len(rows), max_n=max(n for n, _ in rows),
                         first_update=recipe['first_update'])
            if recipe['simulation_kind'] == 'random':
                entry['samples'] = 'North-first seeded samples'
        planned.append(entry)
    return {'mode': mode, 'figures': planned}


def _simulate_states(root, recipes, states):
    keys = {p['state'] for recipe in recipes if recipe['kind'] == 'states' for p in recipe['panels']}
    groups = defaultdict(list)
    generated = {}
    for key in sorted(keys):
        entry = states[key]
        if entry['first_update'] != 'north':
            raise ValueError('panel data must use North-first updates')
        if entry.get('engine') == 'analytical':
            generated[key] = linear_state(entry['n'], entry['time'])
        else:
            groups[(entry['tile'], entry['n'], entry['first_update'], entry.get('initial_state'))].append(key)
    for (tile, n, first, initial_key), members in groups.items():
        grid = _load_state(root, states[initial_key]) if initial_key else periodic(parse_tile(tile), n)
        times = {states[k]['time'] for k in members}
        print(f'snapshot simulation: n={n}, times={sorted(times)}, first={first}', flush=True)
        for time, grid_at_time in states_at(grid, times, first):
            for key in members:
                if states[key]['time'] == time:
                    generated[key] = grid_at_time
    for key, grid in generated.items():
        reference = _load_state(root, states[key])
        if not np.array_equal(grid, reference):
            count = int(np.count_nonzero(grid != reference))
            raise ValueError(f'{key}: simulation differs from recorded state at {count} sites')
    return generated


def _measurements(root, recipe, mode, seed):
    path = root / recipe['data']
    if path.parent.name == 'north_first':
        metadata = json.loads(path.with_suffix('.json').read_text())
        if metadata['first_update'] != 'north' or metadata['sha256'] != _sha(path):
            raise ValueError('North-first measurement integrity check failed')
    rows = read_csv(path)
    indexed = list(enumerate(rows))[recipe.get('skip_rows', 0):]
    if mode == 'recorded':
        return [(n, time) for _, (n, time) in indexed]
    deterministic, replicate_counts = {}, defaultdict(int)
    result = []
    for row_index, (n, _) in indexed:
        if recipe['simulation_kind'] == 'periodic':
            if n not in deterministic:
                grid = periodic(parse_tile(recipe['tile']), n)
                deterministic[n] = clearing_time(grid, first_update=recipe['first_update'])
            time = deterministic[n]
        else:
            replicate = replicate_counts[n]
            replicate_counts[n] += 1
            grid = random_grid(n, np.random.SeedSequence([seed, n, replicate]))
            time = clearing_time(grid, first_update=recipe['first_update'])
        print(f'figure {recipe["number"]}: row={row_index}, n={n}, T={time}', flush=True)
        result.append((n, time))
    if recipe['simulation_kind'] == 'periodic':
        expected = [(n, time) for _, (n, time) in indexed]
        if result != expected:
            raise ValueError(f'figure {recipe["number"]}: clearing times differ from recorded measurements')
    return result


def reproduce(root, numbers, output, mode='recorded', dpi=300, seed=2026, update=False):
    """Build complete figures and numerical sidecars into a new output directory."""
    if mode not in {'recorded', 'simulate'}:
        raise ValueError('mode must be recorded or simulate')
    if not isinstance(dpi, int) or dpi < 50:
        raise ValueError('dpi must be an integer of at least 50')
    root, output = Path(root), Path(output)
    recipes = load_recipes(root, numbers)
    if not recipes:
        raise ValueError('select at least one figure')
    plan(root, numbers, mode)
    states = json.loads((root / 'data/figure_states/states.json').read_text())
    output.mkdir(parents=True, exist_ok=update)
    generated = _simulate_states(root, recipes, states) if mode == 'simulate' else {}
    reports = []
    for recipe in recipes:
        number = recipe['number']
        directory = output / f'figure{number:02d}'
        directory.mkdir(exist_ok=update)
        stem = directory / f'figure{number:02d}'
        report = {'figure': number, 'title': recipe['title'], 'mode': mode,
                  'python': platform.python_version(), 'numpy': np.__version__,
                  'recipe_sha256': _sha(root / 'figures/recipes' / f'figure{number:02d}.json'),
                  'first_update': 'north'}
        if recipe['kind'] == 'states':
            panels = []
            for i, panel in enumerate(recipe['panels']):
                key = panel['state']
                grid = generated[key] if mode == 'simulate' else _load_state(root, states[key])
                panels.append((panel, grid))
                np.savez_compressed(directory / f'panel{i+1:02d}.npz', grid=grid)
            save_states(recipe, panels, stem, dpi)
            report['panels'] = [dict(states[p['state']], crop_pixels=p.get('crop_pixels')) for p in recipe['panels']]
            report['states_match_recorded'] = True
        else:
            rows = _measurements(root, recipe, mode, seed)
            with (directory / 'measurements.csv').open('w', newline='') as stream:
                writer = csv.writer(stream)
                writer.writerow(['n', 'clearing_time'])
                writer.writerows(rows)
            report['fits'] = save_scaling(recipe, rows, stem, dpi)
            report['data_sha256'] = _sha(root / recipe['data'])
            report['observations'] = len(rows)
            data_metadata = (root / recipe['data']).with_suffix('.json')
            if data_metadata.is_file():
                report['measurement_provenance'] = json.loads(data_metadata.read_text())
            if mode == 'simulate' and recipe['simulation_kind'] == 'random':
                report['random_stream'] = f'default_rng(SeedSequence([{seed}, n, replicate]))'
                report['sample_provenance'] = 'North-first seeded samples'
            else:
                report['sample_provenance'] = 'North-first measurements'
        (directory / 'recipe.json').write_text(json.dumps(recipe, indent=2) + '\n')
        (directory / 'provenance.json').write_text(json.dumps(report, indent=2) + '\n')
        print(f'figure {number}: {stem}.png and .pdf', flush=True)
        reports.append(report)
    all_reports = [json.loads(p.read_text()) for p in sorted(output.glob('figure*/provenance.json'))]
    (output / 'index.json').write_text(json.dumps(all_reports, indent=2) + '\n')
    _write_statistics(output, all_reports)
    if output.resolve() == (root / 'figures/outputs').resolve():
        provenance = root / 'data/provenance'
        provenance.mkdir(parents=True, exist_ok=True)
        for report in all_reports:
            number = report['figure']
            if number not in {6, 7, 12}:
                continue
            summary = {
                'recipe': f'figures/recipes/figure{number:02d}.json',
                'first_update': 'north',
                'observations': report['observations'],
                'fits': report['fits'],
            }
            (provenance / f'figure{number:02d}-fit.json').write_text(
                json.dumps(summary, indent=2) + '\n'
            )
    return reports


def _write_statistics(output, reports):
    words = {2: 'Two', 6: 'Six', 7: 'Seven', 12: 'Twelve'}
    lines = ['% Numerical summaries for the generated paper figures.']
    for report in reports:
        n = report['figure']
        if n not in words:
            continue
        rows = read_csv_with_header(output / f'figure{n:02d}' / 'measurements.csv')
        prefix = 'Figure' + words[n]
        lines.append('\\newcommand{\\' + prefix + 'MaxN}{' + str(max(x for x, _ in rows)) + '}')
        lines.append('\\newcommand{\\' + prefix + 'Count}{' + str(len(rows)) + '}')
        for group, fit in report['fits'].items():
            suffix = {'all': '', 'n_mod_3_equals_2': 'Superlinear', 'other_residues': 'Other'}[group]
            for key in ['power', 'intercept', 'coefficient']:
                value = f"{fit[key]:.3f}"
                lines.append('\\newcommand{\\' + prefix + suffix + key.capitalize() + '}{' + value + '}')
    (output / 'figure_statistics.tex').write_text('\n'.join(lines) + '\n')


def read_csv_with_header(path):
    with path.open(newline='') as stream:
        rows = csv.reader(stream)
        next(rows)
        return [(int(r[0]), int(r[1])) for r in rows]
