"""Import the numerical states associated with the paper's original figure files.

Usage: python scripts/import_figure_states.py --images PATH --snapshots PATH
The image directory contains the PNGs referenced by the paper's LaTeX source.
The snapshot directory contains random_1100/ and 133131313_999/.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image


SPECIFICATIONS = [
    ('figure01_n600', '133333113_600.png', 600, 3000, '133333113', 'north', None),
    ('figure01_n599', '133333113_599.png', 599, 2995, '133333113', 'north', None),
    ('figure03_t150', '1133_regions_150.png', 50, 150, '1313', 'north', None),
    ('figure03_t220', '1133_regions_220.png', 50, 220, '1313', 'north', None),
    ('figure04', '333131313.png', 498, 996, '333131313', 'east', None),
    ('fault_lines', '1111111311331333_1000.png', 1000, 5000, '1111111311331333', 'east', None),
    *[(f'reorganisation_t{t}', f'133131313_999_{t}.png', 999, t, '133131313', 'east',
       f'133131313_999/mat_{t}.npy') for t in [2000, 4000, 6000, 8000]],
    ('random_t6500', 'random_1100.png', 1100, 6500, None, 'east', 'random_1100/mat_6500.npy'),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decode(path, n):
    """Read cell centres from a borderless, lossless white/red/blue grid raster."""
    image = Image.open(path).convert('RGB')
    pixels = np.asarray(image)
    y = ((np.arange(n)+.5)*image.height/n).astype(int)
    x = ((np.arange(n)+.5)*image.width/n).astype(int)
    cells = pixels[y[:, None], x]
    white = np.all(cells == [255, 255, 255], axis=-1)
    east = np.all(cells == [255, 0, 0], axis=-1)
    north = np.all(cells == [0, 0, 255], axis=-1)
    if not np.all(white | east | north):
        raise ValueError(f'{path}: cell centres contain colours outside the model palette')
    return (east + 3*north).astype(np.uint8), list(image.size)


def import_states(images, snapshots, output):
    output.mkdir(parents=True, exist_ok=True)
    state_directory = output / 'states'
    state_directory.mkdir(exist_ok=True)
    entries = {}
    for key, image, n, time, tile, first, source_state in SPECIFICATIONS:
        source = images / image
        grid, pixels = decode(source, n)
        if source_state and not np.array_equal(grid, np.load(snapshots / source_state, allow_pickle=False)):
            raise ValueError(f'{image}: numerical snapshot disagrees with source image')
        path = state_directory / f'{key}.npz'
        np.savez_compressed(path, grid=grid)
        entries[key] = {
            'path': f'data/figures/states/{key}.npz', 'n': n, 'time': time,
            'tile': tile, 'first_update': first, 'sha256': sha(path),
            'state_sha256': hashlib.sha256(grid.tobytes()).hexdigest(),
            'source_image': image, 'source_image_sha256': sha(source),
            'source_pixels': pixels,
            'source_kind': 'numerical_snapshot' if source_state else 'lossless_grid_raster',
            'source_state': source_state,
        }
        if key.startswith('figure03'):
            entries[key]['engine'] = 'analytical'
    first = np.load(snapshots / 'random_1100/mat_1.npy', allow_pickle=False)
    zeros = np.argwhere(first == 0)
    if first.shape != (1100, 1100) or not np.all(zeros[:, 1] == 1099):
        raise ValueError('the first random snapshot must have vacancies only at the East boundary')
    initial = first.copy()
    initial[initial == 0] = 1
    path = state_directory / 'random_initial.npz'
    np.savez_compressed(path, grid=initial)
    entries['random_initial'] = {
        'path': 'data/figures/states/random_initial.npz', 'n': 1100, 'time': 0,
        'tile': None, 'first_update': 'east', 'sha256': sha(path),
        'state_sha256': hashlib.sha256(initial.tobytes()).hexdigest(),
        'source_kind': 'reconstructed_initial_state',
        'derivation': 'The fully occupied initial state is recovered from the first East update by restoring an East car at each empty right-boundary site.',
        'first_step_sha256': hashlib.sha256(first.tobytes()).hexdigest(),
    }
    entries['random_t6500']['initial_state'] = 'random_initial'
    (output / 'states.json').write_text(json.dumps(entries, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--images', required=True, type=Path)
    parser.add_argument('--snapshots', required=True, type=Path)
    parser.add_argument('--output', default=Path('data/figures'), type=Path)
    args = parser.parse_args()
    import_states(args.images, args.snapshots, args.output)
