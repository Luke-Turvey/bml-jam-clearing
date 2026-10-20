# Numerical conventions and reproducibility

All current simulation entry points use North updates at odd times, starting
at t=1, and East updates at even times. Requests for an East-first simulation are
rejected. Every numbered figure recipe and recorded panel uses this convention.

## Numerical records

`data/figures/states.json` records the North-first panel matrices, grid sizes,
snapshot times and SHA256 hashes. The periodic states are regenerated from their
tiles; Figure 3 evaluates the explicit two-column formula, tested against the
simulator. Figure 13 uses the supplied fully occupied random initial matrix.
That matrix was recovered from a historical first-step snapshot; the present
trajectory is recomputed from time zero with North updates first.

Figures 2 and 7 use historical measurements already verified as North-first.
Figures 6 and 12 use new North-first measurements in `data/north/`, with their
source size lists and provenance in adjacent JSON files. The distributed sweep
for those two figures reaches n=999. Figure 12's samples use
`default_rng(SeedSequence([seed, n, replicate]))`, with seed 2026.

Extend the two sweeps with `bml refresh-data --max-n 10000 --skip-states`.
Completed observations are checkpointed. The full-size sweep is optional and
is not run by the figure renderer or paper build. Smaller sweeps are not
represented as the original full-size empirical evidence.

The original mixed-convention CSVs remain unchanged in `data/reference/`.
Historical figure metadata and fit reports are under `data/historical/`; they
are not inputs to current figure generation. The reference audit compares
North-first trajectories with the historical data. For an old East-first
record, it applies the directional duality: reflect the grid across its
anti-diagonal and exchange East and North cars, then run the North-first model.
No alternate first-update simulation is needed.

## Model and phase

Array rows increase downward and columns increase rightward. Repeated tiles are
anchored at the bottom left. Updates are simultaneous: a car cannot enter a
site vacated during the same update. Cars leave through the top/right boundary.
Time counts individual directional updates.

Figure 3 uses tile `1313`, consistent with the explicit formula and the copied
paper's updated two-column illustration. Its panels show n=50 at t=150 and
220. The tested formula and its region boundaries are included in the paper.

## Figures and manuscript

`bml figures all --output paper/generated --update` writes all numbered PDFs and
PNGs, numerical sidecars, provenance, and `figure_statistics.tex`. The manuscript
includes those PDFs directly and reads its fitted coefficients and sample
ranges from the generated TeX file. `make -C paper` performs that figure build
and compiles the paper to `paper/build/main.pdf`.

Detail crops retain their specified positions in the full grid. All snapshots
were regenerated with North-first updates; they are not relabelled East-first
images. The [figure catalogue](figures.md) lists their parameters.

The copied appendix retains the original exploratory classification tables,
explicitly identified as historical estimates. Recomputing that entire survey
is separate from updating the thirteen figures; the North-first experiment is
specified in `configs/all-3x3.json`.

## Fits and validation

Fits use ordinary least squares on
`log2(T) = power × log2(n) + intercept`. The coefficient in original coordinates
is `2^intercept`. Repeated observations retain their regression weights. Figure
7 excludes its first three data rows and pools residues 0 and 1. Fits and actual
sample sizes are recorded in each build's `provenance.json`.

Tests compare the update rules with an independent car-by-car simulator,
validate the explicit evolution, check reference-data and panel hashes, and
build every numbered figure. Tests also ensure that all simulation and figure
inputs specify North-first updates and that every manuscript figure refers to
a generated output. Large sweeps are opt-in.

Simulation working memory is O(n²), plus requested snapshots; intermediate
frames are not retained. The default clearing-time budget is the paper's bound
5n²−n. Numerical experiments do not establish asymptotic conjectures.
