"""Frozen held-out-seed evaluation for the local candidate.

Run from this directory: python3 candidate_study.py
The protocol is in CANDIDATE_PROTOCOL.md. This is a synthetic graph benchmark.
"""
import hashlib
import json
import math
import platform
import random
from collections import defaultdict
from pathlib import Path

from lattice import (build_pattern, catastrophe_front, count_flips,
                     random_flips, row_slip, seam_shift)
from lat import combined_score, lateral_score
from memory import overlap

HERE = Path(__file__).resolve().parent
VALIDATION_SEEDS = list(range(12000, 12050))
HELDOUT_SEEDS = list(range(22000, 22200))
CONTROL_REPS = 64
BOOTSTRAP_REPS = 10_000
BOOTSTRAP_SEED = 773300
CORRUPTIONS = [
    ("seam_shift", seam_shift),
    ("row_slip", row_slip),
    ("catastrophe_front", catastrophe_front),
]


def _stable_seed(*parts):
    payload = "|".join(str(p) for p in parts).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")


def _rng(*parts):
    return random.Random(_stable_seed("candidate-v1", *parts))


def _pair_auc(positive, controls):
    wins = sum(1.0 if positive > x else 0.5 if positive == x else 0.0
               for x in controls)
    return wins / len(controls)


def _make_records(split, seeds):
    records = []
    for pattern_seed in seeds:
        pat = build_pattern(pattern_seed)
        for corruption_name, corruption_fn in CORRUPTIONS:
            structured = corruption_fn(pat)
            k = count_flips(pat, structured)
            controls = [
                random_flips(
                    pat, k,
                    _rng(split, pattern_seed, corruption_name, rep))
                for rep in range(CONTROL_REPS)
            ]
            pos_overlap = overlap(pat, structured)
            control_overlaps = [overlap(pat, x) for x in controls]
            if any(abs(x - pos_overlap) > 1e-12 for x in control_overlaps):
                raise AssertionError("exact-count controls must match overlap")
            pos_lateral = lateral_score(pat, structured)
            control_lateral = [lateral_score(pat, x) for x in controls]
            pos_combined = combined_score(pat, structured, overlap)
            control_combined = [combined_score(pat, x, overlap)
                                for x in controls]
            records.append({
                "pattern_seed": pattern_seed,
                "corruption": corruption_name,
                "k": k,
                "positive_overlap": pos_overlap,
                "positive_lateral": pos_lateral,
                "positive_combined": pos_combined,
                "mean_control_overlap": sum(control_overlaps) / CONTROL_REPS,
                "mean_control_lateral": sum(control_lateral) / CONTROL_REPS,
                "mean_control_combined": sum(control_combined) / CONTROL_REPS,
                "auc_overlap": _pair_auc(pos_overlap, control_overlaps),
                "auc_lateral": _pair_auc(pos_lateral, control_lateral),
                "auc_combined": _pair_auc(pos_combined, control_combined),
                "lateral_margin": pos_lateral - sum(control_lateral) / CONTROL_REPS,
                "positive_combined_for_gate": pos_combined,
                "control_combined_for_gate": control_combined,
            })
    return records


