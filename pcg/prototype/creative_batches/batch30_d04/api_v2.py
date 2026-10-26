"""D04 registration over immutable v5 geometry/programs; original Cell pipeline.

Two forward Module routes plus separate validation-only continuous return
fixtures. An A-return fixture never becomes a fake second physical A port.
"""
import copy,math
from pathlib import Path
from . import rules_v7 as rules
from pcg.prototype.workshop.rules import cmd,settle
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=rules.RECIPES
SOURCE_DEPENDENCIES=rules.SOURCE_DEPENDENCIES+[Path(rules.__file__),HERE/'protocol-v1.json',HERE/'protocol-v2.json',HERE.parents[1]/'workshop/transitions.py']
CONTROL={0:0,1:3}
RETURN_CONTROL={0:0,1:1}

def prepare(c):
 c=copy.deepcopy(c);park=c['rule_parameters']['park'];interface=c['interface']
 c['id']=c['id'].replace('b30-d04-v7','b30-d04-api2')
 c['required_carrier_park']=dict(id='return-deck',running=False,x_range=[515,635]if park=='middle'else[785,930])
 c['layout_title']='去程留下的桥 / '+('宽回廊'if interface==0 else'偏东侧洞')
 c['rule_parameters']['core']='outbound air shot freezes the same carrier later used for direct return or reward detour; choice persists'
 c['generation_rule']=dict(id='batch30/D04',version=7,source_path=str(Path(rules.__file__).relative_to(HERE.parents[3])),registration_source=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 # Standard forward routes are allowed to have different future world outcomes.
 # Counterexamples must compare the same one, and continuous fixtures test
 # whether the world-state difference has a real downstream action consequence.
 return c

def layouts(recipe,interface):
 if recipe not in RECIPES or interface not in CONTROL:raise ValueError('outside registered D04 recipe/interface')
 out=[prepare(rules.materialize(interface,'middle','outbound',CONTROL[interface],RETURN_CONTROL[interface])),prepare(rules.materialize(interface,'reward','reward-out',CONTROL[interface],RETURN_CONTROL[interface]))]
 for c,rid in zip(out,['park-middle-and-cross','park-reward-and-descend']):
  c['route_spec']['id']=rid;c['challenge_route']=rid=='park-reward-and-descend';c['expected_reward']=12 if c['challenge_route']else 0
  c['rule_parameters']['external_goal']='destination plus declared persistent carrier park; continuous return is separate fixture'
 spec=specification(interface,out)
 for c in out:c['map_specification']=copy.deepcopy(spec)
 return out

def specification(interface,cs):
 c=cs[0]
 return dict(schema='map-notes/challenge-specification/v1',id=f'batch30/D04/{interface}',source_type='model_authored_challenge_spec',region='plains',required_family=RECIPES[0],objective=dict(recipe=RECIPES[0],interface=interface,physical_layout_sha256=c['layout_uid'],core='same outgoing shot leaves carrier at meaningful future parking state',route_world_outcomes={v['route_spec']['id']:dict(required_carrier_park=v['required_carrier_park'])for v in cs},continuity_fixture_control_domain=rules.RETURN_CONTROLS,continuity_fixture_scope='One selected same-world return control, frozen before held; fixtures are not Module self-loop routes'),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=len(c['ports']),required_normals=[p['normal']for p in c['ports']]),relations=[dict(from_port=v['route_spec']['from_port'],to_port=v['route_spec']['to_port'],role=v['route_spec']['role'],route_id=v['route_spec']['id'])for v in cs],space=dict(max_width=2200,max_height=1800,max_port_span_x=1300),boundary_policy='open',enclosing_walls=False,difficulty=dict(intent='regular',human_score=None),risk_reward=dict(mandatory_damage=False,reward_sites=c['reward_sites']),resource_state=dict(reset_between_components=False,entry='original supported fresh scene at A; every route has identical Cells and parked initial carrier',exit='observed stable exit and route-specific carrier park; arbitrary states UNKNOWN'),return_conditions='Two exact same-world A-return fixtures; generic return transfer remains UNKNOWN',budget=dict(generator_candidates=1,director_revisions=0))

def fixtures(interface,return_control=None):
 if return_control is None:return_control=RETURN_CONTROL[interface]
 out=[prepare(rules.materialize(interface,'middle','return-middle',CONTROL[interface],return_control)),prepare(rules.materialize(interface,'reward','reward-return',CONTROL[interface],return_control))]
 for c in out:
  c['validation_fixture']['definition_marker_reason']='Original Definition rejects identical entry/exit position; marker B is a validation-only field. Actual goal/ending body are original A; no added port/solid/resource reset.'
 return out

