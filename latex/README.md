# Building the paper

This directory contains the manuscript, preamble, bibliography and algorithm
appendix. The manuscript includes the thirteen saved PDFs in
[`../figures/paper/`](../figures/paper/README.md). Regression coefficients and
sample ranges are loaded from the matching `figure_statistics.tex` in that
directory. These assets are included in version control.

From the repository root:

```bash
make -C latex
```

This compiles `latex/build/main.pdf` using the saved figures. It requires
`latexmk`, `pdflatex`, BibTeX, and the LaTeX packages used by `preamble.sty`
(including TikZ, PGFPlots, Forest and subfiles). Python is not required for
normal compilation. The build does not render figures or run simulations.
Missing saved figures produce an error rather than starting a computation.

## Update the saved figures

With the Python package installed, explicitly render the recorded numerical
data and replace the saved manuscript set:

```bash
python -m pip install -e .
make -C latex figures
make -C latex
```

The `figures` target renders into `figures/outputs/`, then saves copies of all
thirteen PDFs, their matching caption values and a checksum manifest into
`figures/paper/`. It does not run the simulation sweeps. Generating new outputs
with `bml figures` alone leaves the manuscript's saved figure set unchanged.
To save an already rendered complete build, use
`bml save-paper-figures --source figures/outputs`.

## Regenerate the numerical data

Simulation runs are separate, explicit steps. To regenerate the snapshot
matrices and Figure 6/12 measurements through n=999, then update the paper:

```bash
make -C latex refresh
make -C latex figures
make -C latex
```

To extend Figures 6 and 12 to the original size lists, through n=10000, use
`make -C latex full-data` instead of `refresh`. Full sweeps may take substantial
time. Completed observations are saved in
`data/clearing_times/north_first/checkpoints.json`, so an interrupted refresh
resumes from them. The saved captions report the sample counts, maximum sizes
and fits of the saved figure set.

All current simulations and numbered figures start with North updates at t=1.
The appendix retains the original exploratory classification tables and
identifies them as historical estimates; they are not recomputed by the figure
build. `figures/experiments/all-3x3.json` supplies the North-first exhaustive
sweep for a new survey.

The saved manuscript assets are small files intended for Git. Working outputs
in `figures/outputs/`, LaTeX auxiliary files and the compiled paper PDF remain
ignored. See [the data guide](../data/README.md) for the numerical sources of
every figure and the status of the appendix estimates.
