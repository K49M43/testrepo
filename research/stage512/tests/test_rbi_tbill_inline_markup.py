"""Regression for historical RBI auction notices with inline-split wording."""
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "research/stage512/2026-11-06/g6_3/acquire_rbi_tbill_window.py"
SPEC = importlib.util.spec_from_file_location("rbi_tbill_capture", SOURCE)
CAPTURE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CAPTURE)
AUDIT_SOURCE = ROOT / "decision/audit_g6_3_rbi_tbill_window.py"
AUDIT_SPEC = importlib.util.spec_from_file_location("rbi_tbill_audit", AUDIT_SOURCE)
AUDIT = importlib.util.module_from_spec(AUDIT_SPEC)
AUDIT_SPEC.loader.exec_module(AUDIT)
NOTICE_FIXTURE = ROOT / "research/stage512/2026-11-24/g6_3/rbi_tbill_window_2023_2024/notices/notice_prid56607.html"


class TBillNoticeMarkupRegression(unittest.TestCase):
    def test_method_word_split_across_inline_markup_is_normalized(self):
        body = NOTICE_FIXTURE.read_bytes()

        parsed = CAPTURE.notice_data(body)
        independently_parsed = AUDIT.notice(body)

        self.assertEqual(parsed["auction_date"], "2023-10-25")
        self.assertEqual(parsed["issue_date"], "2023-10-26")
        self.assertEqual(parsed["auction_method"], "price based using multiple price method")
        self.assertEqual(independently_parsed["auction_method"], "price based using multiple price method")


if __name__ == "__main__":
    unittest.main()
