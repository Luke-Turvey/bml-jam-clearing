"""Generate the numerical figure records with North updates at odd times."""
import csv
import hashlib
import json
import platform
from collections import defaultdict
from pathlib import Path
import numpy as np
from .analytical import linear_state
from .experiments import read_csv
from .initial import periodic, parse_tile, random_grid
from .model import clearing_time, states_at


def _write_json(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    temporary.replace(path)


def refresh_data(root='.', max_n=999, seed=2026, update_states=True):
    if max_n < 3 or seed < 0:
        raise ValueError('max-n must be at least 3 and seed must be nonnegative')
    root = Path(root)
    ledger_path = root / 'data/figure_states/states.json'
    states = json.loads(ledger_path.read_text())
    if update_states:
        groups = defaultdict(list)
        for key, entry in states.items():
            if key == 'random_initial':
                continue
            if entry.get('engine') == 'analytical':
                _store_state(root, key, entry, linear_state(entry['n'], entry['time']))
            else:
                groups[(entry['tile'], entry['n'], entry.get('initial_state'))].append(key)
        for (tile, n, initial_key), members in groups.items():
            if initial_key:
                with np.load(root / states[initial_key]['path'], allow_pickle=False) as archive:
                    initial = archive['grid'].copy()
            else:
                initial = periodic(parse_tile(tile), n)
            times = {states[k]['time'] for k in members}
            print(f'North-first snapshots: n={n}, times={sorted(times)}', flush=True)
            for time, grid in states_at(initial, times):
                for key in members:
                    if states[key]['time'] == time:
                        _store_state(root, key, states[key], grid)
        states['random_initial']['first_update'] = 'north'
        if 'first_step_sha256' in states['random_initial']:
            states['random_initial']['reconstruction_step_sha256'] = states['random_initial'].pop('first_step_sha256')
        _write_json(ledger_path, states)
    directory = root / 'data/clearing_times/north_first'
    directory.mkdir(parents=True, exist_ok=True)
    checkpoint_path = directory / 'checkpoints.json'
    checkpoints = json.loads(checkpoint_path.read_text()) if checkpoint_path.exists() else {}
    for number in [6, 12]:
        recipe = json.loads((root / f'figures/recipes/figure{number:02d}.json').read_text())
        source = root / recipe['size_source']
        rows = read_csv(source)
        identity = f'{number}:{seed if number == 12 else "periodic"}'
        cache = checkpoints.setdefault(identity, {})
        counts, results, source_rows = defaultdict(int), [], []
        for row, (n, _) in enumerate(rows):
            replicate = counts[n]
            counts[n] += 1
            if n > max_n:
                continue
            key = str(row)
            if key not in cache:
                if number == 6:
                    grid = periodic(parse_tile(recipe['tile']), n)
                else:
                    grid = random_grid(n, np.random.SeedSequence([seed, n, replicate]))
                time = clearing_time(grid)
                cache[key] = {'n': n, 'replicate': replicate, 'time': time}
                _write_json(checkpoint_path, checkpoints)
                print(f'North-first figure {number}: n={n}, replicate={replicate}, T={time}', flush=True)
            result = cache[key]
            if (result['n'], result['replicate']) != (n, replicate):
                raise ValueError('size-source rows changed; use a new checkpoints file')
            results.append((n, result['time']))
            source_rows.append(row)
        output = root / recipe['data']
        temporary = output.with_suffix('.csv.tmp')
        with temporary.open('w', newline='') as stream:
            csv.writer(stream).writerows(results)
        temporary.replace(output)
        _write_json(output.with_suffix('.json'), {
            'first_update': 'north', 'max_n': max(n for n, _ in results),
            'size_source': recipe['size_source'], 'source_rows': source_rows,
            'seed': seed if number == 12 else None,
            'random_stream': 'default_rng(SeedSequence([seed, n, replicate]))' if number == 12 else None,
            'numpy': np.__version__, 'python': platform.python_version(),
            'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
        })


def _store_state(root, key, entry, grid):
    path = root / entry['path']
    with path.with_suffix('.tmp').open('wb') as stream:
        np.savez_compressed(stream, grid=grid.astype(np.uint8))
    path.with_suffix('.tmp').replace(path)
    entry['first_update'] = 'north'
    entry['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    entry['state_sha256'] = hashlib.sha256(grid.astype(np.uint8).tobytes()).hexdigest()
    entry['source_kind'] = 'North-first explicit evolution' if entry.get('engine') else 'North-first simulation'
    for field in ['source_image', 'source_image_sha256', 'source_state']:
        entry.pop(field, None)
