"""Stage 5.12 risk-model audit, November 2026. Illustrative assumptions; not investment advice or calibrated probabilities.
Measures provisional full-liquidation equivalent value in 2026 rupees. All amounts INR lakh.
Current tax rules are not forecasts of 2036 rules. No executable investment is represented.
"""
import argparse, numpy as np, csv, json
from pathlib import Path
parser=argparse.ArgumentParser(description='Reproduce synthetic Stage 5.12 risk assumptions; no historical return replay is performed.')
parser.add_argument('--output-dir',required=True,help='New output directory; do not point at the preserved 2026-11-02 artifacts.')
OUT=Path(parser.parse_args().output_dir)
OUT.mkdir(parents=True,exist_ok=True)
SEED=20261102
N=25000
MONTHS=122
START=42.0
SIP=np.array([.25*1.1**(m//12) for m in range(MONTHS)],dtype=float)
W={
 'Balanced 65/20/10/5':np.array([.65,.20,.10,.05]),
 'Growth 75/15/10/0':np.array([.75,.15,.10,.0]),
 'Defensive 50/30/20/0':np.array([.50,.30,.20,.0]),
}
CORR_BASE=np.array([
 [1,.10,-.10,.20,-.15],
 [.10,1,.10,.05,-.15],
 [-.10,.10,1,.60,.25],
 [.20,.05,.60,1,.20],
 [-.15,-.15,.25,.20,1]],float)
CORR_STRESS=np.array([
 [1,.40,.10,.45,-.25],
 [.40,1,.15,.20,-.25],
 [.10,.15,1,.65,.25],
 [.45,.20,.65,1,.15],
 [-.25,-.25,.25,.15,1]],float)
for c in [CORR_BASE,CORR_STRESS]:
 assert np.max(np.abs(c-c.T))<1e-12 and np.min(np.linalg.eigvalsh(c))>1e-8, np.linalg.eigvalsh(c)
PE0=21.; DIV=.0128
EQUITY_GEO=lambda g,end_pe:(1+g)*(end_pe/PE0)**.1*(1+DIV)-1
SCENARIOS={
 'Adverse valuation':{'eps':.06,'terminal_pe':16.,'returns':[None,.065,.03,.02],'vol':[.22,.07,.18,.35], 'cpi':.07, 'cpi_vol':.03,'corr':CORR_STRESS},
 'Central assumptions':{'eps':.09,'terminal_pe':19.,'returns':[None,.07,.055,.06],'vol':[.17,.05,.16,.28], 'cpi':.06, 'cpi_vol':.02,'corr':CORR_BASE},
 'Strong equity':{'eps':.11,'terminal_pe':23.,'returns':[None,.075,.07,.09],'vol':[.17,.05,.16,.28], 'cpi':.045, 'cpi_vol':.02,'corr':CORR_BASE},
 'Synthetic 11.8% equity geometric-return assumption':{'eps':None,'terminal_pe':None,'equity_geo':.118,'returns':[None,.07,.055,.06],'vol':[.17,.05,.16,.28], 'cpi':.06, 'cpi_vol':.02,'corr':CORR_BASE},
 'Central fat tails':{'eps':.09,'terminal_pe':19.,'returns':[None,.07,.055,.06],'vol':[.17,.05,.16,.28], 'cpi':.06, 'cpi_vol':.02,'corr':CORR_BASE, 'shock_dist':'student_t_5'},
 'Stagflation stress':{'eps':.06,'terminal_pe':16.,'returns':[None,.05,.09,.03],'vol':[.25,.08,.22,.35], 'cpi':.08, 'cpi_vol':.04,'corr':CORR_STRESS},
}
COST=np.array([.002,.002,.004,.007]) # cost is deducted because assumed returns are pre-fees
rng=np.random.default_rng(SEED)
Z=rng.standard_normal((N,MONTHS,5),dtype=np.float32)

def final_tax(w, price, units, monthly_prices, t):
    # Tax lot approximation for one fund per sleeve, no transactions until hypothetical full redemption.
    # Purchases at the end of the month; purchases at exactly 12 months treated as ST.
    # No capital-loss netting, external CG, surcharge, or inflation-linked instrument.
    prior_unit=units
    recent_prices=monthly_prices[:,max(1,t-12):t+1,:]
    recent_sips=SIP[max(0,t-13):t]
    assert len(recent_sips)==recent_prices.shape[1]
    recent_units=(recent_sips[None,:,None]/recent_prices).sum(axis=1)
    recent_basis=recent_sips.sum()
    gross_by_asset=price*prior_unit*w
    st_value=price*recent_units*w
    st_basis=recent_basis*w
    lt_value=gross_by_asset-st_value
    lt_basis=(START+SIP[:t].sum()-recent_basis)*w
    lt_gain=lt_value-lt_basis
    st_gain=st_value-st_basis
    # Only positive gains charged; loss offset and loss carry-forward omitted.
    eqtax=.13*np.maximum(lt_gain[:,0]-1.25,0)+.208*np.maximum(st_gain[:,0],0)
    debttax=.312*np.maximum(gross_by_asset[:,1]-(START+SIP[:t].sum())*w[1],0)
    metaltax=(.13*np.maximum(lt_gain[:,2:],0)+.312*np.maximum(st_gain[:,2:],0)).sum(axis=1)
    friction=.001*gross_by_asset.sum(axis=1)+.00001*gross_by_asset[:,0]
    tax=eqtax+debttax+metaltax
    return gross_by_asset.sum(axis=1)-tax-friction,tax,friction

def simulate(s):
    ret=np.array(s['returns'],float);ret[0]=s.get('equity_geo',EQUITY_GEO(s['eps'],s['terminal_pe']) if s.get('eps') is not None else float('nan'))
    logdrift=np.log1p(ret)-np.log1p(COST)
    std=np.array([*s['vol'],s['cpi_vol']])
    ch=np.linalg.cholesky(s['corr'])
    z=Z if s.get('shock_dist') is None else (np.random.default_rng(SEED+1).standard_t(5,size=Z.shape)*np.sqrt(3/5)).astype(np.float32)
    shocks=(z@ch.T)*std[None,None,:]/np.sqrt(12)
    # lognormal shocks; specified long-run return is geometric median for constant regime
    growth=np.exp(logdrift[None,None,:]/12+shocks[:,:,:4])
    cpi_grow=np.exp(np.log1p(s['cpi'])/12+shocks[:,:,4])
    prices=np.ones((N,MONTHS+1,4),dtype=np.float32)
    for m in range(1,MONTHS+1):prices[:,m,:]=prices[:,m-1,:]*growth[:,m-1,:]
    units=np.full((N,4),START,dtype=float)
    cpi=np.ones(N,dtype=float)
    rows=[]
    first_hit={key:np.zeros(N,dtype=bool) for key in W}
    floor_hit={key:np.zeros(N,dtype=bool) for key in W}
    out={}
    for month in range(1,MONTHS+1):
        units+=SIP[month-1]/prices[:,month,:]
        cpi*=cpi_grow[:,month-1]
        if month<111:continue
        for name,w in W.items():
            net,tax,friction=final_tax(w,prices[:,month,:],units,prices,month)
            real=net/cpi
            first_hit[name]|=(real>=100)
            floor_hit[name]|=(real>=90)
            if month not in (120,122):continue
            miss=real<90
            p5=np.percentile(real,5)
            row={
             'scenario':s['name'],
             'scenario_classification':('SYNTHETIC_ASSUMPTION_NOT_HISTORICAL_REPLAY' if s['name'].startswith('Synthetic 11.8%') else 'SYNTHETIC_MODEL_SCENARIO'),
             'equity_return_provenance_status':('UNVERIFIED_THIRD_PARTY_REPORTED_CAGR_USED_AS_SYNTHETIC_ASSUMPTION' if s['name'].startswith('Synthetic 11.8%') else 'MODEL_ASSUMPTION_NOT_INDEPENDENTLY_VALIDATED'),
             'portfolio':name,'month':month,'gross_median_L':round(float(np.median((prices[:,month,:]*units*w).sum(axis=1))),3),
             'tax_median_L':round(float(np.median(tax)),3),'net_median_L':round(float(np.median(net)),3),
             'real_median_L':round(float(np.median(real)),3),'real_p05_L':round(float(p5),3),'real_p15_L':round(float(np.percentile(real,15)),3),
             'real_p95_L':round(float(np.percentile(real,95)),3),'model_floor_hit_pct':round(float(100*(~miss).mean()),2),
             'model_target_hit_pct':round(float(100*(real>=100).mean()),2),
             'conditional_shortfall_L':round(float(np.mean(90-real[miss])),3) if miss.any() else 0,
             'expected_shortfall_L':round(float(np.maximum(90-real,0).mean()),3),
             'median_inflation_factor':round(float(np.median(cpi)),4),
             'median_friction_L':round(float(np.median(friction)),3),
            }
            rows.append(row)
    for row in rows:
        if row['month']==122:
            key=row['portfolio']
            row['window_ever_reach_90_pct']=round(float(floor_hit[key].mean()*100),2)
            row['window_ever_reach_100_pct']=round(float(first_hit[key].mean()*100),2)
        else:
            row['window_ever_reach_90_pct']=''
            row['window_ever_reach_100_pct']=''
    return rows,ret

rows=[];assumptions=[]
for name,s0 in SCENARIOS.items():
 s={**s0,'name':name};r,ret=simulate(s);rows.extend(r)
 assumptions.append({'scenario':name,'scenario_classification':('SYNTHETIC_ASSUMPTION_NOT_HISTORICAL_REPLAY' if name.startswith('Synthetic 11.8%') else 'SYNTHETIC_MODEL_SCENARIO'),
 'equity_return_provenance_status':('UNVERIFIED_THIRD_PARTY_REPORTED_CAGR_USED_AS_SYNTHETIC_ASSUMPTION' if name.startswith('Synthetic 11.8%') else 'MODEL_ASSUMPTION_NOT_INDEPENDENTLY_VALIDATED'),
 'equity_return_geometric_assumed':round(float(ret[0]),5),'gilt_return_assumed':ret[1],
 'gold_return_assumed':ret[2],'silver_return_assumed':ret[3], 'cpi_drift':s['cpi'], 'vol_equity':s['vol'][0],
 'vol_gilt':s['vol'][1], 'vol_gold':s['vol'][2], 'vol_silver':s['vol'][3], 'cpi_vol':s['cpi_vol'],
 'max_corr_eigenvalue':float(np.linalg.eigvalsh(s['corr']).max()),'min_corr_eigenvalue':float(np.linalg.eigvalsh(s['corr']).min()), 'shock_dist':s.get('shock_dist','normal')})
# unit tests for basics
assert abs(START+SIP[:120].sum()-89.812273803)<1e-7
assert abs(START+SIP[:122].sum()-91.109)<.01
assert abs((1.06)**10-1.7908477)<1e-5
assert abs((1.06)**(122/12)-1.8083)<.001
assert all(abs(w.sum()-1)<1e-12 for w in W.values())
assert all(row['real_p05_L']<=row['real_median_L']<=row['real_p95_L'] for row in rows)
assert all(row['net_median_L']<row['gross_median_L'] for row in rows)
# Falsification tests: flat asset prices imply zero CG tax; only stated redemption friction applies.
prices_flat=np.ones((1,15,4));t=14;units_flat=np.full((1,4),START+SIP[:t].sum())
flat_net,flat_tax,flat_friction=final_tax(np.array([.65,.2,.1,.05]),np.ones((1,4)),units_flat,prices_flat,t)
assert np.max(np.abs(flat_tax))<1e-9
assert np.allclose(flat_net+flat_friction,START+SIP[:t].sum())
assert np.isclose((1.06)**10/(1.05)**10,1.0994,atol=.001)
with (OUT/'stage512_risk_scenarios.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
with (OUT/'stage512_assumption_register.json').open('w') as f:
 json.dump({'source_evidence':'The 0.118 equity input is a third-party reported historical CAGR used only as a synthetic model parameter; its exact as-of calculation and raw 1995-to-2026 TRI path are not independently verified. It is not a forecast or historical replay.',
 'model_run_type':'SYNTHETIC_ASSUMPTION_SCENARIOS_ONLY_NO_HISTORICAL_REPLAY',
 'g5_1_correction_record':'research/stage512/2026-11-05/g5_1_118_claim_lineage_v1.json',
 'return_caveat':'Hypothetical valuation-sensitive geometric returns, forward risk distributions uncalibrated.',
 'tax':'Simplified current-law terminal liquidation, no gains/loss cross offset and no future rate changes',
 'correlation':'Hypothetical positive definite matrices; not history fitted.',
 'models':assumptions},f,indent=2)
print('Assumptions:')
for a in assumptions:print(a)
print('\nOct 2036 / 120 month results:')
for r in rows:
 if r['portfolio']=='Balanced 65/20/10/5' and r['month']==120:print({k:r[k] for k in ('scenario','gross_median_L','tax_median_L','net_median_L','real_median_L','real_p05_L','model_floor_hit_pct','model_target_hit_pct')})
print('\nDec 2036 / 122 month results:')
for r in rows:
 if r['portfolio']=='Balanced 65/20/10/5' and r['month']==122:print({k:r[k] for k in ('scenario','gross_median_L','tax_median_L','net_median_L','real_median_L','real_p05_L','model_floor_hit_pct','model_target_hit_pct')})
print('Run complete',len(rows),'rows')
