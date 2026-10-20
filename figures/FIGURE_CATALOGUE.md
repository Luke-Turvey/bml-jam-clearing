# Figure catalogue

Build all figures with `bml figures all --update`. Individual
figures use the same command with their numbers, for example `bml figures 8 9 --output figures/outputs/details`.
The default reads the supplied numerical records. Add `--mode simulate` to replay
the numerical computation, or `--dry-run` to inspect its inputs.

Tiles are row-major strings with 1=East and 3=North. Grid states and crops are
indexed from the top left. Every recipe is in `figures/recipes/figureNN.json`.

| Figure | Tile / data | Size and time | First update |
| --- | --- | --- | --- |
| 1 | `133333113` | n=600, t=3000; n=599, t=2995 | North |
| 2 | `data/clearing_times/historical/log2_133333113.csv`, rows 30 onward | Linear axes; 43 observations | North |
| 3 | Explicit evolution; tile `1313` | n=50, t=150 and 220 | North |
| 4 | `333131313` | n=498, t=996 | North |
| 5 | `133131313` | n=999, t=6000 | North |
| 6 | `data/clearing_times/north_first/figure06.csv`, all rows | Base-2 logarithmic axes; one fit | North |
| 7 | `data/clearing_times/historical/log2_133333113.csv`, rows 3 onward | Base-2 axes; fits for n mod 3=2 and n mod 3≠2 | North |
| 8 | `1111111311331333` | n=1000, t=5000; full grid and fault-line detail | North |
| 9 | Same state as Figure 8 | Highway detail | North |
| 10 | `133131313` | n=999, t=2000, 4000, 6000, 8000 | North |
| 11 | Figure 10's t=4000 state | Boundary detail | North |
| 12 | `data/clearing_times/north_first/figure12.csv`, all rows | Base-2 axes; one fit | North |
| 13 | Supplied original random initial state | n=1100, t=6500 | North |

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

The rectangles retain the original detail locations, applied to regenerated
North-first states. Figure 5 uses the same state as Figure 10's t=6000 panel.

## Scaling fits

Regressions use `log2(T) = power × log2(n) + intercept`; the coefficient in
original coordinates is `2^intercept`. Figure 7 keeps separate fits for residue
2 and the pooled other residues. Every fit is written to the figure provenance
and to `figure_statistics.tex`. `make -C latex figures` saves the PDFs and
matching numerical captions together in `figures/paper/` for the manuscript.
Normal paper compilation uses that fixed set without rendering again.

Figures 6 and 12 contain freshly computed North-first sweeps up to n=999.
`bml refresh-data --max-n 10000 --skip-states` extends them to the full source
size lists. The distributed measurements are not the historical East-first
Figure 6 values or unseeded Figure 12 samples.

## Outputs and provenance

Each output directory contains `figureNN.png`, `figureNN.pdf`, `recipe.json`,
and `provenance.json`. State figures include one compressed numerical matrix
per panel; scaling figures include the selected `measurements.csv` and their
fits in the provenance report. `index.json` at the build root collects all
reports. PNG/PDF layout and font rendering may vary with Matplotlib versions;
the matrix contents, selected observations, crops and regression definitions
are the reproducibility targets.

`data/figure_states/states.json` records numerical hashes, initial tiles, sizes,
times and the uniform North-first update convention. States are stored as
uint8 matrices inside compressed NumPy archives. They occupy less than one megabyte in total and
contain no executable pickle data.
