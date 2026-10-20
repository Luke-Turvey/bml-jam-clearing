# Data accompanying the paper

`reference/` contains the clearing-time measurements. Files are headerless
`(n, clearing_time)` pairs. Blank lines and repeated observations are retained;
figure recipes specify their selections explicitly. `manifest.json` contains
SHA256 hashes for all reference files.

`figures/states/` contains the numerical matrices for the figure panels and the
original random initial state used in Figure 13. `figures/states.json` records
their hashes, physical parameters and North-first generation methods.

`north/` contains the freshly computed North-first Figure 6 and Figure 12
measurements, their provenance and resumable checkpoints. Current figure
recipes use these files or verified North-first reference measurements.
`historical/` retains metadata for the earlier mixed-convention figure records.
Historical random Figure 12 samples do not include seeds; current Figure 12
measurements instead use explicit seeded North-first simulations.
