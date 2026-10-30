"""Native ingress inputs for exact reviewed interfaces; no world/state edits."""
import copy
from .revision063_boundary_v1 import VERSIONS
TOP={'idea-spec02-s04-001','idea-spec02-s06-001'}
def adjust(case):
 s=case.get('approved_implementation',{});p=case.get('migration_probe',{})
 if VERSIONS.get(s.get('reviewId'))!=s.get('designVersion') or p.get('direction')!='ingress':return False
 if s['reviewId']in TOP and p.get('portId')=='T' and p.get('normal')==[0,-1]:
  plan=case['control_plan'];assert [c['op']for c in plan[:3]]==['drop_through','settle','wait']
  plan.insert(3,dict(op='wait',trigger=dict(after=4)))
  p['revision063FixtureRepair']=dict(kind='four_native_frames_after_neighbor_drop_landing',actorOrResourceWrites=False)
  return True
 if s['reviewId']=='idea-spec02-s09-001' and p.get('portId')=='B' and p.get('normal')==[0,1]:
  plan=case['control_plan'];j=next(i for i,c in enumerate(plan)if c['op']=='jump_release');plan[j]['trigger']['after']=8
  plan.insert(j+1,dict(op='shoot',aim_cell=dict(kind='enemy',id='middle-air-enemy'),observed_y=dict(direction='lte',value=588),trigger=dict(after=0,state='observed_height',timeout=120)))
  p['revision063FixtureRepair']=dict(kind='short_native_jump_and_braking_shot_above_owned_deck',actorOrResourceWrites=False)
  return True
 return False
