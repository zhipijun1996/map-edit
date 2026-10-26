"""J06 asymmetric three-port fork; original static Cells and actor only.

This rule creates supported external corridors, not reward/recovery extra ports.
The authored upper descent is a design asymmetry, never a proven no_path claim.
"""
import copy
from pathlib import Path
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.factory.core.quality import digest

HERE=Path(__file__).parent
RECIPES=('windgap-junction',)
SOURCE_DEPS=[HERE/'protocol-v1.json']
CAPS=['move','jump','shot_recoil']

def port(id,xy,index,normal,role):return dict(id=id,position=xy,support_index=index,normal=normal,map_role=role)

def pause_on_ground():return [cmd('axis',value=0),cmd('wait',60),ground(),cmd('wait',10)]
def hop(takeoff,land):
 return [cmd('axis',value=1),wait_x(takeoff),cmd('jump'),cmd('jump_release',12),wait_x(land),*pause_on_ground()]

def layouts(recipe,interface):
 if recipe not in RECIPES or interface not in [0,1]:raise ValueError('unsupported windgap recipe/interface')
 # Wider horizontal and narrower/taller demand; same fork grammar, not new family.
 step=150 if interface==0 else 125; rise=70 if interface==0 else 85
 start=300 if interface==0 else 275; lower=720 if interface==0 else 760
 upper=180 if interface==0 else 150
 c=base('windgap-junction');c['family']='windgap-junction';c['capabilities']=CAPS[:]
 c['platforms']=[[-160,upper,start+130,90],[-160,lower,start+160,100]]
 # Lower-west reaches into the shared court; ascending terraces open east.
 for i in range(3):c['platforms'].append([start+step*i,lower-rise*(i+1),step+12,100+rise*i])
 east=start+step*3;etop=lower-rise*4
 c['platforms'].append([east,etop,350,100+rise*3])
 c['ports']=[port('A',[40,upper-18],0,[-1,0],'west_upper_external'),port('B',[40,lower-18],1,[-1,0],'west_lower_external'),port('C',[east+240,etop-18],5,[1,0],'east_external')]
 c['world_bounds']=[-800,-700,3000,2300];c['reward_sites']=[]
 # Both A routes share the same real landing state before branching west/east.
 descend=[cmd('axis',value=1),wait_x(start+35),*pause_on_ground()]
 climb=[]
 for i in range(1,4):climb+=hop(start+step*i-40,start+step*i+60)
 to_c=climb+[settle(east+240,6)]
 to_b=[settle(40,6)]
 b_to_c=hop(start-40,start+60)+to_c
 plans=[('a-b','A','B','main',descend+to_b,[]),('a-c','A','C','main',descend+to_c,[]),('b-c','B','C','main',b_to_c,[]),('c-b','C','B','return',to_b,[])]
 # Actual first B visit, no settled-controller before continuation and no reset.
 visit_b=[cmd('axis',value=-1),wait_x(45,-1),*pause_on_ground()]
 plans.append(('a-b-c','A','C','main',descend+visit_b+b_to_c,['B']))
 physical_keys=['capabilities','platforms','ports','reward_sites','world_bounds','one_way_platform_indices','hazards','thorns','saws','moving_platforms','hooks','latches','enemies']
 uid=digest(dict(recipe=recipe,interface=interface,physical={k:c.get(k,[])for k in physical_keys}))
 out=[]
 for rid,a,b,role,plan,via in plans:
  v=copy.deepcopy(c);ps=next(p for p in c['ports']if p['id']==a);pe=next(p for p in c['ports']if p['id']==b)
  v.update(id=f'junction-windgap-{interface}-{rid}',layout_uid=uid,layout_title=f'双岸会合风口 / 3口 / {"横向宽"if interface==0 else"紧凑高差"}',spawn=ps['position'],entry_port=ps['position'],exit_port=pe['position'],goal=[pe['position'][0]-25,pe['position'][1]-4,50,8],control_plan=copy.deepcopy(plan),max_frames=2200,trace_all=False,interface=interface,production_recipe=recipe,challenge_route=False,expected_reward=0)
  v['route_spec']=dict(id=rid,from_port=a,to_port=b,role=role,via_ports=via,require_bell=False)
  v['rule_parameters']=dict(recipe=recipe,interface=interface,step_run=step,step_rise=rise,upper_surface=upper,lower_surface=lower,shared_decision=dict(x=start+35,y=lower-rise-18),purpose='high-west entry drops into common court, then lower-west/east continuations',no_path_claim=False)
  v['generation_rule']=dict(id='junction/'+recipe,version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=v['rule_parameters'],source_type='executable_rule')
  v['idea_ids']=['J06'];out.append(v)
 spec=dict(schema='map-notes/challenge-specification/v1',id=f'junction/J06/{interface}',source_type='model_authored_challenge_spec',region='plains',required_family=c['family'],objective=dict(recipe=recipe,interface=interface,junction_role='fork_with_directional_merge',physical_layout_sha256=uid,branch_ports=c['ports']),capabilities=dict(version=1,status='defined',allOf=CAPS,anyOfGroups=[]),ports=dict(count=3,required_normals=[p['normal']for p in c['ports']]),relations=[dict(from_port=v['route_spec']['from_port'],to_port=v['route_spec']['to_port'],role=v['route_spec']['role'],route_id=v['route_spec']['id'])for v in out],space=dict(max_width=1800,max_height=1400,max_port_span_x=1500),boundary_policy='open',enclosing_walls=False,difficulty=dict(intent='regular',human_score=None),risk_reward=dict(mandatory_damage=False,reward_sites=[]),resource_state=dict(reset_between_components=False,entry='original supported scene capture before input',exit='stable observation only'),return_conditions='C→B and continuous A→B→C explicitly tested; A reverse UNKNOWN',budget=dict(generator_candidates=1,director_revisions=0))
 for v in out:v['map_specification']=spec
 return out

def purpose(c,r):
 fs=r.get('frames',[]);reasons=[]
 if not r.get('ok'):reasons.append(r.get('reason','not_stable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):reasons.append('player_harm')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):reasons.append('forbidden_ability')
 if r.get('returns'):reasons.append('unexpected_teleport_or_reset')
 via={}
 for p in c['route_spec'].get('via_ports',[]):
  xy=next(x['position']for x in c['ports']if x['id']==p)
  via[p]=any(f.get('grounded')and abs(f['x']-xy[0])<35 and abs(f['y']-xy[1])<1 for f in fs)
  if not via[p]:reasons.append('missing_actual_via_port/'+p)
 return dict(ok=not reasons,reasons=reasons,causal=dict(visited=via,shots_optional=True,rewards_required=False),behavior=dict(shots=r.get('shots'),jumps=r.get('jumps')))

def alternatives(c):
 out=[]
 for label,plan in [('direct-walk',[settle(c['exit_port'][0])]),('ordinary-jump',[cmd('axis',value=1),cmd('jump'),cmd('jump_release',12),settle(c['exit_port'][0])]),('reverse-jump',[cmd('axis',value=-1),cmd('jump'),cmd('jump_release',12),settle(c['exit_port'][0])])]:
  v=copy.deepcopy(c);v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan']=plan;out.append(v)
 return out
