"""Original independent timed doors and real pass-before-turn recoil fork."""
import copy
from pathlib import Path
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.creative_batches.batch30_blockpilot.rules_v1 import block_port
from pcg.map_directed.block_grid.contracts import declare,validate,raster
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=('pass-receiver-turn-fork',)
RUNNER_SCRIPT=HERE.parents[1]/'workshop/runner.gd';NATIVE_SCENE=HERE/'main_v1.tscn'
SOURCE_DEPENDENCIES=[Path(__file__),HERE/'protocol-v1.json',HERE/'main_v1.gd',HERE/'main_v1.tscn',HERE.parent/'batch30_runtime/block_draw_v1.gd',HERE.parent/'batch30_blockpilot/rules_v1.py',HERE.parents[2]/'map_directed/block_grid/contracts.py',HERE.parents[2]/'creative-production/batch30/block-next-ideas-v3.json',HERE.parents[2]/'creative-production/batch30/map-constraint-source-v3/source-index.json']

def candidate(target='B',control=0):
 if target not in ['B','C']or control not in [0,1]:raise ValueError('outsideN14firstdomain')
 c=base('N14');c['family']=RECIPES[0];c['capabilities']=['move','jump','shot_recoil'];c['platforms']=[[0,736,368,64],[416,608,192,64],[0,352,224,96],[800,352,224,96],[96,928,832,40]]
 docks={'A':[24,718],'B':[24,334],'C':[1000,334]};indices={'A':0,'B':2,'C':3};bports={'A':block_port('A',[0,5],'W',docks['A']),'B':block_port('B',[0,2],'W',docks['B']),'C':block_port('C',[7,2],'E',docks['C'])}
 c['ports']=[dict(id=k,position=docks[k],normal=bports[k]['normal'],support_index=indices[k])for k in ['A','B','C']];c['spawn']=docks['A'][:];c['entry_port']=docks['A'][:];c['exit_port']=docks[target][:];c['goal']=[docks[target][0]-7,330,14,8]
 c['latches']=[dict(id='left-way',bell=[384,640],gate=[224,64,24,576],open_seconds=1.),dict(id='right-way',bell=[640,640],gate=[776,64,24,576],open_seconds=1.)]
 c['reward_sites']=[];c['expected_reward']=0;c['required_rewards']=[]
 side=-1 if target=='B'else 1;takeoff=440 if target=='B'else 584;shot_x=(352 if target=='B'else 672)if control==0 else(368 if target=='B'else 656);hold=20 if control==0 else 12;bell='left-way'if target=='B'else'right-way';end=docks[target][0]
 prefix=[cmd('axis',value=1),wait_x(340),cmd('jump'),cmd('jump_release',24),settle(512),ground(),cmd('wait',20)]
 c['control_plan']=prefix+[settle(end),wait_x(takeoff,side),cmd('jump'),cmd('jump_release',hold),wait_x(shot_x,side),cmd('shoot',aim_cell=dict(kind='bell',id=bell)),ground(),cmd('wait',20)]
 c.update(id=f'b31-blockn14-v1-i0-{target}-c{control}',interface=0,max_frames=1400,trace_all=False,production_recipe=RECIPES[0],challenge_route=True,idea_ids=['B31-N14'],layout_title='越过铃，再回身选路',native_scene='res://prototype/creative_batches/batch30_blockn14/main_v1.tscn',native_block_scene=str(NATIVE_SCENE.relative_to(HERE.parents[3])))
 c['route_spec']=dict(id='A-to-'+target,from_port='A',to_port=target,role='main',via_ports=[],require_bell=True,required_rewards=[])
 c['rule_parameters']=dict(target=target,control=control,takeoff=takeoff,shot_x=shot_x,hold=hold,bell=bell,side=side)
 proj=declare(dict(case=c,ports=bports,action_clearance=[]),[(x,y)for x in range(8)for y in range(8)]);assert not validate(proj),validate(proj);c['block_grid']=proj['block_grid'];c['block_ports']=bports;c['block_reservations']=[]
 c['layout_uid']=digest({k:c.get(k)for k in ['platforms','ports','latches','reward_sites','block_grid','block_ports']});c['generation_rule']=dict(id='B31-N14/static-vantage-fork',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),source_map_contract='862b736c491502ae9934265bc7415805b4c122b9',parameters=c['rule_parameters'])
 c['map_specification']=dict(schema='map-notes/challenge-specification/v1',id='B31-N14/static-three-sideports',source_type='explicit_model_authored_interface_demand',region='plains',required_family=c['family'],objective=dict(recipe=RECIPES[0],physical_layout_sha256=c['layout_uid'],junction_role='fork',core='Passselectedbellthenoriginalairshotturnsbackopeningdoorandpropelsforward'),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=3,required_normals=[p['normal']for p in c['ports']]),relations=[dict(from_port='A',to_port=t,role='main')for t in ['B','C']],space=dict(block_size=128,max_width=1024,max_height=1024,max_port_span_x=1024,port_profiles=['ground64/v1']),boundary_policy='open',enclosing_walls=False,difficulty=dict(intent='regular',human_score=None),risk_reward=dict(mandatory_damage=False,reward_sites=[]),resource_state=dict(reset_between_components=False,entry='Aoriginalfullresources/closedindependentdoors',exit='ActualstablehighB/C;genericstateUNKNOWN'),return_conditions='Other4pairs/secondinput/failure/MapUNKNOWN',budget=dict(generator_candidates=4,director_revisions=0))
 return c

def purpose(c,r):
 fs=r.get('frames',[]);why=[];shots=[f for f in fs if any(e.get('type')=='shot'for e in f.get('accepted',[]))];p=c['rule_parameters'];side=p['side'];bell=next(l for l in c['latches']if l['id']==p['bell']);shot=shots[-1]if shots else None
 hits=[e for e in r.get('plains',{}).get('events',[])if e.get('type')=='bell_open'and e.get('id')==p['bell']]
 m=[f for f in fs if f.get('grounded')and f.get('support_id')=='Platform1'];favourable=bool(shot and side*(shot['x']-bell['bell'][0])>0 and not shot.get('grounded'))
 if not r.get('ok'):why.append(r.get('reason','notstable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
 if r.get('returns'):why.append('world_reset')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 if not m:why.append('real_common_M_landing_missing')
 if not hits:why.append('selected_actual_door_not_opened')
 if not favourable:why.append('nominal_pass_receiver_then_turn_shot_missing')
 owned=set(map(tuple,c['block_grid']['cells']));outside=[b['frame']for a,b in zip(fs,fs[1:])if not raster([min(a['x'],b['x'])-12,min(a['y'],b['y'])-18,abs(a['x']-b['x'])+24,abs(a['y']-b['y'])+36])<=owned]
 if outside:why.append('actual_body_left_frozen_Block_ownership')
 return dict(ok=not why,reasons=why,causal=dict(actual_M_frames=len(m),last_actual_shot={k:shot.get(k)for k in ['frame','x','y','grounded','vx','vy']}if shot else None,pass_receiver=favourable,selected_hits=hits,outside_frames=outside[:20]),behavior={k:r.get(k)for k in ['shots','jumps','ticks']})
