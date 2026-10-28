"""Explicit no-reward Map A3 variant, unchanged original timed mechanism."""
import copy,json
from pathlib import Path
from pcg.prototype.workshop import rules as source
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.map_directed.block_grid.contracts import anchor,declare,regions,raster,validate
from pcg.map_directed.content_domains.reservation import connect
from pcg.prototype.factory.core.quality import digest
from .door_metrics_v1 import inspect as door_metrics
HERE=Path(__file__).parent
RECIPES=('block128-human-A3-bidirectional',)
RUNNER_SCRIPT=HERE.parents[1]/'workshop/runner.gd'
NATIVE_SCENE='res://prototype/creative_batches/batch30_blocka3/main_v1.tscn'
SOURCE_DEPENDENCIES=[Path(source.__file__),HERE.parents[1]/'workshop/ideas.json',HERE.parents[1]/'workshop/gate_window.py',HERE.parents[1]/'workshop/transitions.py',HERE/'source-baseline-v1.json',HERE/'map-input-v1.json',HERE/'required-pairs-v1.json',HERE/'protocol-v1.json',HERE/'door_metrics_v1.py',HERE/'main_v1.gd',HERE/'main_v1.tscn',HERE.parent/'batch30_runtime/block_draw_v1.gd',HERE.parents[2]/'map_directed/block_grid/contracts.py',HERE.parents[2]/'map_directed/content_domains/reservation.py']

def candidate(interface=0,control=0,route='outbound'):
 if interface not in [0,1]or route not in ['outbound','return']or control not in range(3)or(route=='outbound'and control>1):raise ValueError('outsideA3registeredcontrols')
 c=copy.deepcopy(source.timed(interface));dx=32 if interface==0 else 0;dy=-86
 def pt(p):return[p[0]+dx,p[1]+dy]
 def rect(p):return[*pt(p),*p[2:]]
 c['platforms']=[rect(p)for p in c['platforms']]
 a=c['platforms'][0];end=a[0]+a[2];a[0]=0;a[2]=end
 b=c['platforms'][1];before=b[:];bottom=b[1]+b[3];b[1]=352;b[3]=bottom-b[1];b[2]=768-b[0]
 assert abs(b[1]-before[1])<=32 and max(0,768-before[0]-before[2])<=32
 oldwall=c['platforms'][3][:];c['platforms'][3]=[738,oldwall[1],30,288-oldwall[1]]
 for l in c['latches']:l['bell']=pt(l['bell']);l['gate']=rect(l['gate']);l['return_access']=pt(l['return_access'])
 c['reward_sites']=[];c['expected_reward']=0;c['required_rewards']=[]
 c['ports']=[dict(id='A',position=[24,334],normal=[-1,0],support_index=0),dict(id='B',position=[744,334],normal=[1,0],support_index=1)]
 if route=='outbound':
  release,after=[(8,8),(10,6)][control]
  plan=[cmd('axis',value=1),wait_x(80+dx),cmd('axis',value=0),ground(),cmd('wait',8),cmd('axis',value=1),wait_x(205+dx),cmd('jump'),cmd('jump_release',release),cmd('shoot',after,aim_cell=dict(kind='bell',id='short-bell')),settle(744,6)]
  start=[24,334];target=[744,334];fromid='A';toid='B'
 else:
  if control in [0,1]:
   takeoff=b[0]+[180,100][control]
   plan=[cmd('axis',value=-1),wait_x(takeoff,-1),cmd('jump'),cmd('jump_release',8),cmd('shoot',8,aim_cell=dict(kind='bell',id='short-bell',receiver='access')),settle(24,6)]
  else:
   gx=c['latches'][0]['gate'][0]
   plan=[cmd('axis',value=-1),wait_x(gx+60,-1),cmd('axis',value=0),ground(),cmd('shoot',aim_cell=dict(kind='bell',id='short-bell',receiver='access')),cmd('wait',6),cmd('axis',value=-1),wait_x(290+dx,-1),cmd('axis',value=0),ground(),cmd('wait',20),cmd('axis',value=0),cmd('jump'),cmd('jump_release',20),cmd('shoot',4,direction=[.5,.8660254037844386]),cmd('axis',value=-1,after=9),settle(24,6)]
  start=[744,334];target=[24,334];fromid='B';toid='A'
 c.update(id=f'b30-blocka3-v1-i{interface}-{route}-c{control}',family=RECIPES[0],capabilities=['move','jump','shot_recoil'],spawn=start,entry_port=start[:],exit_port=target,goal=[target[0]-7,330,14,8],control_plan=plan,max_frames=1700,trace_all=False,interface=interface,production_recipe=RECIPES[0],challenge_route=True,idea_ids=['human-A3-short-gate'],native_scene=NATIVE_SCENE,native_block_scene=str((HERE/'main_v1.tscn').relative_to(HERE.parents[3])))
 c['route_spec']=dict(id=route,from_port=fromid,to_port=toid,role='main'if route=='outbound'else'return',via_ports=[],require_bell=True,required_rewards=[])
 ports={}
 for p,cell,edge in zip(c['ports'],[[0,2],[5,2]],['W','E']):
  point=anchor(cell,edge);ports[p['id']]=dict(position=point,normal=p['normal'],grid=dict(cell=cell,edge=edge,profile='ground64/v1',stagingPosition=p['position']),crossing_offset=[0,14],aperture=[point[0]-32,point[1]-32,64,64])
 reserves=[[12,128,744,526]];m=dict(case=c,ports=ports,action_clearance=reserves)
 cells=set().union(*(raster(v)for v in regions(m)));cells,air=connect(cells,ports);m=declare(m,cells)
 errors=validate(m)
 if errors:raise ValueError('blockA3static/'+','.join(errors))
 c['block_grid']=m['block_grid'];c['block_ports']=ports;c['block_reservations']=reserves
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','latches','reward_sites','block_grid','block_ports']})
 c['layout_title']='A3 短时风铃门 / '+('东岸地面口'if interface==0 else'深顶双向口')
 c['rule_parameters']=dict(interface=interface,control=control,route=route,source='originalhumanA3timed-'+str(interface),translation=[dx,dy],bank_B_top_delta=b[1]-before[1],bank_B_extension=max(0,768-before[0]-before[2]),old_farwall=oldwall,new_farwall=c['platforms'][3],real_farwall_floor_opening=[738,288,30,64],original_recovery_bank_preserved=True,original_anti_pinch_unchanged=True,explicit_Map_no_reward_variant=True,original_currency_removed_explicitly=12)
 c['generation_rule']=dict(id='batch30/blockA3',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 c['map_specification']=specification(c)
 return c

def specification(c):
 cells=c['block_grid']['cells'];xs=[x for x,y in cells];ys=[y for x,y in cells]
 return dict(schema='map-notes/challenge-specification/v1',id=f'block-demand/A3-bidirectional/Map-traversal-{c["interface"]}',source_type='human_A3_and_actual6c_Map_exp0_0',region='plains',required_family=RECIPES[0],objective=dict(recipe=RECIPES[0],interface=c['interface'],physical_layout_sha256=c['layout_uid'],roles=['traversal'],core='Sameairshot opens actualshortgate andrecoilsactor through realbody aperture; independent returnreceiver recovery',human_idea='human-A3-short-gate',explicit_no_reward_variant=True,original_human_text_requires_chest=False,independent_new_family_claim=False),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=2,required_normals=[[-1,0],[1,0]],block_profiles=['ground64/v1']),relations=[dict(from_port=a,to_port=b,role=role,route_id=rid)for a,b,role,rid in [('A','B','main','outbound'),('B','A','return','return')]],space=dict(block_size=128,max_width=(max(xs)-min(xs)+1)*128,max_height=(max(ys)-min(ys)+1)*128,boundary_policy='open',ownership_shape='connected_irregular_cells'),boundary_policy='open',enclosing_walls=False,rewards=[],difficulty=dict(intent='regular',human_score=None),risk_reward=dict(mandatory_damage=False,reward_sites=[],reason='Explicit actualMap no-reward traversal variant; old12currencyversions unchanged'),resource_state=dict(reset_between_components=False,entry='Bothauthoredworlds originalgateclosed, truegroundeddock, originalfreshresources; genericopengatestateUNKNOWN',exit='Observedstableactualdock/resources andactualgatetimer only; no genericstateensures'),return_conditions='B->A mustpass independently; exactsameworlddelayedcloseddoorreturn fixtureseparate. No boundarycrossing/fullMap promise',budget=dict(generator_candidates=3,director_revisions=0))

