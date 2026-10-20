# Data sources for the paper

This directory separates the compact inputs needed to reproduce the paper from
the much larger local collections retained from the research. All current
figure trajectories and new clearing-time simulations use North cars first.

## Contents

| Location | Contents | Used by the default figure build? |
| --- | --- | --- |
| `figure_states/matrices/` | Twelve compact uint8 grid archives, including the original random initial matrix | Yes |
| `figure_states/states.json` | Grid parameters, numerical hashes and generation methods | Yes |
| `clearing_times/north_first/` | New Figure 6 and 12 measurements, generation metadata and resumable checkpoints | Yes |
| `clearing_times/historical/` | Original clearing-time CSVs and periodic-tile surveys | Selected files for Figures 2 and 7 |
| `clearing_times/model_variants/` | Exploratory measurements for modified models | No |
| `provenance/clearing_times_checksums.json` | SHA256 hashes for all 597 reference measurement files | Integrity checks |
| `provenance/figure06-fit.json`, `figure07-fit.json`, `figure12-fit.json` | Regression summaries for the paper’s scaling figures | Paper fits |
| `evolution_snapshots/periodic/<tile>/n_<size>/` | Large saved periodic trajectories, with original `mat_<time>` filenames | No |
| `evolution_snapshots/random/n_<size>/` | Large saved random trajectories | No |
| `videos/` | Original animations and modified-model videos | No |

The evolution snapshots and videos are local collections excluded from Git. The committed matrices and CSVs are sufficient for
a fresh clone to generate all thirteen figures. Generated bundles in
`../figures/outputs/` also contain copies of the exact numerical selections used
in each plot, alongside their PNGs, PDFs and provenance reports.

## Source of each numbered figure

All paths in the following table are relative to this directory. Each recipe is
in `../figures/recipes/figureNN.json`.

| Figure | Numerical input | How the input is obtained |
| --- | --- | --- |
| 1 | `figure_states/matrices/figure01_n600.npz`, `figure01_n599.npz` | North-first evolution of tile `133333113`: n=600 at t=3000 and n=599 at t=2995. Clearing times 4390 and 7207 were checked separately. |
| 2 | `clearing_times/historical/log2_133333113.csv` | Original deterministic North-first measurements; discard the first 30 nonblank rows and plot the remaining 43 observations on linear axes. |
| 3 | `figure_states/matrices/figure03_t150.npz`, `figure03_t220.npz` | Evaluate `linear_state(50, t)` for t=150 and 220. The explicit formula starts with tile `1313` and is tested against the simulator throughout its evolution. |
| 4 | `figure_states/matrices/figure04.npz` | North-first evolution of tile `333131313`, n=498, t=996. |
| 5 | `figure_states/matrices/reorganisation_t6000.npz` | North-first evolution of tile `133131313`, n=999, t=6000; also used in Figure 10. |
| 6 | `clearing_times/north_first/figure06.csv` | New North-first clearing times for tile `113133313`. The 28 supplied sizes, through n=999, come from the original `log2_113133313.csv` size list; its historical time values are not reused. |
| 7 | `clearing_times/historical/log2_133333113.csv` | Discard the first three nonblank rows, retain 70 observations, and fit n mod 3=2 separately from the pooled other residues. |
| 8 | `figure_states/matrices/fault_lines.npz` | North-first evolution of tile `1111111311331333`, n=1000, t=5000. The recipe renders the complete grid and a specified detail crop. |
| 9 | Same matrix as Figure 8 | Render the highway crop specified by the recipe. |
| 10 | `figure_states/matrices/reorganisation_t2000.npz`, `reorganisation_t4000.npz`, `reorganisation_t6000.npz`, `reorganisation_t8000.npz` | Collect the four North-first states of tile `133131313`, n=999, in one trajectory. |
| 11 | `figure_states/matrices/reorganisation_t4000.npz` | Render the boundary crop from the t=4000 state of Figure 10. |
| 12 | `clearing_times/north_first/figure12.csv` | 110 new seeded, fully occupied random simulations through n=999. Each cell independently contains an East or North car with probability 1/2. |
| 13 | `figure_states/matrices/random_initial.npz`, `random_t6500.npz` | Evolve the supplied n=1100 initial matrix from time zero to t=6500 with North updates first. |

