"""Same M and initial XOR state: horizontal hold or upward exchange."""
import math
from pathlib import Path
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.creative_batches.batch30_blockpilot.rules_v1 import block_port
from pcg.map_directed.block_grid.contracts import declare,validate,raster
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent;CELL=HERE.parent/'batch30_cell'
RECIPES=('cross-shaft-direction-fork',);RUNNER_SCRIPT=CELL/'runner_v3.gd';NATIVE_SCENE=HERE/'main_v1.tscn'
SOURCE_DEPENDENCIES=[Path(__file__),HERE/'protocol-v1.json',HERE/'main_v1.gd',HERE/'main_v1.tscn',HERE.parent/'batch30_runtime/block_draw_v1.gd',HERE.parent/'batch30_blockpilot/rules_v1.py',*[CELL/n for n in ['pair_latch_v1.gd','pair_latch_v2.gd','pair_latch_v3.gd','runtime_v3.gd','runner_v3.gd','main_v3.gd','main_v3.tscn']],HERE.parents[2]/'map_directed/block_grid/contracts.py',HERE.parents[2]/'creative-production/batch30/block-next-ideas-v4.json',HERE.parents[2]/'creative-production/batch30/map-constraint-source-v3/source-index.json']

def candidate(target='B',control=0):
 if target not in ['B','C']or control not in [0,1]:raise ValueError('outsideN17registeredfirstdomain')
 c=base('N17');c['family']=RECIPES[0];c['capabilities']=['move','jump','shot_recoil'];c['platforms']=[[0,736,256,64],[320,608,288,48],[832,480,192,96],[576,352,192,24],[352,288,160,48],[0,224,256,64],[128,928,768,32],[288,800,192,40]]
 c['latches']=[dict(id='cross-pair',bell=[560,500],gate=[0,352,768,20],paired_gate=[768,320,24,256],initial_open='B')]
 docks={'A':[24,718],'B':[1000,462],'C':[24,206]};ports={'A':block_port('A',[0,5],'W',docks['A']),'B':block_port('B',[7,3],'E',docks['B']),'C':block_port('C',[0,1],'W',docks['C'])};support={'A':0,'B':2,'C':5}
 c['ports']=[dict(id=k,position=docks[k][:],normal=ports[k]['normal'],support_index=support[k])for k in ['A','B','C']];c['spawn']=docks['A'][:];c['entry_port']=docks['A'][:];c['exit_port']=docks[target][:];c['goal']=[docks[target][0]-7,docks[target][1]-4,14,8]
 c['reward_sites']=[];c['required_rewards']=[];c['expected_reward']=0
 prefix=[cmd('axis',value=1),wait_x(240),cmd('jump'),cmd('jump_release',24),settle(560),wait_x(553),ground(),cmd('wait',20)]
 if target=='B':
  dy=[.15,.25][control];branch=[settle(1000),wait_x(592),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[-math.sqrt(1-dy*dy),dy]),ground(),cmd('wait',20)]
 else:
  dy=1.;branch=[cmd('jump'),cmd('jump_release',[20,24][control]),cmd('shoot',aim_cell=dict(kind='bell',id='cross-pair')),settle(688),ground(),cmd('wait',12),settle(430),wait_x(592,-1),cmd('jump'),cmd('jump_release',20),ground(),wait_x(436,-1),cmd('wait',12),settle(24),wait_x(368,-1),cmd('jump'),cmd('jump_release',20),ground(),cmd('wait',20)]
 c.update(id=f'b31-blockn17-v1-i0-A-{target}-c{control}',interface=0,control_plan=prefix+branch,max_frames=1800,trace_all=False,production_recipe=RECIPES[0],challenge_route=True,idea_ids=['B31-N17'],layout_title='十字井：横渡保侧门，上穿换顶门',native_scene='res://prototype/creative_batches/batch30_blockn17/main_v1.tscn',native_block_scene=str(NATIVE_SCENE.relative_to(HERE.parents[3])))
 c['route_spec']=dict(id='A-to-'+target,from_port='A',to_port=target,role='main',via_ports=[],require_bell=target=='C',required_rewards=[]);c['rule_parameters']=dict(target=target,control=control,horizontal_dy=dy,vertical_hold=[20,24][control],first_upper_index=3,new_family=False)
 proj=declare(dict(case=c,ports=ports,action_clearance=[]),[(x,y)for x in range(8)for y in range(8)]);assert not validate(proj),validate(proj);c['block_grid']=proj['block_grid'];c['block_ports']=ports;c['block_reservations']=[]
 c['layout_uid']=digest({k:c.get(k)for k in ['platforms','ports','latches','reward_sites','block_grid','block_ports']});c['generation_rule']=dict(id='B31-N17/cross-shaft-native',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),source_map_contract='862b736c491502ae9934265bc7415805b4c122b9',parameters=c['rule_parameters'])
 c['map_specification']=dict(schema='map-notes/challenge-specification/v1',id='B31-N17/threeport-cross-shaft',source_type='explicit_model_authored_fork_demand',region='plains',required_family=c['family'],objective=dict(recipe=RECIPES[0],physical_layout_sha256=c['layout_uid'],junction_role='fork',core='SharedMkeepopenhorizontaldoor orshootexchangeceiling/openupwardgateandlandfixedupper',new_family=False),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=3,required_normals=[p['normal']for p in c['ports']]),relations=[dict(from_port='A',to_port=t,role='main')for t in ['B','C']],space=dict(block_size=128,max_width=1024,max_height=1024,max_port_span_x=1024,port_profiles=['ground64/v1']),rewards=[],boundary_policy='open',enclosing_walls=False,difficulty=dict(intent='regular',human_score=None),risk_reward=dict(mandatory_damage=False,reward_sites=[]),resource_state=dict(reset_between_components=False,entry='SupportedAoriginalfullresources, Aclosed/Bopen, sameworldforallroutes',exit='ActualB/Csupportedstage;particularpairstateobservednotgeneric'),return_conditions='Other4pairs/failure/retry/secondinput/seams/fullMapUNKNOWN',budget=dict(generator_candidates=4,director_revisions=0))
 return c

