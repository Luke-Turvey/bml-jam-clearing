# Supplementary research material

| Location | Contents |
| --- | --- |
| [survey/](survey/README.md) | Measurement, fitting and diagram generation for the paper's complete 512-tile catalogue |
| `verification/` | Finite checks of the paper's mathematical formulas and update-map arguments |
| `scripts/` | Exploratory simulations, searches, animations and model variants |
| `notebooks/` | Plotting and exploratory analysis |

`scripts/` contains exploratory simulation, search, animation and analysis
programs, including the blocked-model and vanishing-model variants under
`scripts/model_variants/`. `notebooks/` contains the original plotting notebook.
These files document the research; the maintained paper workflow is in
`../src/bml/`, with recipes in `../figures/recipes/`.

The notebook reads the historical CSVs from `../data/clearing_times/historical/`.
Many exploratory scripts retain their original working-directory assumptions,
such as `csv_files/`, `images/` and `videos/`, and some start work when imported.
They require their own data-path setup and are not used by the figure build or
its tests. Optional analysis dependencies are available with
`pip install -e '.[legacy]'`; video export also requires FFmpeg.

Saved evolution snapshots and videos are labelled under `../data/`, rather than
mixed into the script directories. See the
[data provenance guide](../data/README.md) for their roles.

The survey uses the measurements in
`../data/clearing_times/survey_north_first/`. The paper includes its saved
catalogue directly; compiling the LaTeX source does not rerun the analysis.
