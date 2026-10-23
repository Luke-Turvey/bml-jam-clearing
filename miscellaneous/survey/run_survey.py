"""Validate and run the fully occupied 3-by-3 tile survey.

Compile bitset_survey.cpp first; completed measurements are retained per tile.
"""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import hashlib
import itertools
import json
from pathlib import Path
import platform
import subprocess
import time


ROOT = Path(__file__).resolve().parents[2]
TILES = [''.join(tile) for tile in itertools.product('13', repeat=9)]
SIZES = list(range(3, 499, 3))


def literal_time(tile, n):
    """Independent site-by-site reference; masks and vector operations are absent."""
    grid = [[int(tile[((row + (3 - n % 3) % 3) % 3) * 3 + col % 3])
             for col in range(n)] for row in range(n)]
    remaining = n*n
    for step in range(1, 2*n*n*n + 3):
        result = [row[:] for row in grid]
        car = 3 if step % 2 else 1
        for row in range(n):
            for col in range(n):
                if grid[row][col] != car:
                    continue
                rr, cc = (row-1, col) if car == 3 else (row, col+1)
                if rr < 0 or cc >= n:
                    result[row][col] = 0
                    remaining -= 1
                elif grid[rr][cc] == 0:
                    result[row][col] = 0
                    result[rr][cc] = car
        grid = result
        if not remaining:
            return step
    raise RuntimeError('independent cubic budget exceeded')


def backend(binary, tile, sizes):
    completed = subprocess.run([str(binary), tile, *map(str, sizes)],
                               check=True, text=True, capture_output=True)
    return [(name, int(n), int(t)) for name, n, t in csv.reader(completed.stdout.splitlines())]


def validate(binary, output):
    started = time.perf_counter()
    # Exhaust all 512 occupied binary 3-by-3 states, independently of NumPy.
    checked = []
    for tile in TILES:
        observed = backend(binary, tile, [3])[0][2]
        expected = literal_time(tile, 3)
        if observed != expected:
            raise AssertionError((tile, 3, observed, expected))
        checked.append((tile, 3, observed))
    # Sizes straddling word boundaries and partial tiles exercise carries,
    # padded bits, exits and the bottom-left phase.
    for tile in ['111111111', '333333333', '131313131',
                 '113133313', '133333113', '133131313']:
        for n in [1, 2, 4, 6, 7, 63, 64, 65, 66, 127, 128, 129]:
            observed = backend(binary, tile, [n])[0][2]
            if n <= 7:
                expected = literal_time(tile, n)
            else:
                # Maintained NumPy backend has its own independent literal-rule
                # tests; these cases exercise the 64-bit backend at larger n.
                from bml.initial import periodic, parse_tile
                from bml.model import clearing_time
                expected = clearing_time(periodic(parse_tile(tile), n), max_steps=2*n**3+2)
            if observed != expected:
                raise AssertionError((tile, n, observed, expected))
            checked.append((tile, n, observed))
    # Directly compare representative current Figure 6 measurements.
    with (ROOT/'data/clearing_times/north_first/figure06.csv').open() as stream:
        current = dict((int(n), int(t)) for n, t in csv.reader(stream))
    for n in [3, 66, 138, 285, 498]:
        observed = backend(binary, '113133313', [n])[0][2]
        if observed != current[n]:
            raise AssertionError(('Figure 6', n, observed, current[n]))
        checked.append(('113133313', n, observed))
    report = {
        'checks': len(checked), 'exhaustive_binary_3x3': 512,
        'larger_and_phase_cases': 72, 'current_figure06_cases': 5,
        'rule': 'simultaneous North updates at odd times; open top/right boundaries',
        'elapsed_seconds': time.perf_counter()-started,
        'cases': [{'tile': t, 'n': n, 'clearing_time': v} for t,n,v in checked],
    }
    (output/'validation.json').write_text(json.dumps(report, indent=2)+'\n')
    return report


