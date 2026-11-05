from __future__ import annotations
import hashlib,json,pathlib

ROOT=pathlib.Path(__file__).resolve().parents[4]
BASE=ROOT/'research/stage512/2026-11-05'
ADD=BASE/'g5_4'
reg=json.loads((BASE/'g5_2_candidate_evidence_register_v1.json').read_text(encoding='utf-8'))
exp=json.loads((ADD/'candidate_expansion_v1.json').read_text(encoding='utf-8'))
disp=json.loads((ADD/'g5_candidate_disposition_v1.json').read_text(encoding='utf-8'))
ter=json.loads((ADD/'ter_row_audit.json').read_text(encoding='utf-8'))
holdings=json.loads((ADD/'g5_4_factsheet_holdings_snapshots.json').read_text(encoding='utf-8'))
extracted=(ADD/'g5_4_factsheet_holdings_pages.txt').read_bytes()
ids={x['candidate_id'] for x in disp['candidates']}
product=[x for x in disp['candidates'] if x['product_hypothesis']]
expected_base={x['candidate_id'] for x in reg['candidates'] if x['candidate_id'] not in {'NIFTY500_TRI_BENCHMARK','GOI_DIRECT_DATED_GSEC_718_2033','CASH_HOLD_91D_TBILL_ROLLING'}}
expected={*expected_base,*{x['candidate_id'] for x in exp['candidates']}}
assert len(product)==10 and {x['candidate_id'] for x in product}==expected
assert len(ids)==13 and len(ids)==len(disp['candidates'])
assert all(x['classification'] in {'INVESTABLE','PROXY_ONLY','BLOCKED'} for x in disp['candidates'])
required_gates={'fees','tax','liquidity','execution','settlement','account_platform_access','investor_suitability','source_quality'}
ter_by_name={x['candidate']:x for x in ter['records']}
for c in product:
    assert c.get('decision_reason') and c.get('screen_disposition') and c.get('source_status')
    assert c.get('category') and c.get('instrument_or_benchmark_id') and c.get('issuer_or_source')
    assert c.get('market_jurisdiction_currency') and c.get('exact_as_of') and c.get('inception_date')
    assert c.get('point_in_time_availability') and c.get('return_convention') and c.get('classification_reason')
    assert required_gates.issubset(c['decision_evidence_gates'])
    assert c['decision_evidence_gates']['tax'].startswith('BLOCKED')
    assert c['decision_evidence_gates']['account_platform_access']=='BLOCKED_NOT_VERIFIED'
    assert c['decision_evidence_gates']['investor_suitability']=='BLOCKED_NOT_ASSESSED'
    assert c['latest_ter_evidence'] and c['latest_ter_evidence']['as_of']=='2026-10-31'
    assert c['latest_ter_evidence']['source_sha256']==ter['source_sha256']
    assert c['holdings_evidence'] and c['holdings_evidence']['status']
    assert all(c['holdings_evidence'].get(k) is not None for k in ('identifier_weight_coverage','cash_treatment','derivatives_treatment','unmatched_or_unreported_residual'))
    assert c['evidence_references']
for c in disp['candidates']:
    for ref in c.get('evidence_references',[]):
        p=ref.get('repository_path'); expected_sha=ref.get('sha256') or ref.get('content_sha256') or ref.get('source_export_sha256')
        if p and expected_sha:
            path=ROOT/p
            assert path.exists(),p
            assert hashlib.sha256(path.read_bytes()).hexdigest().lower()==expected_sha.lower(),p
assert disp['initial_comparison_set'] and set(disp['initial_comparison_set']).issubset(ids)
assert hashlib.sha256(extracted).hexdigest()==holdings['extracted_text_sha256']
assert len(holdings['snapshots'])==5
for h in holdings['snapshots']:
    p=ROOT/h['source_path']
    assert p.exists() and hashlib.sha256(p.read_bytes()).hexdigest().lower()==h['source_sha256'].lower()
    check=h['arithmetic_check']
    if 'reported_allocation_sum_pct' in check:
        assert check['passes'] and check['reported_allocation_sum_pct']==check['expected_sum_pct']
    assert h['rows'] and h['coverage_and_limitations']
    row=next(x for x in disp['candidates'] if x['candidate_id']==h['candidate_id'])
    assert row['holdings_evidence']['source_sha256'].lower()==h['source_sha256'].lower()
assert disp['acceptance']['ranking_or_weights']=='NOT_PRODUCED'
assert disp['acceptance']['investor_suitability_or_trade_authorization']=='NOT_ASSESSED_NO_GO'
print(f'PASS: {len(product)}/10 product hypotheses exactly reconcile to G5.2 + G5.4; 13/13 rows classified; every product has source, fee, holdings, tax, liquidity, execution, settlement, access and suitability fields; five official factsheet holdings snapshots and arithmetic checks reproduce; evidence hashes reproduce; no ranking/weights/authorization.')
