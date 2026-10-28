"""A shared central landing branches into preserving or exchanging real bridges."""
import copy,math
from pathlib import Path
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.creative_batches.batch30_blockpilot.rules_v1 import block_port
from pcg.map_directed.block_grid.contracts import declare,raster,validate
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent;CELL=HERE.parent/'batch30_cell'
RECIPES=('central-two-wing-bridge-choice',)
RUNNER_SCRIPT=CELL/'runner_v3.gd'
NATIVE_SCENE=HERE/'main_v1.tscn'
SOURCE_DEPENDENCIES=[HERE/'protocol-v2.json',HERE/'protocol-v1.json',HERE/'design-card-v1.json',HERE/'main_v1.gd',HERE/'main_v1.tscn',HERE.parent/'batch30_runtime/block_draw_v1.gd',*[CELL/n for n in ['pair_latch_v1.gd','pair_latch_v2.gd','pair_latch_v3.gd','runtime_v3.gd','runner_v3.gd','main_v3.gd','main_v3.tscn']]]

def rest():return[cmd('axis',value=0),ground(),cmd('wait',8)]
def candidate(target='B',control=0):
 if target not in ['B','C']or control not in [0,1]:raise ValueError('outsideN06v1registeredcontrols')
 side=-1 if target=='B'else 1;c=base('N06');c['family']=RECIPES[0];c['capabilities']=['move','jump','shot_recoil']
 c['platforms']=[[0,736,256,64],[544,608,192,64],[0,96,128,96],[1152,96,128,96],[128,224,128,64],[1024,224,128,64],[96,992,1088,160],[96,864,128,32],[224,736,128,32]]
 c['latches']=[dict(id='wing-pair',bell=[800,672],gate=[192,416,256,24],paired_gate=[832,416,256,24],initial_open='B')]
 docks={'A':[24,718],'B':[24,78],'C':[1256,78]};ports={k:block_port(k,cell,edge,docks[k])for k,cell,edge in [('A',[0,5],'W'),('B',[0,0],'W'),('C',[9,0],'E')]}
 c['ports']=[dict(id=k,position=docks[k],normal=ports[k]['normal'],support_index=j)for k,j in [('A',0),('B',2),('C',3)]]
 c['spawn']=docks['A'][:];c['entry_port']=docks['A'][:];c['exit_port']=docks[target][:];c['goal']=[docks[target][0]-7,74,14,8]
 # Ordinary source mechanism only. Each observed landing uses original ground renewal.
 first_dx=[.7,.75][control];first_dy=math.sqrt(1-first_dx**2)
 p=[cmd('axis',value=1),wait_x(225),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[-first_dx,first_dy]),wait_x(610),*rest()]
 takeoff=570 if side<0 else 710
 p +=[cmd('axis',value=side),wait_x(takeoff,side),cmd('jump'),cmd('jump_release',20)]
 p +=[cmd('shoot',aim_cell=dict(kind='bell',id='wing-pair'))]if side>0 else[cmd('shoot',direction=[.5,math.sqrt(.75)])]
 p +=[wait_x(352 if side<0 else 960,side),*rest()]
 p +=[cmd('axis',value=side),wait_x(320 if side<0 else 960,side),*rest(),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[0,1]),cmd('wait',10),cmd('axis',value=side),wait_x(192 if side<0 else 1088,side),*rest()]
 p +=[cmd('axis',value=side),cmd('jump'),cmd('jump_release',20),settle(docks[target][0],0)]
 c.update(id=f'b30-blockn06-v2-A-{target}-c{control}',control_plan=p,max_frames=2000,trace_all=False,interface=0,production_recipe=RECIPES[0],challenge_route=True,expected_reward=0,required_rewards=[],idea_ids=['B31-N06'],layout_title='中庭双翼换桥',native_scene='res://prototype/creative_batches/batch30_blockn06/main_v1.tscn',native_block_scene=str(NATIVE_SCENE.relative_to(HERE.parents[3])))
 c['route_spec']=dict(id='A-to-'+target,from_port='A',to_port=target,role='main',via_ports=[],required_rewards=[],require_bell=side>0)
 projection=declare(dict(case=c,ports=ports,action_clearance=[[0,0,1280,1152]]),[(x,y)for x in range(10)for y in range(9)])
 assert not validate(projection),validate(projection)
 c['block_grid']=projection['block_grid'];c['block_ports']=ports;c['block_reservations']=[[0,0,1280,1152]]
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','latches','reward_sites','block_grid','block_ports']})
 c['rule_parameters']=dict(control=control,source_idea='B31-N06',entry='A',target=target,first_recoil_dx=first_dx,shared_choice_M=[544,608,192,64],bridge_index=0 if target=='B'else 1)
 c['generation_rule']=dict(id='batch30/blockN06',version=2,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 c['map_specification']=dict(schema='map-notes/challenge-specification/v1',id='batch30/blockN06/fork-interface0',source_type='explicit_model_authored_fork_demand_notactualMap',region='plains',required_family=RECIPES[0],objective=dict(recipe=RECIPES[0],interface=0,physical_layout_sha256=c['layout_uid'],junction_role='fork',core='SharedMstablechoice preserveleftbridge or shoot-exchange to rightbridge, truegroundrenewalbefore highcontinuation',independent_new_family_claim=False),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=3,required_normals=[p['normal']for p in c['ports']]),relations=[dict(from_port='A',to_port=t,role='main',route_id='A-to-'+t)for t in ['B','C']],space=dict(block_size=128,max_width=1280,max_height=1152,max_port_span_x=1280,port_profiles=['ground64/v1']),boundary_policy='open',enclosing_walls=False,rewards=[],difficulty=dict(intent='regular',human_score=None),risk_reward=dict(mandatory_damage=False,reward_sites=[]),resource_state=dict(reset_between_components=False,entry='SupportedAoriginalfullresources andleftclosed/rightopen, sameworldforallchoices',exit='Actualhighdock; arbitraryphase/stateUNKNOWN'),return_conditions='Other4directedpairsUNKNOWN; originalfloorretained butretry/seams/fullMapUNKNOWN',budget=dict(generator_candidates=2,director_revisions=0))
 return c

