"""Displace a live native enemy out of a precise landing; version 3."""
from pathlib import Path
import copy
from pcg.prototype.creative_batches.enemy_world.probe_v4 import cases
from pcg.prototype.workshop.rules import cmd,settle,wait_x
from pcg.prototype.workshop.evaluate import purpose as original_purpose
from pcg.prototype.workshop.production_loop import run
from pcg.prototype.workshop.engine import ROOT
HERE=Path(__file__).parent

def compiler(request):
 if request.get('recipe')!='displace-landing':return dict(status='needs_design',gaps=['unimplemented relationship'],cases=[])
 cs=cases()[:4]
 s=dict(schema='map-notes/challenge-specification/v1',id='creative/enemy-world/displace-landing-v3/0',region='plains',required_family='enemy-displace-landing',objective=dict(recipe='displace-landing',relationship='Actual enemy-body knockback clears the landing footprint; defeat is an allowed substitute if it truly clears that footprint'),capabilities=dict(version=1,status='defined',allOf=cs[0]['capabilities'],anyOfGroups=[]),ports=dict(count=2,required_normals=[[-1,0],[1,0]]),relations=[dict(from_port='entry',to_port='exit',role='reward')],entry_y=220,rise=-200,space=dict(max_width=1500,max_height=1000,max_port_span_x=900),boundary_policy='open',enclosing_walls=False,risk_reward=dict(amount=12,mandatory_damage=False),difficulty=dict(intent='regular',human_score=None),resource_state=dict(reset_between_components=False,entry='original supported resources',exit='observed only'),return_conditions='UNKNOWN',budget=dict(generator_candidates=4,director_revisions=0))
 for c in cs:
  c['id']=c['id'].replace('ew-late-displace','ew-displace-landing-v3');c['map_specification']=s;c['idea_ids']=['enemy-world/live-knockback-aperture']
  c['rule_parameters']=dict(relationship=s['objective']['relationship'],source_type='llm_subagent_implementation',producer_task='/root/enemy_world_creator')
  c['generation_rule']=dict(id='creative/enemy-world/displace-landing',version=3,source_path=str(Path(__file__).relative_to(ROOT.parent)),parameters=c['rule_parameters'])
 return dict(status='requires_physics',specifications=[s],cases=cs)

def purpose(c,r):
 p=original_purpose(c,r);fs=r.get('frames',[]);events=r.get('plains',{}).get('events',[])
 targets=[e for e in events if e['type']=='damage'and e.get('target')=='occupant']
 displaced=any(f.get('plains',{}).get('enemies')and f['plains']['enemies'][0]['x']>=233 for f in fs)
 removed=any(e['type']=='enemy_defeated'and e['id']=='occupant'for e in events)
 landing=any(f['grounded']and f['y']>400 and 202<=f['x']<=214 and f['x']+12<next(iter(f['plains']['enemies']))['x']-14 for f in fs if f.get('plains',{}).get('enemies'))
 relation=bool(targets and (displaced or removed) and (landing or removed))
 p['causal'].update(actual_enemy_body_displaced=displaced,enemy_removed=removed,landing_body_clearance=landing,damage_target_id='occupant')
 if not relation:p['reasons'].append('enemy_body_not_removed_from_landing')
 p['ok']=not p['reasons'];return p

def alternatives(c):
 out=[]
 def add(label,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan']=plan;out.append(v)
 p=copy.deepcopy(c['control_plan']);p[3]=dict(op='wait',trigger=p[3]['trigger']);add('omit-hit',p)
 for x in [150,180,205,220]:
  for hold in [0,8,20,30]:
   add('no-hit-jump-'+str(x)+'-'+str(hold),[cmd('axis',value=1),wait_x(x),cmd('jump'),cmd('jump_release',hold),settle(208,6)])
 for delay in [0,35,70,120]:add('wait-drop-'+str(delay),[cmd('wait',delay),settle(208)])
 for n in [2,3]:
  p=copy.deepcopy(c['control_plan']);p[4:4]=[cmd('shoot',20,aim_cell=dict(kind='enemy',id='occupant'))for _ in range(n-1)];add('extra-hits-'+str(n),p)
 return out
if __name__=='__main__':
 run('workshop-creative-enemy-world-production-v3',requests=[dict(recipe='displace-landing',interfaces=[0])],cycles=1,library_root=ROOT/'results/workshop-creative-enemy-world-library-v1',compiler=compiler,checker=purpose,counter_builder=alternatives,source_file=Path(__file__),extra_sources=[HERE/'probe_v4.py',HERE/'runner_v1.gd'],runner_script=HERE/'runner_v1.gd')
