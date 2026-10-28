# Local candidate notes

This directory is a local, unpublished copy of the v0.1.0 toy package. The original upload is preserved separately. All baseline source files and the baseline demo remain present; the v0.1.0 algorithms and numerical weights are not retuned.

The candidate adds two things:

1. `candidate_study.py` evaluates the fixed structured-corruption score on pattern seeds held out from threshold calibration. Its scattered controls have exactly the same flip count as the structured probe, so overlap-only is an explicit tied-score baseline. The protocol and interpretation rule were frozen in `CANDIDATE_PROTOCOL.md` before running this study.
2. `coverage_gate.py` reports observed vertex/edge coverage and abstains on any incomplete probe. This closes a sparse-input false-acceptance path in the original raw score. It preserves the original combined score for complete probes and makes no claim to have validated partial-data scoring.

Run from this directory:

```bash
python3 -m unittest tests -v
python3 -m unittest test_candidate -v
python3 candidate_study.py
```

The package remains a synthetic graph toy. Names such as “microtubule,” “catastrophe,” and “GTP-like” are not evidence of biological modeling or experimental validation.