def purpose(c,r):
 why=[]
 if not r.get('ok'):why.append(r.get('reason','not_stable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 if r.get('returns'):why.append('world_reset')
 m=door_metrics(c,r)
 if not m['actual_bell_open_events']:why.append('actual_gate_open_missing')
 if not m['body_door_frames']or m['full_body_clear_frame']is None:why.append('actual_complete_body_through_gate_missing')
 if m['closed_during_body_overlap']:why.append('actual_closed_gate_body_overlap')
 if c['route_spec']['from_port']=='A'and not m['first_air_shot_open']and r.get('shots',0)<2:why.append('neither_same_airshot_nor_costed_multishot_forward_policy')
 owned=set(map(tuple,c['block_grid']['cells']));outside=[f['frame']for f in r.get('frames',[])if not raster([f['x']-12,f['y']-18,24,36])<=owned]
 if outside:why.append('actual_complete_body_outside_frozen_block_ownership')
 return dict(ok=not why,reasons=why,causal=dict(door=m,outside_body_frames=outside[:12],outside_count=len(outside),paid_multishot_forward_accepted=bool(c['route_spec']['from_port']=='A'and not m['first_air_shot_open']and r.get('shots',0)>=2),return_receiver_recovery_mode=c['route_spec']['from_port']=='B',explicit_Map_no_reward_variant=True),behavior=dict(shots=r.get('shots'),jumps=r.get('jumps'),ticks=r.get('ticks')))
