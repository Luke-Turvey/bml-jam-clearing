# Mathematical checks

These finite checks support the paper's proofs and use literal update rules
independent of the maintained simulator. They do not replace the arguments for
arbitrary grid sizes.

Run from the repository root:

```bash
python miscellaneous/verification/check_linear_evolution.py --max-n 60 --output data/metadata/verification/linear-evolution.json
python miscellaneous/verification/check_trm.py --max-n 4 --output data/metadata/verification/trm.json
```

The linear-evolution check compares the Cartesian regional formula and every
labelled car trajectory against simultaneous moves at every time through
clearing. The Top Row Model check enumerates valid matrix-stack states and
verifies the update-map identities used in its monotonicity proof.

The saved reports cover 11,040 linear-evolution states and 2,448 Top Row Model
states. `algorithm-updates.json` records the independent comparison of the
appendix's arithmetic-mask algorithm with simultaneous directional updates.
