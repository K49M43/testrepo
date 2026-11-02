#!/usr/bin/env python3
"""Stage 5.12: controlled model/parameter uncertainty audit, 2 November 2026.
Research only. All figures are synthetic conditional simulation frequencies, NOT empirical
future success probabilities, and not a guaranteed CPI-linked floor.
NumPy required. Run: python stage512_model_uncertainty.py
"""
from pathlib import Path
import csv,json,math
import numpy as np

OUT=Path(__file__).resolve().parent
H=json.loads((OUT/'stage512_empirical_calibration.json').read_text())
N=20000; M=122; SEED=20261102
W=np.array([.65,.20,.10,.05])
INITIAL=42.; MONTHLY=np.array([.25*1.1**(i//12) for i in range(M)])
EXPENSE=np.array([.002,.002,.004,.007]); FRICTION=0.001
BASE=np.array([.09328,.07,.07304,.045]); INFL=.06
rng=np.random.default_rng(SEED)
# Shared, paired innovations: use identical random numbers for all sensitivity cases.
Z=rng.standard_normal((N,M,5),dtype=np.float32)
CHI=rng.chisquare(5,size=(N,M)).astype(np.float32)

# Model variants are NOT assigned likelihoods, to avoid false Bayesian confidence.
VARIANTS=[
 {'name':'Base iid Gaussian','type':'baseline','panel':'2007_2024'},
 {'name':'Recent covariance only','type':'covariance','panel':'2013_2024'},
 {'name':'Equity -2pp CAGR','type':'mean return','panel':'2007_2024','shift':[-.02,0,0,0]},
 {'name':'Equity -4pp CAGR','type':'mean return','panel':'2007_2024','shift':[-.04,0,0,0]},
 {'name':'Risky assets -2pp CAGR','type':'mean return','panel':'2007_2024','shift':[-.02,0,-.02,-.02]},
 {'name':'Gilt return -1pp','type':'mean return','panel':'2007_2024','shift':[0,-.01,0,0]},
 {'name':'Inflation 7% iid','type':'inflation mean','panel':'2007_2024','inflation':.07},
 {'name':'Inflation 8% iid','type':'inflation mean','panel':'2007_2024','inflation':.08},
 {'name':'Persistent inflation AR 0.85','type':'inflation dependence','panel':'2007_2024','phi':.85},
 {'name':'Multivariate Student-t df5','type':'fat tails','panel':'2007_2024','t5':True},
 {'name':'Market shock Aug 2036','type':'deterministic stress','panel':'2007_2024','shock':True},
 {'name':'Equity -2pp + CPI7% + persistence','type':'compound stress','panel':'2007_2024','shift':[-.02,0,0,0],'inflation':.07,'phi':.85},
 {'name':'Stagflation + CPI8% persistence','type':'compound stress','panel':'2007_2024','returns':[.05,.055,.03,-.02],'inflation':.08,'phi':.85},
]


def paths(spec):
    p=H['panels'][spec['panel']]
    vol=np.array(p['annualized_log_vol_pct'],float)/100
    corr=np.array(p['correlation'],float)
    assert np.linalg.eigvalsh(corr).min()>0
    shock=np.matmul(Z,np.linalg.cholesky(corr).T).astype(np.float64)
    if spec.get('t5'):
        # Standardized unit-variance multivariate Student t; common stochastic
        # variance scale for each month creates symmetric fat tails / co-tail moves.
        shock*=np.sqrt((5-2)/CHI)[:,:,None]
    annual=np.array(spec.get('returns',BASE),dtype=float)+np.array(spec.get('shift',[0]*4),float)
    assert np.all(annual>-1)
    logmeans=(np.log1p(annual)-np.log1p(EXPENSE))/12
    rlog=logmeans[None,None,:]+shock[:,:,:4]*vol[None,None,:4]/np.sqrt(12)
    if spec.get('shock'):
        # 118th month (Aug 2036). All paths impacted; scenario-conditioned,
        # NOT a random event assigned an ex-ante occurrence probability.
        rlog[:,117,:]+=np.log(np.array([.65,.96,.95,.75]))
    cpi_center=spec.get('inflation',INFL)
    phi=spec.get('phi',0)
    base_sd=vol[4]/np.sqrt(12)
    if phi:
        cpi_deviation=np.empty((N,M),dtype=np.float64)
        cpi_deviation[:,0]=base_sd*shock[:,0,4]
        for t in range(1,M):
            cpi_deviation[:,t]=phi*cpi_deviation[:,t-1]+np.sqrt(1-phi*phi)*base_sd*shock[:,t,4]
    else:cpi_deviation=base_sd*shock[:,:,4]
    inflog=np.log1p(cpi_center)/12+cpi_deviation
    return rlog,inflog,annual,cpi_center


def terminal_outcome(rlog,inflog,term):
    rlog=rlog[:,:term,:];inflog=inflog[:,:term]
    cumlogs=np.cumsum(rlog,axis=1)
    # Actual modeled NAV starts at 1 before any purchase, grows monthly.
    current_price=np.exp(cumlogs[:,-1,:]); buyprice=np.exp(cumlogs)
    # Base at time zero, then end-of-month monthly SIP payments, FIFO tax lots.
    gross_asset=INITIAL*W[None,:]*current_price
    sip_units=MONTHLY[:term][None,:,None]*W[None,None,:]/buyprice
    gross_asset+=np.sum(sip_units,axis=1)*current_price
    gross=float('nan')
    total_contrib=INITIAL+MONTHLY[:term].sum()
    short_start=max(0,term-12-1) # includes purchases aged exactly 12 months
    recent_units=sip_units[:,short_start:,:].sum(axis=1)
    recent_basis=MONTHLY[short_start:term].sum()*W
    short_val=recent_units*current_price
    short_gain=short_val-recent_basis
    long_gain=gross_asset-short_val-(total_contrib*W-recent_basis)
    # Flat 2026-level hypothetical tax rules, no cross-asset loss carry/offset.
    eq_lt=.13*np.maximum(long_gain[:,0]-1.25,0)
    eq_st=.208*np.maximum(short_gain[:,0],0)
    debt=.312*np.maximum(gross_asset[:,1]-total_contrib*W[1],0)
    metal_lt=.13*np.maximum(long_gain[:,2:],0).sum(axis=1)
    metal_st=.312*np.maximum(short_gain[:,2:],0).sum(axis=1)
    gross=gross_asset.sum(axis=1)
    taxes=eq_lt+eq_st+debt+metal_lt+metal_st
    fr=FRICTION*gross+.00001*gross_asset[:,0]
    net=gross-taxes-fr
    cpi=np.exp(np.sum(inflog,axis=1));real=net/cpi
    assert np.isfinite(real).all() and (real>0).all()
    return real,net,gross,taxes,cpi


def summarize(spec,term,real,net,gross,tax,cpi,annual,inf):
    fails=real<90
    failrate=fails.mean(); n=len(real)
    shortfall=np.maximum(90-real,0)
    out={
      'variant':spec['name'],'variant_type':spec['type'],'month':term,'n_paths':n,
      'equity_gross_return_hypothesis_pct':round(100*annual[0],3),
      'annual_inflation_center_pct':round(100*inf,2),
      'median_gross_nominal_L':round(float(np.median(gross)),3),
      'median_tax_L':round(float(np.median(tax)),3),
      'median_net_nominal_L':round(float(np.median(net)),3),
      'median_real_L':round(float(np.median(real)),3),
      'p05_real_L':round(float(np.percentile(real,5)),3),
      'p15_real_L':round(float(np.percentile(real,15)),3),
      'p95_real_L':round(float(np.percentile(real,95)),3),
      'pct_above_90':round(100*(1-failrate),2),
      'pct_above_100':round(100*np.mean(real>=100),2),
      'expected_shortfall_90_L':round(float(shortfall.mean()),3),
      'conditional_shortfall_90_L':round(float(shortfall[fails].mean()),3),
      'bottom5_mean_L':round(float(real[real<=np.percentile(real,5)].mean()),3),
      'median_CPI_factor':round(float(np.median(cpi)),4),
      'MC_sampling_SE_floor_percent_points':round(100*math.sqrt(failrate*(1-failrate)/n),3),
      'floor85_pass':bool(np.percentile(real,15)>=90),
    }
    return out


def main():
    rows=[];baseline_by_term={}
    for s in VARIANTS:
        print('RUN',s['name'],flush=True)
        rlog,inflog,ret,inf=paths(s)
        for term in (120,122):
            real,net,gross,tax,cpi=terminal_outcome(rlog,inflog,term)
            if s['name']=='Base iid Gaussian':baseline_by_term[term]=real
            rows.append(summarize(s,term,real,net,gross,tax,cpi,ret,inf))
    fn=OUT/'stage512_model_uncertainty_results.csv'
    with fn.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    # Model validation and invariants: no genuine forecast gate can be granted.
    assert abs(INITIAL+MONTHLY[:120].sum()-89.812273803)<1e-7
    assert abs(INITIAL+MONTHLY[:122].sum()-91.109)<.01
    assert all(r['p05_real_L']<=r['p15_real_L']<=r['median_real_L']<=r['p95_real_L'] for r in rows)
    # Intentionally do not hard-code the expected GO/NO-GO outcome; gate is computed from results.
    # CPI shift test must monotonically lower real wealth under paired paths.
    for term in (120,122):
        a=next(r for r in rows if r['variant']=='Inflation 7% iid' and r['month']==term)
        b=next(r for r in rows if r['variant']=='Inflation 8% iid' and r['month']==term)
        assert a['median_real_L']>b['median_real_L']
    manifest={'date':'2026-11-02','decision':'Scenario-robustness stress audit; NO-GO remains, NOT a calibrated 2036 probability',
    'n_paths':N,'seed':SEED,'period_months':[120,122],
    'starting_amount_lakh':INITIAL,'initial_sip_lakh':MONTHLY[0],
    'annual_sip_step_up_pct':10,'gross_nominal_hypotheses_by_asset':dict(zip(['equity','gilt_fund','gold','silver'],BASE.tolist())),
    'inflation_primary':INFL,'portfolio_weights':W.tolist(),'variants':VARIANTS,
    'important_caveats':[
      'No real-world probabilities assigned to scenario variants; cannot average scenario frequencies into calibrated investor success odds.',
      'Stated 85% floor success is a criterion, not a guarantee; any simulated pass would still not create contractual protection.',
      'Historical covariance based on third-party total return, yields-to-duration proxy, bullion converted from USD and CPI compilation, joint sample ends Sep 2024.',
      '2024=100 CPI rebasing from Feb 2026; historical 2012-linked series needs official back-series reconciliation.',
      'All shocks are synthetic conditional cases; not empirically calibrated conditional crash frequency.',
      'AR(1) inflation persistence phi=0.85 is hypothetical and deliberately preserves marginal monthly inflation variance; cumulative CPI uncertainty grows.',
      'Student-t5 innovations standardized to unit variance and coupled by one per-month mixing variance, an assumed co-tail structure.',
      'Market-shock case forces a crisis in every trajectory in Aug 2036; not an estimated event probability.',
      'One notional mutual fund/ETF sleeve per class, static contribution allocation, no interim rebalancing.',
      '2026 simplified tax rates and lot rules, no investor-specific realized losses, surcharge, changes to future taxes, or actual products/retail pricing.',
      'Govt bond proxy is a tradable duration fund proxy, not a maturity-matched, held-to-maturity G-Sec or guaranteed yield.',
      'Parameter perturbations are explicit stress designs rather than formal posterior confidence/credible intervals.',
      'Returns and CPI are synchronous monthly; real CPI release lags are not simulated.',
    ],
    'sensitivity_results_file':fn.name}
    (OUT/'stage512_model_uncertainty_assumptions.json').write_text(json.dumps(manifest,indent=2))
    print('RESULTS:')
    for r in rows:
        if r['month']==122:
            print(f"{r['variant']:<38} median={r['median_real_L']:>7.2f} p15={r['p15_real_L']:>7.2f} hit90={r['pct_above_90']:>6.2f}% tail5={r['p05_real_L']:>7.2f}")
    print('ROWS',len(rows),'PATHS',N,'CSV',fn)

if __name__=='__main__': main()