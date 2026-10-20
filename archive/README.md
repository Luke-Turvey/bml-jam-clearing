# Supplementary research scripts

`scripts/` contains the exploratory simulation, search, animation and analysis
programs. `notebooks/` contains the plotting notebook. The numbered figure
workflow is implemented in `src/bml/`, with recipes in `figures/`.

These research scripts use working-directory paths such as `csv_files/`,
`images/` and `videos/`, and some start computations at import time. To run one,
use a separate working directory with the required data paths and add this
`scripts/` directory to PYTHONPATH. Optional dependencies are available through
`pip install -e '.[legacy]'`; video export also requires FFmpeg.