def _percentile(values, q):
    ordered = sorted(values)
    if not ordered:
        raise ValueError("cannot form interval from no values")
    pos = q * (len(ordered) - 1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return ordered[lo]
    frac = pos - lo
    return ordered[lo] * (1.0 - frac) + ordered[hi] * frac


def _bootstrap_mean_ci(values, rng):
    n = len(values)
    boots = []
    for _ in range(BOOTSTRAP_REPS):
        boots.append(sum(values[rng.randrange(n)] for _ in range(n)) / n)
    return [_percentile(boots, 0.025), _percentile(boots, 0.975)]


def _exact_sign_p(values):
    nonzero = [x for x in values if x != 0]
    n = len(nonzero)
    if n == 0:
        return {"n_nonzero": 0, "n_positive": 0, "two_sided_p": 1.0}
    positives = sum(x > 0 for x in nonzero)
    tail = min(positives, n - positives)
    p = 2.0 * sum(math.comb(n, k) for k in range(tail + 1)) / (2 ** n)
    return {"n_nonzero": n, "n_positive": positives,
            "two_sided_p": min(1.0, p)}


def _by_seed(records):
    grouped = defaultdict(list)
    for row in records:
        grouped[row["pattern_seed"]].append(row)
    return grouped


def _mean(values):
    return sum(values) / len(values) if values else 0.0


def _gate_threshold(validation_records):
    positives = [r["positive_combined_for_gate"] for r in validation_records]
    controls = [s for r in validation_records
                for s in r["control_combined_for_gate"]]
    values = sorted(set(positives + controls))
    candidates = [(values[0] - 0.01)]
    candidates.extend((a + b) / 2.0 for a, b in zip(values, values[1:]))
    candidates.append(values[-1] + 0.01)
    best = None
    for tau in candidates:
        tpr = sum(s >= tau for s in positives) / len(positives)
        fpr = sum(s >= tau for s in controls) / len(controls)
        j = tpr - fpr
        if (best is None or j > best[1] + 1e-12
                or (abs(j - best[1]) <= 1e-12 and tau < best[0])):
            best = (tau, j, tpr, fpr)
    return best


def _gate_by_seed(records, tau):
    grouped = _by_seed(records)
    per_seed = {}
    for seed, rows in grouped.items():
        pos = [r["positive_combined_for_gate"] for r in rows]
        ctrl = [s for r in rows for s in r["control_combined_for_gate"]]
        per_seed[seed] = {
            "tpr": sum(s >= tau for s in pos) / len(pos),
            "fpr": sum(s >= tau for s in ctrl) / len(ctrl),
        }
    return per_seed


def _summarize(split, records, rng):
    by_seed = _by_seed(records)
    per_seed = {}
    for seed, rows in by_seed.items():
        per_seed[seed] = {
            "auc_overlap": _mean([r["auc_overlap"] for r in rows]),
            "auc_lateral": _mean([r["auc_lateral"] for r in rows]),
            "auc_combined": _mean([r["auc_combined"] for r in rows]),
            "combined_minus_overlap_auc": _mean(
                [r["auc_combined"] - r["auc_overlap"] for r in rows]),
            "lateral_margin": _mean([r["lateral_margin"] for r in rows]),
        }

    by_corruption = {}
    for corruption_name, _ in CORRUPTIONS:
        rows = [r for r in records if r["corruption"] == corruption_name]
        margins = [r["lateral_margin"] for r in rows]
        aucs = [r["auc_combined"] for r in rows]
        overlap_aucs = [r["auc_overlap"] for r in rows]
        by_corruption[corruption_name] = {
            "n_patterns": len(rows),
            "mean_flip_count": _mean([r["k"] for r in rows]),
            "mean_lateral_margin": _mean(margins),
            "lateral_margin_ci95_seed_bootstrap":
                _bootstrap_mean_ci(margins, rng),
            "mean_combined_auc": _mean(aucs),
            "combined_auc_ci95_seed_bootstrap":
                _bootstrap_mean_ci(aucs, rng),
            "mean_overlap_only_auc": _mean(overlap_aucs),
        }

    seed_margins = [per_seed[s]["lateral_margin"] for s in sorted(per_seed)]
    seed_auc = [per_seed[s]["auc_combined"] for s in sorted(per_seed)]
    seed_auc_delta = [per_seed[s]["combined_minus_overlap_auc"]
                      for s in sorted(per_seed)]
    overall = {
        "n_pattern_seeds": len(per_seed),
        "mean_lateral_margin": _mean(seed_margins),
        "lateral_margin_ci95_seed_bootstrap":
            _bootstrap_mean_ci(seed_margins, rng),
        "mean_combined_auc": _mean(seed_auc),
        "combined_auc_ci95_seed_bootstrap":
            _bootstrap_mean_ci(seed_auc, rng),
        "mean_overlap_only_auc": _mean(
            [per_seed[s]["auc_overlap"] for s in sorted(per_seed)]),
        "mean_combined_minus_overlap_auc": _mean(seed_auc_delta),
        "combined_minus_overlap_auc_ci95_seed_bootstrap":
            _bootstrap_mean_ci(seed_auc_delta, rng),
        "exact_sign_test_on_seed_margins": _exact_sign_p(seed_margins),
    }
    if split == "heldout":
        pass_l1 = (
            sum(v["mean_lateral_margin"] >= 0.10
                for v in by_corruption.values()) >= 2
            and overall["mean_lateral_margin"] >= 0.15
        )
        overall["legacy_L1_bar_pass"] = pass_l1
        overall["incremental_discrimination_criteria_pass"] = (
            overall["combined_auc_ci95_seed_bootstrap"][0] > 0.5
            and overall["lateral_margin_ci95_seed_bootstrap"][0] > 0
            and sum(v["mean_lateral_margin"] > 0
                    for v in by_corruption.values()) >= 2
        )
    return {"overall": overall, "by_corruption": by_corruption,
            "per_seed": per_seed}


def _gate_summary(records, tau, rng):
    by_seed = _gate_by_seed(records, tau)
    tprs = [by_seed[s]["tpr"] for s in sorted(by_seed)]
    fprs = [by_seed[s]["fpr"] for s in sorted(by_seed)]
    positives = [r["positive_combined_for_gate"] for r in records]
    controls = [s for r in records for s in r["control_combined_for_gate"]]
    return {
        "tau": tau,
        "n_positive": len(positives),
        "n_control": len(controls),
        "tpr": sum(s >= tau for s in positives) / len(positives),
        "fpr": sum(s >= tau for s in controls) / len(controls),
        "youden_j": (sum(s >= tau for s in positives) / len(positives)
                     - sum(s >= tau for s in controls) / len(controls)),
        "tpr_ci95_seed_bootstrap": _bootstrap_mean_ci(tprs, rng),
        "fpr_ci95_seed_bootstrap": _bootstrap_mean_ci(fprs, rng),
    }


def _compact_records(records):
    return [{
        "pattern_seed": r["pattern_seed"],
        "corruption": r["corruption"],
        "k": r["k"],
        "positive_overlap": round(r["positive_overlap"], 12),
        "positive_lateral": round(r["positive_lateral"], 12),
        "mean_control_lateral": round(r["mean_control_lateral"], 12),
        "auc_overlap": round(r["auc_overlap"], 12),
        "auc_lateral": round(r["auc_lateral"], 12),
        "auc_combined": round(r["auc_combined"], 12),
        "lateral_margin": round(r["lateral_margin"], 12),
    } for r in records]


def run():
    validation = _make_records("validation", VALIDATION_SEEDS)
    heldout = _make_records("heldout", HELDOUT_SEEDS)
    tau, validation_j, validation_tpr, validation_fpr = _gate_threshold(validation)

    bootstrap_rng = random.Random(BOOTSTRAP_SEED)
    result = {
        "title": "Held-out exact-count structured-versus-scattered toy benchmark",
        "scope": "Synthetic 13x12 graph only; not microtubule biology or neuroscience.",
        "protocol": {
            "validation_seed_range_inclusive": [VALIDATION_SEEDS[0], VALIDATION_SEEDS[-1]],
            "heldout_seed_range_inclusive": [HELDOUT_SEEDS[0], HELDOUT_SEEDS[-1]],
            "control_replicates_per_pattern_corruption": CONTROL_REPS,
            "bootstrap_replicates": BOOTSTRAP_REPS,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "corruptions": [n for n, _ in CORRUPTIONS],
            "score_weights": {"overlap": 0.5, "lateral": 0.5},
        },
        "runtime": {"python": platform.python_version()},
        "validation": {
            "summary": _summarize("validation", validation, bootstrap_rng),
            "gate_calibration": {
                "tau": tau, "validation_j": validation_j,
                "validation_tpr": validation_tpr,
                "validation_fpr": validation_fpr,
                "selection": "maximum Youden J; smallest threshold breaks ties",
            },
        },
        "heldout": {
            "summary": _summarize("heldout", heldout, bootstrap_rng),
            "frozen_gate": _gate_summary(heldout, tau, bootstrap_rng),
            "records": _compact_records(heldout),
        },
    }
    path = HERE / "candidate_results.json"
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "validation_gate": result["validation"]["gate_calibration"],
        "heldout": {
            "overall": result["heldout"]["summary"]["overall"],
            "by_corruption": result["heldout"]["summary"]["by_corruption"],
            "frozen_gate": result["heldout"]["frozen_gate"],
        },
        "results_path": str(path),
    }, indent=2))


if __name__ == "__main__":
    run()
