# Figure catalogue

Build all figures with `bml figures all --output results/figures`. Individual
figures use the same command with their numbers, for example `bml figures 8 9`.
The default reads the supplied numerical records. Add `--mode simulate` to replay
the numerical computation, or `--dry-run` to inspect its inputs.

Tiles are row-major strings with 1=East and 3=North. Grid states and crops are
indexed from the top left. Every recipe is in `figures/figureNN.json`.

| Figure | Tile / data | Size and time | First update |
| --- | --- | --- | --- |
| 1 | `133333113` | n=600, t=3000; n=599, t=2995 | North |
| 2 | `log2_133333113.csv`, rows 30 onward | Linear axes; 43 observations | North |
| 3 | Explicit evolution; tile `1313` | n=50, t=150 and 220 | North |
| 4 | `333131313` | n=498, t=996 | East |
| 5 | `133131313` | n=999, t=6000 | East |
| 6 | `log2_113133313.csv`, all rows | Base-2 logarithmic axes; one fit | East |
| 7 | `log2_133333113.csv`, rows 3 onward | Base-2 axes; fits for n mod 3=2 and n mod 3≠2 | North |
| 8 | `1111111311331333` | n=1000, t=5000; full grid and fault-line detail | East |
| 9 | Same state as Figure 8 | Highway detail | East |
| 10 | `133131313` | n=999, t=2000, 4000, 6000, 8000 | East |
| 11 | Figure 10's t=4000 state | Boundary detail | East |
| 12 | `log2_random.csv`, all nonblank rows | Base-2 axes; one fit | Unrecorded for historical samples; North for new simulations |
| 13 | Supplied original random initial state | n=1100, t=6500 | East |

Row offsets are zero-based and applied after discarding blank CSV lines. Repeated
observations are retained, including their weights in the regressions. Figure 2
uses the sampled dataset shown in its original source image, rather than the
much denser general-periodic sweep.

## Crops

Crops are specified as `[top, bottom, left, right]`, with exclusive lower/right
bounds, in the original full-grid raster's pixel coordinates. The renderer
converts these to fractional cell bounds before plotting, so changing DPI does
not change the selected region.

| Panel | Full-grid raster width × height | Crop |
| --- | --- | --- |
| Figure 8, fault line | 4435 × 4435 | `[2902, 3533, 104, 754]` |
| Figure 9, highway | 4435 × 4435 | `[1054, 1322, 59, 619]` |
| Figure 11, boundary | 7392 × 7392 | `[3336, 4928, 68, 1560]` |

These rectangles were identified by exact pixel matching of the original detail
images against their full-grid counterparts. Figure 5's source image is the
same state as Figure 10's t=6000 panel.

## Scaling fits

Each regression uses ordinary least squares on
`log2(T) = power × log2(n) + intercept`. The equivalent coefficient in
`T ≈ coefficient × n^power` is `2^intercept`.

| Figure / group | Observations | Power | Base-2 intercept |
| --- | --- | --- | --- |
| 6 | 38 | 1.27001450 | 1.74798696 |
| 7, n mod 3=2 | 29 | 1.21344664 | 1.75462744 |
| 7, other residues | 41 | 1.02292500 | 2.63806924 |
| 12 | 123 | 1.15628468 | 2.09239527 |

The recipes fit the recorded observations; caption values are not substituted
for fitted values. See the numerical notes for caption and phase conventions.

## Outputs and provenance

Each output directory contains `figureNN.png`, `figureNN.pdf`, `recipe.json`,
and `provenance.json`. State figures include one compressed numerical matrix
per panel; scaling figures include the selected `measurements.csv` and their
fits in the provenance report. `index.json` at the build root collects all
reports. PNG/PDF layout and font rendering may vary with Matplotlib versions;
the matrix contents, selected observations, crops and regression definitions
are the reproducibility targets.

`data/figures/states.json` records numerical hashes, source-image hashes, sizes,
times and update conventions. States are stored as uint8 matrices inside
compressed NumPy archives. They occupy less than one megabyte in total and
contain no executable pickle data.
