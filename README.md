# Jam Clearing in the Biham–Middleton–Levine Traffic Model

Computational companion to the paper by **Alexander E. Holroyd and Luke A.
Turvey**. The repository contains the simulator, numerical inputs and recipes
for Figures 1–13, the complete periodic-tile survey, and a standalone LaTeX
copy of the paper.

## Directory layout

| Directory | Purpose |
| --- | --- |
| [src/](src/) | Maintained BML simulator, explicit evolution, experiments and figure renderer |
| [figures/](figures/README.md) | Numbered recipes, experiment configurations and generated figure bundles |
| [data/](data/README.md) | Figure matrices, clearing-time measurements, provenance and local research collections |
| [latex/](latex/README.md) | Standalone paper source, bibliography, saved figures and appendices |
| [tests/](tests/) | Numerical, data-integrity and figure-workflow tests |
| [miscellaneous/](miscellaneous/README.md) | Tile-survey analysis, mathematical verification scripts and exploratory work |

The root also contains package configuration and this guide. The hidden
`.github/` directory contains the GitHub Actions workflow.

## Install, test and generate the figures

Use Python 3.10 or newer, from the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
python -m pytest -q
bml figures all --update
```

The default output is `figures/outputs/`. Each numbered directory contains a
PNG, a PDF, its exact recipe, a provenance report and the selected numerical
values. These generated bundles are ignored by Git and rebuilt from the compact
inputs in `data/`. GitHub Actions builds every figure and uploads the bundles
as artifacts.

Select figures or choose a new output directory with:

```bash
bml figures 3 8 9 10 11 --output figures/outputs/selected
```

Use `--update` when writing to an existing output directory. The default export
resolution is 300 dpi; `--dpi 600` increases it without changing the crop region.

## Build the paper

```bash
cd latex
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

This produces `latex/main.pdf` using the saved PDFs in `latex/figures/` and
the matching `latex/figure_statistics.tex`. Alternatively, run
`latexmk -pdf main.tex` inside `latex/`. The folder contains the bibliography
and saved assets and can be copied or uploaded on its own. Compilation needs
only a LaTeX installation with the packages in `latex/preamble.sty`.

To replace the saved figure set from the recorded numerical data, run from
the repository root:

```bash
bml figures all --update
bml save-paper-figures
```

The second command saves the PDFs in `latex/figures/` and the matching numerical
values in `latex/figure_statistics.tex`. Rendering into `figures/outputs/`
alone leaves the saved paper figures unchanged. See the
[paper compilation instructions](latex/README.md).

## Where the paper's data comes from

The [data provenance guide](data/README.md) maps every numbered figure to its
input file, numerical construction and generation code. The
[figure catalogue](figures/FIGURE_CATALOGUE.md) gives the tiles, sizes, times,
row selections and crops.

- The state illustrations are trajectories generated from periodic tiles or
  the supplied random initial matrix. Figure 3 evaluates the explicit
  evolution formula, checked against the simulator.
- Figures 2 and 7 select observations from the original deterministic
  `133333113` clearing-time records, which use North-first updates.
- Figures 6 and 12 use the datasets in
  `data/clearing_times/north_first/`. The supplied measurements reach n=999; Figure 12
  records a reproducible seed and replicate scheme.
- The appendix collects all 512 periodic tilings, with 235 observed affine or
  linear-plus-periodic formulas and 277 conjectured power laws, drawn from
  84,992 saved measurements. The affine and periodic formulas are checked on
  sizes excluded from their construction; the power laws are fitted over the
  recorded range. See the
  [survey guide](miscellaneous/survey/README.md). Normal paper
  compilation uses the saved tile catalogue without repeating the analysis.

## Replay or extend the simulations

```bash
bml figures 1 3 4 5 8 9 10 11 13 --mode simulate --output figures/outputs/replay
bml figures all --mode simulate --dry-run
bml refresh-data --max-n 10000 --skip-states
bml figures all --update
bml save-paper-figures
```

The refresh command extends Figures 6 and 12 to their full source size lists.
It can require substantial time; completed observations are checkpointed in
`data/clearing_times/north_first/checkpoints.json`. To regenerate the snapshots
and the supplied measurements through n=999, run `bml refresh-data --max-n 999`.
Updating the saved manuscript figures also updates the caption values to match
the generated sample ranges.

Additional experiments are configured in `figures/experiments/`:

```bash
bml run figures/experiments/smoke.json --output figures/outputs/smoke
bml simulate --tile 113133313 -n 30
bml verify-reference --max-n 30
```

See [numerical conventions](figures/NUMERICAL_NOTES.md) for update rules,
coordinate phase, regression definitions and data limitations.
Saved trajectories are labelled under `data/evolution_snapshots/` and videos
under `data/videos/`; both collections are ignored by Git. They are not required for the compact figure or manuscript build.
