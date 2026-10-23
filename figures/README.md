# Paper figures

This directory contains the recipes, experiment configurations and rendered
outputs for Figures 1–13. The numerical inputs live in `../data/`, and the paper
source lives in `../latex/`.

| Location | Purpose |
| --- | --- |
| `recipes/figure01.json` … `figure13.json` | Exact panel, data-selection and fitting recipes |
| `experiments/` | Small checks, experiments over specified sizes and the exhaustive periodic experiment |
| [../latex/figures/](../latex/figures/) | Saved paper PDFs; included in version control |
| `../data/metadata/paper-figures.json` | Checksums and computation reports for the saved paper figure set |
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
selected states or clearing times and checks them against the records. Figure 3 evaluates an explicit formula
that is checked against the update rules in the tests.

The paper includes the saved PDFs in `../latex/figures/`. Its captions read
matching fits and sample ranges from `../latex/figure_statistics.tex`.
To replace that set from a complete rendered build, run
`bml save-paper-figures` from the repository root. Ordinary LaTeX compilation
uses the saved assets. See the [paper guide](../latex/README.md).
