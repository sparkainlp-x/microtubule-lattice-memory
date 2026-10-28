# DESIGN.md — microtubule-lattice-memory v0.1.0

## Decisions

- Lateral score is pattern-specific, not generic. A generic
  lattice term (neighbours should agree, seam should
  disagree) was tried in prototype and failed: the stored
  pattern itself only agrees 0.615 vertically and 0.119
  horizontally, so enforcing generic lattice perfection
  fights the stored pattern. Pattern-specific products
  (stored pair product x probe pair product) score 1.0 for
  the stored pattern by construction, and fall only where
  the probe actually breaks stored neighbour relations.
- Combined score weights are 0.5 / 0.5, fixed in PREREG.
  No weight was tuned after the demo.
- Gate calibration follows the refusing family: Youden's J
  on validation only, frozen, held-out reported separately.

## Falsified designs, kept in the record

- Iterative lateral recall (generic lattice term, lambda
  sweep 0, 0.5, 1, 2, 4, 8, single seed 42): at lambda <= 1
  all accuracies stayed 1.000, ceiling; at lambda >= 2
  clean recall fell to 0.929, seam to 0.910, random
  same-count to ~0.885 — no corruption-vs-random gap,
  only added noise. Not shipped.
- Mean lattice coherence (generic vertical agreement with
  seam inverted): clean 0.615, seam 0.385, random 20 flips
  0.359 — seam and random are almost identical, because
  random flips break many edges. Mean coherence does not
  separate structured from scattered damage. Not shipped.
- Minimum-edge agreement: seam separates (-1.0 vs random
  mean -0.167), slip is weak (-0.5 vs -0.233), catastrophe
  does not separate at all (-0.333, same as clean).
  A single-edge statistic is not a general lattice detector.
  Not shipped.

## What would falsify this package

- If the lateral gap mean falls below 0.15, or fewer than
  2 of 3 corruptions clear 0.10, on a fresh pattern seed
  set, L1 fails and the lattice-aware gate claim fails
  with it. The package does not claim the gate works for
  arbitrary lattice geometries — it was measured on this
  13x12 construction only.
