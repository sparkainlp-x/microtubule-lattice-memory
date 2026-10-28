# Microtubule Lattice Memory — synthetic graph toy

> **Important result: the candidate’s secondary gate fails its held-out false-positive-rate criterion.** On 200 held-out pattern seeds, the validation-calibrated gate has TPR **0.982** (95% CI 0.970–0.992), FPR **0.403** (95% CI 0.388–0.418), and Youden J **0.579**. Do not present the original, easier random-pattern gate result as a successful validation of this gate.

This repository contains a reproducible synthetic graph simulation, not a biological microtubule or neuroscience model. It scores pairwise edge products on 156 arbitrary ±1 values arranged on a 13×12 square grid. It contains no tubulin, GTP chemistry, polymer dynamics, neural data, or physical measurements. Nothing here establishes biological function, memory in cells or brains, quantum coherence, consciousness, medical benefit, or experimental validation. The row-slip result is also weak and remains below the original per-class cutoff.

## Contents

- `archive/microtubule-lattice-memory-v0.1.0.zip` — the original uploaded ZIP, preserved byte-for-byte. Verify it from `archive/` with `sha256sum -c SHA256SUMS`.
- `review/REVIEW_REPORT.md` — the scientific and reproducibility review, including the analysis and claim limits.
- `candidate/microtubule-lattice-memory/` — the frozen candidate protocol, code, results, tests, coverage guard, and SHA-256 manifest. Verify its frozen files by running `sha256sum -c FROZEN_FILES.sha256` from that directory.

## Rechecking the candidate

From `candidate/microtubule-lattice-memory/`, run:

```sh
python3 -m unittest discover -v
python3 demo.py
```

The test suite includes nine baseline tests and six coverage-guard tests. The demo is the copied baseline demo; its historical gate output is not the held-out candidate-gate result. For that result, see `candidate_results.json` and the prominently reported failure above.
