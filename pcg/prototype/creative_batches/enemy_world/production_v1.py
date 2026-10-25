"""Enemy-body sightline clearing; version 1, original physics only."""
from pathlib import Path
import copy
from pcg.prototype.workshop.rules import base,cmd,settle,reward,finish,wait_x
from pcg.prototype.workshop.evaluate import purpose as original_purpose
from pcg.prototype.workshop.production_loop import run
from pcg.prototype.workshop.engine import ROOT

RECIPES=['clear-sightline']

def candidates(recipe):
 if recipe not in RECIPES:raise ValueError(recipe)
 out=[]
 for spacing in [24,27,30,33]:
  c=base('ew-clear-sightline-v1-'+str(spacing));c['family']='enemy-clear-sightline';c['production_recipe']=recipe
  c['platforms']=[[-160,438,1000,100],[-160,330,1000,66],[-20,396,30,42]]
  c['spawn']=[30,420];c['entry_port']=[30,420]
  c['enemies']=[dict(id='absorber',definition='plains_sentry',position=[240,422],initial_idle_cooldown=.6)]
  c['latches']=[dict(id='far-bell',bell=[390,416],gate=[490,396,24,42],open_seconds=0)]
  reward(c,650,420,14)
  plan=[cmd('axis',value=0)]+[cmd('shoot',spacing if i else 0,aim_cell=dict(kind='bell',id='far-bell'))for i in range(4)]+[settle(650,40)]
  c['rule_parameters']=dict(relationship='original 3HP enemy absorbs shots and prevents contact-safe passage; actual defeat clears the only bell sightline',ground_clearance=42,spacing=spacing,source_type='llm_subagent_implementation',producer_task='/root/enemy_world_creator')
  finish(c,650,420,plan);c['max_frames']=420;c['trace_all']=False
  c['generation_rule']['source_path']=str(Path(__file__).relative_to(ROOT.parent));out.append(c)
 return out

def specification(recipe):
 c=candidates(recipe)[0]
 return dict(schema='map-notes/challenge-specification/v1',id='creative/enemy-world/'+recipe+'/0',region='plains',required_family=c['family'],objective=dict(recipe=recipe,relationship=c['rule_parameters']['relationship']),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=2,required_normals=[[-1,0],[1,0]]),relations=[dict(from_port='entry',to_port='exit',role='reward')],entry_y=420,rise=0,space=dict(max_width=1500,max_height=1000,max_port_span_x=900),boundary_policy='open',enclosing_walls=False,risk_reward=dict(amount=14,mandatory_damage=False),difficulty=dict(intent='regular',human_score=None),resource_state=dict(reset_between_components=False,entry='original supported resources',exit='observed only'),return_conditions='UNKNOWN',budget=dict(generator_candidates=4,director_revisions=0))

def compiler(request):
 recipe=request.get('recipe')
 if recipe not in RECIPES:return dict(status='needs_design',gaps=['missing implemented relationship '+str(recipe)],cases=[])
 s=specification(recipe);cs=candidates(recipe)
 for c in cs:c['map_specification']=s;c['idea_ids']=['enemy-world/absorber-bell','enemy-world/brace-clearance']
 return dict(status='requires_physics',specifications=[s],cases=cs)

def purpose(c,r):
 p=original_purpose(c,r);events=r.get('plains',{}).get('events',[])
 damage=[e for e in events if e['type']=='damage'and e.get('target')=='absorber']
 defeat=[e for e in events if e['type']=='enemy_defeated'and e['id']=='absorber']
 opened=[e for e in events if e['type']=='bell_open'and e['id']=='far-bell']
 altered=bool(defeat and opened and defeat[0]['frame']<opened[0]['frame'] and sum(e['amount']for e in damage)>=3)
 p['causal']['enemy_death_clears_sightline']=altered
 p['causal']['enemy_damage_target_id']='absorber';p['causal']['damage_events']=damage
 if not altered:p['reasons'].append('original_enemy_not_cleared_before_bell')
 p['ok']=not p['reasons'];return p

def alternatives(c):
 out=[]
 def add(label,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan']=plan;out.append(v)
 for i,s in enumerate(c['control_plan']):
  if s['op']=='shoot':
   p=copy.deepcopy(c['control_plan']);p[i]=dict(op='wait',trigger=s.get('trigger',{}));add('omit-'+str(i),p)
 add('walk',[settle(650)])
 add('wait-walk',[cmd('wait',180),settle(650)])
 for x in [30,100,180,210]:
  for hold in [0,8,24]:
   add(f'jump-bypass-{x}-{hold}',[cmd('axis',value=1),wait_x(x),cmd('jump'),cmd('jump_release',hold),cmd('shoot',6,aim_cell=dict(kind='bell',id='far-bell')),settle(650,25)])
 for delay in [0,40,100]:
  add('one-bell-shot-'+str(delay),[cmd('shoot',delay,aim_cell=dict(kind='bell',id='far-bell')),settle(650,25)])
 return out
if __name__=='__main__':
 import sys
 run(sys.argv[1]if len(sys.argv)>1 else 'workshop-creative-enemy-world-production-v1',requests=[dict(recipe=r,interfaces=[0])for r in RECIPES],cycles=1,library_root=ROOT/'results/workshop-creative-enemy-world-library-v1',compiler=compiler,checker=purpose,counter_builder=alternatives,source_file=Path(__file__))
