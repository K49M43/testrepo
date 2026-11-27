#!/usr/bin/env python3
"""Reproduce the bounded NSE HDFCGOLD close/AMFI NAV date-label audit.

Uses only Python's standard library. This is descriptive source validation, not
an estimator of synchronized ETF premium, bid/ask spread, or transaction cost.
"""
import argparse
import csv
import hashlib
import json
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


def summarize(values):
    if not values:
        return {'count': 0}
    return {
        'count': len(values), 'median': s(median_dec(values)),
        'median_absolute': s(median_dec([abs(x) for x in values])),
        'p05_linear_interpolation': s(pct(values, 0.05)),
        'p95_linear_interpolation': s(pct(values, 0.95)),
        'min': s(min(values)), 'max': s(max(values)),
    }


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
            'high': dec(row['High Price  ']),
            'low': dec(row['Low Price  ']),
            'reported_average': dec(row['Average Price ']),
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
    close_vs_average = [(r['close'] / r['reported_average'] - 1) * 100
                       for r in nse_rows if r['reported_average'] > 0]
    high_low_range = [(r['high'] - r['low']) / r['reported_average'] * 100
                      for r in nse_rows if r['reported_average'] > 0]
    policy_regimes = [
        {
            'name': 'pre_2026_04_01_lbma_valuation_pre_fund_attribute_change',
            'start': '2021-11-08', 'end': '2026-03-31',
            'basis': 'HDFC 2024 SID: LBMA AM fixing in USD, metric and FEDAI currency conversion, delivery costs, and notional customs duty/taxes/levies; pre-2026-04-22 HDFC ETF asset mandate',
            'source': 'https://files.hdfcfund.com/s3fs-public/SID/2024-06/SID%20-%20HDFC%20Gold%20Exchange%20Traded%20Fund%20dated%20June%2028%2C%202024.pdf',
        },
        {
            'name': '2026_04_01_to_2026_04_21_exchange_spot_pre_fund_attribute_change',
            'start': '2026-04-01', 'end': '2026-04-21',
            'basis': 'SEBI exchange-polled domestic spot valuation effective 2026-04-01; original HDFC fund asset mandate remained in force through 2026-04-21',
            'source': 'https://www.sebi.gov.in/legal/circulars/feb-2026/valuation-of-physical-gold-and-silver-held-by-mutual-fund-schemes_100001.html',
        },
        {
            'name': 'post_2026_04_22_exchange_spot_post_fund_attribute_change',
            'start': '2026-04-22', 'end': '2026-10-30',
            'basis': 'Exchange-polled domestic spot valuation plus HDFC fundamental-attribute amendment effective 2026-04-22 permitting specified gold-related instruments including ETCDs; actual snapshots are separately recorded below',
            'source': 'https://www.sebi.gov.in/legal/circulars/feb-2026/valuation-of-physical-gold-and-silver-held-by-mutual-fund-schemes_100001.html',
            'fund_source': 'https://files.hdfcfund.com/s3fs-public/2026-03/2059-%20Notice-%20Change%20in%20Fundamental%20attributes%20-%20HDFC%20Gold%20ETF-%20ETCD-w.e.f-%20April%2022%2C%202026.pdf?VersionId=vqbMTvRC.oT_yPvSfogeDNdsg1p9lpSA',
        },
    ]
    regime_comparison = {}
    for regime in policy_regimes:
        vals = [r['gap_pct'] for r in joined if regime['start'] <= r['date'] <= regime['end']]
        regime_comparison[regime['name']] = {
            'period': [regime['start'], regime['end']],
            'valuation_basis': regime['basis'],
            'source': regime.get('source'),
            'fund_source': regime.get('fund_source'),
            'matched_dates': len(vals),
            'median_close_to_nav_difference_pct': s(median_dec(vals)) if vals else None,
            'median_absolute_difference_pct': s(median_dec([abs(v) for v in vals])) if vals else None,
            'p05_linear_interpolation_pct': s(pct(vals, 0.05)),
            'p95_linear_interpolation_pct': s(pct(vals, 0.95)),
            'min_pct': s(min(vals)) if vals else None,
            'max_pct': s(max(vals)) if vals else None,
        }
    event_dates = ['2024-07-19', '2024-07-22', '2024-07-23', '2024-07-24', '2024-07-25', '2024-07-26', '2024-07-29']
    nse_by_date = {r['date']: r for r in nse_rows}
    joined_by_date = {r['date']: r for r in joined}
    customs_event_rows = []
    for event_date in event_dates:
        row = joined_by_date.get(event_date)
        if row is None:
            continue
        previous_nse = next((r for r in reversed(nse_rows) if r['date'] < event_date), None)
        previous_nav_dates = [d for d in nav_by_date if d < event_date]
        previous_nav = nav_by_date[max(previous_nav_dates)] if previous_nav_dates else None
        customs_event_rows.append({
            'date': event_date,
            'nse_symbol': row['symbol'],
            'nse_close_inr': s(row['close']),
            'nse_close_to_previous_nse_observation_pct': s((row['close'] / previous_nse['close'] - 1) * 100) if previous_nse else None,
            'amfi_nav_inr': s(row['nav']),
            'amfi_nav_to_previous_amfi_observation_pct': s((row['nav'] / previous_nav - 1) * 100) if previous_nav else None,
            'same_date_close_to_nav_difference_pct': s(row['gap_pct']),
            'nse_volume_units': row['volume'],
            'nse_trade_count': row['trades'],
        })
    customs_duty_event = {
        'event': '2024 Union Budget gold-bar import duty reduction',
        'announcement_date': '2024-07-23',
        'effective_date': '2024-07-24',
        'official_source': 'https://www.indiabudget.gov.in/budget2024-25/doc/cen/dojstru1.pdf',
        'official_source_statement': 'Government of India Ministry of Finance document dated 23-Jul-2024 states gold-bar total customs duty changed from 15% to 6%; the relevant changes became effective from midnight 23/24-Jul-2024 / 24-Jul-2024.',
        'pre_event_fund_valuation_context': 'HDFC June-2024 SID describes its valuation as including notional customs duty, taxes and levies: https://files.hdfcfund.com/s3fs-public/SID/2024-06/SID%20-%20HDFC%20Gold%20Exchange%20Traded%20Fund%20dated%20June%2028%2C%202024.pdf',
        'observations': customs_event_rows,
        'inference_limit': 'The timing and contemporaneous series moves are documented alignment only. They do not establish how much of any ETF/NAV move was caused by the duty change; global gold prices, USD/INR, market timing, valuation inputs and trading supply/demand may also contribute. Same-date close/NAV remains an unsynchronized date-label comparison, not an executable premium/discount.',
    }
    largest_ranges = sorted([r for r in nse_rows if r['reported_average'] > 0], key=lambda r: (r['high'] - r['low']) / r['reported_average'], reverse=True)[:10]
    activity_diagnostics = {
        'reported_close_vs_daily_average_pct': summarize(close_vs_average),
        'daily_high_low_range_as_pct_of_reported_average': summarize(high_low_range),
        'daily_volume_units': summarize([Decimal(r['volume']) for r in nse_rows]),
        'daily_trade_count': summarize([Decimal(r['trades']) for r in nse_rows]),
        'largest_observed_daily_ranges': [
            {'date': r['date'], 'symbol': r['symbol'], 'high_inr': s(r['high']), 'low_inr': s(r['low']),
             'close_inr': s(r['close']), 'reported_average_inr': s(r['reported_average']),
             'range_pct_of_average': s((r['high'] - r['low']) / r['reported_average'] * 100),
             'volume_units': r['volume'], 'trade_count': r['trades']}
            for r in largest_ranges
        ],
        'interpretation_limit': 'NSE close-versus-daily-average and intraday high-low range are price/activity diagnostics, not quoted bid-ask spread, order-book depth, slippage, or execution cost.',
    }

    out = {
        'audit_id': 'hdfcgold_nse_amfi_date_label_bridge_2026-11-06_v2',
        'classification': 'bounded official-source capture and descriptive exact-date comparison; not execution-cost qualification',
        'source_capture': {
            'source': 'NSE Security-wise Archives',
            'url': 'https://www.nseindia.com/report-detail/eq_security',
            'query': {'selected_instrument': 'Equity', 'symbol_filter': 'HDFCGOLD', 'series_filter': 'ALL', 'window': '5Y', 'displayed_window': '2021-11-06 through 2026-11-06'},
            'workstation_file_creation_time_utc': '2026-11-06T17:39:43.9505271Z',
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
            'normalization_note': 'HDFC states that unit face value changed from ₹100 to ₹1 effective 2021-02-19 and all return computations were adjusted. The retained raw AMFI series reports ₹100-basis NAV through 2021-02-19 and ₹1-basis NAV from 2021-02-22. A separately preserved derivative applies the documented 100:1 unit rebase; this NSE overlap begins 2021-11-08 and is unaffected by the split.',
            'rebased_series_artifact': {'repo_path': 'research/stage512/2026-11-06/hdfcgold_execution_evidence/nav_113049_current_unit_basis.csv', 'sha256': '51B8427BB06317078BF860E4B9F1CD85249587C7D27666408BB2F28F1CBA6FD5'}
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
            'unmatched_within_amfi_retained_coverage': [d for d in unmatched if min(nav_by_date) <= d <= max(nav_by_date)],
            'unmatched_within_coverage_note': 'Seven NSE trade dates lack a same-date row in the retained AMFI snapshot; session-specific explanations are not source-audited in this package.',
            'nse_dates_after_amfi_retained_snapshot': [d for d in unmatched if d > max(nav_by_date)],
            'duplicate_amfi_dates_for_identity': sorted(set(duplicate_amfi_dates)),
        },
        'nav_valuation_method_and_clock': {
            'pre_2026_04_01_basis_source': 'https://files.hdfcfund.com/s3fs-public/SID/2024-06/SID%20-%20HDFC%20Gold%20Exchange%20Traded%20Fund%20dated%20June%2028%2C%202024.pdf',
            'regulatory_change_source': 'https://www.sebi.gov.in/legal/circulars/feb-2026/valuation-of-physical-gold-and-silver-held-by-mutual-fund-schemes_100001.html',
            'post_2026_04_01_fund_source': 'https://files.hdfcfund.com/s3fs-public/SID/2026-04/SID%20-%20HDFC%20Gold%20ETF%20dated%20April%2022%2C%202026.pdf?VersionId=.N7oTFaaYPc1Mm9b8jO.Fp0lk077FkFh',
            'method_change_effective_date': '2026-04-01',
            'fund_nav_clock': 'HDFC 2026 SID says NAV is calculated at each business-day close and disclosed to AMFI/by 11 p.m. (or 9 a.m.); iNAV is provided during exchange trading hours and can be static or dynamic depending on latest available gold data.',
            'inference_limit': 'These published methods establish that same-date NSE close and AMFI NAV are not necessarily synchronized valuations and that the NAV basis changed on 2026-04-01. The lower observed absolute difference after that date is descriptive, not causal proof; market regime and the short post-change sample also differ.',
            'source_documents_reviewed_on': '2026-11-06; first-party text reviewed; original PDF raw bytes and hashes are not retained in this package.',
            'hdfc_fundamental_attribute_change_effective_date': '2026-04-22',
            'hdfc_fundamental_attribute_change_source': 'https://files.hdfcfund.com/s3fs-public/2026-03/2059-%20Notice-%20Change%20in%20Fundamental%20attributes%20-%20HDFC%20Gold%20ETF-%20ETCD-w.e.f-%20April%2022%2C%202026.pdf?VersionId=vqbMTvRC.oT_yPvSfogeDNdsg1p9lpSA',
            'hdfc_fundamental_attribute_change_note': 'Permitted asset types expanded to specified gold-related instruments, including gold ETCDs; this is a separate regime boundary from SEBI valuation change effective 2026-04-01.',
            'documented_customs_duty_event_alignment': customs_duty_event,
        },
        'date_label_close_vs_reported_nav_difference': {
            'definition': '(NSE close / same-calendar-date AMFI NAV - 1) * 100',
            'interpretation_limit': 'Dates are joined by date label only. This is not a synchronized intraday premium/discount, bid/ask spread, transaction cost, or executable price estimate.',
            'matched_dates': len(joined),
            'median_pct': s(median_dec(gaps)) if gaps else None,
            'median_absolute_pct': s(median_dec(abs_gaps)) if gaps else None,
            'p05_linear_interpolation_pct': s(pct(gaps, 0.05)),
            'p95_linear_interpolation_pct': s(pct(gaps, 0.95)),
            'min_pct': s(min(gaps)) if gaps else None,
            'max_pct': s(max(gaps)) if gaps else None,
            'by_calendar_year': gaps_by_year,
            'by_nav_valuation_policy_regime': regime_comparison,
            'largest_absolute_differences': [
                {'date': r['date'], 'symbol': r['symbol'], 'close_inr': s(r['close']), 'amfi_nav_inr': s(r['nav']),
                 'difference_pct': s(r['gap_pct']), 'volume_units': r['volume'], 'trade_count': r['trades']}
                for r in largest
            ],
        },
        'fund_economics_and_portfolio_snapshots': {
            'official_source': 'HDFC Mutual Fund factsheets',
            'factsheets': [
                {'as_of': '2026-05-29', 'ter_pct_per_annum': '0.59', 'gold_pct_nav': '98.62', 'cash_and_net_assets_pct_nav': '1.38', 'tracking_error_pct': '0.39', 'source': 'https://files.hdfcfund.com/s3fs-public/2026-06/Fund%20Facts%20-%20HDFC%20NIFTY%20Gold%20ETF_June%2026.pdf'},
                {'as_of': '2026-07-31', 'ter_pct_per_annum': '0.59', 'gold_pct_nav': '98.44', 'cash_and_net_assets_pct_nav': '1.56', 'tracking_error_pct': '0.39', 'source': 'https://files.hdfcfund.com/s3fs-public/2026-08/HDFC%20MF%20Index%20Solutions%20Factsheet%20-%20July%202026.pdf'},
                {'as_of': '2026-09-30', 'ter_pct_per_annum': '0.59', 'gold_pct_nav': '98.51', 'cash_and_net_assets_pct_nav': '1.49', 'tracking_error_pct': '0.39', 'source': 'https://files.hdfcfund.com/s3fs-public/Others/2026-10/Fund%20Facts%20-%20HDFC%20NIFTY%20Gold%20ETF_Oct%2026.pdf?VersionId=Urji0l0XNDIBQJrIAuoj84IDXdJFPsm9'}
            ],
            'factsheet_note': 'Snapshots report aggregate Gold and cash. They do not separately disclose exposure to permitted ETCDs; do not infer actual ETCD use or zero exposure from aggregate categories.',
            'inception_date': '2010-08-13'
        },
        'nse_daily_price_and_activity_diagnostics': activity_diagnostics,
        'historical_order_book_access': {
            'source': 'NSE Data & Analytics 2026 domestic tariff and historical order/trade specification',
            'tariff_url': 'https://nsearchives.nseindia.com//web/mediaattachment/2026-04/Download_Pricing_file_-_Domestic_clients_20260424122229.pdf',
            'specification_url': 'https://nsearchives.nseindia.com/web/mediaattachment/2026-05/NSE_Hist_Order_Trade_Data_1.18_20260518122214.pdf',
            'published_list_price_inr_per_year_single_site': 1250000,
            'listed_product': 'Historical Order & Trade Data, Capital Market; taxes/levies excluded; tariff effective 2026-04-01',
            'historical_trade_only_list_price_inr_per_year_single_site': 110000,
            'trade_only_limit': 'Trade-only data do not include the order-book event history required to reconstruct quoted bid/ask depth.',
            'disposition': 'No subscription or purchase was made. If acquired solely for the HDFCGOLD gate, the annual list price is about 29.8% of the mandate’s initial capital before tax. Broader value across all planned listed candidates has not been assessed. Keep spread/slippage unqualified; do not procure without a specific investor-approved value case.',
        },
        'qualification': {
            'qualified': ['raw NSE archive capture and byte hash', 'basic daily-row/date/price integrity for this five-year file', 'exact-date descriptive close-to-AMFI-NAV comparison over available retained overlap', 'first-party review of NAV valuation-method and publication-clock changes', 'descriptive pre/post 2026-04-01 valuation-regime comparison', 'daily high-low, close-to-average, volume and trade-count diagnostics'],
            'not_qualified': ['historical bid/ask spread or market depth', 'execution costs or slippage', 'synchronized intraday premium/discount', 'investor-specific broker availability or suitability', 'full HDFCGOLD investability gate', 'G6.3 closure or investment authorization'],
            'next_evidence_needed': ['timestamped iNAV or historical order-book data for event-level premium/spread diagnostics only if the cost is justified and explicitly approved', 'source-level review of the seven in-window NSE dates without same-date AMFI rows if they affect a return series', 'capture/retention of official AMFI observations after 2026-10-30 before extending the matched-date window'],
            'decision_state': 'G6.3 OPEN; NO-GO / NOT YET EVALUATED'
        }
    }
    args.output.write_text(json.dumps(out, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(out, indent=2, ensure_ascii=True))

if __name__ == '__main__':
    main()




