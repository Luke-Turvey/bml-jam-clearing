# Data accompanying the paper

`reference/` contains the clearing-time measurements. Files are headerless
`(n, clearing_time)` pairs. Blank lines and repeated observations are retained;
figure recipes specify their selections explicitly. `manifest.json` contains
SHA256 hashes for all reference files.

`figures/states/` contains the numerical matrices for the figure panels and the
original random initial state used in Figure 13. `figures/states.json` records
their hashes, physical parameters, original source images and derivations.

Update conventions vary between datasets. The figure recipes and numerical
notes identify North-first and East-first experiments. Historical random
measurements for Figure 12 do not include seeds or initial states; its recorded
measurements remain available for plotting, and new simulations use explicit
random streams.
