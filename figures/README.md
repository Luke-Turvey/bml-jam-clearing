# Paper figures

This directory contains the recipes, experiment configurations and rendered
outputs for Figures 1–13. The numerical inputs live in `../data/`, and the paper
source lives in `../latex/`.

| Location | Purpose |
| --- | --- |
| `recipes/figure01.json` … `figure13.json` | Exact panel, data-selection and fitting recipes |
| `experiments/` | Small checks, size sweeps and the exhaustive periodic experiment |
| [paper/](paper/README.md) | Saved manuscript PDFs, matching numerical captions and checksum manifest; included in version control |
| `outputs/` | Generated PNG/PDF bundles, numerical sidecars and provenance; ignored by Git |
| [FIGURE_CATALOGUE.md](FIGURE_CATALOGUE.md) | Parameters, row selections and crops for every figure |
| [NUMERICAL_NOTES.md](NUMERICAL_NOTES.md) | Model conventions, regression definitions and validation |
| [Data provenance guide](../data/README.md) | Where each paper dataset comes from and how it is regenerated |

From the repository root:

```bash
bml figures all --update
bml figures 8 9 --mode simulate --output figures/outputs/fault-lines
bml figures all --mode simulate --dry-run
```

Recorded mode uses the supplied numerical inputs. Simulation mode recomputes
selected states or clearing times and checks them against the records. Every
active simulation starts with North cars. Figure 3 evaluates an explicit formula
that is checked against the update rules in the tests.

The paper includes the saved PDFs in `paper/`. Its captions read matching fits
and sample ranges from `paper/figure_statistics.tex`. `make -C latex` only
compiles the manuscript from those saved assets. Use `make -C latex figures`
explicitly to render the recorded data and replace the saved set. Simulations
remain separate commands.
