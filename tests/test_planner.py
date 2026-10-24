import tempfile
import unittest
import pandas as pd
from audit_planner.demo import generate
from audit_planner.core import build_features,rank_processes,allocate_capacity,historical_model,Config
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.t=generate(self.tmp.name)
 def features(self):return build_features(self.t['universe'],self.t['findings'],self.t['incidents'])
 def test_current_only(self):
  r=rank_processes(self.features(),Config());self.assertEqual(len(r),48);self.assertTrue(r.cutoff_year.eq(2026).all());self.assertTrue(r.process_id.is_unique)
 def test_unknown_sources(self):
  f=build_features(self.t['universe']);self.assertTrue(f.findings_score.isna().all());self.assertTrue(rank_processes(f,Config()).priority_score.notna().all())
 def test_empty_sources_zero(self):
  f=build_features(self.t['universe'],self.t['findings'].iloc[:0],self.t['incidents'].iloc[:0]);self.assertTrue(f.findings_score.eq(0).all());self.assertTrue(f.incident_score.eq(0).all())
 def test_future_and_closure(self):
  u=self.t['universe'].iloc[:1].copy();p=u.iloc[0].process_id
  e=pd.DataFrame([['f1',p,'2022-03-01','2023-02-01','high',0],['f2',p,'2023-01-01',None,'critical',0]],columns=['finding_id','process_id','identified_date','closed_date','severity','recurrent'])
  f=build_features(u,e);self.assertEqual(f.iloc[0].findings_high_open,1);self.assertEqual(f.iloc[0].findings_high,1)
 def test_capacity_shortfall(self):
  r,m=allocate_capacity(rank_processes(self.features(),Config()),self.t['capacity'].assign(available_hours=0),Config())
  self.assertTrue(r.loc[r.mandatory.eq(1),'selected'].all());self.assertFalse(r.loc[r.mandatory.eq(0),'selected'].any());self.assertTrue(m['over_capacity'])
 def test_duplicates(self):
  with self.assertRaises(ValueError):build_features(pd.concat([self.t['universe'],self.t['universe'].iloc[:1]]))
 def test_missing_capacity(self):
  with self.assertRaises(ValueError):allocate_capacity(rank_processes(self.features(),Config()),self.t['capacity'].iloc[:1],Config())
 def test_model_temporal(self):
  f=self.features();p,m=historical_model(f,2027);self.assertTrue(m['used']);self.assertEqual(m['holdout_year'],2025);self.assertEqual(len(p),48)
  f.loc[f.cutoff_year.eq(2026),'selected_next_year']=1;p2,_=historical_model(f,2027);pd.testing.assert_series_equal(p,p2)
 def test_missing_labels(self):
  p,m=historical_model(self.features().drop(columns='selected_next_year'),2027);self.assertFalse(m['used']);self.assertTrue(p.isna().all())
 def test_reproducible(self):pd.testing.assert_frame_equal(rank_processes(self.features(),Config()),rank_processes(self.features(),Config()))