def over(f,r):return bool(f.get('grounded'))and r[0]-1<=f['x']<=r[0]+r[2]+1 and abs(f['y']+18-r[1])<1
def purpose(c,r):
 fs=r.get('frames',[]);why=[];target=c['route_spec']['to_port'];gate=c['latches'][0]['gate'if target=='B'else'paired_gate']
 if not r.get('ok'):why.append(r.get('reason','not_stable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 if r.get('returns'):why.append('world_reset')
 m=[f for f in fs if over(f,c['platforms'][1])and f.get('shot_charges',0)==1]
 branch_shots=[f for f in fs if m and f['frame']>m[0]['frame']and any(e.get('type')=='shot'for e in f.get('accepted',[]))]
 landed=next((f for f in fs if branch_shots and f['frame']>branch_shots[0]['frame']and f.get('grounded')),None)
 switches=[e for p in r.get('workshop',{}).get('paired_gates',[])for e in p.get('events',[])if e.get('type')=='pair_switch']
 if not m:why.append('shared_actual_M_landing_renewal_missing')
 if not landed or not over(landed,gate):why.append('first_branch_landing_not_corresponding_bridge')
 if landed and landed.get('shot_charges')!=1:why.append('actual_bridge_resource_renewal_missing')
 if target=='C'and not any(e.get('open')=='A'for e in switches):why.append('actual_right_bridge_exchange_missing')
 if landed:
  state=next((p for p in landed.get('workshop',{}).get('paired_gates',[])if p.get('id')=='wing-pair'),{})
  if state.get('open_a')!=(target=='C'):why.append('actual_corresponding_bridge_collision_state_missing')
 owned=set(map(tuple,c['block_grid']['cells']));outside=[f['frame']for f in fs if not raster([f['x']-12,f['y']-18,24,36])<=owned]
 if outside:why.append('actual_body_outside_frozen_ownership')
 return dict(ok=not why,reasons=why,causal=dict(M_ground_frames=[f['frame']for f in m],first_branch_shot=branch_shots[0]['frame']if branch_shots else None,first_branch_landing={k:landed.get(k)for k in ['frame','x','y','support_id','shot_charges']}if landed else None,pair_switches=switches,outside_count=len(outside),outside_frames=outside[:12]),behavior={k:r.get(k)for k in ['shots','jumps','ticks']})
