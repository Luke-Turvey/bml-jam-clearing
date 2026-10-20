# Saved manuscript figures

This directory is the fixed figure set included by `latex/main.tex`:

- `figure01.pdf` through `figure13.pdf` are the saved publication images.
- `figure_statistics.tex` contains their matching regression values and sample ranges.
- `manifest.json` records file checksums and the computation reports associated
  with this figure set.

These small PDF assets and caption values are included in version control.
The normal `make -C latex` build reads them without running Python, rendering
figures, or simulating the model. Regenerating `figures/outputs/` does not change
the manuscript's saved figures.

To replace the complete publication set explicitly, from the repository root:

```bash
make -C latex figures
make -C latex
```

The first command renders from the recorded numerical data and saves a matched
set of PDFs, captions and checksums. To save an already rendered complete build
without redrawing it, use `bml save-paper-figures --source figures/outputs`.
Simulation commands and data refreshes are separate operations.
