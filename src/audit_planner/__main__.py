import argparse
import hashlib
import json
from dataclasses import asdict
from pathlib import Path
import pandas as pd
from .core import Config, VERSION, build_features, historical_model, rank_processes, allocate_capacity
from .demo import generate

def main():
    p=argparse.ArgumentParser(description='Explainable audit planning with synthetic demo')
    p.add_argument('--demo',action='store_true')
    p.add_argument('--data-dir',type=Path,default=Path('data/synthetic'))
    p.add_argument('--output',type=Path,default=Path('outputs'))
    p.add_argument('--plan-year',type=int,default=2027)
    p.add_argument('--reserve',type=float,default=.15)
    p.add_argument('--top-n',type=int,default=12)
    p.add_argument('--with-model',action='store_true')
    a=p.parse_args(); cfg=Config(a.plan_year,a.reserve,a.top_n)
    if a.demo and a.plan_year!=2027: p.error('Built-in demo supports plan year 2027')
    if a.demo: generate(a.data_dir)
    tables={name:pd.read_csv(a.data_dir/f'{name}.csv') if (a.data_dir/f'{name}.csv').exists() else None for name in ['universe','findings','incidents','capacity']}
    if tables['universe'] is None: p.error('universe.csv is required')
    features=build_features(tables['universe'],tables['findings'],tables['incidents'])
    meta={'used':False,'reason':'Optional model disabled'}
    if a.with_model:
        prediction,meta=historical_model(features,cfg.plan_year)
        features.loc[prediction.index,'historical_selection_estimate']=prediction
    rank=rank_processes(features,cfg)
    rank,capacity=allocate_capacity(rank,tables['capacity'],cfg)
    a.output.mkdir(parents=True,exist_ok=True)
    rank.to_csv(a.output/f'ranking_{cfg.plan_year}.csv',index=False)
    rank[rank.selected].to_csv(a.output/f'portfolio_{cfg.plan_year}.csv',index=False)
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(a.data_dir.glob('*.csv'))}
    manifest={'version':VERSION,'config':asdict(cfg),'data_origin':'synthetic' if a.demo else 'user-supplied; provenance not verified','input_sha256':hashes,'rows':len(rank),'selected':int(rank.selected.sum()),'model':meta,'capacity':capacity}
    (a.output/'run_manifest.json').write_text(json.dumps(manifest,indent=2,allow_nan=False),encoding='utf-8')
    print(f'Ranked {len(rank)} processes; selected {int(rank.selected.sum())}.')
    if capacity['over_capacity']: print('WARNING: mandatory work exceeds capacity:',capacity['over_capacity'])
if __name__=='__main__': main()
