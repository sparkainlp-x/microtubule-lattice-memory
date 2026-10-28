"""Experiments for microtubule-lattice-memory v0.1.0.
All bars are in PREREG.md. No bar is moved here.
"""
import random

from lattice import (build_pattern, catastrophe_front, count_flips,
                     flip_bits, random_flips, random_pattern, row_slip,
                     scrambled, seam_shift)
from lat import combined_score, lateral_score
from memory import (accuracy, build_W, calibrate_gate, overlap, recall,
                    roc_table)

CORRUPTIONS = [
    ("seam_shift", seam_shift),
    ("row_slip", row_slip),
    ("catastrophe_front", catastrophe_front),
]
PATTERN_SEEDS = [42, 43, 44]


def mean_std(vals):
    m = sum(vals) / len(vals)
    var = sum((v - m) ** 2 for v in vals) / len(vals)
    return m, var ** 0.5


def exp1_lateral_gap(reps=20):
    """Structured vs random same-count lateral score, per seed."""
    out = {}
    for name, fn in CORRUPTIONS:
        gaps = []
        struct_vals = []
        rand_vals = []
        for seed in PATTERN_SEEDS:
            pat = build_pattern(seed)
            corr = fn(pat)
            k = count_flips(pat, corr)
            struct_vals.append(lateral_score(pat, corr))
            rvals = []
            for rep in range(reps):
                rf = random_flips(pat, k, random.Random(100 + rep))
                rvals.append(lateral_score(pat, rf))
            rand_vals.append(sum(rvals) / len(rvals))
            gaps.append(struct_vals[-1] - rand_vals[-1])
        gm, gs = mean_std(gaps)
        out[name] = {
            "structured_mean": round(sum(struct_vals) / len(struct_vals), 3),
            "random_mean": round(sum(rand_vals) / len(rand_vals), 3),
            "gap_mean": round(gm, 3), "gap_std": round(gs, 3),
            "gap_per_seed": [round(g, 3) for g in gaps],
            "gap_ge_0.10": gm >= 0.10,
        }
    mean_gap = sum(v["gap_mean"] for v in out.values()) / len(out)
    passed = (sum(1 for v in out.values() if v["gap_ge_0.10"]) >= 2
              and mean_gap >= 0.15)
    out["bar_L1"] = {"mean_gap": round(mean_gap, 3),
                     "n_ge_0.10": sum(1 for v in out.values()
                                      if v["gap_ge_0.10"]),
                     "pass": passed}
    return out


def exp2_gate():
    """Two-factor gate: calibrate on combined score, freeze, held-out."""
    pat = build_pattern(42)
    rng = random.Random(11)
    val_true = [flip_bits(pat, 0.10, rng) for _ in range(100)]
    val_ctrl = [random_pattern(rng) for _ in range(100)]
    true_s = [combined_score(pat, x, overlap) for x in val_true]
    ctrl_s = [combined_score(pat, x, overlap) for x in val_ctrl]
    tau, j, tpr, fpr = calibrate_gate(true_s, ctrl_s)
    rng2 = random.Random(22)
    held_true = [flip_bits(pat, 0.10, rng2) for _ in range(100)]
    held_ctrl = [random_pattern(rng2) for _ in range(100)]
    ht = [combined_score(pat, x, overlap) for x in held_true]
    hc = [combined_score(pat, x, overlap) for x in held_ctrl]
    held = roc_table(ht, hc, tau)
    passed = held["J"] > 0.50 and held["TPR"] >= 0.80 \
        and held["FPR"] <= 0.20
    return {"tau": round(tau, 3), "validation_J": round(j, 3),
            "held_out": held, "pass_L2": passed}


def exp3_recall_ceiling():
    """Recall accuracy, reported as ceiling where it is 1.000."""
    pat = build_pattern(42)
    W = build_W([pat])
    out = {}
    for name, fn in CORRUPTIONS:
        out[name] = round(accuracy(recall(W, fn(pat)), pat), 3)
    out["clean"] = round(accuracy(recall(W, pat), pat), 3)
    return out


def exp4_controls(reps=20):
    pat = build_pattern(42)
    rp = [lateral_score(pat, random_pattern(random.Random(s)))
          for s in range(reps)]
    sc = [lateral_score(pat, scrambled(pat, random.Random(s)))
          for s in range(reps)]
    return {"random_pattern_mean": round(sum(rp) / len(rp), 3),
            "scrambled_mean": round(sum(sc) / len(sc), 3),
            "pass_L4": sum(rp) / len(rp) < 0.20
            and sum(sc) / len(sc) < 0.20}


def run_all():
    return {"exp1_lateral_gap": exp1_lateral_gap(),
            "exp2_gate": exp2_gate(),
            "exp3_recall_ceiling": exp3_recall_ceiling(),
            "exp4_controls": exp4_controls()}
