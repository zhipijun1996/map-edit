"""Original persistent sequence progress becomes a real courtyard choice."""
import math
from pathlib import Path
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.creative_batches.batch30_blockpilot.rules_v1 import block_port
from pcg.map_directed.block_grid.contracts import declare,raster,validate
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent;SEQUENCE=HERE.parent/'plains50_new_relations'
RECIPES=('persistent-sequence-courtyard-fork',)
RUNNER_SCRIPT=HERE/'runner_v1.gd';NATIVE_SCENE=HERE/'main_v1.tscn'
SOURCE_DEPENDENCIES=[HERE/n for n in ['protocol-v1.json','idea-source-v1.json','observe_v1.gd','runner_v1.gd','main_v1.gd','main_v1.tscn']]+[SEQUENCE/'sequence_runner_v1.gd',SEQUENCE/'sequence_main_v1.gd',HERE.parent/'batch30_runtime/block_draw_v1.gd']
def prefix():
 return[cmd('axis',value=1),wait_x(200),cmd('axis',value=0),ground(),cmd('shoot',aim_cell=dict(kind='bell',id='courtyard-sequence')),cmd('wait',16),cmd('axis',value=1),wait_x(230),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[-.6,.8]),settle(576),ground(),cmd('wait',8)]
def branch(target,delay=0):
 if target=='B':return[cmd('axis',value=-1),wait_x(500,-1),cmd('jump'),cmd('jump_release',20),cmd('shoot',delay,direction=[.5,math.sqrt(.75)]),settle(384),ground(),cmd('wait',8),cmd('axis',value=-1),wait_x(345,-1),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[.35,math.sqrt(1-.35**2)]),settle(24),ground(),cmd('wait',10)]
 return[cmd('axis',value=1),wait_x(680),cmd('jump'),cmd('jump_release',20),cmd('shoot',delay,aim_cell=dict(kind='bell',id='courtyard-sequence',receiver='second')),settle(896),ground(),cmd('wait',8),cmd('axis',value=1),wait_x(964),cmd('jump'),cmd('jump_release',20),settle(1256),ground(),cmd('wait',10)]
def candidate(target='B',delay=0):
 if target not in ['B','C']or delay not in [0,4]:raise ValueError('outsidefirstN21registeredcontrol')
 c=base('N21');c['family']=RECIPES[0];c['capabilities']=['move','jump','shot_recoil'];c['interface']=0
 c['platforms']=[[0,736,256,64],[0,224,256,416],[448,608,256,48],[320,416,128,48],[800,352,192,64],[1088,352,192,64],[128,928,1024,32],[288,800,192,40]]
 c['latches']=[dict(id='courtyard-sequence',bell=[176,640],sequence_offset=[548,-32],sequence_gate=[352,0,24,736],gate=[1024,0,24,352],open_seconds=0)]
 docks={'A':[24,718],'B':[24,206],'C':[1256,334]};grid={'A':([0,5],'W'),'B':([0,1],'W'),'C':([9,2],'E')};support={'A':0,'B':1,'C':5}
 ports={k:block_port(k,*grid[k],docks[k])for k in grid};c['ports']=[dict(id=k,position=docks[k][:],normal=ports[k]['normal'],support_index=support[k])for k in grid]
 c['spawn']=docks['A'][:];c['entry_port']=docks['A'][:];c['exit_port']=docks[target][:];c['goal']=[docks[target][0]-7,docks[target][1]-4,14,8];c['control_plan']=prefix()+branch(target,delay)
 reservations=[[0,0,1280,1024]];m=declare(dict(case=c,ports=ports,action_clearance=reservations),[(x,y)for x in range(10)for y in range(8)]);assert not validate(m),validate(m)
 c['block_grid']=m['block_grid'];c['block_ports']=ports;c['block_reservations']=reservations
 c.update(id=f'b30-blockn21-v1-A-{target}-d{delay}',route_spec=dict(id='A-to-'+target,from_port='A',to_port=target,role='main',via_ports=[],required_rewards=[],require_bell=True),max_frames=2200,trace_all=False,production_recipe=RECIPES[0],challenge_route=True,expected_reward=0,required_rewards=[],idea_ids=['B31-N21'],native_scene='res://prototype/creative_batches/batch30_blockn21/main_v1.tscn',native_block_scene=str(NATIVE_SCENE.relative_to(HERE.parents[3])),layout_title='离开第一层，还是补完第二铃')
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','latches','reward_sites','block_grid','block_ports']})
 c['rule_parameters']=dict(target=target,branch_shot_delay=delay,sequence_second=[724,608],original_concept_second=[592,656],stage1_persistent=True,final_permanent=True)
 c['generation_rule']=dict(id='batch30/N21',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 c['map_specification']=dict(schema='map-notes/challenge-specification/v1',id='batch30/N21/three-courtyard',source_type='explicit_model_derived_no_reward_threeportfork',region='plains',required_family=RECIPES[0],objective=dict(recipe=RECIPES[0],physical_layout_sha256=c['layout_uid'],core='Originalpermanentsequencefirstcommit admitscourtyard; choosewestclimborcompleteeastreceiver; noindependentnewfamily'),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=3,required_normals=[[-1,0],[-1,0],[1,0]]),relations=[dict(from_port='A',to_port=k,role='main',route_id='A-to-'+k)for k in ['B','C']],space=dict(block_size=128,max_width=1280,max_height=1024,max_port_span_x=1280,port_profiles=['ground64/v1']),boundary_policy='open',enclosing_walls=False,rewards=[],difficulty=dict(intent='regular',human_score=None),risk_reward=dict(mandatory_damage=False),resource_state=dict(reset_between_components=False,entry='OriginalAshore sequence_step0 bothrealgatesclosed',exit='ObservedB atstep1 orCfinalopen only; arbitrarytransferUNKNOWN'),return_conditions='Other4orderedpairs/recovery/fourthport/seam/wholeMapUNKNOWN; originalsecondreceiverlayer0afterfinalopen has no timerrestorepromise',budget=dict(generator_candidates=2,director_revisions=0))
 return c
