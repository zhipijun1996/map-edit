"""Native attack resources: living charger position sensor and attack-commit relay."""
from pathlib import Path
import copy,json,hashlib,shutil
from pcg.prototype.creative_batches.enemy_world.probe_v9 import cases as lure_cases
from pcg.prototype.creative_batches.enemy_world.probe_v10 import cases as relay_cases
from pcg.prototype.workshop.rules import cmd,settle,wait_x
from pcg.prototype.workshop.production_loop import run
from pcg.prototype.workshop.engine import ROOT
HERE=Path(__file__).parent
GUARD_SHA='b8a44cd25ee62c409aea335dfcdd0667de32b445a4d50cfe213dfd20e2b8a4ee'

def compiler(request):
 recipe=request.get('recipe')
 if recipe not in ['lure-sensor','attack-relay']:return dict(status='needs_design',gaps=['unsupported native relationship'],cases=[])
 cs=lure_cases()if recipe=='lure-sensor'else relay_cases()
 if recipe=='lure-sensor' and hashlib.sha256((HERE/'guard_charger_v1.tres').read_bytes()).hexdigest()!=GUARD_SHA:raise RuntimeError('immutable_guard_resource_changed')
 s=dict(schema='map-notes/challenge-specification/v1',id='creative/enemy-world/'+recipe+'-v7/0',region='plains',required_family=cs[0]['family'],objective=dict(recipe=recipe,relationship='native enemy movement supplies live sensor occupancy'if recipe=='lure-sensor'else'actual native enemy attack commitment supplies a short gate opening',derived_resource_sha256=GUARD_SHA if recipe=='lure-sensor'else'not_used'),capabilities=dict(version=1,status='defined',allOf=cs[0]['capabilities'],anyOfGroups=[]),ports=dict(count=2,required_normals=[[-1,0],[1,0]]),relations=[dict(from_port='entry',to_port='exit',role='reward')],entry_y=cs[0]['entry_port'][1],rise=cs[0]['entry_port'][1]-420,space=dict(max_width=1500,max_height=1000,max_port_span_x=900),boundary_policy='open',enclosing_walls=False,risk_reward=dict(amount=12,mandatory_damage=False),difficulty=dict(intent='regular',human_score=None),resource_state=dict(reset_between_components=False,entry='original supported resources',exit='observed only'),return_conditions='UNKNOWN',budget=dict(generator_candidates=4,director_revisions=0))
 for c in cs:
  c['id']='ew-'+recipe+'-production-v7-'+c['id'].split('-')[-1];c['map_specification']=copy.deepcopy(s);c['idea_ids']=['enemy-world/'+recipe]
  if recipe=='lure-sensor':c['platforms'][2]=[270,80,500,316]
  c['rule_parameters']=dict(relationship=s['objective']['relationship'],source_type='llm_subagent_implementation',producer_task='/root/enemy_world_creator',no_forced_shooting=True)
  c['generation_rule']=dict(id='creative/enemy-world/'+recipe,version=7,source_path=str(Path(__file__).relative_to(ROOT.parent)),parameters=c['rule_parameters'])
  c['world_cell_sources']=dict(attack_relay='pcg/prototype/creative_batches/enemy_world/attack_relay_v1.gd',occupancy='pcg/prototype/creative_batches/occupancy/occupancy_latch_v1.gd',guard_definition='pcg/prototype/creative_batches/enemy_world/guard_charger_v1.tres',guard_sha256=GUARD_SHA)
 return dict(status='requires_physics',specifications=[s],cases=cs)

