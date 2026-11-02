"""Forward-return hypothesis calibration for 2036, research-only; 2026-11-02.
Reproducible simulation with fixed forward hypotheses and independently calculated
historical covariance matrices. All amounts INR lakh. Neither a market-calibrated
forecast nor a buy recommendation; no enforceable real-wealth floor.
"""
from pathlib import Path
import numpy as np, csv, json
OUT=Path('/mnt/data')
H=json.loads((OUT/'stage512_empirical_calibration.json').read_text())
SEED=20261102
N=18000
M=122
W={'65E20G10Au5Ag':np.array([.65,.20,.10,.05]),
   '75E15G10Au0Ag':np.array([.75,.15,.10,0]),
   '50E30G20Au0Ag':np.array([.50,.30,.20,0])}
COST=np.array([.002,.002,.004,.007])
SIP=np.array([.25*1.1**(m//12) for m in range(M)],float)
START=42.0
PE0=21.0; DIV=0.0131

def eq_return(eps,pe1):
    return (1+eps)*(pe1/PE0)**.1*(1+DIV)-1

def gold_fxcross(usd,fx):return (1+usd)*(1+fx)-1

# Returns are hypotheses or structural scenario values, NOT estimated expected values.
# Fixed inflation cases deliberately preserve identical market paths for a clean sensitivity.
central_g=gold_fxcross(.052,.02)
RISK={k:{'vol':np.array(v['annualized_log_vol_pct'])/100,
         'corr':np.array(v['correlation'],float)}
      for k,v in H['panels'].items() if 'correlation' in v}
for k,r in RISK.items():
    assert np.linalg.eigvalsh(r['corr']).min()>1e-6

SCENARIOS=[
 {'name':'Central CPI6 / full risk','eps':.09,'pe':19,'gilt':.07,'gold':central_g,'silver':.045,'cpi':.06,'risk':'2007_2024','type':'valuation hypothesis'},
 {'name':'Central CPI6 / recent risk','eps':.09,'pe':19,'gilt':.07,'gold':central_g,'silver':.045,'cpi':.06,'risk':'2013_2024','type':'covariance sensitivity'},
 {'name':'Central CPI4 / full risk','eps':.09,'pe':19,'gilt':.07,'gold':central_g,'silver':.045,'cpi':.04,'risk':'2007_2024','type':'inflation sensitivity'},
 {'name':'Central CPI8 / full risk','eps':.09,'pe':19,'gilt':.07,'gold':central_g,'silver':.045,'cpi':.08,'risk':'2007_2024','type':'inflation sensitivity'},
 {'name':'Adverse joint regime','eps':.06,'pe':16,'gilt':.06,'gold':.00,'silver':-.02,'cpi':.08,'risk':'2007_2024','type':'adverse scenario'},
 {'name':'Favorable joint regime','eps':.11,'pe':23,'gilt':.074,'gold':gold_fxcross(.052,.04),'silver':.10,'cpi':.04,'risk':'2007_2024','type':'favorable scenario'},
 {'name':'Higher bond carry only','eps':.09,'pe':19,'gilt':.074,'gold':central_g,'silver':.045,'cpi':.06,'risk':'2007_2024','type':'bond sensitivity'},
 {'name':'Gold zero USD + FX2','eps':.09,'pe':19,'gilt':.07,'gold':gold_fxcross(.00,.02),'silver':.045,'cpi':.06,'risk':'2007_2024','type':'gold sensitivity'},
]

# Generate common standard-normal innovations across all scenarios.
rng=np.random.default_rng(SEED)
Z=rng.standard_normal((N,M,5),dtype=np.float32)

def simulate(s):
    r=RISK[s['risk']]
    vol=r['vol']; ch=np.linalg.cholesky(r['corr'])
    innovation=np.matmul(Z,ch.T).astype(np.float64)*vol[None,None,:]/np.sqrt(12)
    hypoth=np.array([eq_return(s['eps'],s['pe']),s['gilt'],s['gold'],s['silver']])
    assert (hypoth>-1).all()
    loggeometric=np.log1p(hypoth)-np.log1p(COST)
    g=np.exp(loggeometric[None,None,:]/12+innovation[:,:,:4])
    infl=np.exp(np.log1p(s['cpi'])/12+innovation[:,:,4])
    price=np.ones((N,M+1,4),dtype=np.float64)
    for t in range(1,M+1):price[:,t]=price[:,t-1]*g[:,t-1]
    ipath=np.cumprod(infl,axis=1)
    # Principal: one synthetic holding per fund/ETF, no rebalancing or interim sales.
    unit=np.full((N,4),START,dtype=np.float64)
    output=[]
    for t in range(1,M+1):
        unit+=SIP[t-1]/price[:,t]
        if t not in (120,122): continue
        contribution=START+SIP[:t].sum()
        # End-of-month SIP at t is age zero, SIP at t-12 is age 12 and treated ST.
        lo=max(1,t-12)
        recent_price=price[:,lo:t+1,:]
        recent_sip=SIP[lo-1:t]
        recent_unit=np.sum(recent_sip[None,:,None]/recent_price,axis=1)
        recent_basis=recent_sip.sum()
        gross_total=price[:,t]*unit
        gross_short=price[:,t]*recent_unit
        gross_long=gross_total-gross_short
        basis_long=contribution-recent_basis
        for name,w in W.items():
            gross=(gross_total*w).sum(axis=1)
            gain_short=(gross_short-recent_basis)*w
            gain_long=(gross_long-basis_long)*w
            # Current-rate simplified full redemption, not future tax-law forecast.
            eq_ltcg=.13*np.maximum(gain_long[:,0]-1.25,0)
            eq_stcg=.208*np.maximum(gain_short[:,0],0)
            gilt=.312*np.maximum((gross_total[:,1]-contribution)*w[1],0)
            metals=(.13*np.maximum(gain_long[:,2:],0)+.312*np.maximum(gain_short[:,2:],0)).sum(axis=1)
            tax=eq_ltcg+eq_stcg+gilt+metals
            friction=.001*gross+.00001*gross_total[:,0]*w[0]
            net=gross-tax-friction
            real=net/ipath[:,t-1]
            bottom=real[real<=np.percentile(real,5)]
            misses=real<90
            def pct(x):return round(float(np.mean(x)*100),2)
            output.append({'scenario':s['name'],'model_type':s['type'],'portfolio':name,'month':t,
                'inflation_scenario_pct':s['cpi']*100,'equity_hypothesis_pct':round(hypoth[0]*100,3),
                'gilt_hypothesis_pct':round(hypoth[1]*100,3),'gold_hypothesis_pct':round(hypoth[2]*100,3),
                'silver_hypothesis_pct':round(hypoth[3]*100,3),'risk_panel':s['risk'],
                'median_gross_nominal_L':round(float(np.median(gross)),3),
                'median_tax_L':round(float(np.median(tax)),3),
                'median_net_nominal_L':round(float(np.median(net)),3),
                'median_real_L':round(float(np.median(real)),3),
                'real_p05_L':round(float(np.percentile(real,5)),3),
                'real_p15_L':round(float(np.percentile(real,15)),3),
                'real_p95_L':round(float(np.percentile(real,95)),3),
                'pct_real_below90':pct(misses),'pct_real_above90':pct(~misses),
                'pct_real_above100':pct(real>=100),
                'mean_shortfall_all_L':round(float(np.maximum(90-real,0).mean()),3),
                'mean_shortfall_conditional_L':round(float(np.mean(90-real[misses])),3) if misses.any() else 0,
                'lowest5_mean_L':round(float(bottom.mean()),3),
                'median_cpi_factor':round(float(np.median(ipath[:,t-1])),5)})
    return output

rows=[]
for s in SCENARIOS:
    r=simulate(s)
    rows.extend(r)
    print(s['name'],[(a['portfolio'],a['month'],a['median_real_L'],a['real_p15_L'],a['pct_real_above90']) for a in r if a['month']==122],flush=True)
assert abs(START+SIP[:120].sum()-89.812273803)<1e-7
assert abs(START+SIP[:122].sum()-91.109)<.01
assert all(x['real_p05_L']<=x['real_p15_L']<=x['median_real_L']<=x['real_p95_L'] for x in rows)
assert len(rows)==len(SCENARIOS)*len(W)*2
p=OUT/'stage512_forward_calibration_scenarios.csv'
with p.open('w',newline='') as f:
    wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
assumptions={'as_of':'2026-11-02','seed':SEED,'n_paths':N,'term_months':[120,122],
 'investment_lakh':START,'monthly_sip_first_lakh':.25,'annual_step_up':.1,
 'equity_pe0':PE0,'equity_dividend_yield':DIV,'expense_drag_yearly':COST.tolist(),
 'covariance_source':'stage512_empirical_calibration.json, secondary proxy observations 2007–2024 or 2013–2024',
 'WGC_usd_gold_longterm_2024_estimate':.052,'usd_inr_fx_growth_hypothesis':.02,
 'scenarios':SCENARIOS,'interpretation':'illustrative model frequencies conditional on assumptions, not calibrated probability',
 'critical_limitations':['historical covariance proxy not investment NAVs','CPI drawn with monthly independent innovations, regime persistence not included',
 'Gaussian log shocks, insufficient tail characterization','inflation and returns contemporaneous covariance only',
 'tax rates held constant at 2026 levels','simplified 13-month short-term tax lots and one synthetic fund per asset class','no dynamic tax loss set-off',
 'gilt-fund sleeve not a direct held-to-maturity G-sec','gold/silver expected geometric returns hypotheses, no intrinsic carry',
 'allocation static purchases, no rebalancing','fund costs assumed before investor taxes and not added twice',
 'no interim coupon tax or cash-flow modeling for a direct G-sec','no capital withdrawal','conditional 85% goal not contractual guarantee']}
(OUT/'stage512_forward_calibration_assumptions.json').write_text(json.dumps(assumptions,indent=2))
# Deterministic equity scenario grid based on actual starting valuation anchor.
with (OUT/'stage512_equity_return_grid.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['assumed_eps_growth_pct','terminal_pe','current_pe','dividend_yield_pct','gross_nominal_equity_return_pct'])
    for eps in (.04,.06,.08,.09,.10,.11,.12):
        for pe in (15,16,18,19,21,23,25):w.writerow([eps*100,pe,PE0,DIV*100,round(eq_return(eps,pe)*100,4)])
print('OUTPUT',p)