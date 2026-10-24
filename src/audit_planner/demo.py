"""Entirely fictional data, unrelated to any employer or real audit plan."""
from pathlib import Path
import numpy as np
import pandas as pd

def generate(folder):
    folder = Path(folder); folder.mkdir(parents=True,exist_ok=True)
    rng = np.random.default_rng(73)
    u=[]; f=[]; e=[]
    for i in range(48):
        pid=f'SYN-{i:03d}'; latent=float(rng.uniform(.15,.85))
        for year in range(2022,2027):
            risk=float(np.clip(latent*100+rng.normal(0,12),0,100))
            months=int(rng.integers(0,65))
            label=int(rng.random() < 1/(1+np.exp(-(-3+0.04*risk+0.025*months)))) if year<2026 else np.nan
            u.append([pid,f'Synthetic process {i:03d}',f'Team {i%3+1}',year,round(risk,2),round(risk*.75,2),50,75 if i%4==0 else 25,months,36,int(i%13==0),int(rng.integers(60,181)),label])
        for j in range(int(rng.integers(0,7))):
            date=pd.Timestamp('2022-01-01')+pd.Timedelta(days=int(rng.integers(0,1825)))
            close=date+pd.Timedelta(days=int(rng.integers(40,600))) if rng.random()<.7 else pd.NaT
            f.append([f'F-{i}-{j}',pid,date.date(),'' if pd.isna(close) else close.date(),rng.choice(['low','medium','high','critical']),int(rng.random()<.25)])
        for j in range(int(rng.integers(0,10))):
            date=pd.Timestamp('2022-01-01')+pd.Timedelta(days=int(rng.integers(0,1825)))
            e.append([f'E-{i}-{j}',pid,date.date(),rng.choice(['low','medium','high','critical'])])
    tables={
      'universe':pd.DataFrame(u,columns=['process_id','process_name','unit','cutoff_year','risk_final','risk_residual','risk_trend','criticality','months_since_audit','audit_interval_months','mandatory','estimated_hours','selected_next_year']),
      'findings':pd.DataFrame(f,columns=['finding_id','process_id','identified_date','closed_date','severity','recurrent']),
      'incidents':pd.DataFrame(e,columns=['incident_id','process_id','event_date','severity']),
      'capacity':pd.DataFrame({'unit':['Team 1','Team 2','Team 3'],'available_hours':[900,1100,1000]})}
    for name,df in tables.items(): df.to_csv(folder/f'{name}.csv',index=False)
    return tables