def purpose(c,r):
 reasons=[];events=r.get('plains',{}).get('events',[]);fs=r.get('frames',[])
 if not r.get('ok'):reasons.append(r.get('reason','unstable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage') or r.get('returns'):reasons.append('player_harm_or_return')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):reasons.append('forbidden_ability')
 if r.get('workshop',{}).get('coins',0)<12:reasons.append('actual_reward_missing')
 gx,gy,gw,gh=c['latches'][0]['gate'];door_frames=[f for f in fs if f['x']-12<gx+gw and f['x']+12>gx and f['y']+18>gy and f['y']-18<gy+gh]
 clear=next((f['frame']for f in fs if f['x']-12>=gx+gw and f['y']>390),None)
 if not door_frames or clear is None:reasons.append('actual_full_body_gate_crossing_missing')
 if c['production_recipe']=='lure-sensor':
  occupied=[e for e in events if e['type']=='occupancy_changed'and e.get('occupied')]
  # A genuine projectile push, patrol arrival or later kill is not forbidden if
  # the same actual occupancy/crossing relation has already been obtained.
  relation=bool(occupied and clear is not None and occupied[0]['frame']<=clear)
  causal=dict(live_occupancy_events=occupied,body_clear_frame=clear,shooting_not_required=True,reasonable_alternate_body_delivery_allowed=True)
 else:
  attack=[e for e in events if e['type']=='enemy_attack_relay_open'];seeds=[e for e in r.get('enemy_world',{}).get('events',[])if e['type']=='native_seed_spawn']
  relation=bool(attack and seeds and clear is not None and attack[0]['frame']<=clear and any(abs(e['frame']-attack[0]['frame'])<=1 for e in seeds))
  causal=dict(native_attack_relay_events=attack,native_projectile_events=seeds,body_clear_frame=clear,ground_wait_and_pretrigger_allowed=True)
 if not relation:reasons.append('native_enemy_world_relation_missing')
 return dict(ok=not reasons,reasons=reasons,causal=causal)

def alternatives(c):
 out=[]
 def add(label,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan']=plan;out.append(v)
 for delay in [0,20,45,75,120]:add('direct-wait-'+str(delay),[cmd('wait',delay),settle(420)])
 for x in [80,140,180,230]:
  for hold in [0,12,28]:add('ordinary-jump-'+str(x)+'-'+str(hold),[cmd('axis',value=1),wait_x(x),cmd('jump'),cmd('jump_release',hold),settle(420,8)])
 for dx,dy in [(-.15,.988686),(-.5,.866025),(0,1)]:
  add('up-recoil-bypass-'+str(dx),[cmd('axis',value=1),cmd('jump'),cmd('jump_release',12),cmd('shoot',6,direction=[dx,dy]),settle(420,8)])
 id=c['enemies'][0]['id']
 add('kill-first',[cmd('axis',value=0)]+[cmd('shoot',24 if i else 0,aim_cell=dict(kind='enemy',id=id))for i in range(3)]+[settle(420,20)])
 add('single-hit',[cmd('shoot',aim_cell=dict(kind='enemy',id=id)),settle(420,20)])
 add('motion-sensor-self-weight',[cmd('axis',value=-1),wait_x(130,-1),settle(420)])
 add('far-roof-return',[cmd('axis',value=1),cmd('jump'),cmd('jump_release',28),cmd('shoot',6,direction=[-.15,.988686]),wait_x(790),settle(420,8)])
 return out

def sources():
 names=['production_v7.py','probe_v6.py','probe_v7.py','probe_v8.py','probe_v9.py','probe_v10.py','runner_v1.gd','attack_relay_v1.gd','attack_runner_v1.gd','occupancy_runner_v2.gd','export_v1.mjs']
 return [HERE/n for n in names]+list((HERE.parent/'occupancy').glob('*v1.gd'))+[HERE.parent/'occupancy/main_v1.tscn']
if __name__=='__main__':
 import sys
 recipe=sys.argv[1];name='workshop-creative-enemy-world-'+recipe+'-production-v7'
 out=run(name,requests=[dict(recipe=recipe,interfaces=[0])],cycles=1,library_root=ROOT/'results/workshop-creative-enemy-world-library-v1',compiler=compiler,checker=purpose,counter_builder=alternatives,source_file=Path(__file__),extra_sources=sources(),runner_script=HERE/('occupancy_runner_v2.gd'if recipe=='lure-sensor'else'attack_runner_v1.gd'),export_script=HERE/'export_v1.mjs')
 if recipe=='lure-sensor':
  dest=out/'derived-assets';dest.mkdir();shutil.copy2(HERE/'guard_charger_v1.tres',dest/'guard_charger_v1.tres')
  (dest/'manifest.json').write_text(json.dumps(dict(source=str((HERE/'guard_charger_v1.tres').relative_to(ROOT.parent)),sha256=GUARD_SHA,runtime_checked_every_case=True,engine_extra_source_filter='tres excluded; SHA is in frozen raw case and rule; exact asset retained here'),indent=2))
