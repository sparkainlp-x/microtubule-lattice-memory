# microtubule-lattice-memory v0.1.0

**A lattice-aware GATE on a microtubule-like lattice toy —
not a lattice-aware recall, not a microtubule, not biology.**

Stdlib-only Python, seeded, reproducible, AGPL-3.0-only.

## Run

```bash
python demo.py    # experiments, writes results.json
python3 -m unittest tests -v  # 9 tests
```

## What it is

microtubule-crystallize v0.1.0 Exp4 was negative: outer-product
recall was 1.000 for seam shift, row slip, and catastrophe
front, exactly like same-count random flips, because the
outer product only cares how many cells match.

This package adds a pattern-specific lateral score: mean
over the 299 lattice neighbour pairs (vertical, seam, and
horizontal) of (stored product) x (probe product). For the
stored pattern it is 1.0 by construction; for a random
pattern it is ~0. Structured flips preserve many neighbour
products — a whole inverted row keeps its horizontal
products, a flipped front keeps its internal vertical
products — while scattered flips break them everywhere.
That difference is measured, and it is the lattice signal.

Recall itself is unchanged (outer product, one step).
What is lattice-aware is the score and the gate:
S = 0.5 * overlap + 0.5 * lateral_score, calibrated by
Youden's J on validation probes only, then frozen.

## Measured (demo, patterns seeds 42, 43, 44; reps 20)

- Seam shift: structured lateral 0.730, random 0.599, **gap +0.131**
- Row slip: structured 0.893, random 0.849, **gap +0.043** (fails
  the 0.10 bar on its own — reported, not hidden; only 6 cells
  change, so scattered flips also preserve most pairs)
- Catastrophe front: structured 0.906, random 0.486, **gap +0.420**
- **Bar L1: mean gap 0.198, 2/3 >= 0.10, PASS**
- Gate: tau 0.354, validation J 1.000, held-out J 1.000,
  TPR 1.00, FPR 0.00, **PASS**
- Recall: clean 1.000, seam 1.000, slip 1.000, catastrophe
  1.000 — **CEILING, not evidence** for lattice-awareness
- Controls: random pattern lateral 0.018, scrambled 0.087,
  **PASS**

## Honest limits — read before any use

- **No crystal grown, no microtubule measured, no brain,
  no quantum state, no consciousness or Orch OR validation.
  Penrose's 2020 Nobel was for black holes.**
- The gate is lattice-aware; recall is not. Claiming
  lattice-aware recall from this package would be false.
- Row slip does not pass on its own. A lattice-aware gate
  that cannot separate a 6-cell slip from 6 scattered flips
  is a limited gate, and is labelled as such.
- Single-pattern recall is ceiling at any positive overlap,
  which is why the evidence is in the score gap and the
  gate, not in recall accuracy.
- `lattice.py` and `memory.py` are reused exactly from
  microtubule-crystallize v0.1.0, same author, same licence.

## Files

- `lat.py` — lateral score and combined score
- `lattice.py` — 13x12 lattice, reused exactly
- `memory.py` — outer-product memory and gate, reused exactly
- `experiments.py` — Exp1-Exp4
- `demo.py` — measured demo, writes results.json
- `tests.py` — 9 tests
- `PREREG.md` — bars, written before the demo run
- `DESIGN.md` — decisions, falsified designs, limits
- `LICENSE` — AGPL-3.0-only
