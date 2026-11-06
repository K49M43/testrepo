#!/usr/bin/env python3
"""Reproduce the bounded NSE HDFCGOLD close/AMFI NAV date-label audit.

Uses only Python's standard library. This is descriptive source validation, not
an estimator of synchronized ETF premium, bid/ask spread, or transaction cost.
"""
import argparse
import csv
import hashlib
import json
import statistics
from collections import Counter
from datetime import datetime
from decimal import Decimal
from pathlib import Path


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest().upper()


def median_dec(values):
    vals = sorted(values)
    if not vals:
        return None
    n = len(vals)
    if n % 2:
        return vals[n // 2]
    return (vals[n // 2 - 1] + vals[n // 2]) / Decimal(2)

def pct(values, p):
    vals = sorted(values)
    if not vals:
        return None
    pos = Decimal(str(p)) * Decimal(len(vals) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(vals) - 1)
    frac = pos - lo
    return vals[lo] * (1 - frac) + vals[hi] * frac


def dec(value):
    return Decimal(value.replace(',', '').strip())


def s(value):
    return format(value, 'f') if value is not None else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--nse-csv', required=True, type=Path)
    ap.add_argument('--amfi-csv', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    args = ap.parse_args()

    with args.nse_csv.open(encoding='utf-8-sig', newline='') as f:
        nse = list(csv.DictReader(f))
    with args.amfi_csv.open(encoding='utf-8-sig', newline='') as f:
        amfi = list(csv.DictReader(f))

    nse_rows = []
    for row in nse:
        date = datetime.strptime(row['Date  '].strip(), '%d-%b-%Y').date().isoformat()
        nse_rows.append({
            'date': date, 'symbol': row['Symbol  '].strip(),
            'series': row['Series  '].strip(),
            'close': dec(row['Close Price  ']),
            'volume': int(row['Total Traded Quantity  '].replace(',', '').strip()),
            'trades': int(row['No. of Trades  '].replace(',', '').strip()),
        })
    nse_rows.sort(key=lambda r: r['date'])
    nav_by_date = {}
    duplicate_amfi_dates = []
    identity_values = set()
    for row in amfi:
        if row['scheme_code'] == '113049' and row['isin'] == 'INF179KC1981':
            date = row['date'].strip()
            if date in nav_by_date:
                duplicate_amfi_dates.append(date)
            nav_by_date[date] = dec(row['nav'])
            identity_values.add((row['scheme_code'], row['isin']))

    date_counts = Counter(r['date'] for r in nse_rows)
    symbol_counts = Counter(r['symbol'] for r in nse_rows)
    series_counts = Counter(r['series'] for r in nse_rows)
    joined = []
    for row in nse_rows:
        nav = nav_by_date.get(row['date'])
        if nav is not None:
            gap = (row['close'] / nav - 1) * 100
            joined.append({**row, 'nav': nav, 'gap_pct': gap})
    gaps = [r['gap_pct'] for r in joined]
    abs_gaps = [abs(x) for x in gaps]
    unmatched = [r['date'] for r in nse_rows if r['date'] not in nav_by_date]
    gaps_by_year = {}
    for year in sorted({r['date'][:4] for r in joined}):
        vals = [r['gap_pct'] for r in joined if r['date'].startswith(year)]
        gaps_by_year[year] = {
            'matched_dates': len(vals),
            'median_close_to_nav_difference_pct': s(median_dec(vals)),
            'median_absolute_difference_pct': s(median_dec([abs(x) for x in vals])),
            'min_pct': s(min(vals)), 'max_pct': s(max(vals)),
        }
    largest = sorted(joined, key=lambda r: abs(r['gap_pct']), reverse=True)[:12]
    calendar_gaps = [(datetime.fromisoformat(b['date']) - datetime.fromisoformat(a['date'])).days
                     for a, b in zip(nse_rows, nse_rows[1:])]
    symbols_by_date = [(r['date'], r['symbol']) for r in nse_rows]
    symbol_transitions = [
        {'effective_date_in_observed_rows': symbols_by_date[i][0],
         'from': symbols_by_date[i-1][1], 'to': symbols_by_date[i][1]}
        for i in range(1, len(symbols_by_date))
        if symbols_by_date[i][1] != symbols_by_date[i-1][1]
    ]

    out = {
        'audit_id': 'hdfcgold_nse_amfi_date_label_bridge_2026-11-06_v1',
        'classification': 'bounded official-source capture and descriptive exact-date comparison; not execution-cost qualification',
        'source_capture': {
            'source': 'NSE Security-wise Archives',
            'url': 'https://www.nseindia.com/report-detail/eq_security',
            'query': {'selected_instrument': 'Equity', 'symbol_filter': 'HDFCGOLD', 'series_filter': 'ALL', 'window': '5Y', 'displayed_window': '2021-11-06 through 2026-11-06'},\n            'workstation_file_creation_time_utc': '2026-11-06T17:39:43.9505271Z',
            'download_filename': '06-11-2021-TO-06-11-2026-HDFCGOLD-ALL-N.csv',
            'bytes': args.nse_csv.stat().st_size,
            'sha256': sha256(args.nse_csv),
            'archive_identity': {'isin': 'INF179KC1981', 'scheme_code': '113049', 'historical_symbol': 'HDFCMFGETF', 'current_symbol': 'HDFCGOLD', 'identity_sources': ['https://archives.nseindia.com/content/circulars/CML57054.pdf', 'https://nsearchives.nseindia.com/content/circulars/CML72944.pdf']},
            'symbol_transitions_in_file': symbol_transitions,
        },
        'amfi_comparison_input': {
            'source_class': 'official AMFI scheme-specific historical NAV observations, normalized in retained repo artifact',
            'repo_path': 'research/stage512/2026-11-05/source_retrieval_followup/candidates/nav_113049_daily.csv',
            'sha256': '66B5253E897A89FB0BFFF1A44E83BC909C31373040389A32A561B5DBDDD3EF0B',
            'scheme_code': '113049', 'isin': 'INF179KC1981',
            'coverage': {'first_date': min(nav_by_date), 'last_date': max(nav_by_date), 'observations': len(nav_by_date)},
            'normalization_note': 'The retained AMFI series shows a 100x level discontinuity between 2021-02-19 and 2021-02-22. Its corporate-action/normalization cause is not established by this audit. The NSE comparison begins 2021-11-08, after that discontinuity; no cross-discontinuity level comparison is performed here.'
        },
        'data_quality': {
            'nse_rows': len(nse_rows), 'unique_dates': len(date_counts),
            'duplicate_dates': sorted(d for d,c in date_counts.items() if c > 1),
            'symbol_row_counts': dict(sorted(symbol_counts.items())),
            'series_row_counts': dict(sorted(series_counts.items())),
            'invalid_or_nonpositive_closes': [r['date'] for r in nse_rows if r['close'] <= 0],
            'max_calendar_gap_days': max(calendar_gaps) if calendar_gaps else None,
            'matched_exact_date_rows': len(joined),
            'unmatched_nse_dates': unmatched,
            'unmatched_within_amfi_retained_coverage': [d for d in unmatched if min(nav_by_date) <= d <= max(nav_by_date)],\n            'unmatched_within_coverage_note': 'Seven NSE trade dates lack a same-date row in the retained AMFI snapshot; session-specific explanations are not source-audited in this package.',
            'nse_dates_after_amfi_retained_snapshot': [d for d in unmatched if d > max(nav_by_date)],
            'duplicate_amfi_dates_for_identity': sorted(set(duplicate_amfi_dates)),
        },
        'date_label_close_vs_reported_nav_difference': {
            'definition': '(NSE close / same-calendar-date AMFI NAV - 1) * 100',
            'interpretation_limit': 'Dates are joined by date label only. This is not a synchronized intraday premium/discount, bid/ask spread, transaction cost, or executable price estimate.',
            'matched_dates': len(joined),
            'median_pct': s(median_dec(gaps)) if gaps else None,
            'median_absolute_pct': s(Decimal(str(statistics.median(abs_gaps)))) if gaps else None,
            'p05_linear_interpolation_pct': s(pct(gaps, 0.05)),
            'p95_linear_interpolation_pct': s(pct(gaps, 0.95)),
            'min_pct': s(min(gaps)) if gaps else None,
            'max_pct': s(max(gaps)) if gaps else None,
            'by_calendar_year': gaps_by_year,
            'largest_absolute_differences': [
                {'date': r['date'], 'symbol': r['symbol'], 'close_inr': s(r['close']), 'amfi_nav_inr': s(r['nav']),
                 'difference_pct': s(r['gap_pct']), 'volume_units': r['volume'], 'trade_count': r['trades']}
                for r in largest
            ],
        },
        'qualification': {
            'qualified': ['raw NSE archive capture and byte hash', 'basic daily-row/date/price integrity for this five-year file', 'exact-date descriptive close-to-AMFI-NAV comparison over available retained overlap'],
            'not_qualified': ['historical bid/ask spread or market depth', 'execution costs or slippage', 'synchronized intraday premium/discount', 'investor-specific broker availability or suitability', 'full HDFCGOLD investability gate', 'G6.3 closure or investment authorization'],
            'next_evidence_needed': ['official historical quote/trade/order evidence with lawful access if execution-cost estimation is required', 'independent review of large close/NAV differences and their source timestamp conventions', 'capture/retention of official AMFI observations after 2026-10-30 if extending the matched-date window'],
            'decision_state': 'G6.3 OPEN; NO-GO / NOT YET EVALUATED'
        }
    }
    args.output.write_text(json.dumps(out, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(out, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()

