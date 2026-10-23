# Periodic-tile survey

This experiment measures the fully occupied 3-periodic tilings at every size
`n = 3, 6, ..., 498`.
The 512 tiles and 166 sizes give **84,992 observations**. The measurements
and their analysis generate the paper's catalogue of periodic tilings.

The standalone C++17 backend stores rows as 64-bit occupancy masks. It uses
simultaneous updates and removes cars crossing the North or East boundary.
Completed measurements are checkpointed in a separate CSV for each tile.

Run from the repository root, with a C++17 compiler and the normal Python
dependencies available:

```bash
g++ -O3 -std=c++17 -Wall -Wextra -pedantic miscellaneous/survey/bitset_survey.cpp -o /tmp/bml-bitset-survey
PYTHONPATH=src python miscellaneous/survey/run_survey.py --workers 6
python miscellaneous/survey/analyse_survey.py
```

The runner allows one to six workers and resumes from complete CSV rows.
`--validate-only` runs the independent comparisons without launching the survey.
`--binary` and `--output` select another compiled backend or data directory.
The analysis command reads the canonical data directory.
It writes the catalogue directly to `latex/sections/survey.tex`; compiling the
paper uses that saved file and does not run the analysis or simulations.

Validation exhausts all 512 binary 3-by-3 states against a separate literal
car-by-car implementation. Another 72 comparisons cover partial tiles and
sizes on either side of 64-bit word boundaries, using the literal reference
for small grids and the maintained NumPy simulator for larger ones. Five
existing Figure 6 observations, including n=498, provide additional checks.

The independent stopping budget is `2*n**3+2`, which does not rely on the
paper's sharper quadratic theorem. If a configuration is nonempty, some car
has maximal sum of coordinates. If neither of the next two directional updates
moves any car, that car would have an occupied destination with a larger
coordinate sum, a contradiction. Thus at least one car moves during every pair
of steps before clearing. Each of at most n² cars makes at most n moves before
leaving, giving the conservative budget.

The power fits and original strict affine-tail diagnostic are specified in
[analysis-plan.json](analysis-plan.json). The power fits use ordinary least
squares in `log2(T) = alpha*log2(n) + log2(C)`, with equal weight per sampled
size; `C*n**alpha` is fitted over the 133 sizes 102 through 498 and retained
in the numerical catalogue for cases without a validated exact formula; these
277 cases appear under conjectured power laws in the paper's appendix.

The exact formula search is specified in
[affine-periodic-plan.json](affine-periodic-plan.json). With `q=n/3`, it tests
`T(n)=a*n+b[q mod p]` for periods 1 through 12. The smallest period fitting all
77 training sizes, 102 through 330, is selected using rational arithmetic.
Its fixed coefficients must then match all 56 validation sizes, 333 through
498, exactly; the search does not switch to another period after validation.
Every tested residue has at least six training and four validation observations.
The same coefficients are also checked against earlier measurements to record
their earliest exact suffix, without refitting.

The saved measurements give 166 affine formulas (`p=1`), 69 formulas with a
nonconstant periodic correction, and 277 remaining power fits. The nonconstant
period counts are 48 with `p=3`, three with `p=4`, 17 with `p=9`, and one with
`p=12`. Every selected exact training model passed validation. These are
finite-data results for sizes divisible by three, and establish no asymptotic
classification or formula at unmeasured sizes.

`independent-validation.json` records checks of all 512 CSV hashes against the
completed simulation metadata, independent minimum-period checks using first
differences, and exact integer cross multiplication of every stored rational
formula across all 133 training and validation sizes. Synthetic tests cover
phase alignment, a rational slope, rejection after a changed validation value,
and a genuinely quadratic sequence:

```bash
python -m pytest tests/test_survey_analysis.py
```

`printed_catalogue.json` retains the original 512 printed values and source
lines for comparison only, together with the original appendix SHA256. The
analyser reads this immutable mapping rather than parsing the current LaTeX
appendix, so replacing the manuscript's catalogue does not change the analysis.

Results and checksums are in `data/clearing_times/survey_north_first/`. The
full coefficients, periods, fits and checked ranges are in `analysis.json`,
with a compact `summary.json` and a per-tile `catalogue.csv`. The generated
LaTeX catalogue is `latex/sections/survey.tex`.
[render_survey.py](render_survey.py) renders its tile diagrams using the paper's
TikZ car commands. The paper displays all 512 cases, with the 235 affine or
periodic cases collected together and the 277 conjectured power laws in a
second group. Diagrams are enlarged, with no printed identifiers, period
lengths or offset lists; the full coefficients remain in the data files.
Running only the analysis command regenerates the derived
files and the LaTeX catalogue from saved measurements without running any
simulations.