def external_outcome(c,r):
 """Compare actual destination/reward/world, not a required button sequence."""
 fs=r.get('frames',[]);meta=c['required_carrier_park'];state=next((p for p in r.get('workshop',{}).get('carriers',[])if p['id']==meta['id']),{});body=next((p for p in (fs[-1].get('moving_platforms',[])if fs else[])if p['id']==meta['id']),{})
 parked=bool(body and state.get('running')is False and meta['x_range'][0]<=body['position'][0]<=meta['x_range'][1]);reward_ok=r.get('workshop',{}).get('coins',0)>=c['expected_reward']
 visits={}
 for pid in c['route_spec'].get('via_ports',[]):
  xy=next(p['position']for p in c['ports']if p['id']==pid);visits[pid]=any(f.get('grounded')and abs(f['x']-xy[0])<=30 and abs(f['y']-xy[1])<=1 for f in fs)
 return dict(ok=bool(r.get('ok'))and parked and reward_ok and all(visits.values()),park_valid=parked,park_x=body.get('position',['UNKNOWN'])[0],actual_running=state.get('running','UNKNOWN'),coins=r.get('workshop',{}).get('coins'),via_visits=visits)

def purpose(c,r):
 fs=r.get('frames',[]);why=[];outcome=external_outcome(c,r);toggles=[e for e in r.get('workshop',{}).get('events',[])if e['type']=='carrier_toggle']
 if not r.get('ok'):why.append(r.get('reason','not_stable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 if r.get('returns'):why.append('unexpected_reset_or_teleport')
 if not outcome['park_valid']:why.append('required_persistent_carrier_state_not_met')
 if not outcome['ok']and r.get('ok'):why.append('external_reward_or_visit_transaction_missing')
 same_shot=bool(len(toggles)>=2 and toggles[0]['running']and not toggles[1]['running']and toggles[1]['airborne'])
 # Three-shot shore-preparking is an allowed planning alternative with extra
 # action cost. The canonical two-shot programme demonstrates coupling; don't
 # forbid all equivalent methods just to force one precise action sequence.
 if not same_shot and r.get('shots',0)<3:why.append('neither_coupled_park_nor_costed_prepark')
 support=[f for f in fs if f.get('support_id')=='return-deck']
 if c['route_spec']['to_port']=='C' or c.get('validation_fixture'):
  if len(support)<6:why.append('actual_later_carrier_use_missing')
 if c.get('validation_fixture'):
  last=fs[-1]if fs else{}
  if not last.get('grounded')or abs(last.get('x',999)-80)>25 or abs(last.get('y',999)-420)>1:why.append('not_back_on_original_A')
 return dict(ok=not why,reasons=why,causal=dict(same_outgoing_air_shot_parks=same_shot,carrier_toggles=toggles,carrier_supported_frames=len(support),world_outcome=outcome,real_landing_refills=[dict(frame=f['frame'],shots=f.get('shot_charges'),energy=f.get('energy'),support=f.get('support_id'))for f in fs if f.get('grounded')and f.get('shot_charges',0)>0][::20]),behavior=dict(shots=r.get('shots'),ticks=r.get('ticks')))

def alternatives(c):
 out=[]
 def add(label,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan']=plan;out.append(v)
 source=copy.deepcopy(c['control_plan'])
 shot_indices=[i for i,q in enumerate(source)if q['op']=='shoot']
 for index in shot_indices:
  p=copy.deepcopy(source);p[index]=dict(op='wait',trigger=p[index]['trigger']);add('omit-shot-'+str(index),p)
 for hold in [6,12,20,28]:
  for dy in [.15,.5,.8660254]:
   p=[cmd('axis',value=1),rules.wait_x(225),cmd('jump'),cmd('jump_release',hold),cmd('shoot',6,direction=[-math.sqrt(1-dy*dy),dy]),settle(c['exit_port'][0],6)];add(f'direct-no-world-control-{hold}-{dy}',p)
 for shift in [-35,-18,18,35]:
  p=copy.deepcopy(source);p[1]['trigger']['after']=max(0,int(p[1]['trigger']['after'])+shift);add('wrong-park-timing-'+str(shift),p)
 # An actual shore-prepark alternative consumes an extra shot before the
 # normal outgoing recoil. Rest of the same world programme remains intact.
 for delay in [25,40,55,80,110,125,140]:
  p=[copy.deepcopy(source[0]),cmd('axis',value=1),rules.old.wait_x(120),cmd('axis',value=0),rules.old.ground(),cmd('wait',delay),cmd('shoot',aim_cell=dict(kind='bell',id='return-control')),cmd('wait',20)]+copy.deepcopy(source[2:])
  # The outgoing shot now uses a fixed recoil ray, not another control toggle.
  for q in p[8:]:
   if q['op']=='shoot':q.pop('aim_cell',None);q['direction']=[-.8839535,.4675748];break
  add('shore-prepark-extra-shot-'+str(delay),p)
 assert len(out)>=18
 return out


def fixture_task_outcome(c,r):
 """Falsifier comparison ignores desired final park, keeps physical trip/reward."""
 fs=r.get('frames',[]);visits={}
 for pid in c['route_spec'].get('via_ports',[]):
  xy=next(p['position']for p in c['ports']if p['id']==pid);visits[pid]=any(f.get('grounded')and abs(f['x']-xy[0])<=30 and abs(f['y']-xy[1])<=1 for f in fs)
 ok=bool(r.get('ok'))and r.get('hp')==5 and not r.get('returns')and not any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples'])and r.get('workshop',{}).get('coins',0)>=c['expected_reward']and all(visits.values())
 return dict(ok=ok,via_visits=visits,coins=r.get('workshop',{}).get('coins'),shots=r.get('shots'),ticks=r.get('ticks'),ignores_required_park_for_necessity_test=True)
