"""Tests for microtubule-lattice-memory v0.1.0.
Run: python3 -m unittest tests -v
"""
import random
import unittest

from experiments import exp1_lateral_gap, exp2_gate, exp4_controls
from lat import PAIRS, combined_score, lateral_score
from lattice import (build_pattern, catastrophe_front, random_flips,
                     row_slip, seam_shift)
from memory import build_W, overlap, recall


class TestLatticeMemory(unittest.TestCase):
    def test_pairs_count(self):
        self.assertEqual(len(PAIRS), 299)

    def test_clean_lateral_is_one(self):
        pat = build_pattern(42)
        self.assertAlmostEqual(lateral_score(pat, pat), 1.0)

    def test_random_lateral_near_zero(self):
        pat = build_pattern(42)
        rng = random.Random(1)
        from lattice import random_pattern
        vals = [lateral_score(pat, random_pattern(rng))
                for _ in range(20)]
        self.assertLess(abs(sum(vals) / len(vals)), 0.20)

    def test_combined_score_weights(self):
        pat = build_pattern(42)
        self.assertAlmostEqual(combined_score(pat, pat, overlap), 1.0)

    def test_seam_gap_positive(self):
        pat = build_pattern(42)
        corr = seam_shift(pat)
        from lattice import count_flips
        k = count_flips(pat, corr)
        rvals = [lateral_score(pat, random_flips(pat, k,
                                                random.Random(100 + s)))
                 for s in range(20)]
        self.assertGreater(lateral_score(pat, corr)
                           - sum(rvals) / len(rvals), 0.10)

    def test_catastrophe_gap_positive(self):
        pat = build_pattern(42)
        corr = catastrophe_front(pat)
        from lattice import count_flips
        k = count_flips(pat, corr)
        rvals = [lateral_score(pat, random_flips(pat, k,
                                                random.Random(100 + s)))
                 for s in range(20)]
        self.assertGreater(lateral_score(pat, corr)
                           - sum(rvals) / len(rvals), 0.10)

    def test_gate_passes(self):
        g = exp2_gate()
        self.assertTrue(g["pass_L2"])

    def test_controls_pass(self):
        self.assertTrue(exp4_controls()["pass_L4"])

    def test_recall_ceiling_reported(self):
        pat = build_pattern(42)
        W = build_W([pat])
        from memory import accuracy
        self.assertEqual(accuracy(recall(W, pat), pat), 1.0)


if __name__ == "__main__":
    unittest.main()
