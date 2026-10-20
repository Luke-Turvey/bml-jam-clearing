# Paper source and generated figures

This directory contains the manuscript, preamble, bibliography and algorithm
appendix. The manuscript includes `generated/figureNN/figureNN.pdf` directly;
these are outputs of the repository's numbered-figure renderer. Regression
coefficients and sample ranges are loaded from `generated/figure_statistics.tex`.

From the repository root, install the package and build the paper:

```bash
python -m pip install -e '.[test]'
make -C paper
```

This requires `latexmk`, `pdflatex`, BibTeX, and the LaTeX packages used by
`preamble.sty` (including TikZ, PGFPlots, Forest and subfiles). The resulting PDF
is `paper/build/main.pdf`. A build regenerates figures from the supplied
North-first numerical records; it does not launch the large simulation sweeps.

To regenerate the snapshot matrices and the new Figure 6/12 measurements up to
n=999, then rebuild:

```bash
make -C paper refresh
make -C paper
```

To extend Figures 6 and 12 to the original size lists, up to n=10000:

```bash
make -C paper full-data
make -C paper
```

The full sweeps may take substantial time. Completed observations are saved in
`data/north/checkpoints.json`, so an interrupted refresh resumes from them.
The captions use the actual generated sample counts, maximum sizes and fits.

All current simulations and numbered figures use North updates at odd times,
starting at t=1. The appendix retains the original exploratory classification
tables and identifies them as historical estimates; they have not been
recomputed as part of the figure build. `configs/all-3x3.json` supplies the
North-first exhaustive sweep for a new survey.

Generated figures, LaTeX auxiliary files and the compiled PDF are ignored by Git.
The source files and numerical data are sufficient for a fresh build.
