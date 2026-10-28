from pathlib import Path
from . import rules_v1 as prior
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=prior.RECIPES
RUNNER_SCRIPT=prior.RUNNER_SCRIPT
NATIVE_SCENE=prior.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(prior.__file__),*prior.SOURCE_DEPENDENCIES,HERE/'protocol-v2.json']
def candidate(interface=0,control=0):
 c=prior.candidate(interface,control);c['id']=c['id'].replace('-v1-','-v2-')
 c['platforms'][1]=[214,470,130,30];c['latches'][0]['paired_gate']=[190,300,24,170]
 c['control_plan'][9]['trigger']['dynamic']['value']=325
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','latches','reward_sites']})
 c['generation_rule']=dict(id='batch30/C07',version=2,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 return c
def purpose(c,r):
 q=prior.purpose(c,r);fs=r.get('frames',[]);contact=q['causal']['wall_side_contacts'];switches=q['causal']['switches'];gate=c['latches'][0]['paired_gate']
 if contact:
  hit=contact[0]['frame'];before=next((f for f in fs if f['frame']==hit-1),{})
  q['causal']['preimpact_velocity']=[before.get('vx'),before.get('vy')]
  if before.get('vx',0)>-400:q['reasons'].append('first_contact_only_walk_not_recoil')
  if not switches or switches[0]['frame']>=hit:q['reasons'].append('wall_contact_not_after_switch')
 clearances=[]
 for event in switches:
  commit=next((f for f in fs if f['frame']==event['frame']),None)
  if commit:
   # Original pair guard also checks full real CharacterBody collision shape.
   dx=max(gate[0]-(commit['x']+12),(commit['x']-12)-(gate[0]+gate[2]),0)
   dy=max(gate[1]-(commit['y']+18),(commit['y']-18)-(gate[1]+gate[3]),0)
   clearances.append(dict(frame=commit['frame'],body=[commit['x']-12,commit['y']-18,24,36],axis_clearance=max(dx,dy)))
 if not clearances or min(v['axis_clearance']for v in clearances)<6:q['reasons'].append('complete_body_clearance_at_close_not_witnessed')
 if not switches or not switches[0].get('airborne'):q['reasons'].append('same_air_shot_not_witnessed')
 q['causal']['close_clearances']=clearances;q['ok']=not q['reasons'];return q
