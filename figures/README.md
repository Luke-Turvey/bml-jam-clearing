# Numbered figure recipes

Each `figureNN.json` defines one complete numbered figure in the paper.

```bash
bml figures all --output results/figures
bml figures 8 9 --mode simulate --output results/fault-lines
bml figures all --mode simulate --dry-run
```

State recipes refer to matrices and simulation inputs in
`data/figures/states.json`. Detail panels specify exact crop rectangles in the
original full-grid raster coordinates. Scaling recipes specify their CSV,
nonblank-row offset, axes and regression groups. See `docs/figures.md` for the
complete catalogue and `docs/reproducibility.md` for numerical conventions.
