"""Transparent audit prioritization. All example assumptions are illustrative."""
from dataclasses import dataclass, asdict
import numpy as np
import pandas as pd

VERSION = '3.0.0'

@dataclass(frozen=True)
class Config:
    plan_year: int = 2027
    reserve: float = 0.15
    top_n: int = 12

FEATURES = ['risk_score', 'coverage_score', 'findings_score', 'incident_score']

def validate_universe(df):
    required = {'process_id','process_name','unit','cutoff_year','risk_final','risk_residual',
                'risk_trend','criticality','months_since_audit','audit_interval_months',
                'mandatory','estimated_hours'}
    if not required.issubset(df):
        raise ValueError(f'Missing columns: {sorted(required-set(df))}')
    d = df.copy()
    if d[list(required)].isna().any().any():
        raise ValueError('Required universe values cannot be missing')
    if d.duplicated(['process_id','cutoff_year']).any():
        raise ValueError('Duplicate process-year snapshot')
    for c in ['process_id','process_name','unit']:
        if d[c].astype(str).str.strip().eq('').any():
            raise ValueError(f'Empty {c}')
    for c in required-{'process_id','process_name','unit'}:
        d[c] = pd.to_numeric(d[c], errors='raise')
        if not np.isfinite(d[c]).all(): raise ValueError(f'Non-finite {c}')
    for c in ['risk_final','risk_residual','risk_trend','criticality']:
        if not d[c].between(0,100).all(): raise ValueError(f'{c} outside 0..100')
    if not d.mandatory.isin([0,1]).all(): raise ValueError('mandatory must be 0/1')
    if (d.months_since_audit < 0).any() or (d.audit_interval_months <= 0).any() or (d.estimated_hours <= 0).any():
        raise ValueError('Invalid time interval or effort')
    if not d.cutoff_year.eq(d.cutoff_year.astype(int)).all(): raise ValueError('Year must be integer')
    return d

def build_features(universe, findings=None, incidents=None):
    """Join events at each snapshot date, including historical closure state."""
    d = validate_universe(universe)
    for table, required, idcol in [(findings, {'finding_id','process_id','identified_date','closed_date','severity','recurrent'}, 'finding_id'),
                                    (incidents, {'incident_id','process_id','event_date','severity'}, 'incident_id')]:
        if table is not None:
            if not required.issubset(table): raise ValueError(f'Missing event columns: {required-set(table)}')
            if table[idcol].isna().any() or table[idcol].duplicated().any(): raise ValueError('Event IDs must be unique and present')
            if not table.process_id.isin(d.process_id).all(): raise ValueError('Event refers to unknown process')
            if not table.severity.isin(['low','medium','high','critical']).all(): raise ValueError('Unknown severity')
    f = None if findings is None else findings.copy()
    e = None if incidents is None else incidents.copy()
    if f is not None:
        f['identified_date'] = pd.to_datetime(f.identified_date, errors='raise')
        f['closed_date'] = pd.to_datetime(f.closed_date, errors='raise')
        if f.identified_date.isna().any() or not f.recurrent.isin([0,1]).all(): raise ValueError('Invalid finding')
        if (f.closed_date < f.identified_date).any(): raise ValueError('Closure precedes finding')
    if e is not None:
        e['event_date'] = pd.to_datetime(e.event_date, errors='raise')
        if e.event_date.isna().any(): raise ValueError('Missing incident date')
    records = []
    for _, r in d.iterrows():
        cut = pd.Timestamp(int(r.cutoff_year),12,31)
        row = r.to_dict()
        row.update(findings_high=0, findings_open=0, findings_recurrent=0, findings_high_open=0, incidents_12m=0, incidents_high_12m=0)
        if f is not None:
            sub = f[(f.process_id == r.process_id) & (f.identified_date <= cut)]
            high = sub.severity.isin(['high','critical'])
            opened = sub.closed_date.isna() | (sub.closed_date > cut)
            row.update(findings_high=int(high.sum()), findings_open=int(opened.sum()),
                       findings_recurrent=int(sub.recurrent.sum()), findings_high_open=int((high & opened).sum()))
        if e is not None:
            sub = e[(e.process_id == r.process_id) & (e.event_date <= cut) & (e.event_date > cut-pd.DateOffset(years=1))]
            row.update(incidents_12m=len(sub), incidents_high_12m=int(sub.severity.isin(['high','critical']).sum()))
        row['findings_available'] = f is not None
        row['incidents_available'] = e is not None
        records.append(row)
    if not records: raise ValueError('Empty universe')
    out = pd.DataFrame(records)
    out['risk_score'] = .4*out.risk_final + .25*out.risk_residual + .2*out.risk_trend + .15*out.criticality
    out['coverage_score'] = (100*out.months_since_audit/out.audit_interval_months).clip(0,100)
    out['findings_score'] = (.45*(out.findings_high/5).clip(0,1) + .30*(out.findings_recurrent/3).clip(0,1) + .25*(out.findings_open/8).clip(0,1))*100
    out['incident_score'] = (.6*(out.incidents_high_12m/3).clip(0,1)+.4*(out.incidents_12m/10).clip(0,1))*100
    if f is None: out['findings_score'] = np.nan
    if e is None: out['incident_score'] = np.nan
    return out

