# Jam Clearing in the Biham–Middleton–Levine Traffic Model

Computational companion to the paper by **Alexander E. Holroyd and Luke A.
Turvey**. The repository contains the simulation model, measurements and grid
states used in the paper, and recipes for **Figures 1–13**.

## Reproduce the figures

Use Python 3.10 or newer, from the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
bml figures all --output results/figures
```

This builds all thirteen figures from the supplied numerical data. Each figure
has PNG and PDF versions, the exact plotting recipe, numerical panel states or
measurements, and a provenance report. The paper's LaTeX project and original
large simulation directories are not required.

Select individual figures by number:

```bash
bml figures 3 8 9 10 11 --output results/selected
```

Output directories must be new. Figures are written to
`results/figures/figure01/figure01.pdf`, and similarly for the other numbers.
The default resolution is 300 dpi; use `--dpi 600` for higher-resolution raster
panels. Crops are defined in the recipes, independently of export resolution.

## Replay simulations

The simulation mode recomputes grid states and clearing times before rendering.
Deterministic results are checked against the supplied numerical records.
Figure 3 evaluates the explicit formula, which is also tested against the
step-by-step simulator. The four Figure 10 states are collected in one run.

```bash
bml figures 1 3 4 5 8 9 10 11 13 --mode simulate --output results/replay

# Inspect all simulation inputs without starting any computations.
bml figures all --mode simulate --dry-run

# Recompute the size sweeps for the scaling figures.
bml figures 2 6 7 12 --mode simulate --output results/scaling-replay
```

The largest sweeps reach n=10000 and can require substantial computing time.
They are separate from the automated tests. Simulation memory scales with n²;
selected snapshots are retained, rather than an entire animation history.

Figure 13 includes its reconstructed original initial state, so its recorded
random realisation can be replayed exactly. The individual initial states behind
Figure 12's historical measurements were not recorded. Simulation mode for
Figure 12 therefore uses new random samples with an explicit seed (default
2026, configurable with `--seed`); recorded mode reproduces its original data.

See the [figure catalogue](docs/figures.md) for every tile, size, time, crop and
fit selection, and [numerical conventions](docs/reproducibility.md) for the
relationship between the archived figures and the paper's equations.

## Model

A grid entry is `0` for a vacancy, `1` for an East car, and `3` for a North car.
Updates are simultaneous within each direction. Cars leave through the top and
right boundaries. Time counts individual directional updates. Array row zero
is the top of the grid; repeated tiles are anchored at the bottom left.

The default model starts with North cars, as in the paper. Several recorded
figures and datasets start with East cars; each figure recipe specifies its
convention explicitly.

```bash
bml simulate --tile 113133313 -n 30 --first-update east
bml verify-reference --max-n 30
```

## Validation

```bash
python -m pytest -q
```

Tests check the dynamics against an independent car-by-car implementation,
verify the explicit Figure 3 evolution, audit historical clearing times, check
data integrity, and build every numbered figure. GitHub Actions runs these
checks on Python 3.10 and 3.12 and publishes the resulting figures as artifacts.

## Contents

| Path | Contents |
| --- | --- |
| `figures/figure01.json` … `figure13.json` | Numbered figure recipes |
| `data/figures/` | Compact panel states, original random initial state and provenance |
| `data/reference/` | Clearing-time measurements and periodic-tile survey |
| `src/bml/` | Dynamics, explicit evolution, figure rendering and command-line tools |
| `tests/` | Numerical and figure-workflow checks |
| `docs/` | Figure catalogue and numerical conventions |
| `configs/` | Supplementary size sweeps and exhaustive periodic experiments |
| `scripts/` | Import tools for original numerical and figure records |
| `archive/` | Exploratory research scripts and plotting notebook |

Generated outputs belong in `results/`. Additional local simulation histories
and videos can be retained in `local_artifacts/`; neither directory is required
for the figure build or included in version control.
