"""Fail-closed wrapper for the package's complete-input toy gate.

The raw v0.1.0 scores renormalize after missing cells/edges are skipped.
This wrapper makes no partial-observation claim: it abstains unless every
probe cell is observed. It does not change scoring for complete probes.
"""
from lat import PAIRS, combined_score
from memory import overlap


def probe_coverage(pattern, probe):
    if len(pattern) != len(probe):
        raise ValueError("pattern and probe must have the same length")
    if any(v not in (-1, 1) for v in pattern):
        raise ValueError("stored pattern must contain only -1 or +1")
    if any(v not in (-1, 0, 1) for v in probe):
        raise ValueError("probe values must be -1, 0, or +1")
    observed_cells = sum(v != 0 for v in probe)
    total_edges = len(PAIRS)
    observed_edges = sum(probe[i] != 0 and probe[j] != 0
                         for i, j in PAIRS)
    return {
        "observed_cells": observed_cells,
        "total_cells": len(probe),
        "cell_fraction": observed_cells / len(probe) if probe else 0.0,
        "observed_edges": observed_edges,
        "total_edges": total_edges,
        "edge_fraction": observed_edges / total_edges if total_edges else 0.0,
    }


def score_and_gate(pattern, probe, tau):
    """Return an abstention for any missing probe cell, else score normally."""
    coverage = probe_coverage(pattern, probe)
    complete = (coverage["observed_cells"] == coverage["total_cells"]
                and coverage["observed_edges"] == coverage["total_edges"])
    if not complete:
        return {
            "score": None,
            "accepted": False,
            "reason": "incomplete_probe_abstain",
            "coverage": coverage,
        }
    score = combined_score(pattern, probe, overlap)
    return {
        "score": score,
        "accepted": score >= tau,
        "reason": "scored_complete_probe",
        "coverage": coverage,
    }
