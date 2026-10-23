# Complete 3-by-3 tile survey

The survey contains all **512** fully occupied 3-by-3 tiles, each simulated at
all **166** sizes `n = 3, 6, ..., 498`: **84,992 clearing times**. North
updates occur at odd times, East updates at even times, and time counts one
directional update. Cars leave through the North or East boundary. Every tile
is anchored at the bottom left; its nine digits are read top to bottom and
left to right, with 1 denoting East and 3 North.

| File | Contents |
| --- | --- |
| `<nine-digit tile>.csv` | Header `n,clearing_time` and all 166 measurements for that tile |
| `metadata.json` | Completed run parameters, compiler/flags, source/binary hashes, elapsed time and SHA256 for each tile CSV |
| `validation.json` | All 589 independent-backend validation comparisons |
| `analysis.json` | Analysis specification, rational affine-plus-periodic formulas, exact checked ranges, five cutoff fits per tile and comparison source references |
| `summary.json` | Descriptive totals and six selected examples, including the principal paper tiles |
| `catalogue.csv` | Compact descriptive catalogue suitable for analysis |
| `independent-validation.json` | Raw CSV hash checks, independent period-selection checks and exact rational formula validation |
| `printed_catalogue.json` | Immutable mapping of the 512 original printed estimates and source lines, with the original appendix SHA256; used for comparison only |

The analysis uses equal weight per sampled size in ordinary least squares on
`log2(T) = power*log2(n) + intercept`, at lower-size cutoffs 3, 30, 100, 250,
and 350. The strict descriptor **observed affine tail** requires every
successive difference `T(n+3)-T(n)` to be exactly equal at the last 56 sizes,
n=333 through 498. All other tiles have descriptor **observed non-affine tail**.
An affine law plus a periodic correction can fail this criterion. Neither
descriptor nor a fitted slope assigns an asymptotic growth class.

The exact formula search tests `T(n)=a*n+b[(n/3) mod p]` for `p=1,...,12`.
It selects the smallest period matching all 77 sizes from 102 through 330,
then checks the fixed rational coefficients at all 56 sizes from 333 through
498. This gives 166 affine formulas and 69 formulas with nonconstant periodic
corrections; the remaining 277 tiles retain power fits. These statements refer
to the finite observations and do not establish asymptotic growth laws.

The exploratory printed catalogue is retained as a comparison field, with its
source lines, rather than serving as an input to any fitted formula. The
paper's catalogue in `latex/sections/survey.tex` is generated directly from the
saved measurements and their derived analysis.

Generation, validation and analysis commands are documented in
[the survey code guide](../../../miscellaneous/survey/README.md).
