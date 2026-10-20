# Paper data provenance

| File | Purpose |
| --- | --- |
| `clearing_times_checksums.json` | SHA256 checksums for the 597 reference measurement files, with keys relative to `../clearing_times/historical/` |
| `figure06-fit.json` | Fit for the 28 North-first observations in Figure 6 |
| `figure07-fit.json` | Fits for the 70 observations in Figure 7, separated into n mod 3=2 and the pooled other residues |
| `figure12-fit.json` | Fit for the 110 seeded North-first observations in Figure 12 |

The standard figure build updates these fit summaries from the same regressions
used in the manuscript captions. Each fit summary identifies its numbered recipe, update convention, observation
count, fitted power, base-2 intercept and multiplicative coefficient. The data
sources and selections are specified by those recipes in `../../figures/recipes/`.

The authoritative inputs are the numerical matrices and clearing-time CSVs.
Their generation parameters and hashes are recorded in
`../figure_states/states.json` and the JSON files beside the measurements in
`../clearing_times/north_first/`. Generated figure bundles also contain their
selected values and complete build provenance. The manuscript reads its
regression values directly from the figure build.
