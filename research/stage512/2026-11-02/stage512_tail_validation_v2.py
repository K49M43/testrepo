#!/usr/bin/env python3
"""Stage 5.12: reproducible competing-tail predictive-score audit.

Requires original pinned six source files retrieved by stage512_predictive_validation.py.
Run:
    python stage512_tail_validation_v2.py --fetch --out-dir out
Or:
    python stage512_tail_validation_v2.py --data-dir ./snapshots --out-dir out
    python stage512_tail_validation_v2.py --self-test

Does NOT validate an investor's 2036 wealth probability, a true G-Sec total return,
a 2024-base MoSPI-linked CPI, or ETF NAV series. Tail-test input is the *old proxy*
panel, and result MUST retain PROVISIONAL until primary source replacements pass.
"""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
import numpy as np
from scipy.stats import t, norm
from scipy.special import gammaln
from stage512_predictive_validation import get_monthly_data, portfolio_log_return

LOOKBACK = 60
START = '2016-01'
NUS = (3, 5, 8, 12)  # All alternatives frozen before evaluation


def student_logpdf_unitvariance(z: float, nu: int) -> float:
    """Student-t density of standardized residual with VARIANCE 1, nu>2."""
    if nu <= 2:
        raise ValueError('nu must exceed 2 for finite variance')
    scale = math.sqrt((nu - 2) / nu)
    raw = z / scale
    return float(t.logpdf(raw, df=nu) - math.log(scale))


def student_unit_quantile(p: float, nu: int) -> float:
    return float(t.ppf(p, nu) * math.sqrt((nu - 2)/nu))


def score_series(rows, which: str):
    histories = []
    for month, x in rows:
        pr = portfolio_log_return(x)
        val = {'equity': x[0], 'portfolio': pr, 'real_portfolio': pr-x[4], 'cpi': x[4]}[which]
        histories.append((month, float(val)))
    scores = []
    for i in range(LOOKBACK, len(histories)):
        if histories[i][0] < START:
            continue
        past = np.array([x[1] for x in histories[i-LOOKBACK:i]], dtype=float)
        mu = float(past.mean())
        sd = float(past.std(ddof=1))
        assert sd>0 and np.isfinite(sd)
        month, observed = histories[i]
        z = (observed-mu)/sd
        glog = float(norm.logpdf(z)-math.log(sd))
        alt = {f't{nu}': student_logpdf_unitvariance(z,nu)-math.log(sd) for nu in NUS}
        row={'month':month,'z':float(z),'gaussian_logpdf':glog,
            'gaussian_var_1pct':bool(z<norm.ppf(.01)),
            'gaussian_var_5pct':bool(z<norm.ppf(.05))}
        for nu in NUS:
            row[f't{nu}_logpdf']=alt[f't{nu}']
            row[f't{nu}_var_1pct']=bool(z<student_unit_quantile(.01,nu))
            row[f't{nu}_var_5pct']=bool(z<student_unit_quantile(.05,nu))
        scores.append(row)
    assert scores and scores[0]['month'] == START
    out = {'series':which,'oos_start':scores[0]['month'],'oos_end':scores[-1]['month'],
           'observations':len(scores),'training_months':LOOKBACK,
           'total_gaussian_log_score':round(sum(x['gaussian_logpdf'] for x in scores),3),
           'student_log_scores':{f't{nu}':round(sum(x[f't{nu}_logpdf'] for x in scores),3) for nu in NUS},
           'gaussian_1pct_exceptions':sum(x['gaussian_var_1pct'] for x in scores),
           'student5_1pct_exceptions':sum(x['t5_var_1pct'] for x in scores),
           'gaussian_5pct_exceptions':sum(x['gaussian_var_5pct'] for x in scores),
           'student5_5pct_exceptions':sum(x['t5_var_5pct'] for x in scores)}
    out['student5_minus_gaussian_log_score']=round(out['student_log_scores']['t5']-out['total_gaussian_log_score'],3)
    no_mar=[x for x in scores if x['month']!='2020-03']
    out['student5_minus_gaussian_excluding_mar2020']=round(sum(x['t5_logpdf']-x['gaussian_logpdf'] for x in no_mar),3)
    lows=sorted(scores,key=lambda x:x['z'])[:3]
    out['worst_standardized_residuals']=[{'month':x['month'],'z':round(x['z'],3)} for x in lows]
    return out, scores


def self_test():
    for nu in NUS:
        assert abs(student_unit_quantile(.5,nu))<1e-12
        assert np.isfinite(student_logpdf_unitvariance(-6.8,nu))
    assert student_logpdf_unitvariance(-6.8,5)>float(norm.logpdf(-6.8))
    assert student_unit_quantile(.01,5)<float(norm.ppf(.01))
    from stage512_predictive_validation import selftest as original_selftest
    original_selftest()
    print('TAIL MODEL SELFTEST PASSED: standardized scale, crisis score, quantile, and base arithmetic')


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--self-test',action='store_true')
    p.add_argument('--fetch',action='store_true')
    p.add_argument('--data-dir',default='.')
    p.add_argument('--out-dir',default='.')
    a=p.parse_args()
    if a.self_test:
        self_test();return
    rows=get_monthly_data(a.fetch,Path(a.data_dir))
    assert len(rows)==219 and rows[0][0]=='2006-07' and rows[-1][0]=='2024-09', 'Historical panel changed'
    results={}
    for s in ('equity','portfolio','real_portfolio','cpi'):
        results[s],_ =score_series(rows,s)
    manifest={
      'status':'PROVISIONAL. FULL 2036 PREDICTIVE VALIDATION NOT COMPLETE',
      'source':'six-pinned-proxy historical series; see stage512_predictive_validation.py',
      'strict_training':'60 prior months, monthly predictions 2016-01 to 2024-09',
      'models':['Gaussian','variance-normalized fixed t(3), t(5), t(8), t(12)'],
      'model_selection_warning':'Comparing choices on this same holdout is exploratory; winning t(5) is not independently confirmed',
      'limitations':['2024-base linked official CPI absent', 'Bond duration proxy is not bond-index TRI',
       'Metals USD*FX are not RBI Mumbai or ETFs', 'One crisis dominates t superiority',
       'Only 105 out-of-sample months; rare tails and 10-year success cannot be calibrated',
       'Historical scores are monthly simple-allocation proxies, not SIP lot-based investor outcomes'],
      'results':results}
    out=Path(a.out_dir);out.mkdir(parents=True,exist_ok=True)
    (out/'stage512_tail_validation_v2_results.json').write_text(json.dumps(manifest,indent=2))
    print(json.dumps(results,indent=2))

if __name__=='__main__': main()