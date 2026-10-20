"""Publication panels and scaling plots for the numbered paper figures."""
import numpy as np


def _pyplot():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    return plt


def save_states(recipe, panels, output, dpi=300):
    """Render grid panels; crops use pixels in the original full-grid raster."""
    from matplotlib.colors import ListedColormap
    plt = _pyplot()
    columns = recipe.get('columns', 1)
    rows = (len(panels) + columns - 1)//columns
    fig, axes = plt.subplots(rows, columns, squeeze=False,
                             figsize=recipe.get('figsize', [6*columns, 6*rows]))
    for ax in axes.flat:
        ax.set_axis_off()
    for ax, (panel, grid) in zip(axes.flat, panels):
        n = len(grid)
        ax.imshow(grid, cmap=ListedColormap(['white', 'red', 'white', 'blue']),
                  vmin=0, vmax=3, interpolation='nearest', extent=[0, n, n, 0])
        if 'crop_pixels' in panel:
            top, bottom, left, right = panel['crop_pixels']
            width, height = panel['source_pixels']
            ax.set_xlim(left*n/width, right*n/width)
            ax.set_ylim(bottom*n/height, top*n/height)
        if panel.get('label'):
            ax.set_title(panel['label'], fontsize=11)
    fig.subplots_adjust(left=.015, right=.985, bottom=.015, top=.94,
                        wspace=.04, hspace=.12)
    _save(fig, output, dpi)
    plt.close(fig)


def fit_power(x, y, base=2):
    """Fit log_base(T) = power*log_base(n) + intercept."""
    if len(np.unique(x)) < 2:
        raise ValueError('a power fit requires at least two distinct sizes')
    logs = np.log(float(base))
    power, intercept = np.linalg.lstsq(
        np.column_stack((np.log(x)/logs, np.ones(len(x)))), np.log(y)/logs, rcond=None
    )[0]
    return {'power': float(power), 'intercept': float(intercept),
            'coefficient': float(base**intercept), 'log_base': base,
            'observations': len(x)}


def save_scaling(recipe, measurements, output, dpi=300):
    plt = _pyplot()
    values = np.asarray(measurements)
    x, y = values[:, 0], values[:, 1]
    fig, ax = plt.subplots(figsize=recipe.get('figsize', [7.5, 5]))
    ax.scatter(x, y, marker='.', s=20, color='#1f77b4')
    if recipe['scale'] == 'log':
        ax.set_xscale('log', base=2)
        ax.set_yscale('log', base=2)
    fits = {}
    for group in recipe.get('fit_groups', []):
        if group['selection'] == 'all':
            mask = np.ones(len(x), dtype=bool)
        elif group['selection'] == 'residue_equals':
            mask = x % group['modulus'] == group['residue']
        elif group['selection'] == 'residue_not_equals':
            mask = x % group['modulus'] != group['residue']
        else:
            raise ValueError('unknown fit selection')
        fit = fit_power(x[mask], y[mask])
        fits[group['name']] = fit
        xx = np.sort(x[mask])
        ax.plot(xx, fit['coefficient']*xx**fit['power'], color='red', alpha=.25)
    ax.set(xlabel='$n$', ylabel='$T(W_n,n)$')
    ax.grid(True, which='major', linewidth=.5, alpha=.7)
    ax.set_axisbelow(True)
    fig.tight_layout()
    _save(fig, output, dpi)
    plt.close(fig)
    return fits


def _save(fig, output, dpi):
    fig.savefig(output.with_suffix('.png'), dpi=dpi, bbox_inches='tight', pad_inches=.06)
    fig.savefig(output.with_suffix('.pdf'), dpi=dpi, bbox_inches='tight', pad_inches=.06,
                metadata={'Title': output.stem, 'Creator': 'BML jam clearing'})
