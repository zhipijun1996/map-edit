"""Structural regressions only; actual physics evidence lives in run archives."""
import json,tempfile,unittest
from pathlib import Path
from pcg.map_directed.direct_join.director import requests
from pcg.map_directed.region_scale.evaluate import acceptance

class RegionalClearanceTests(unittest.TestCase):
 def layout(self,enabled):
  return dict(units=[448,192],physical_port_clearance=enabled,
   rooms={key:dict(x=0,y=3*i,w=2,h=3)for i,key in enumerate(['upper','middle','lower'])},
   source_graph=dict(entry='lower',goal='upper',nodes=[dict(id=k,role='hub',grants=[],opens=[],reward=0)for k in ['upper','middle','lower']],
    edges=[dict(id='e0',**{'from':'upper','to':'middle'},bidirectional=True,requires=[],switch=None,cost=1),dict(id='e1',**{'from':'middle','to':'lower'},bidirectional=True,requires=[],switch=None,cost=1)]))
 def test_bottom_export_is_not_under_parked_lift(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/'layout.json';p.write_text(json.dumps(self.layout(False)));_,_,old=requests(p)
   self.assertEqual(old[0]['column_x'],old[1]['column_x'])
   p.write_text(json.dumps(self.layout(True)));_,specs,seams=requests(p)
   self.assertGreaterEqual(abs(seams[0]['column_x']-seams[1]['column_x']),192)
   for seam in seams:
    endpoints=[]
    for spec in specs:
     port=next((v for v in spec['ports']if v['id']==seam['id']),None)
     if port:endpoints.append([a+b for a,b in zip(port['position'],spec['placement'])])
    self.assertEqual(endpoints,[seam['position'],seam['position']])
 def test_complete_graph_coverage_cannot_admit_missing_content(self):
  c=dict(exploration_graph=self.layout(True)['source_graph'],case=dict(reward_sites=[],enemies=[]),unresolved_rewards=['missing-cache'])
  rows=[dict(observed_directed_arcs=[['e0','upper','middle'],['e0','middle','upper'],['e1','middle','lower'],['e1','lower','middle']])]
  result=acceptance(c,rows)
  self.assertEqual(result['missing_directed_arcs'],[])
  self.assertFalse(result['target_met']);self.assertFalse(result['production_admitted'])
  self.assertIn('reward_demands_not_materialized',result['blockers'])
  self.assertIn('no_actual_challenge_chests',result['blockers'])

if __name__=='__main__':unittest.main()
