"""Headless figures and explicit power-law fits; no notebook state required."""
import csv
import json
from pathlib import Path
import numpy as np


def plot_csv(source, output, skip=0, split_modulo=None):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    with open(source, newline='') as stream:
        rows = [r for r in csv.reader(stream) if r and any(r)]
    if rows and rows[0][0] == 'n':
        rows = rows[1:]
    values = np.array([[float(r[0]), float(r[1])] for r in rows[skip:]])
    if values.ndim != 2 or len(values) < 2 or np.any(values <= 0):
        raise ValueError('need at least two positive observations after skipping rows')
    x, y = values.T
    fig, ax = plt.subplots()
    groups = [(str(r), x % split_modulo == r) for r in range(split_modulo)] if split_modulo else [('all', np.ones(len(x), dtype=bool))]
    fits = {}
    for label, mask in groups:
        a, b = x[mask], y[mask]
        if not len(a):
            continue
        ax.loglog(a, b, '.', label=label)
        if len(np.unique(a)) >= 2:
            power, intercept = np.linalg.lstsq(np.column_stack((np.log(a), np.ones(len(a)))), np.log(b), rcond=None)[0]
            fits[label] = {'power': float(power), 'coefficient': float(np.exp(intercept)), 'count': len(a)}
            xx = np.sort(a)
            ax.loglog(xx, np.exp(intercept) * xx**power, alpha=.5)
    ax.set(xlabel='$n$', ylabel='$T(W_n,n)$')
    ax.grid(True, which='both', linewidth=.3)
    ax.legend(title='n modulo ' + str(split_modulo) if split_modulo else None)
    fig.tight_layout()
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output)
    plt.close(fig)
    report = {'source': str(source), 'skip_rows': skip, 'split_modulo': split_modulo,
              'fit': 'ln(T) = power * ln(n) + ln(coefficient)', 'groups': fits}
    output.with_suffix('.fit.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def snapshot(tile, n, time, output):
    """Save a state image and machine-readable state without storing every frame."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    from .initial import periodic, parse_tile
    from .model import evolve
    grid = evolve(periodic(parse_tile(tile), n), time)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots()
    ax.imshow(grid, cmap=ListedColormap(['white', 'red', 'white', 'blue']), vmin=0, vmax=3,
              interpolation='nearest')
    ax.set_title(f'n = {n}, t = {time}')
    ax.set_axis_off()
    fig.savefig(output, bbox_inches='tight', dpi=200)
    plt.close(fig)
    np.save(output.with_suffix('.npy'), grid)
    output.with_suffix('.json').write_text(json.dumps({
        'tile': tile, 'n': n, 'time': time, 'first_update': 'north',
        'anchor': 'bottom-left', 'remaining_cars': int(np.count_nonzero(grid))
    }, indent=2) + '\n')
