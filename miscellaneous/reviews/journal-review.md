# Journal submission review

Manuscript: *Jam Clearing in the Biham–Middleton–Levine Traffic Model*, by
Alexander E. Holroyd and Luke A. Turvey. Reviewed 20 October 2026, against the
34-page compiled paper, the LaTeX sources, saved publication figures, numerical
records, recipes and maintained simulator. Source fingerprints and independently
recomputed fit diagnostics are recorded in [review-evidence.json](review-evidence.json).

**Recommendation: substantial revision before submission.** This is an assessment
of the current manuscript, not a prediction of an editor's decision. The central
extremal question, explicit periodic examples, residue-class effects and
reproducible numerical material could make a useful experimental mathematics
paper. The present version has errors in the formal proof, incomplete
justification of an infinite-family theorem, and experimental conclusions that
need more careful qualification. Copyediting alone will not resolve these issues.

No manuscript, figure, simulation source or numerical input has been changed by
this review. All proposed edits below are **pending author approval**. A proposal
to repair a proof is not a claim that the repair has already been established.

## Journal choice

My first choice would be **Experimental Mathematics**, after the revisions below.
Its stated scope includes experimental conjectures and formal results motivated
by computation. Its guidance also emphasises precise conjectures and repeatable
experiments. That combination fits the mathematical question and the companion
repository. The strongest framing would be: an extremal clearing problem, a
proved bound with a complete proof, explicit candidate families and a transparent
assessment of finite-size evidence. This recommendation is my judgement of fit;
it does not establish novelty or likely acceptance.
[Experimental Mathematics: aims and scope](https://www.tandfonline.com/journals/uexm20/about-this-journal).

**Journal of Statistical Physics** is a reasonable alternative if the paper
emphasises interacting dynamics, the clearing bound and the relation to jamming.
Its scope covers statistical physics and related collective phenomena.
[Official scope](https://link.springer.com/journal/10955/aims-and-scope).

**Physical Review E** is another plausible alternative if the work develops a
more quantitative study of scaling and geometric mechanisms, with stronger
finite-size analysis and random-sample uncertainty. Its remit includes
statistical physics, nonlinear dynamics and computational physics. This would
require more than changing the journal template.
[Official scope and criteria](https://journals.aps.org/pre/about).

I would prioritise the first two venues for the present mathematical emphasis.
The principal submission obstacle is the evidence and proof, rather than journal
formatting. A targeted current literature search did not establish a competing
finite-clearing theorem, but it is not a comprehensive novelty assessment.

## Assessment of the contribution

The main mathematical question is clear: how large can the clearing time of a
finite configuration be? Explicit periodic families and their sharply different
behaviour across residue classes give the experimental part a mathematical
purpose beyond pictures of traffic. The North-first convention, compact input
matrices, retained measurements, hashes and independent simulator checks are
valuable foundations for repeatability. The static saved figure set also makes
it possible to compile the paper without repeating expensive computations.

However, the paper currently merges four different levels of assertion:
proved finite-grid statements, exact identities observed at sampled sizes,
finite-range regressions, and proposed infinite-volume mechanisms. The revision
should keep these levels explicit while retaining ambitious conjectures.

## Proposed edits and approval ledger

Choose **approve**, **deny**, or **hold** for each ID. Every item is currently
pending. An approval of textual changes does not authorise a large simulation
campaign. E11 and E04 contain explicit alternative treatments; state which one
you prefer when approving them.

| ID | Priority | Proposed change | Decision |
| --- | --- | --- | --- |
| E01 | Essential | Correct and consistently define the Top Row Model state space and maps | Pending |
| E02 | Essential | Rework the monotonicity proof and the peeling argument supporting the quadratic bound | Pending |
| E03 | Essential | Fix the boundary proposition's update parity and complete its induction | Pending |
| E04 | Essential | Supply the odd-size argument for the linear theorem, or restrict its statement to even sizes | Pending: choose treatment |
| E05 | Essential | Separate the meanings of superlinear growth and correct the claimed equivalence | Pending |
| E06 | Essential | Qualify asymptotic claims and replace the abstract with accurately scoped wording | Pending |
| E07 | Essential | Add fit-range sensitivity and alternative-scaling diagnostics from existing measurements | Pending |
| E08 | Important | Report the observed affine formulas for the linear residue branches; resolve the appendix coefficient | Pending |
| E09 | Essential | State the random-data target and report replication and variability | Pending |
| E10 | Essential | Add a self-contained methods and data-availability subsection | Pending |
| E11 | Essential | Move unverified survey tables to supplementary material, or regenerate and validate them | Pending: choose treatment |
| E12 | Important | Recast phase-transition and geometric mechanisms as explicitly conditional heuristics | Pending |
| E13 | Important | Improve legends, crop location, state keys and figure captions | Pending |
| E14 | Important | Reorganise the discussion and split the algorithm and survey appendices | Pending |
| E15 | Important | Correct bibliographic records and qualify literature-wide claims | Pending |
| E16 | Minor | Apply copyediting, notation and submission-metadata corrections | Pending |

### E01 — Top Row Model definitions

Sources: `latex/main.tex:154–195`.

The written state-space condition is `M(i,j)=0 if i>j`, but the shift map retains
entries with row index at least the destination column. These conventions
contradict one another. This is a demonstrated error, not just a preference for
matrix notation.

For example, at n=3 a state whose only nonzero column is
`M(.,2)=(2,2,0)` is valid under the written definition. Moving this stack to
column 3 and deleting its old diagonal entry gives `(2,0,0)` in column 3,
which violates the stated condition on nonzero columns. Consequently the claim
that the dynamics preserve the valid state space is false as written.

The apparent intended convention has `M(i,j)=0` for **i<j**, with the future
waiting-time entries at i>=j. Rewrite all three validity conditions together
under that convention, explain the coordinate orientation, and check every
displayed update against it. Define explicitly how a stack exits from column n
and how simultaneous assignments are combined.

The formal definition of `g_{i,j}` also changes every 4 to 2, although the prose
requires changing only the specified entry. The proposed replacement is:

```latex
\bigl(g_{i,j}(M)\bigr)(k,l)=
\begin{cases}
2, & (k,l)=(i,j)\text{ and }M(i,j)=4,\\
M(k,l), & \text{otherwise}.
\end{cases}
```

Replace the undefined `A` in the monotonicity lemma with the valid-state space
`\mathcal M`. Explain why the generated relation is an antisymmetric order,
rather than merely referring to its transitive closure. Specify the clearing
time of the zero state as well.

### E02 — Proof of the quadratic bound

Sources: `latex/main.tex:202–262`.

The monotonicity case check has false identities. At line 212,
`f_{j+2}\circ f_j` should be `f_{j+1}\circ f_j` in the corresponding two-shift
case. With the intended triangular convention, a sole stack `(4,2,4)` in
column 1 of a 3-column system gives a concrete witness: the printed composition
does not advance the stack to column 3 as required. Line 222 also applies maps
to `M_t` where the argument needs the updated state, and contains incomplete
parentheses. Assertions about unaffected adjacent columns at lines 207 and 209
are too broad. These are substantive problems in the written verification.

Rewrite the argument using labelled stacks and their remaining waiting-time
lists, or provide a complete corrected local case table. Verify the corrected
finite cases independently, but retain a mathematical proof for arbitrary n.
Correcting the definitions in E01 alone is insufficient.

The final peeling argument has a separate timing gap. It bounds North-car
clearance of the rightmost column by time **8n−3**, then discards the boundary
at **8n−4**. The former statement does not imply the latter. Furthermore, the
quadrant proposition starts with no exterior cars; it cannot be applied without
explanation after restarting with cars already outside a smaller square. A car
that subsequently moves freely can still occupy the destination of a car's
first attempted move under simultaneous updates.

State an induction invariant controlling the restart time, update parity,
remaining interior configuration and residual exterior cars. Derive the stage
costs from that invariant, then sum them. Retain **5n²−n** only if the repaired
argument actually proves that coefficient and lower-order term. The intended
algebra `sum_{k=1}^n ((8k−4)+2(n−k))=5n²−n` is correct; the issue is justifying
its summands for the process.

Exhaustive small-grid checks found maximum clearing times **2, 9 and 17** for
n=1,2,3, respectively. They found no counterexample to the bound and do not
certify its proof. The simulator raises an error if its default theorem-based
time cap is exceeded, so it does not silently replace longer clearing times by
the cap. Independent checks of the theorem should nevertheless use a separately
justified conservative stopping rule.

### E03 — Boundary proposition

Sources: `latex/main.tex:120–140`.

The proof studies the transition from time t to t+1, but assumes t is even when
considering East motion. Under the stated model, the **destination time t+1**
must be even, so t must be odd. Express all transitions using their destination
time and check the North case analogously.

Add the induction base case in the free-flow lemma. Define exit times when they
are finite, rather than implicitly assuming every car in an arbitrary
infinite quadrant configuration exits. The lemma appears plausible; the
identified parity error concerns its use in the proposition.

### E04 — Explicit linear family

Sources: `latex/main.tex:288–328`.

The theorem states `T(W_n,n)=6n−4` without a parity restriction, while the
displayed evolution formula is supplied only for **even n**. There is no
odd-size proof. Small simulations for n=1 through 11 satisfy the formula,
including odd sizes: this is a proof gap, not a discovered counterexample.

Preferred treatment: add a complete odd-size argument and a sufficiently
explicit verification of the piecewise evolution. Alternative: restrict the
proved theorem to even n and state the odd-size extension as a conjecture
until it is proved. This choice changes the scope of a theorem and should be
approved explicitly. Finite automated checks can support the argument but
cannot replace the missing all-n proof.

### E05 — Definitions, quantifiers and implication

Sources: `latex/main.tex:47–57`.

The following properties differ:

1. T(n) is not O(n).
2. T(n)/n tends to infinity.
3. T(n)>=c n^alpha eventually, for some alpha>1.

The third implies the second, which implies the first; the converses do not
hold. In particular, n log n satisfies the first two but not the third.
Define the term used in the paper and keep the polynomial conjecture separate.
Put its quantifiers in the order: there exist c>0 and alpha in (1,2] such that
the inequality holds for every n, or for every sufficiently large n.

The claimed equivalence between a superlinear **fixed periodic** family and
failure of a linear bound on the maximum is unsupported. Maximising
configurations could require patterns that vary with n. Replace the sentence
with:

> Proving the existence of a superlinear periodic sequence would, in particular,
> rule out a linear upper bound for the maximal clearing time.

Separate conjectures about a fixed tile, residue subsequences and unrestricted
maximising configurations. Avoid treating their quantifiers as interchangeable.

### E06 — Abstract and strength of the empirical claims

Sources: `latex/main.tex:10`, `53`, `70`, `267–269`, `348`, `381`, `445–453`.

Replace definitive asymptotic language with finite-range observations followed
by explicitly labelled conjectures. For example, the statement that removing a
boundary increases the clearing time by **at least** n^0.21 does not follow
from a regression with slope near 1.21. Report the measured comparison and
formulate a separate conjecture about an unbounded ratio. Likewise, a finite
sample cannot establish a property that holds asymptotically with high
probability.

Suggested replacement at line 381:

> For the sampled sizes, the residue-two subsequence has a fitted exponent
> greater than one, whereas the other residue classes are consistent with
> linear growth. We conjecture that this distinction persists asymptotically.

Suggested replacement at line 453:

> The sampled fully occupied random configurations also exhibit fitted growth
> exceeding linear growth over the investigated sizes. Determining their
> asymptotic clearing behaviour remains open.

Suggested abstract, **conditional on a completed proof of the stated bound**:

> We study the time required for a finite Biham–Middleton–Levine configuration
> to empty an n-by-n square under alternating North and East updates with open
> boundaries. We prove that the maximal clearing time is at most 5n²−n.
> Computations for spatially periodic and independently sampled fully occupied
> configurations produce finite-size growth consistent with superlinear
> clearing times. We identify explicit candidate families, examine sensitivity
> to the residue class of n, and describe geometric features of their
> evolution. The existence of a superlinear family remains open.

This preserves the mathematical ambition while accurately describing what the
displayed experiments establish.

### E07 — Regression robustness

Sources: `latex/main.tex:365`, `385`, `449`; the Figure 6/7/12 CSVs and recipes.

Independent OLS calculations on the existing records give the following
slopes. Parentheses give the number of observations. The original weighting
and row selections are retained; no new simulations were used.

| Data group | Current selection | n>=100 | n>=300 | n>=1000 |
| --- | ---: | ---: | ---: | ---: |
| Figure 6 | 1.229813 (28) | 1.287190 (13) | 1.280159 (7) | — |
| Figure 7, residue 2 | 1.213447 (29) | 1.296920 (18) | 1.338192 (12) | 1.395707 (5) |
| Figure 7, residues 0/1 | 1.022925 (41) | 1.001958 (23) | 1.000946 (17) | 1.000303 (10) |
| Figure 12 | 1.178147 (110) | 1.143485 (49) | 1.146297 (25) | — |

The five residue-two observations passing n>=1000 are actually at sizes from
2000 to 5999. These increasingly sparse fits do not determine a limiting
exponent. In particular, **1.21 should not be presented as a stable asymptotic
exponent**.

Add this sensitivity analysis, plots of T(n)/n and effective slopes or
residuals, and a comparison with plausible alternatives such as an affine
model, n log n and finite-size corrections. State fitting objectives, weights,
number of parameters and any model-comparison criterion. A better finite-range
fit still does not prove an asymptotic law. Deterministic measurements do not
have independent sampling errors; conventional regression confidence intervals
would obscure systematic finite-size variation.

Give a scientific reason for dropping the first three rows in Figure 7 and
the first 30 in Figure 2, or report how the conclusion changes with that choice.
Do not choose cutoffs solely because they produce a preferred exponent.

### E08 — Linear branches and the printed coefficient

Sources: `latex/main.tex:381–385`; `latex/sections/appendix.tex:1717`;
`data/clearing_times/historical/log2_133333113.csv`.

All 20 supplied observations with n divisible by 3 satisfy
`T=(22n−30)/3`. All 22 observations with n congruent to 1 modulo 3 and n>=4
satisfy `T=(22n−28)/3`; the separate n=1 observation has T=2.

These are exact identities **on the observed sizes**, not all-n proofs.
Report them as such and, if desired, formulate explicit conjectures. They are
more informative for the putatively linear branches than a pooled fit to
n^1.022925, whose slope approaches one after small sizes are excluded.

The appendix gives coefficient **7** for this tile, rather than the observed
**22/3**. Recover and explain its rounding convention, phase or source, or
correct/remove the unsupported number. Do not silently present it as an exact
linear coefficient.

### E09 — Random configurations

Sources: `latex/main.tex:445–453`; Figure 12 generation metadata.

The random study has 110 realisations at **29 distinct sizes**, through n=999.
Most sizes have 3–5 observations, n=327 has one, and the four largest sizes
(597,717,864,999) have only three each. State these replication counts and
show the variability.

Specify the quantity of interest: arithmetic mean, median, geometric mean or
a probability statement. OLS on individual log times fits the observed log
times with replicate-dependent weights; it is not automatically a model for
the arithmetic mean clearing time. A claim about high-probability behaviour
needs a precise event and much stronger supporting evidence.

State prominently that every initial site is independently East or North with
probability one half: this is **p=1**, not an experiment across positive
densities. Report the seed and the independent size/replicate stream scheme.
Improved reporting and descriptive uncertainty can use the current data;
additional independent realisations are a separate experimental decision.

### E10 — Methods, ranges and availability

Sources: `latex/main.tex:109–145`, `361`, `409`, `449`; repository data guide.

The paper should explain the design without requiring a referee to infer it
from JSON recipes. Add the bottom-left tile phase, row-major encoding, time
unit, simultaneous movement, first-update convention, boundary removal,
stopping rule, actual size lists, replication, row selections, seeds, fitting
weights and validation methods.

| Figure/data group | Observations | Actual n range |
| --- | ---: | --- |
| 2 | 43 | Selected larger sizes, through 10000 |
| 6 | 28 | 3–999 |
| 7, residue 2 | 29 | 5–5999 |
| 7, residues 0/1 | 41 | 4–10000 |
| 12 | 110 at 29 sizes | 3–999 |

The methods' statement about runs through n=10000 is not globally false:
Figures 2/7 retain such measurements. Distinguish those completed original
experiments from the new Figure 6/12 sweeps through 999 and from optional
configurations that have not been run. Identify which retained records support
the claim of more than one million time steps; runnable code alone is not
evidence of a completed experiment.

Remove the unbenchmarked speed comparison with “traditional implementations”,
or provide actual hardware, timings and a clearly specified baseline. Cite
NumPy in the implementation description.

Add a versioned public code/data URL and release identifier once available,
with the environment used for the submitted figures. Do not invent an archive
DOI. Explain that ordinary paper compilation uses saved assets; image
regeneration and numerical replay are separate operations. This remains
compatible with the requested static manuscript build.

### E11 — Exhaustive survey: explicit author choice

Sources: `latex/main.tex:267`, `350`; `latex/sections/appendix.tex:28–29`, `1692`;
the limitations already documented in `data/README.md`.

The appendix does contain all **512 unique fully occupied 3-by-3 tiles**:
276 are labelled superlinear and 236 linear. The issue is not missing tiles.
The printed estimates are not all linked to identified runs or recomputed
under the current convention. An experiment configuration alone does not
reproduce the classifications or their printed coefficients. The main-text
claim of an exhaustive classification therefore needs qualification.

**Recommended treatment A:** move the original detailed catalogue to clearly
labelled supplementary exploratory material, remove it from the argument
supporting current conclusions, and narrow the main claims to the verified
experiments. Keep the original material available without presenting it as a
validated current classification.

**Alternative treatment B:** recompute and validate the survey under a single
phase/update convention, recover the classification rules and fitting ranges,
and generate the printed tables from machine-readable results. Identify the
specific size subsequences being classified, since the same tile can behave
differently by residue. This includes experimental and analysis work and is
not part of a purely textual approval.

If neither treatment is approved, the unresolved provenance should remain a
clearly visible submission limitation.

### E12 — Heuristics and geometric language

Sources: `latex/main.tex:96–106`, `340–348`, `389–421`, `452`.

The finite-jam feedback mechanism does not follow from a large isolated
clearing time. It additionally assumes sustained blocking over an appropriate
cross-section, sufficient incoming flux and the formation of another slow jam.
Nonmonotonicity creates a further obstacle: surrounding cars may reorganise or
accelerate the original configuration. Rare-pattern occurrence in an infinite
i.i.d. field does not alone establish a growing jam or global fixation.

Suggested replacement introduction to that discussion:

> Superlinear worst-case clearing times would not alone imply almost-sure
> jamming at positive density. The following feedback mechanism is heuristic:
> it assumes that incoming traffic preserves long delays and creates another
> sufficiently slow jam. Neither assumption is established by the finite
> open-boundary experiments reported here.

The possibility of a density threshold tending to zero was already discussed
in the introduction of [Austin and Benjamini (2006)](https://arxiv.org/pdf/math/0607759).
Distinguish that finite-torus discussion from an infinite-lattice conjecture
and explain what the finite-clearing viewpoint adds. The bootstrap-percolation
analogy is motivation, not a transfer of a theorem to this nonmonotone model.

Use “irregular” descriptively in place of formal-sounding “chaotic” or
“aperiodic”, unless those terms are defined and tested. Counts of fault-lines,
claims of superlinearly many jams, and the proportion of moved cars during
reorganisation need operational definitions and measurements to become
quantitative conclusions. Otherwise label them explicitly as visual
observations or possible mechanisms. Do not infer a causal delay from a single
snapshot of a highway.

### E13 — Figures and captions

Sources: `latex/main.tex:75`, `83`, `336`, `365`, `385`, `406`, `415`, `435`,
`441`, `449`, `457`; saved figures and `src/bml/figure_rendering.py`.

Figure 7 uses identical markers for both residue populations and identical
line styles for both fits, with no identifying legend. Use distinct markers
and line styles, also readable without colour; do the same for Figure 2.
Give each fitted group's count and range. In particular, the residue-two
branch ends at **5999**, despite the combined Figure 7 range ending at 10000.

State the key **red = East, blue = North, white = vacant** prominently and
consistently. Give snapshot panel labels, n, t, and coordinates in captions.
Define the tile encoding before captioning Figure 4 with `333131313`.

In Figure 1 explain that the panels are at matched scaled times t=5n, namely
3000 and 2995, rather than the same absolute time. Give their measured clearing
times 4390 and 7207. These are useful finite observations of the deletion
effect; the asymptotic ratio remains conjectural.

Mark the detail regions on the full grids for Figures 8–11, and identify them
with lattice coordinates. Replace “selected by the figure recipe” with
scientific information that makes the figure self-contained. Describe the
distribution and archived initial matrix for Figure 13, rather than referring
only to a supplied matrix. Show random variability in Figure 12 and use its
caption to state replication and the fitted quantity.

These changes would deliberately replace the saved publication assets once
approved. They do not require launching large simulations, and the normal
LaTeX build would remain static.

### E14 — Structure and balance

Keep the finite-clearing question and the precise results/conjectures early.
Put the experimental protocol before the numerical conclusions. Move the
infinite-volume speculation to a discussion after the finite results, where
its assumptions and limitations can be assessed. Add a short final discussion
listing established results, strongest open questions and current evidence
limits.

Split the vectorised algorithm and the classification catalogue into separate
appendices or supplementary material. At present both are under “Vectorised
Algorithm”, and references to that appendix mean different things in different
paragraphs. Reduce repetition of the same 3-by-3 tile at equations 1 and 5.
Improve float placement: Figure 12 currently occupies a largely empty page.
Do not solve this by shrinking labels to an unreadable size.

### E15 — Bibliography and relation to prior work

Sources: `latex/refs.bib`; `latex/main.tex:30`, `145`.

The original BML paper is entered as a book with a combined author field. Use
an article record with three separately parsed authors, the journal, volume,
pages and DOI. [Publisher record](https://doi.org/10.1103/PhysRevA.46.R6124).

Where it supports the same discussion, replace the D’Souza preprint citation
with the published article, whose title is *Coexisting phases and lattice
dependence of a cellular automaton model for traffic flow*, Physical Review E
71, 066112 (2005). Resolve the incomplete duplicate entry.
[Author-hosted published article](https://mae.engr.ucdavis.edu/dsouza/Pubs/dsouza-p4.pdf).

Correct the spelling and BibTeX parsing of van Enter, normalise DOI fields and
protect proper names/acronyms in titles. Check for published successors to the
2023 preprints before the final submission. Cite the implementation libraries
actually used.

The claim that a particular theorem is the “only rigorous progress” should be
qualified by its exact setting and checked against current literature. The
2005 result establishes jamming for sufficiently high density; distinguish it
from torus, modified-model or finite-clearing results.
[Angel, Holroyd and Martin](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/12/bml.pdf).
A targeted search is not proof that no other relevant theorem exists.

### E16 — Copyediting, notation and metadata

Apply these specific corrections after the scientific changes:

| Location | Correction |
| --- | --- |
| `main.tex:27` | Repair the misplaced parentheses in the empty-site probability |
| `main.tex:53` | “a periodic of n” -> “a periodic function of n” |
| `main.tex:130,140,260,328,331` | Correct variants of “similiar/similiary” |
| `main.tex:134` | “neigbours” -> “neighbours” |
| `main.tex:150` | “Theorem ... the time to clear” -> “Theorem ... for the clearing time”; “can found” -> “can be found” |
| `main.tex:162` | “the a temporary” -> “a temporary” |
| `main.tex:265` | Require a positive integer period and close the set-membership parenthesis |
| `main.tex:286` | Remove repeated article; “infeasabile” -> “infeasible” |
| `main.tex:389` | “phenomona” -> “phenomena” |
| `main.tex:391,421` | Use singular “phenomenon” where appropriate |
| `appendix.tex:22` | Append a **column**, not a row, to the left |

Standardise British spelling, “superlinear”, “subsequence”, “piecewise” and
“space–time”. Use references rather than hard-coded lemma numbers. Repair the
malformed summation parentheses in the theorem proof. Check the indexing and
domains of all maps after the TRM rewrite.

For submission, add author-provided affiliations/contact information,
appropriate keywords and classifications, acknowledgements/funding where
applicable, and the versioned data-availability statement. Do not fabricate
these details. Clean duplicate package loads, unused draft-note macros and
redundant externalisation settings; provide useful PDF metadata and unobtrusive
links. Follow the selected journal's current template after substantive
revision.

## Further experiments: separate from edit approval

The following are recommended research extensions, not necessary to write an
honest account of the current finite evidence, and are not authorised by an
approval of E01–E16 alone:

| Study | Purpose | Needs additional simulations? |
| --- | --- | --- |
| Extend the residue-two branch with more matched sizes | Compare residue classes over similar ranges | Yes |
| Extend Figure 6/12 to the configured larger sizes | Assess whether fitted trends persist | Yes, potentially expensive |
| More independent random realisations at larger n | Characterise spread and assess a precisely stated probability claim | Yes |
| New survey under one convention | Replace the unverified classification catalogue | Yes, under E11 treatment B |
| Measure fault-lines/highways across sizes and times | Turn visual mechanisms into testable quantitative statements | Usually yes, unless adequate saved states exist |
| Prove one observed affine residue formula | Establish a rigorous example beyond finite observations | Mathematical work; simulation alone is insufficient |

Before submission, I would prioritise E01–E06 and the survey decision, then the
existing-data analyses and methods. Extending the maximum grid size is useful
research, but it does not repair a proof or substitute for clearly stated
limitations.

To authorise changes, reply with IDs, for example:
`approve E03,E05,E06,E10,E15,E16; hold E01,E02,E04,E07,E08,E09,E11,E12,E13,E14`.
For E04 choose “prove odd sizes” or “even-only theorem”; for E11 choose
“supplementary catalogue” or “recompute survey”. Denied or unmentioned items
will remain unchanged.
