# PREREG — microtubule-lattice-memory v0.1.0

Written BEFORE the demo run. Bars are fixed here and are
not moved after seeing demo results.

## What changed from microtubule-crystallize v0.1.0

That package's Exp4 was NEGATIVE: outer-product recall
accuracy was 1.000 for seam shift, row slip, and catastrophe
front, exactly like same-count random flips. The reason,
proved in its DESIGN.md, is permutation-equivariance: the
outer product only cares how many cells match, not which
cells or how they sit on the lattice.

Prototype exploration (single seed 42, NOT the demo)
found two things, and this package is built on both:

1. Iterative lateral recall does NOT fix Exp4. With a
   generic lattice term, lambda >= 2 degrades even clean
   recall (0.929 at lambda 2, vs 1.000 outer product),
   and the corruption-vs-random gap stays ~0. That
   design is recorded as falsified in DESIGN.md, not shipped
   as the headline.
2. A pattern-specific lateral score DOES separate structured
   probes from scattered probes at equal overlap. The
   score is defined in lat.py: mean over neighbour pairs
   of (stored product) x (probe product). Prototype seed 42:
   seam 0.712 vs random 0.558, slip 0.893 vs 0.849,
   catastrophe 0.906 vs 0.486.

## The lattice-aware memory, honestly stated

Recall itself is unchanged: outer-product, one step.
What is lattice-aware is the SCORE and the GATE:
combined score S = 0.5 * overlap + 0.5 * lateral_score,
weights fixed here, not tuned after the demo. The gate
calibrates tau on S by Youden's J on validation probes
only, then freezes it, exactly as in the refusing family.
A probe is accepted only if S >= tau.

This package therefore claims a lattice-aware GATE, not
a lattice-aware recall. Recall accuracy is reported and
flagged as ceiling where it is 1.000.

## Bars (demo: patterns seeds 42, 43, 44; reps 20 per
## corruption per seed; random same-count controls seeded
## 100 + rep; gate validation 100 true / 100 control,
## held-out 100 / 100, seeds stated in experiments.py)

- L1: Lateral-score gap (structured minus random same
  count) >= 0.10 for at least 2 of 3 corruptions
  (seam shift, row slip, catastrophe front), AND mean
  gap across the three >= 0.15.
- L2: Two-factor gate, held-out Youden J > 0.50,
  TPR >= 0.80, FPR <= 0.20.
- L3: Clean recall accuracy 1.000 and structured recall
  accuracy 1.000 are reported as CEILING, not as evidence
  for lattice-awareness. The evidence is L1 and L2.
- L4: Controls: random-pattern lateral score mean < 0.20
  and scrambled-pattern lateral score mean < 0.20.
- L5: No bar is set on row slip alone. Prototype showed
  its gap is small (0.044 at seed 42) because only 6 cells
  change. If slip fails L1 while seam and catastrophe
  pass, L1 still passes via the 2-of-3 rule, and slip's
  failure is reported, not hidden.
