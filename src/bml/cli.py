"""Command-line entry points for simulations, figures, and validation."""
import argparse
import json
from .experiments import run, verify_reference
from .initial import periodic, parse_tile
from .model import clearing_time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    single = commands.add_parser('simulate')
    single.add_argument('--tile', required=True)
    single.add_argument('-n', type=int, required=True)
    single.add_argument('--max-steps', type=int)
    single.add_argument('--first-update', choices=['north'], default='north')
    experiment = commands.add_parser('run')
    experiment.add_argument('config')
    experiment.add_argument('--output', required=True)
    verify = commands.add_parser('verify-reference')
    verify.add_argument('--data', default='data/clearing_times/historical')
    verify.add_argument('--max-n', type=int, default=30)
    plot = commands.add_parser('plot')
    plot.add_argument('csv')
    plot.add_argument('--output', required=True)
    plot.add_argument('--skip', type=int, default=0)
    plot.add_argument('--split-modulo', type=int)
    snap = commands.add_parser('snapshot')
    snap.add_argument('--tile', required=True)
    snap.add_argument('-n', required=True, type=int)
    snap.add_argument('--time', required=True, type=int)
    snap.add_argument('--output', required=True)
    figures = commands.add_parser('figures', help='reproduce numbered paper figures')
    figures.add_argument('numbers', nargs='*', default=['all'], help='all or figure numbers 1–13')
    figures.add_argument('--root', default='.', help='paper companion repository')
    figures.add_argument('--output', default='figures/outputs')
    figures.add_argument('--mode', choices=['recorded', 'simulate'], default='recorded')
    figures.add_argument('--dry-run', action='store_true', help='print inputs without running a build')
    figures.add_argument('--dpi', type=int, default=300)
    figures.add_argument('--seed', type=int, default=2026)
    figures.add_argument('--update', action='store_true', help='update generated files in an existing output directory')
    refresh = commands.add_parser('refresh-data', help='regenerate North-first numerical figure data')
    refresh.add_argument('--root', default='.')
    refresh.add_argument('--max-n', type=int, default=999)
    refresh.add_argument('--seed', type=int, default=2026)
    refresh.add_argument('--skip-states', action='store_true')
    publication = commands.add_parser('save-paper-figures', help='save rendered PDFs and captions for the manuscript')
    publication.add_argument('--source', default='figures/outputs')
    publication.add_argument('--output', default='figures/paper')
    args = parser.parse_args()
    if args.command == 'save-paper-figures':
        from .publication import save_paper_figures
        try:
            save_paper_figures(args.source, args.output)
        except (ValueError, FileNotFoundError) as exc:
            parser.error(str(exc))
    elif args.command == 'refresh-data':
        from .north_data import refresh_data
        refresh_data(args.root, args.max_n, args.seed, not args.skip_states)
    elif args.command == 'figures':
        from .figures import plan, reproduce
        try:
            numbers = list(range(1, 14)) if args.numbers == ['all'] else [int(n) for n in args.numbers]
            if args.dry_run:
                print(json.dumps(plan(args.root, numbers, args.mode), indent=2))
            else:
                reproduce(args.root, numbers, args.output, args.mode, args.dpi, args.seed, args.update)
        except (ValueError, FileNotFoundError, FileExistsError) as exc:
            parser.error(str(exc))
    elif args.command == 'simulate':
        print(clearing_time(periodic(parse_tile(args.tile), args.n), args.max_steps, args.first_update))
    elif args.command == 'run':
        run(args.config, args.output)
    elif args.command == 'verify-reference':
        report = verify_reference(args.data, args.max_n)
        print(json.dumps(report, indent=2))
        return int(bool(report['mismatches']) or report['checked'] == 0)
    elif args.command == 'snapshot':
        from .plotting import snapshot
        snapshot(args.tile, args.n, args.time, args.output)
    elif args.command == 'plot':
        from .plotting import plot_csv
        if args.skip < 0 or (args.split_modulo is not None and args.split_modulo < 1):
            parser.error('skip must be nonnegative and split-modulo positive')
        print(json.dumps(plot_csv(args.csv, args.output, args.skip, args.split_modulo), indent=2))
    return 0
