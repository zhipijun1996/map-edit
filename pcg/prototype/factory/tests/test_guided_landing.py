import copy,unittest
from pathlib import Path
from prototype.factory.guided_landing import crossing_xs,children,body_half_size
from prototype.factory.compare_landing_repairs import assign_groups

class GuidedLanding(unittest.TestCase):
 def test_crossing_interpolates_and_ignores_pre_double_jump(self):
  a=dict(x=100,y=100,actor_epoch=1,jumps_used=1,grounded=False,vy=200,hp=5,returns=0)
  b=dict(a,x=120,y=140)
  self.assertEqual(crossing_xs([a,b],138,18),[])
  b['jumps_used']=2;self.assertEqual(crossing_xs([a,b],138,18),[110])
 def test_damage_or_return_cannot_be_used_to_infer_landing(self):
  a=dict(x=100,y=100,actor_epoch=1,jumps_used=2,grounded=False,vy=200,hp=5,returns=0)
  for key,value in [('hp',4),('returns',1)]:
   b=dict(a,x=120,y=140);b[key]=value;self.assertEqual(crossing_xs([a,b],138,18),[])
 def test_shared_candidate_is_counted_in_all_arms(self):
  e=dict(uid='same');owners={'same':{('p1','blind'),('p2','parent'),('p3','guided')}}
  g=assign_groups([e],owners);self.assertEqual(len(g),3);self.assertTrue(all(v==[e]for v in g.values()))
 def test_new_children_keep_physics_and_surface_width(self):
  c=dict(id='p',family='carrier_double',platforms=[[885,390,160,72]],goal=[909,348,112,48],exit_port=[965,372],control_plan=[dict(op='settle',target_x=965)],capabilities=['move','jump','double_jump'])
  a=dict(x=860,y=360,actor_epoch=1,jumps_used=2,grounded=False,vy=700,hp=5,returns=0);b=dict(a,x=865,y=380)
  cs,e=children(dict(case=c,uid='parent'),[[a,b]],(12,18));self.assertTrue(cs)
  for child in cs:
   self.assertEqual(child['platforms'][0][2:],c['platforms'][0][2:]);self.assertEqual(child['capabilities'],c['capabilities']);self.assertLessEqual(abs(child['platforms'][0][0]-885),96)
  self.assertEqual(c['platforms'][0][0],885)
 def test_unknown_actual_shape_is_rejected(self):
  import tempfile
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/'player.tscn';p.write_text('[sub_resource type="CapsuleShape2D"]')
   with self.assertRaises(ValueError):body_half_size(p)
