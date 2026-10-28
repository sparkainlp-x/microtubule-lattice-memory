"""Unit tests for the local candidate additions."""
import unittest

from coverage_gate import probe_coverage, score_and_gate
from lat import PAIRS, combined_score
from lattice import build_pattern, mask_row
from memory import overlap


class TestCandidateCoverageGate(unittest.TestCase):
    def test_complete_probe_preserves_score_and_coverage(self):
        pat = build_pattern(42)
        result = score_and_gate(pat, pat, tau=0.5)
        self.assertEqual(result["reason"], "scored_complete_probe")
        self.assertTrue(result["accepted"])
        self.assertAlmostEqual(result["score"], combined_score(pat, pat, overlap))
        self.assertEqual(result["coverage"]["observed_cells"], 156)
        self.assertEqual(result["coverage"]["observed_edges"], 299)

    def test_single_missing_cell_abstains(self):
        pat = build_pattern(42)
        probe = list(pat)
        probe[0] = 0
        result = score_and_gate(pat, probe, tau=0.0)
        self.assertIsNone(result["score"])
        self.assertFalse(result["accepted"])
        self.assertEqual(result["reason"], "incomplete_probe_abstain")
        self.assertLess(result["coverage"]["cell_fraction"], 1.0)

    def test_masked_row_cannot_receive_perfect_gate_score(self):
        pat = build_pattern(42)
        masked = mask_row(pat)
        # The raw score ignores missing cells; the candidate wrapper abstains.
        self.assertAlmostEqual(combined_score(pat, masked, overlap), 1.0)
        result = score_and_gate(pat, masked, tau=0.5)
        self.assertIsNone(result["score"])
        self.assertFalse(result["accepted"])
        self.assertEqual(result["coverage"]["observed_cells"], 144)

    def test_edge_coverage_and_pair_uniqueness(self):
        pat = build_pattern(43)
        coverage = probe_coverage(pat, pat)
        self.assertEqual(len(PAIRS), 299)
        self.assertEqual(len(set(PAIRS)), 299)
        self.assertEqual(coverage["observed_edges"], len(PAIRS))
        self.assertEqual(coverage["edge_fraction"], 1.0)

    def test_invalid_probe_value_rejected(self):
        pat = build_pattern(42)
        probe = list(pat)
        probe[10] = 2
        with self.assertRaises(ValueError):
            score_and_gate(pat, probe, tau=0.0)

    def test_mismatched_lengths_rejected(self):
        pat = build_pattern(42)
        with self.assertRaises(ValueError):
            score_and_gate(pat, pat[:-1], tau=0.0)


if __name__ == "__main__":
    unittest.main()