def purpose(c,r):
 fs=r.get('frames',[]);why=[];target=c['route_spec']['to_port'];m=[f for f in fs if f.get('grounded')and f.get('support_id')=='Platform1'and f.get('shot_charges')==1];shots=[f for f in fs if m and f['frame']>m[0]['frame']and any(e.get('type')=='shot'for e in f.get('accepted',[]))];air=[f for f in shots if not f.get('grounded')]
 switches=[e for pair in r.get('workshop',{}).get('paired_gates',[])for e in pair.get('events',[])if e.get('type')=='pair_switch']
 if not r.get('ok'):why.append(r.get('reason','not_stable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
 if r.get('returns'):why.append('world_reset')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 if not m:why.append('actual_common_M_ground_refill_missing')
 if not shots:why.append('no_actual_branch_recoil')
 crossing=[];clear=None;landing=None
 if target=='C':
  for f in fs:
   state=next((p for p in f.get('workshop',{}).get('paired_gates',[])if p.get('id')=='cross-pair'),{})
   if air and f['frame']>=air[-1]['frame']and f['vy']<0 and f['x']-12>=0 and f['x']+12<=768 and f['y']-18<372 and f['y']+18>352 and state.get('open_a'):crossing.append(f['frame'])
   if crossing and f['frame']>=crossing[0]and f['y']+18<=352 and state.get('open_a')and clear is None:clear=f
  landing=next((f for f in fs if air and f['frame']>air[-1]['frame']and f.get('grounded')),None)
  if not any(e.get('open')=='A'for e in switches):why.append('actual_top_open_side_closed_exchange_missing')
  if not crossing or not clear:why.append('complete_body_upward_crossing_actual_open_top_missing')
  if not landing or landing.get('support_id')!='Platform3' or landing.get('shot_charges')!=1:why.append('first_post_airshot_landing_not_real_fixed_upper_refill')
 owned=set(map(tuple,c['block_grid']['cells']));outside=[b['frame']for a,b in zip(fs,fs[1:])if not raster([min(a['x'],b['x'])-12,min(a['y'],b['y'])-18,abs(a['x']-b['x'])+24,abs(a['y']-b['y'])+36])<=owned]
 if outside:why.append('actual_body_left_frozen_Block_ownership')
 return dict(ok=not why,reasons=why,causal=dict(M_full_shot_ground_frames=len(m),actual_branch_shots=[{k:f.get(k)for k in ['frame','x','y','grounded']}for f in shots],actual_pair_switches=switches,actual_upward_gate_body_intersection_frames=crossing,actual_wholebody_top_clear=clear['frame']if clear else None,actual_first_post_airshot_ground={k:landing.get(k)for k in ['frame','x','y','support_id','shot_charges']}if landing else None,outside_sweep_frames=outside[:20]),behavior={k:r.get(k)for k in ['shots','jumps','ticks']})
