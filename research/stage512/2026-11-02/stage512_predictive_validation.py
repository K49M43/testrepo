#!/usr/bin/env python3
"""Stage 5.12 | honest predictive validation of historical proxy assumptions.

Run in an internet-enabled environment:
  python stage512_predictive_validation.py --fetch --out-dir .
Or use local six pinned CSV snapshots as described by stage512_independent_calibration.py:
  python stage512_predictive_validation.py --data-dir data --out-dir .

IMPORTANT: This is not validation of a 2036 probability or investable NAV series.
It reconstructs historical samples with pinned source hashes. Source revision raises.
"""
import argparse,csv,hashlib,json,math, pathlib, urllib.parse,urllib.request
import numpy as np
from stage512_independent_calibration import SOURCES,read_source,monthly_panel

INITIAL=42.0
WEIGHTS=np.array([0.65,0.20,0.10,0.05])
SIP=np.array([0.25*(1.1**(k//12)) for k in range(120)])


def get_monthly_data(fetch, data_dir):
    loaded=[]
    for idx,(name,repo,gitblob,path) in enumerate(SOURCES):
        target=data_dir/name
        if fetch:
            url='https://raw.githubusercontent.com/'+repo+'/main/'+urllib.parse.quote(path,safe='/')
            with urllib.request.urlopen(url,timeout=90) as resp:raw=resp.read()
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(raw)
        else:raw=target.read_bytes()
        actual=hashlib.sha1(b'blob '+str(len(raw)).encode('ascii')+b'\x00'+raw).hexdigest()
        if actual!=gitblob:
            raise ValueError('SOURCE REVISION '+name+': expected '+gitblob+', found '+actual)
        loaded.append(read_source(raw,idx))
    rows=monthly_panel(loaded)
    return [(month,np.asarray(arr,float)) for month,arr in rows if '2006-07'<=month<='2024-09']


def portfolio_log_return(x):
    return math.log1p(float(WEIGHTS@np.expm1(x[:4])))


def quant(values,q):
    return float(np.quantile(np.asarray(values,float),q))


def out_of_sample(rows, series='real_portfolio', horizon=1, lookback=60, begin='2016-01'):
    vals=[]
    for month,x in rows:
        pr=portfolio_log_return(x)
        vals.append({'equity':float(x[0]),'portfolio':pr,'real_portfolio':pr-float(x[4]),'CPI':float(x[4])}[series])
    vals=np.array(vals,dtype=float)
    pred=[]
    for i in range(lookback,len(vals)-horizon+1):
        if rows[i][0]<begin:continue
        past=vals[i-lookback:i]
        mu=float(past.mean())*horizon
        sig=float(past.std(ddof=1))*math.sqrt(horizon)
        realized=float(vals[i:i+horizon].sum())
        if sig==0:raise ValueError('Degenerate historical volatility in '+rows[i][0])
        pred.append((rows[i][0],(realized-mu)/sig,realized,mu,sig))
    z=np.array([v[1] for v in pred]);n=len(z)
    return {'series':series,'horizon_months':horizon,'training_months':lookback,
            'oos_start':pred[0][0],'last_origin':pred[-1][0],'n_forecasts':n,
            'coverage80_pct':round(100*float(np.mean(np.abs(z)<=1.2815515655446004)),2),
            'coverage90_pct':round(100*float(np.mean(np.abs(z)<=1.6448536269514722)),2),
            'coverage95_pct':round(100*float(np.mean(np.abs(z)<=1.959963984540054)),2),
            'downside_below_5pct_pct':round(100*float(np.mean(z< -1.6448536269514722)),2),
            'mean_standardized_error':round(float(z.mean()),3),
            'sd_standardized_error':round(float(z.std(ddof=1)),3),
            'worst_month_or_origin':pred[int(np.argmin(z))][0],
            'worst_standardized_error':round(float(z.min()),2),
            'overlapping_horizon_test':horizon>1}


def ten_year_replay(win):
    assert len(win)==120
    prices=np.ones(4,dtype=float)
    all_units=[[0.0]*120 for _ in range(4)]
    inflation=1.0
    for i,(_,x) in enumerate(win):
        prices*=np.exp(x[:4]);inflation*=math.exp(float(x[4]))
        for j in range(4):all_units[j][i]=SIP[i]*WEIGHTS[j]/prices[j]
    longval=np.zeros(4);shortval=np.zeros(4)
    longbasis=np.zeros(4);shortbasis=np.zeros(4)
    for j in range(4):
        longval[j]=(INITIAL*WEIGHTS[j]+sum(all_units[j][:108]))*prices[j]
        shortval[j]=sum(all_units[j][108:])*prices[j]
        longbasis[j]=(INITIAL+sum(SIP[:108]))*WEIGHTS[j]
        shortbasis[j]=sum(SIP[108:])*WEIGHTS[j]
    long_gain=longval-longbasis;short_gain=shortval-shortbasis
    assetval=longval+shortval; gross=float(assetval.sum())
    # Back-apply today's simplified tax rates to historical returns; not actual historic tax law.
    tax=(.13*max(0,long_gain[0]-1.25)+.208*max(0,short_gain[0])
        +.312*max(0,assetval[1]-(INITIAL+float(SIP.sum()))*WEIGHTS[1])
        +.13*(max(0,long_gain[2])+max(0,long_gain[3]))
        +.312*(max(0,short_gain[2])+max(0,short_gain[3])))
    net=gross-tax-.001*gross-.00001*assetval[0]
    return {'start':win[0][0],'end':win[-1][0],
        'gross_nominal_L':round(gross,3), 'tax_L':round(tax,3),
        'cpi_factor':round(inflation,6),'real_after_tax_L':round(net/inflation,3)}


def run(rows,out):
    assert len(rows)==219 and rows[0][0]=='2006-07' and rows[-1][0]=='2024-09'
    assert abs(INITIAL+float(SIP.sum())-89.812273803)<1e-7
    # Data gets no future-return leakage: train ends strictly before forecast origin.
    backtests=[out_of_sample(rows,s,h) for s in ('equity','portfolio','real_portfolio','CPI') for h in (1,12,36)]
    replay=[ten_year_replay(rows[i:i+120]) for i in range(len(rows)-119)]
    wealth=np.array([x['real_after_tax_L'] for x in replay])
    corr=np.corrcoef(np.array([x[1][4] for x in rows])[1:], np.array([x[1][4] for x in rows])[:-1])[0,1]
    summary={'as_of':'2026-11-02','joint_data_window':['2006-07','2024-09'],'n_months':len(rows),
      'first_oos_origin':'2016-01','rolling_training_months':60,
      'n_overlapping_ten_year_windows':len(replay),
      'max_nonoverlapping_ten_year_windows':len(rows)//120,
      'ten_year_replay_real_quantiles_lakh':{str(k):round(quant(wealth,k),2) for k in (0,.05,.15,.5,.85,.95,1)},
      'overlapping_fraction_above_90_pct':round(100*float(np.mean(wealth>=90)),1),
      'overlapping_fraction_above_100_pct':round(100*float(np.mean(wealth>=100)),1),
      'lag1_monthly_CPI_logchange_correlation':round(float(corr),3),
      'decision':'PARTIAL historical predictive checks; 2036 confidence NOT calibrated; NO-GO',
      'warnings':['Model is a research proxy: bond carry-duration not an investable G-Sec TRI or bond cashflow','Gold/silver in USD times month-end USD/INR, not domestic bullion/ETF NAV','CPI source not reconciled to MoSPI linked 2024 base series','Overlapping annual and decade windows cannot be interpreted as independent statistical evidence','Historical hypothetical taxes use simplified 2026 rules; fund fees omitted in the replay','Predicted intervals use naive normal sqrt(h) variance scaling and a 60-month trailing estimation window','No forward calibration of 2036 goal-achievement probability','March 2020 is a severe downside-tail miss despite acceptable overall nominal 90% interval coverage']}
    with (out/'stage512_predictive_validation_metrics.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(backtests[0]));w.writeheader();w.writerows(backtests)
    with (out/'stage512_historical_replay_windows.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(replay[0]));w.writeheader();w.writerows(replay)
    (out/'stage512_predictive_validation_summary.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps({'summary':summary,'oos_backtests':backtests},indent=2))


def selftest():
    assert abs(INITIAL+float(SIP.sum())-89.812273803)<1e-7
    x=np.array([0.,0.,0.,0.,0.]);assert portfolio_log_return(x)==0.
    base=[(f'{2000+i//12}-{i%12+1:02d}',x) for i in range(120)]
    a=ten_year_replay(base)
    # Zero market returns => zero capital-gains tax; modeled friction only.
    assert abs(a['tax_L'])<1e-8
    assert abs(a['gross_nominal_L']-89.812)<.002
    assert 89.70<a['real_after_tax_L']<89.80
    print('SELFTEST PASS',a)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--fetch',action='store_true');p.add_argument('--data-dir',default='.')
    p.add_argument('--out-dir',default='.');p.add_argument('--self-test',action='store_true')
    a=p.parse_args()
    if a.self_test:selftest()
    else:
        out=pathlib.Path(a.out_dir);out.mkdir(exist_ok=True,parents=True)
        run(get_monthly_data(a.fetch,pathlib.Path(a.data_dir)),out)