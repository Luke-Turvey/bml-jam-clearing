# Numerical conventions and reproducibility

All current simulation entry points use North updates at odd times, starting
at t=1, and East updates at even times. Requests for an East-first simulation are
rejected. Every numbered figure recipe and recorded panel uses this convention.

## Numerical records

`data/figure_states/states.json` records the North-first panel matrices, grid sizes,
snapshot times and SHA256 hashes. The periodic states are regenerated from their
tiles; Figure 3 evaluates the explicit two-column formula, tested against the
simulator. Figure 13 uses the supplied fully occupied random initial matrix.
That matrix was recovered from a saved first-step snapshot; the present
trajectory is recomputed from time zero with North updates first.

Figures 2 and 7 use historical measurements already verified as North-first.
Figures 6 and 12 use new North-first measurements in `data/clearing_times/north_first/`, with their
source size lists and provenance in adjacent JSON files. The distributed sweep
for those two figures reaches n=999. Figure 12's samples use
`default_rng(SeedSequence([seed, n, replicate]))`, with seed 2026.

Extend the two sweeps with `bml refresh-data --max-n 10000 --skip-states`.
Completed observations are checkpointed. The full-size sweep is optional and
is not run by the figure renderer or paper build. Smaller sweeps are not
represented as the original full-size empirical evidence.

The original mixed-convention CSVs remain unchanged in `data/clearing_times/historical/`.
The paper's fit summaries and measurement checksums are in `data/provenance/`.
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
values and computation reports into `figures/paper/`. The combined command
`make -C latex figures` performs both steps using the recorded data.

The manuscript includes only the saved PDFs and caption values in
`figures/paper/`. A normal `make -C latex` compiles `latex/build/main.pdf`
without running Python, redrawing figures or changing numerical data. The saved
caption values remain matched to the saved images until the set is explicitly
replaced, even if new experiments have updated the working data.

Detail crops retain their specified positions in the full grid. All snapshots
were regenerated with North-first updates; they are not relabelled East-first
images. The [figure catalogue](FIGURE_CATALOGUE.md) lists their parameters.

The appendix retains the original exploratory classification tables,
explicitly identified as historical estimates. Recomputing that entire survey
is separate from updating the thirteen figures; the North-first experiment is
specified in `figures/experiments/all-3x3.json`.

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
check that normal paper compilation does not invoke Python. Large sweeps are opt-in.

Simulation working memory is O(n²), plus requested snapshots; intermediate
frames are not retained. The default clearing-time budget is the paper's bound
5n²−n. Numerical experiments do not establish asymptotic conjectures.