def run_tile(binary, output, tile):
    path = output/f'{tile}.csv'
    existing = {}
    if path.exists():
        with path.open() as stream:
            for row in csv.DictReader(stream):
                n, value = int(row['n']), int(row['clearing_time'])
                if n not in SIZES or n in existing or value < 1:
                    raise ValueError(f'invalid checkpoint: {path}')
                existing[n] = value
    todo = [n for n in SIZES if n not in existing]
    if not todo:
        return tile, 0
    needs_header = not path.exists() or path.stat().st_size == 0
    command = [str(binary), tile, *map(str, todo)]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    with path.open('a', newline='') as stream:
        writer = csv.writer(stream)
        if needs_header:
            writer.writerow(['n', 'clearing_time'])
            stream.flush()
        for row in csv.reader(process.stdout):
            name, n, value = row[0], int(row[1]), int(row[2])
            if name != tile or n not in todo or n in existing or value < 1:
                process.kill()
                raise ValueError(f'invalid backend result: {row}')
            writer.writerow([n, value])
            stream.flush()
            existing[n] = value
    error = process.stderr.read()
    if process.wait():
        raise RuntimeError(f'{tile}: {error}')
    if set(existing) != set(SIZES):
        raise ValueError(f'incomplete backend output: {tile}')
    # Canonical ordering also handles any interrupted and resumed tile.
    temporary = path.with_suffix('.csv.tmp')
    with temporary.open('w', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['n', 'clearing_time'])
        writer.writerows(sorted(existing.items()))
    temporary.replace(path)
    return tile, len(todo)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--binary', type=Path, default=Path('/tmp/bml-bitset-survey'))
    parser.add_argument('--output', type=Path, default=ROOT/'data/clearing_times/survey_north_first')
    parser.add_argument('--workers', type=int, default=6)
    parser.add_argument('--validate-only', action='store_true')
    args = parser.parse_args()
    if not 1 <= args.workers <= 6:
        parser.error('workers must be between 1 and 6')
    args.output.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    validation = validate(args.binary, args.output)
    print(f'Validation passed: {validation["checks"]} comparisons in {validation["elapsed_seconds"]:.2f}s', flush=True)
    if args.validate_only:
        return
    metadata = {
        'first_update': 'north', 'boundary': 'open', 'time_unit': 'one directional update',
        'tile_anchor': 'bottom-left', 'encoding': {'east': 1, 'north': 3},
        'tiles': TILES, 'sizes': SIZES, 'planned_observations': len(TILES)*len(SIZES),
        'backend': 'C++17 64-bit row masks; bitset_survey.cpp',
        'source_sha256': hashlib.sha256((Path(__file__).parent/'bitset_survey.cpp').read_bytes()).hexdigest(),
        'binary_sha256': hashlib.sha256(args.binary.read_bytes()).hexdigest(),
        'compiler': subprocess.run(['g++', '--version'], text=True, capture_output=True, check=True).stdout.splitlines()[0],
        'compile_flags': '-O3 -std=c++17 -Wall -Wextra -pedantic',
        'python': platform.python_version(), 'platform': platform.platform(),
        'workers': args.workers, 'independent_step_budget': '2*n**3+2',
        'validation_checks': validation['checks'], 'status': 'running',
    }
    (args.output/'metadata.json').write_text(json.dumps(metadata, indent=2)+'\n')
    total_new = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(run_tile, args.binary, args.output, tile) for tile in TILES]
        for count, future in enumerate(as_completed(futures), 1):
            tile, new = future.result()
            total_new += new
            if count % 16 == 0 or count == len(TILES):
                print(f'{count}/{len(TILES)} tiles complete; new observations={total_new}; elapsed={time.perf_counter()-started:.1f}s; last={tile}', flush=True)
    metadata.update(status='complete', actual_observations=len(TILES)*len(SIZES),
                    elapsed_seconds=time.perf_counter()-started)
    metadata['csv_sha256'] = {f'{t}.csv': hashlib.sha256((args.output/f'{t}.csv').read_bytes()).hexdigest() for t in TILES}
    (args.output/'metadata.json').write_text(json.dumps(metadata, indent=2)+'\n')


if __name__ == '__main__':
    main()
