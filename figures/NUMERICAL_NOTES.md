# Numerical conventions and reproducibility

North cars update at odd times, starting at t=1, and East cars update at even
times. Every numbered figure recipe and recorded panel uses this convention.

## Numerical records

`data/figure_states/states.json` records the panel matrices, grid sizes,
snapshot times and SHA256 hashes. The periodic states are regenerated from their
tiles; Figure 3 evaluates the explicit two-column formula, tested against the
simulator. Figure 13 uses the supplied fully occupied random initial matrix.
That matrix was recovered from a saved first-step snapshot; the present
trajectory is computed from time zero under the model rules.

Figures 2 and 7 use historical measurements already verified as North-first.
Figures 6 and 12 use measurements in `data/clearing_times/north_first/`, with their
source size lists and provenance in adjacent JSON files. The supplied data
for those two figures reaches n=999. Figure 12's samples use
`default_rng(SeedSequence([seed, n, replicate]))`, with seed 2026.

Extend these measurements with `bml refresh-data --max-n 10000 --skip-states`.
Completed observations are checkpointed. The figure renderer and paper build
use the saved measurements; the recorded sample sizes define the range of the
paper's finite-size evidence.

The original mixed-convention CSVs remain unchanged in `data/clearing_times/historical/`.
The paper's fit summaries and measurement checksums are in `data/metadata/`.
The reference audit compares
North-first trajectories with the historical data. For an old East-first
record, it applies the directional duality: reflect the grid across its
anti-diagonal and exchange East and North cars, then run the North-first model.
No alternate first-update simulation is needed.

## Model and phase

Array rows increase downward and columns increase rightward. Repeated tiles are
anchored at the bottom left. Updates are simultaneous: a car cannot enter a
site vacated during the same update. Cars leave through the top/right boundary.
Time counts individual directional updates.

Figure 3 uses tile `1313`, consistent with the explicit formula and the
paper's two-column illustration. Its panels show n=50 at t=150 and
220. The tested formula and its region boundaries are included in the paper.

## Figures and manuscript

`bml figures all --update` writes all numbered PDFs and PNGs, numerical sidecars,
provenance, and `figure_statistics.tex` into `figures/outputs/`.
`bml save-paper-figures` copies the complete set of PDFs, matching caption
values into the standalone `latex/` folder: PDFs in `latex/figures/`, numerical
values in `latex/figure_statistics.tex`. Checksums and computation reports are
recorded separately in `data/metadata/paper-figures.json`.

From inside `latex/`, compile with `pdflatex main.tex`, `bibtex main`, then
`pdflatex main.tex` twice; alternatively use `latexmk -pdf main.tex`.
The result is `latex/main.pdf`. Compilation uses the saved assets, and the
folder can be copied or uploaded on its own. The saved numerical values remain
matched to the saved images until the set is explicitly replaced.

Detail crops retain their specified positions in the full grid. The
[figure catalogue](FIGURE_CATALOGUE.md) lists their parameters.

The appendix uses 84,992 measurements for all 512 occupied 3-by-3 tiles at
`n=3,6,...,498`. It collects 235 observed affine or linear-plus-periodic formulas
and 277 conjectured power laws. The former are constructed on
`n=102,...,330` and checked exactly on `n=333,...,498`; the latter are fitted on
`n=102,...,498`. The data and complete coefficient records are in
`data/clearing_times/survey_north_first/`; analysis and diagram generation are
described in the [survey guide](../miscellaneous/survey/README.md). The saved
catalogue is included directly in the paper.

## Fits and validation

Fits use ordinary least squares on
`log2(T) = power × log2(n) + intercept`. The coefficient in original coordinates
is `2^intercept`. Repeated observations retain their regression weights. Figure
7 excludes its first three data rows and pools residues 0 and 1. Fits and actual
sample sizes are recorded in each build's `provenance.json`.

Tests compare the update rules with an independent car-by-car simulator,
validate the explicit evolution, check reference-data and panel hashes, and
build every numbered figure. Tests also ensure that all simulation and figure
inputs specify North-first updates, verify the saved manuscript assets, and
check the standalone LaTeX sources and their saved assets. Larger simulations
are requested explicitly.

Simulation working memory is O(n²), plus requested snapshots; intermediate
frames are not retained. The default clearing-time budget is the paper's bound
5n²−n. Numerical experiments do not establish asymptotic conjectures.
