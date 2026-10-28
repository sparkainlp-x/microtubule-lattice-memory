# Scientific and reproducibility review

The archive is a reproducible **synthetic graph toy**, not a biological microtubule or neuroscience model. The uploaded ZIP remains unchanged; its SHA-256 is `a49f623474131d89c372d3c1b8721b3d0cea4c204b0e424b1c933b5ccb496a91`.

## Baseline findings

The original package’s 9 tests pass, and its demo reproduces the checked-in values. Its aggregate L1 bar passes on only three pattern seeds: mean structured-minus-scattered lateral-score gap is 0.198. Seam shift is 0.131 and catastrophe front 0.420, clearing the preregistered 0.10 class cutoff; row-slip is only 0.043 and misses it. The aggregate rule passes because 2 of 3 classes clear the cutoff. Recall is 1.000 for every case and is correctly described as a ceiling, not evidence of lattice-aware recall.

The original “perfect” gate result (Youden J = 1.000) does **not** establish added value from the lateral term. It uses one pattern and contrasts 10%-bit-flipped versions of that pattern with wholly random patterns; it has no overlap-only ablation. Those classes differ strongly in direct similarity to the stored pattern, and the combined score explicitly includes overlap. Its split holds out probe randomness, not patterns.

A separate weakness is missing-data handling: the raw score drops unknown cells and incident edges, then renormalizes. A row with 12 masked cells can still obtain a perfect raw combined score. The package has no coverage floor or abstention rule.

## Frozen local candidate

I kept all baseline scoring functions and weights unchanged. Before running new results, I froze and hashed a protocol that uses 50 validation pattern seeds, 200 distinct held-out pattern seeds, and 64 scattered controls per corruption with exactly the same flip count as the structured probe. The primary comparison is paired discrimination against those matched controls; overlap-only is the prespecified baseline.

On the 200 held-out seeds, combined-score AUC was **0.975** (seed-clustered bootstrap 95% CI 0.967–0.982), versus **0.500** for overlap-only. Mean lateral-score margin was **0.199** (95% CI 0.197–0.200). Seam shift averaged 0.134, row slip 0.031, and catastrophe front 0.431. Thus the preregistered aggregate discrimination criteria pass, but row-slip remains weak and below the original 0.10 per-class threshold.

The secondary, validation-calibrated gate **fails** the original false-positive bar on the matched task: held-out TPR 0.982 (95% CI 0.970–0.992), FPR **0.403** (95% CI 0.388–0.418), J = 0.579. This is a structured-corruption-versus-scattered-corruption discriminator, not evidence of a general memory acceptance gate. Report that failure; do not substitute the original easier random-pattern gate result.

The candidate also adds `coverage_gate.py`, which abstains unless all 156 probe cells are observed. This is a conservative guard for the demonstrated missingness weakness, not a validated partial-observation method. The original 9 tests and 6 new coverage tests pass; the copied baseline demo also passes unchanged.

## Claim limits

The code builds 156 arbitrary ±1 values on a 13×12 square graph and scores their pairwise edge products. It contains no tubulin, GTP chemistry, polymer dynamics, neural data, quantum state, or physical measurements. Structural literature describes microtubules as tubulin heterodimers arranged in protofilaments, commonly 13 or 14, with a lattice seam; that is not the same geometry or mechanism as this toy grid [1]. The package’s note that Roger Penrose’s 2020 Nobel was for black-hole formation is accurate [2], but that prize provides no support for this model. Nothing here establishes biological function, memory in cells or brains, quantum coherence, Orch OR, consciousness, medical benefit, or experimental validation.

## Local artifacts

- Review: `/workspace/microtubule-lattice-memory-review/REVIEW_REPORT.md`
- Frozen candidate protocol: `/workspace/microtubule-lattice-memory-review/candidate/microtubule-lattice-memory/CANDIDATE_PROTOCOL.md`
- Candidate experiment and saved held-out results: `/workspace/microtubule-lattice-memory-review/candidate/microtubule-lattice-memory/candidate_study.py` and `/workspace/microtubule-lattice-memory-review/candidate/microtubule-lattice-memory/candidate_results.json`
- Missing-input abstention wrapper and tests: `/workspace/microtubule-lattice-memory-review/candidate/microtubule-lattice-memory/coverage_gate.py` and `/workspace/microtubule-lattice-memory-review/candidate/microtubule-lattice-memory/test_candidate.py`
- Frozen SHA-256 manifest: `/workspace/microtubule-lattice-memory-review/candidate/microtubule-lattice-memory/FROZEN_FILES.sha256`
- Baseline and candidate test/demo logs: `/workspace/microtubule-lattice-memory-review/baseline-tests.txt`, `/workspace/microtubule-lattice-memory-review/baseline-demo.txt`, `/workspace/microtubule-lattice-memory-review/candidate-baseline-tests.txt`, `/workspace/microtubule-lattice-memory-review/candidate-coverage-tests.txt`, and `/workspace/microtubule-lattice-memory-review/candidate-baseline-demo.txt`
- Archive hash record: `/workspace/microtubule-lattice-memory-review/archive.sha256`

[1]: https://pmc.ncbi.nlm.nih.gov/articles/PMC2120284/ "Direct visualization of the microtubule lattice seam both in vitro and in vivo"
[2]: https://www.nobelprize.org/prizes/physics/2020/summary/ "The Nobel Prize in Physics 2020"