def historical_model(features, plan_year):
    """Predict historical selection, never finding severity or calibrated risk."""
    from sklearn.pipeline import make_pipeline
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
    target = 'selected_next_year'
    meta = {'used':False, 'target':target, 'interpretation':'Historical selection, not adverse audit outcomes'}
    current = features.cutoff_year.eq(plan_year-1)
    empty = pd.Series(np.nan, index=features.index[current])
    if target not in features:
        return empty, dict(meta, reason='No historical labels')
    observed = features[target].dropna()
    if not observed.isin([0,1]).all(): raise ValueError('Historical labels must be 0/1 or empty')
    history = features[(features.cutoff_year < plan_year-1) & features[target].notna()]
    if len(history)<80 or history.cutoff_year.nunique()<3 or history[target].nunique()<2:
        return empty, dict(meta, reason='Insufficient labeled history')
    holdout = int(history.cutoff_year.max())
    train = history[history.cutoff_year < holdout]
    test = history[history.cutoff_year == holdout]
    if len(train)<50 or len(test)<10 or train[target].nunique()<2 or test[target].nunique()<2:
        return empty, dict(meta, reason='Insufficient temporal split or classes')
    model = make_pipeline(SimpleImputer(strategy='median', keep_empty_features=True),StandardScaler(),LogisticRegression(max_iter=2000,random_state=42))
    model.fit(train[FEATURES],train[target])
    p = model.predict_proba(test[FEATURES])[:,1]
    meta.update(used=True, holdout_year=holdout, train_rows=len(train), test_rows=len(test),
                roc_auc=float(roc_auc_score(test[target],p)), average_precision=float(average_precision_score(test[target],p)),
                brier_score=float(brier_score_loss(test[target],p)), prevalence=float(test[target].mean()),
                note='Synthetic evaluation is not evidence of real-world performance; output excluded from priority score')
    model.fit(history[FEATURES],history[target])
    return pd.Series(model.predict_proba(features.loc[current,FEATURES])[:,1],index=features.index[current]), meta

def rank_processes(features, cfg):
    d = features[features.cutoff_year.eq(cfg.plan_year-1)].copy()
    if d.empty: raise ValueError('No snapshot for year preceding plan')
    weights = pd.Series([.45,.25,.20,.10],index=FEATURES)
    den = d[FEATURES].notna().mul(weights).sum(axis=1)
    d['priority_score'] = d[FEATURES].fillna(0).mul(weights).sum(axis=1)/den
    d['priority'] = np.select([d.mandatory.eq(1),d.priority_score.ge(70),d.priority_score.ge(50)],['Mandatory','High','Medium'],default='Low')
    d['reason'] = d.apply(lambda r: ('Mandatory; ' if r.mandatory else '') + '; '.join(f'{c}={r[c]:.1f}' if pd.notna(r[c]) else f'{c}=unavailable' for c in FEATURES),axis=1)
    d = d.sort_values(['mandatory','priority_score','process_id'],ascending=[False,False,True]).reset_index(drop=True)
    d.insert(0,'rank',range(1,len(d)+1))
    return d

def allocate_capacity(rank, capacity, cfg):
    if not 0 <= cfg.reserve < 1 or cfg.top_n < 0: raise ValueError('Invalid reserve or top_n')
    d = rank.copy(); d['selected'] = False; d['selection_reason'] = 'Outside capacity'
    remaining = {}
    if capacity is not None:
        if not {'unit','available_hours'}.issubset(capacity): raise ValueError('Invalid capacity schema')
        if capacity.unit.isna().any() or capacity.unit.duplicated().any(): raise ValueError('Invalid capacity units')
        hours = pd.to_numeric(capacity.available_hours,errors='raise')
        if not np.isfinite(hours).all() or (hours<0).any(): raise ValueError('Invalid capacity hours')
        if not d.unit.isin(capacity.unit).all(): raise ValueError('Missing unit capacity')
        remaining = dict(zip(capacity.unit, hours*(1-cfg.reserve)))
    for i,r in d.iterrows():
        eligible = remaining[r.unit]>=r.estimated_hours if capacity is not None else int(d.selected.sum())<cfg.top_n
        if r.mandatory or eligible:
            d.at[i,'selected'] = True
            d.at[i,'selection_reason'] = 'Mandatory' if r.mandatory else ('Within capacity' if capacity is not None else 'Top N')
            if capacity is not None: remaining[r.unit] -= r.estimated_hours
    return d, {'remaining_hours':remaining,'over_capacity':{k:float(-v) for k,v in remaining.items() if v<0},
               'capacity_validated':capacity is not None,'selection_method':'Greedy priority order; not portfolio optimization'}
