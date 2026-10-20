# Numerical conventions and reproducibility

The [figure catalogue](figures.md) specifies the inputs for Figures 1–13. A
complete recorded-data build requires only the repository and its Python
dependencies. The original LaTeX project, HPC files and video histories are not
runtime dependencies.

## Recorded data and simulation replay

`bml figures all` renders the recorded matrices and clearing-time measurements.
`--mode simulate` recomputes the selected matrices and measurements before
rendering. Periodic simulation results must agree with the recorded numerical
values; a mismatch raises an error. Regenerated panel states are compared at
every grid site. The explicit formula supplies Figure 3, and is independently
checked against the directional update rules throughout the evolution on several
even grid sizes.

The original random realisation in Figure 13 is replayable from its supplied
initial matrix. Figure 12's historical random samples have no recorded seeds or
initial-state identifiers. Its recorded plot is reproducible, but replaying its
size sweep produces new seeded samples. Reports distinguish those new samples
from the historical measurements. The random stream is keyed by seed, grid size
and replicate number.

## Directional updates and phase

The paper defines North updates at odd times and East updates at even times.
Several archived experiments use the opposite first direction. The figure
recipes preserve the actual conventions of the recorded images and measurements.
North-first is the default for general simulation commands; East-first must be
selected explicitly where required.

`reference-audit.json` reports 5,160 deterministic observations through n=30.
Each matches at least one of the two update conventions. The general-periodic
`133333113` dataset matches North-first dynamics; the exhaustive periodic survey
and the selected `113133313` dataset match East-first dynamics. The audit does
not establish a common convention for unrelated random measurements.

Array rows increase downward and columns increase rightward. A tile is written
from top to bottom and repeated with its bottom-left corner fixed. This phase
must be retained when n is not a multiple of the tile size. Updates are
simultaneous: a car cannot enter a site vacated on that same update. Cars are
removed after crossing the top or right boundary.

## Figure 3 and the printed formula

The two archived panels show n=50 at t=150 and t=220. The second panel's printed
caption repeats t=150; its filename and numerical state identify t=220.

The panel-generating formula has the initial column phase `1313`, starting with
an East car at the left boundary. The tile drawn in the paper's theorem has the
opposite column phase, `3131`. The figure recipe preserves the panel phase. The
implemented explicit evolution follows the archived formula; it is not a literal
transcription of the displayed inequalities, whose boundary expressions also
differ from that implementation. The simulator can evaluate either phase.

## Regression conventions

The original scaling plots use base-2 logarithms. Figure 6's full dataset gives
power 1.27001450 and intercept 1.74798696, matching the rounded 1.27 and 1.75 in
the caption. Figure 7 excludes its first three data rows and pools residues 0 and
1. Its fitted powers are 1.21344664 and 1.02292500. Figure 12's power and intercept
are 1.15628468 and 2.09239527.

Intercepts on logarithmic axes must be distinguished from multiplicative
coefficients in the original coordinates. The provenance reports include both.
The captions' regression notation is not uniform: Figure 7 prints `log(1.78)`
and `log(2.64)` where the archived fits give base-2 intercepts approximately 1.75
and 2.64; Figure 12 prints an affine expression in n in its log-log caption. The
figure code records the actual regression definition and values.

## State provenance

The four Figure 10 states and Figure 13's t=6500 state agree exactly with saved
numerical snapshots and the original figure rasters. Other panel matrices were
read at cell centres from lossless, borderless, three-colour grid rasters. Their
source-image hashes are retained in `data/figures/states.json`.

The Figure 4 matrix agrees exactly with an East-first simulation of tile
`333131313` at n=498, t=996. The Figure 8 matrix agrees exactly with an East-first
simulation of tile `1111111311331333` at n=1000, t=5000. Both Figure 1 matrices
agree with North-first simulations at their specified times. Its clearing times
are 4390 for n=600 and 7207 for n=599.

Figure 13's fully occupied initial state is reconstructed from the saved first
East update. Since every interior target is initially occupied, only East cars
on the rightmost boundary can move. Restoring an East car at each right-boundary
vacancy therefore recovers the initial matrix uniquely. Reapplying that update
reproduces the saved first state exactly. No random seed is needed to replay
this particular realisation.

The optional `scripts/import_figure_states.py` importer reconstructs the compact
archives from the original image and snapshot collections. These collections
are not needed for normal figure generation.

## Validation and environment

Tests compare all 2-by-2 configurations, including vacancies, with an independent
car-by-car simulator, and check mixed-state trajectories, boundary exits, phase,
time budgets and random replay. Further tests verify the explicit evolution,
all supplied data hashes, every figure recipe, multi-time simulations, and a
complete recorded-data figure build. Expensive scaling sweeps are opt-in.

The implementation uses O(n²) working memory for a simulation plus storage for
requested snapshots. It does not retain every intermediate frame. The default
clearing-time budget is the paper's bound 5n²−n; exhausting a budget raises an
error. Numerical experiments do not establish the paper's asymptotic conjectures.

Each figure report records Python and NumPy versions. Retain a package snapshot
with an archival computation, for example `python -m pip freeze > environment.txt`.
Dependencies have supported version ranges; CI checks Python 3.10 and 3.12.