The 73 observations in `log2_133333113.csv` are all also present in the denser
`g_periodic_133333113.csv` sweep. The former supplies the sampled points used by
Figures 2 and 7; the latter is retained as an additional historical record.
Automated audits replay small deterministic sizes. Full-size deterministic
replays are available through `bml figures ... --mode simulate`.

## Generation code and numerical provenance

The maintained [model](../src/bml/model.py) implements simultaneous updates and
open North/East boundaries. [Initial configurations](../src/bml/initial.py)
construct periodic tiles with a fixed bottom-left phase, or random grids.
[The explicit evolution](../src/bml/analytical.py) supplies Figure 3.
[Data generation](../src/bml/north_data.py) writes the North-first matrices and
new measurements. [Figure orchestration](../src/bml/figures.py) selects the
records, verifies hashes and prepares the rendering inputs.

Each state ledger entry records its tile or initial matrix, n, t, first update,
file hash and matrix hash. Refreshing states recomputes the trajectories; it does
not change the label on an old East-first state. Crops act on those recomputed
matrices. Their exact rectangles and coordinate convention are documented in
[the figure catalogue](../figures/FIGURE_CATALOGUE.md).

Each new clearing-time CSV has an adjacent JSON file recording the first-update
convention, actual maximum n, original size-source rows, Python/NumPy versions,
seed where applicable, and CSV hash. Measurements are headerless `(n,T)` rows.
Blank source lines are ignored, while repeated measurements retain their
regression weights.

For Figure 12 the seed is **2026**. A sample is constructed with
`default_rng(SeedSequence([seed, n, replicate]))`; replicate counts advance for
each occurrence of n in the source size list. `log2_random.csv` supplies that
list and its repeated sizes, not its historical time values. The original
unseeded samples behind that historical CSV cannot be replayed individually.
The new samples are reproducible with the recorded NumPy environment.

The Figure 13 initial matrix is different: it was recovered from the original
fully occupied realisation's first East update. With every interior site
occupied initially, only East cars on the right boundary could leave. Restoring
those cars recovers the initial matrix uniquely. The original saved first
state is `evolution_snapshots/random/n_1100/mat_1.npy`; its hash is retained
in the initial-state metadata. The current Figure 13 trajectory is recomputed
from that initial matrix with a North update first.

## Historical records and appendix tables

The original CSV files are preserved byte-for-byte. Their manifest keys are
relative to `clearing_times/historical/`. Some historical periodic records use
East-first updates. The reference audit uses directional duality to compare
those records while keeping every current simulator run North-first. The
conventions and audit limits are explained in
[the numerical notes](../figures/NUMERICAL_NOTES.md).

The manuscript's classification tables in
[latex/sections/appendix.tex](../latex/sections/appendix.tex) are static historical
estimates. Related survey measurements are retained in
`clearing_times/historical/periodic_csv/` and `periodic_csv_full/`; the exploratory
analysis scripts are in `../miscellaneous/scripts/`. The tables are not rebuilt
from the current North-first data, and a complete correspondence between each
printed estimate and a particular original analysis run has not been established.
The manuscript identifies them as historical. A new exhaustive North-first
survey is specified by `../figures/experiments/all-3x3.json`.

The provenance directory contains only the paper's fit summaries and reference
measurement checksums. Per-state parameters and hashes remain in
`figure_states/states.json`; run parameters, seeds and software versions remain
beside the corresponding CSV files.

## Extend or regenerate the data

From the repository root:

```bash
# Regenerate the current snapshots and the new sweeps through n=999.
bml refresh-data --max-n 999

# Extend the Figure 6 and Figure 12 sweeps to their full source size lists.
bml refresh-data --max-n 10000 --skip-states

# Replace the saved manuscript figures and their matching numerical captions.
make -C latex figures

# Compile the paper from those saved assets.
make -C latex
```

The full sweeps can be expensive. Completed observations are checkpointed in
`clearing_times/north_first/checkpoints.json`, so a refresh can resume. Rendering
the recorded figures does not run those full sweeps. Normal paper compilation
uses the saved PDFs and caption values in `../figures/paper/` without running
any Python code or updating the data.
