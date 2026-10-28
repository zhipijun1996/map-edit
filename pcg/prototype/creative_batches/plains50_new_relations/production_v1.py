"""Registered recoil/world compositions; original production and regular policy."""
import argparse,copy,json,math
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT
from pcg.prototype.workshop.production_loop import run
from pcg.prototype.workshop.rules import cmd,wait_x,settle,launch
from pcg.prototype.workshop.counterexamples import alternatives as generic_alternatives
from pcg.prototype.creative_batches.plains50_new_relations.probe_v1 import brake_gate
HERE=Path(__file__).parent

def specification(c,v):
 return dict(schema='map-notes/challenge-specification/v1',id=f'plains50-new/{c["family"]}/{v}',region='plains',required_family=c['family'],objective=c['rule_parameters'],capabilities=dict(version=1,status='defined',allOf=['move','jump','shot_recoil'],anyOfGroups=[]),ports=dict(count=2,required_normals=[[-1,0],[1,0]]),relations=[dict(from_port='entry',to_port='exit',role='reward')],entry_y=c['entry_port'][1],rise=c['entry_port'][1]-c['exit_port'][1],space=dict(max_width=1900,max_height=1400,max_port_span_x=1500),boundary_policy='open',enclosing_walls=False,risk_reward=dict(amount=10,mandatory_damage=False),difficulty=dict(intent='regular',human_score=None),resource_state=dict(reset_between_components=False,entry='actual supported entry state; fresh resources captured before inputs',exit='stable supported reward exit; arbitrary-state transfer UNKNOWN'),return_conditions='UNKNOWN; independent entry-to-exit evidence only',budget=dict(generator_candidates=4,director_revisions=0))

def compiler(request):
 cs=[];specs=[]
 for v in [0,1]:
  c=brake_gate(v);c['latches'][0]['bell']=[470+v*10,339]
  c['rule_parameters'].update(bell=c['latches'][0]['bell'],door=c['latches'][0]['gate'],interface=v,domain='two exact pocket elevations/rock-lip reach demands')
  s=specification(c,v);specs.append(s)
  for hold in [7,9]:
   d=copy.deepcopy(c);d['id']=f'p50-brake-gate-i{v}-h{hold}';d['control_plan'][3]=cmd('axis',value=-1,after=hold)
   d['map_specification']=s;d['production_recipe']='brake-gate-catch';d['idea_ids']=['p50-new/brake-gate-catch'];d['generation_rule']=dict(id='plains50-new/brake-gate-catch',version=1,source_type='current_codex_subagent',parameters=d['rule_parameters']);cs.append(d)
 return dict(status='requires_physics',specifications=specs,cases=cs)

def purpose(c,r):
 fs=r.get('frames',[]);why=[]
 if not r.get('ok'):why.append(r.get('reason','unstable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 if r.get('workshop',{}).get('coins',0)<10:why.append('reward_not_claimed')
 shots=[f for f in fs if any(e['type']=='shot'for e in f.get('accepted',[]))];hits=[e for e in r.get('plains',{}).get('events',[])if e['type']=='bell_open']
 air=[f for f in shots if not f['grounded']and f['y']-18>280]
 door=c['latches'][0]['gate'];cross=[f for f in fs if door[0]-12<f['x']<door[0]+door[2]+12 and f['y']+18>door[1]and f['y']-18<door[1]+door[3]]
 if not air or not hits or not cross:why.append('airborne_gate_brake_relationship_not_demonstrated')
 return dict(ok=not why,reasons=why,causal=dict(airborne_shots_below_rock=len(air),actual_bell_hits=len(hits),door_body_cross_frames=len(cross)))

def alternatives(c):
 out=generic_alternatives(c)
 def add(k,p):
  d=copy.deepcopy(c);d['id']+='-counter-'+k;d['counterexample_kind']=k;d['control_plan']=p;out.append(d)
 for x in [80,180,220]:
  p=[cmd('axis',value=1),wait_x(x),cmd('axis',value=0),cmd('shoot',aim_cell=dict(kind='bell',id='pocket-bell')),cmd('axis',value=1),wait_x(340),cmd('axis',value=-1),settle(c['exit_port'][0],6)];add('ground-preopen-drop-'+str(x),p)
 for x in [-180,260,290,320,360]:
  d=-1 if x<0 else 1;add('turn-no-air-shot-'+str(x),[cmd('axis',value=d),wait_x(x,d),settle(c['exit_port'][0],6)])
 for x in [260,300,340,380]:
  p=[cmd('axis',value=1),wait_x(x),cmd('shoot',aim_cell=dict(kind='bell',id='pocket-bell')),settle(c['exit_port'][0],6)];add('early-or-late-gate-brake-'+str(x),p)
 return out

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',default='workshop-plains50-new-brake-production-v1');a=p.parse_args()
 run(a.name,requests=[dict(recipe='brake-gate-catch')],cycles=1,compiler=compiler,checker=purpose,counter_builder=alternatives,source_file=Path(__file__),extra_sources=[HERE/'probe_v1.py'])
