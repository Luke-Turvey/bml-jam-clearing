# Jam Clearing in the Biham–Middleton–Levine Traffic Model

Computational companion to the paper by **Alexander E. Holroyd and Luke A.
Turvey**. The repository contains the North-first simulation model, numerical data,
recipes for **Figures 1–13**, and the manuscript in `paper/`.

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

## Build the paper

```bash
make -C paper
```

This regenerates the numbered figures into `paper/generated/` and compiles
`paper/build/main.pdf`. The manuscript includes those PDFs directly, and its
captions read fitted values and sample ranges from the generated results.
A LaTeX installation with `latexmk` and the packages in `paper/preamble.sty`
is required. See [paper build instructions](paper/README.md).

## Replay and extend simulations

All simulations start with a North update. Replay selected figure states with:

```bash
bml figures 1 3 4 5 8 9 10 11 13 --mode simulate --output results/replay
bml figures all --mode simulate --dry-run
```

The supplied new North-first sweeps for Figures 6 and 12 reach n=999. Extend
those sweeps, then rebuild the paper, with:

```bash
bml refresh-data --max-n 10000 --skip-states
make -C paper
```

This can require substantial computing time. Completed observations are
checkpointed so a refresh can resume after interruption. To regenerate all
snapshot states and the sweeps up to n=999, use `bml refresh-data --max-n 999`.
The paper reports the actual generated sizes rather than assuming a completed
full-size sweep. Figures 2 and 7 retain verified North-first records up to
n=10000. Figure 12 uses explicit seeded samples; Figure 13 reuses its supplied
initial random matrix and evolves it with North updates first.

See the [figure catalogue](docs/figures.md) and
[numerical conventions](docs/reproducibility.md) for the full parameter lists.

## Model

A grid entry is `0` for a vacancy, `1` for an East car, and `3` for a North car.
Updates are simultaneous within each direction. Cars leave through the top and
right boundaries. Time counts individual directional updates. Array row zero
is the top of the grid; repeated tiles are anchored at the bottom left.

The model starts with North cars, as in the paper. Every active experiment and
figure recipe uses the same convention. Historical mixed-convention data is
retained separately for reference.

```bash
bml simulate --tile 113133313 -n 30
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
| `data/north/` | New North-first clearing-time measurements and checkpoints |
| `data/reference/` | Historical measurements and periodic-tile survey |
| `paper/` | LaTeX manuscript, bibliography, appendix and build recipe |
| `src/bml/` | Dynamics, explicit evolution, figure rendering and command-line tools |
| `tests/` | Numerical and figure-workflow checks |
| `docs/` | Figure catalogue and numerical conventions |
| `configs/` | Supplementary size sweeps and exhaustive periodic experiments |
| `archive/` | Exploratory research scripts and plotting notebook |

Generated outputs belong in `results/`. Additional local simulation histories
and videos can be retained in `local_artifacts/`; neither directory is required
for the figure build or included in version control.
