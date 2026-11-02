"""Offline contract tests; never require live market data."""
import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipelines"))
from amfi_source_pilot import parse_nav_text, windows_from_args, classify_name

class OfficialAmfiParserContract(unittest.TestCase):
    def test_latest_six_fields(self):
        raw = b'Scheme Code;ISIN Div Payout/ ISIN Growth;ISIN Div Reinvestment;Scheme Name;Net Asset Value;Date\n123456;INF000000000;-;Test Nifty 500 Direct Growth;123.2500;02-Nov-2026\n'
        rows, meta = parse_nav_text(raw, history=False)
        self.assertEqual((len(rows), meta['rejected'], rows[0].nav), (1, 0, 123.25))
    def test_history_eight_fields(self):
        raw = b'Scheme Code;NAV Name;Plan;Option;ISIN Div Payout/ISIN Growth;ISIN Div Reinvestment;Net Asset Value;Date\n123456;Test Gilt Fund;Direct;Growth;INF000000000;;88.0250;03-Jan-2024\n'
        rows, meta = parse_nav_text(raw, history=True)
        self.assertEqual(len(rows), 1)
        self.assertEqual(meta['rejected'], 0)
        self.assertEqual(rows[0].asof.isoformat(), '2024-01-03')
    def test_live_amfi_eight_column_current(self):
        raw = b'Scheme Code;ISIN Div Payout/ ISIN Growth;ISIN Div Reinvestment;Scheme Name;Plan;Option;Net Asset Value;Date\n123456;INF000000000;-;Test Nifty 500;Direct;Growth;125.2500;30-Oct-2026\n'
        rows, meta = parse_nav_text(raw, history=False)
        self.assertEqual((len(rows), meta['rejected'], rows[0].nav), (1, 0, 125.25))
        self.assertIn('Direct Growth', rows[0].scheme_name)
    def test_html_block_not_nav(self):
        rows, _ = parse_nav_text(b'<html><body>Captcha forbidden</body></html>', history=True)
        self.assertEqual(len(rows), 0)
    def test_invalid_duplicate_does_not_pass(self):
        rows, stats = parse_nav_text(b'123456;Name;ISIN;;-3;;;03-Jan-2024\n123456;Name;ISIN;;1;;;03-Jan-2024\n123456;Name;ISIN;;2;;;03-Jan-2024', history=True)
        self.assertEqual(stats['rejected'], 2)
    def test_window_limits(self):
        with self.assertRaises(ValueError):
            windows_from_args(['2024-01-01:2024-05-01'])
        self.assertEqual(len(windows_from_args(['2024-01-01:2024-01-08'])), 1)
    def test_name_classification_not_scheme_type_claim(self):
        self.assertEqual(classify_name('Fund GOLD ETF'), ['GOLD_ETF_NAMED'])
        self.assertEqual(classify_name('Unknown Fund'), [])

if __name__ == '__main__': unittest.main()
