# Candidate protocol — frozen before candidate results

## Question and scope

Does the package’s pattern-specific lateral edge score add discrimination between the three fixed, hand-designed structured corruptions and scattered flips with exactly the same Hamming count, when evaluated on pattern seeds not used for threshold calibration? This is a synthetic 13×12 graph benchmark only. It is not a model of microtubule biology, neural memory, quantum coherence, consciousness, or a physical outcome.

## Frozen design

- Keep the v0.1.0 lattice constructor, corruption functions, neighbour edges, overlap, lateral score, and combined-score weights unchanged. The combined score remains `0.5 × overlap + 0.5 × lateral_score`. Do not tune these choices on new results.
- Evaluate `seam_shift`, `row_slip`, and `catastrophe_front` in that order.
- Validation patterns use integer seeds 12000 through 12049 inclusive (50 patterns). Held-out patterns use seeds 22000 through 22199 inclusive (200 different patterns). No probe from a validation pattern enters the held-out set.
- For each pattern and corruption, make the single structured probe using the existing deterministic corruption function. Let `k` be its exact Hamming distance from the clean pattern. Generate 64 scattered controls by flipping exactly `k` distinct cells uniformly without replacement. Random streams are keyed deterministically from protocol version, split, pattern seed, corruption name, and replicate index using SHA-256-derived seeds; no stream is reused across units.
- All probes are complete ±1 vectors in the primary evaluation. Missing-data behavior is tested separately by unit tests and is not mixed into these accuracy estimates.

## Outcomes and analysis

- Primary contrast: paired ranking of each structured probe against its 64 same-count scattered controls using the combined score. Report per-seed/per-corruption AUC (ties count 0.5), equal-weighted mean AUC over the three corruptions, and the held-out mean structured-minus-control lateral-score margin. The exact-count design makes overlap-only scores tied within each comparison; report its AUC as the negative-control baseline.
- Report all three corruption classes separately. For the overall held-out mean margin and mean AUC difference (combined minus overlap-only), compute percentile 95% confidence intervals by resampling the 200 held-out pattern seeds as clusters, with 10,000 bootstrap draws and fixed bootstrap RNG seed 773300. Report a two-sided exact sign test on the per-seed overall margins. Do not treat the 64 controls within a pattern as independent pattern replicates.
- Secondary gate: choose one threshold on validation data only by maximizing Youden’s J for structured probes versus same-count scattered controls; break ties by choosing the smallest threshold. Freeze this threshold, then report held-out TPR, FPR, and J, overall and by corruption. Gate results are secondary and do not replace the paired ranking analysis.
- Reproduce the original tests and demo on the candidate copy. Add unit tests ensuring the new complete-input gate abstains on any missing cell and returns the unchanged combined score for a complete input.

## Predeclared interpretation

Evidence for incremental structural discrimination requires all of: (1) the seed-clustered 95% CI for held-out combined-score AUC above 0.5 excludes 0.5; (2) the 95% CI for the equal-weighted held-out lateral margin is wholly above zero; and (3) the mean margin is positive for at least two of the three corruption classes. Also report whether the original L1 descriptive bars replicate: at least two class mean margins ≥0.10 and the three-class mean margin ≥0.15. These criteria do not imply biological relevance.

## Missing-input guard

The original score excludes edges/cells touching zero and renormalizes over what remains. The candidate adds a fail-closed scoring wrapper that abstains unless all 156 probe cells are observed as ±1. This is an out-of-scope rejection policy for the existing complete-input benchmark, not a claim that full observation is biologically required or that partial-data scoring has been validated.

## Frozen artifact and deviations

This protocol is to be frozen together with the candidate implementation by recording SHA-256 hashes before the candidate experiment is run. If implementation or protocol changes after that point, stop, document the deviation, freeze a new version before any further candidate results, and label prior output exploratory. Report failures and deviations as well as successes.
