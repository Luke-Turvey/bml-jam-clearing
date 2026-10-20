"""Configuration-driven, deterministic experiments and historical CSV checks."""
import csv
import hashlib
import json
import platform
from pathlib import Path
import numpy as np
from .initial import parse_tile, periodic, random_grid
from .model import clearing_time


def read_csv(path):
    """Read historical headerless n,T CSVs, allowing blank lines."""
    with open(path, newline='') as stream:
        return [(int(row[0]), int(row[1])) for row in csv.reader(stream) if row and any(row)]


def run(config_path, output):
    config_path, output = Path(config_path), Path(output)
    config = json.loads(config_path.read_text())
    if config.get('first_update', 'north') != 'north':
        raise ValueError('simulations must start with a North update')
    # Each directory contains a single experiment configuration.
    output.mkdir(parents=True, exist_ok=False)
    (output / 'config.json').write_text(json.dumps(config, indent=2) + '\n')
    metadata = {
        'python': platform.python_version(), 'numpy': np.__version__,
        'config_sha256': hashlib.sha256(config_path.read_bytes()).hexdigest(),
        'encoding': {'empty': 0, 'east': 1, 'north': 3},
        'first_update': 'north', 'boundary': 'open',
        'random_stream': 'SeedSequence([seed, n, replicate]), default_rng',
    }
    (output / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    for experiment in config['experiments']:
        name = experiment['name']
        if not name or Path(name).name != name or name in {'.', '..'}:
            raise ValueError('experiment names must be plain filenames')
        sizes = experiment.get('sizes')
        if sizes is None:
            sizes = range(*experiment['range'])
        with (output / f'{name}.csv').open('x', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(['n', 'clearing_time', 'replicate'])
            for n in sizes:
                for replicate in range(experiment.get('replicates', 1)):
                    if experiment['kind'] == 'random':
                        seed = np.random.SeedSequence([config.get('seed', 0), n, replicate])
                        grid = random_grid(n, seed, experiment.get('density', 1.0))
                    elif experiment['kind'] == 'periodic':
                        grid = periodic(parse_tile(experiment['tile']), n)
                    else:
                        raise ValueError('kind must be random or periodic')
                    time = clearing_time(grid, config.get('max_steps'))
                    writer.writerow([n, time, replicate])
                    stream.flush()
                    print(f'{name}: n={n}, replicate={replicate}, T={time}', flush=True)
    return output


def verify_reference(data, max_n=30):
    """Audit historical data using North-first runs and directional duality."""
    data = Path(data)
    sources = [(data / 'periodic_113133313.csv', '113133313'),
               (data / 'g_periodic_133333113.csv', '133333113')]
    sources += [(p, p.stem) for p in sorted((data / 'periodic_csv_full').glob('*.csv'))]
    checked, unresolved, conventions = 0, [], {}
    for path, tile in sources:
        counts = {'north': 0, 'east': 0, 'both': 0, 'neither': 0}
        for n, expected in sorted(set(read_csv(path))):
            if n > max_n:
                continue
            grid = periodic(parse_tile(tile), n)
            north = clearing_time(grid)
            dual = grid.T[::-1, ::-1]
            dual = np.where(dual == 1, 3, np.where(dual == 3, 1, 0))
            east = clearing_time(dual)
            checked += 1
            key = 'both' if north == east == expected else 'north' if north == expected else 'east' if east == expected else 'neither'
            counts[key] += 1
            if key == 'neither':
                unresolved.append({'file': str(path), 'n': n, 'expected': expected, 'north': north, 'east': east})
        conventions[str(path.relative_to(data))] = counts
    return {'checked': checked, 'max_n': max_n, 'conventions': conventions, 'mismatches': unresolved}