def purpose(c,r):
 why=[];fs=r.get('frames',[]);target=c['route_spec']['to_port'];states=[(f,s)for f in fs for s in f.get('n21',[])if s['id']=='courtyard-sequence']
 first=next(((f,s)for f,s in states if s['sequence_step']==1 and s['first_gate_layer']==0 and s['first_gate_disabled']),None)
 middle=[f for f,s in states if first and f['frame']>first[0]['frame']and f.get('grounded')and f.get('support_id')=='Platform2']
 if not r.get('ok'):why.append(r.get('reason','unstable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
 if r.get('returns'):why.append('world_reset')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 if not first:why.append('actual_persistent_stage1_gate_withdraw_missing')
 if not middle or max((f.get('shot_charges',0)for f in middle),default=0)<1:why.append('actual_courtyard_M_ground_resource_missing')
 final=states[-1][1]if states else{}
 relay=[f for f in fs if f.get('grounded')and f.get('support_id')==('Platform3'if target=='B'else'Platform4')]
 if not relay:why.append('actual_corresponding_branch_relay_missing')
 if target=='B'and(final.get('open')or final.get('final_gate_layer')!=1):why.append('nominal_west_branch_did_not_leave_stage2_uncommitted')
 if target=='C'and(not final.get('open')or final.get('final_gate_layer')!=0 or not final.get('final_gate_disabled')):why.append('actual_second_receiver_final_gate_open_missing')
 owned=set(map(tuple,c['block_grid']['cells']));outside=[f['frame']for f in fs if not raster([f['x']-12,f['y']-18,24,36])<=owned]
 if outside:why.append('actual_body_outside_ownership')
 return dict(ok=not why,reasons=why,causal=dict(first_stage=first[0]['frame']if first else None,M_first=({k:middle[0].get(k)for k in ['frame','x','y','support_id','shot_charges']}if middle else None),branch_first_landing=({k:relay[0].get(k)for k in ['frame','x','y','support_id','shot_charges']}if relay else None),final_sequence=final,actual_projectile_impacts=[e for e in r.get('plains',{}).get('events',[])if e['type']=='projectile_impact'],outside_body_frames=outside[:12]),behavior={k:r.get(k)for k in ['shots','jumps','ticks']})
