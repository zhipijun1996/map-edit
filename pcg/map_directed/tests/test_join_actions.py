"""A return-side unlock must survive joining a seam with the same endpoint."""
import unittest
from pcg.map_directed.r2_full.paths import join_waypoints

class JoinActions(unittest.TestCase):
 def test_same_place_unlock_is_not_lost(self):
  dock={'kind':'walk','target':{'position':[10,20]}}
  shot={'kind':'module','target':{'position':[10,20]},'control_plan':[{'op':'shoot'}]}
  result=join_waypoints([dock],[shot,dock])
  self.assertEqual([v['kind']for v in result],['walk','module'])
  self.assertEqual(result[-1]['control_plan'],[{'op':'shoot'}])
 def test_repeated_walk_endpoint_is_collapsed(self):
  dock={'kind':'walk','target':{'position':[10,20]}}
  self.assertEqual(len(join_waypoints([dock],[dock])),1)
