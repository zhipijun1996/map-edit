"""Two original receivers behind a real body-excluding projectile alcove."""
import copy
from pathlib import Path
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.creative_batches.batch30_blockpilot.rules_v1 import block_port
from pcg.map_directed.block_grid.contracts import declare,raster,validate
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=('occluded-receiver-release-window',)
RUNNER_SCRIPT=HERE/'runner_v1.gd';NATIVE_SCENE=HERE/'main_v1.tscn'
SOURCE_DEPENDENCIES=[HERE/n for n in ['protocol-v1.json','idea-source-v1.json','observe_v1.gd','runner_v1.gd','main_v1.gd','main_v1.tscn']]+[HERE.parent/'batch30_runtime/block_draw_v1.gd']
def rest():return[cmd('axis',value=0),ground(),cmd('wait',8)]
def candidate(control=0):
 if control not in [0,1]:raise ValueError('outsideN10v1controls')
 c=base('N10');c['family']=RECIPES[0];c['capabilities']=['move','jump','shot_recoil']
 c['platforms']=[[0,736,832,64],[976,736,128,64],[1152,736,128,96],[96,928,1088,64],[832,816,64,32],[768,624,16,112],[768,624,112,31],[768,689,112,47]]
 c['latches']=[dict(id='near',bell=[832,672],gate=[944,128,16,800],open_seconds=1.8),dict(id='far',bell=[800,672],gate=[1136,128,16,800],open_seconds=0)]
 a=[24,718];b=[1256,718];ports={'A':block_port('A',[0,5],'W',a),'B':block_port('B',[9,5],'E',b)}
 c['ports']=[dict(id='A',position=a[:],normal=[-1,0],support_index=0),dict(id='B',position=b[:],normal=[1,0],support_index=2)]
 c['spawn']=a[:];c['entry_port']=a[:];c['exit_port']=b[:];c['goal']=[1249,714,14,8]
 aim=dict(kind='bell',id='far')
 c['control_plan']=[cmd('axis',value=1),wait_x(740),cmd('jump'),cmd('jump_release',20),wait_x(820),*rest(),cmd('axis',value=1),wait_x(931),cmd('wait',[4,5][control]),cmd('shoot',aim_cell=aim),cmd('wait',8),cmd('axis',value=1),wait_x(1030),*rest(),cmd('axis',value=-1),wait_x(992,-1),*rest(),cmd('jump'),cmd('shoot',4,aim_cell=aim),cmd('jump_release'),settle(1256,0)]
 c['reward_sites']=[dict(id='far-cache',position=b[:],region=[1238,710,36,16],amount=12)]
 c.update(id=f'b30-blockn10-v1-c{control}',max_frames=1800,trace_all=False,interface=0,production_recipe=RECIPES[0],challenge_route=True,expected_reward=12,required_rewards=['far-cache'],idea_ids=['B31-N10'],layout_title='近铃让出的第二条弹道',native_scene='res://prototype/creative_batches/batch30_blockn10/main_v1.tscn',native_block_scene=str(NATIVE_SCENE.relative_to(HERE.parents[3])))
 c['route_spec']=dict(id='A-to-B',from_port='A',to_port='B',role='main',via_ports=[],required_rewards=['far-cache'],require_bell=True)
 m=declare(dict(case=c,ports=ports,action_clearance=[[0,0,1280,1152]]),[(x,y)for x in range(10)for y in range(9)]);assert not validate(m),validate(m)
 c['block_grid']=m['block_grid'];c['block_ports']=ports;c['block_reservations']=[[0,0,1280,1152]]
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','latches','reward_sites','block_grid','block_ports']})
 c['rule_parameters']=dict(control=control,first_drop_wait=[4,5][control],near_seconds=1.8,near_collision_original_size=[28,34],real_projectile_corridor=[880,655,64,34],body_height=36,receiver_pair_centres=[[832,672],[800,672]],M=[976,736,128,64])
 c['generation_rule']=dict(id='batch30/N10',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 c['map_specification']=dict(schema='map-notes/challenge-specification/v1',id='batch30/N10/explicit-sameheight-receiver-window',source_type='explicit_model_authored_demand_notactualMap',region='plains',required_family=RECIPES[0],objective=dict(recipe=RECIPES[0],interface=0,physical_layout_sha256=c['layout_uid'],core='Realnearreceiverinterceptsfirst, deactivateswhiletimeddooropen, actualMrenewalallowsshottoFarbeforeNearrevives',originalconcept_high_B_modified_to_sameheight=True,independent_new_family_claim=False),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=2,required_normals=[[-1,0],[1,0]]),relations=[dict(from_port='A',to_port='B',role='main',route_id='A-to-B')],space=dict(block_size=128,max_width=1280,max_height=1152,max_port_span_x=1280,port_profiles=['ground64/v1']),boundary_policy='open',enclosing_walls=False,rewards=[dict(kind='currency',amount=12,status='explicitderivedallocation_notactualMapbudget')],difficulty=dict(intent='regular',human_score=None),risk_reward=dict(mandatory_damage=False,reward_sites=c['reward_sites']),resource_state=dict(reset_between_components=False,entry='OriginalclosedNear/Far andsupportedAfreshresources',exit='ObservedFarpermanentlyopen;Nearactualtimedstate only, no arbitraryentry/returnclaims'),return_conditions='B->A/failurefloorretry/seams/fullMapUNKNOWN pendingexactproof',budget=dict(generator_candidates=2,director_revisions=0))
 return c

def over(f,r):return bool(f.get('grounded'))and r[0]-1<=f['x']<=r[0]+r[2]+1 and abs(f['y']+18-r[1])<1
def purpose(c,r):
 fs=r.get('frames',[]);why=[];events=[e for e in r.get('plains',{}).get('events',[])if e.get('type')=='bell_open'];nh=[e for e in events if e['id']=='near'];fh=[e for e in events if e['id']=='far']
 if not r.get('ok'):why.append(r.get('reason','not_stable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 if r.get('returns'):why.append('world_reset')
 if r.get('workshop',{}).get('coins',0)!=12:why.append('actual_far_reward_missing')
 m=[f for f in fs if over(f,c['platforms'][1])and f.get('shot_charges')==1]
 farhit=fh[0]['frame']if fh else None;nearhit=nh[0]['frame']if nh else None
 if nearhit is None or farhit is None or nearhit>=farhit:why.append('actual_near_then_far_receiver_hits_missing')
 staged=[f for f in m if nearhit is not None and farhit is not None and nearhit<f['frame']<farhit]
 if not staged:why.append('actual_M_original_ground_renewal_between_targets_missing')
 nfar=next((v for f in fs if farhit is not None and f['frame']==farhit for v in f.get('n10',[])if v['id']=='near'),None)
 if not nfar or nfar.get('bell_layer')!=0 or not nfar.get('open'):why.append('far_hit_did_not_use_original_near_layer0_window')
 # Full body overlaps both actual gate rectangles only while their real collision is open.
 crossing=[]
 for latch in c['latches']:
  gx,gy,gw,gh=latch['gate'];body=[f for f in fs if f['x']-12<gx+gw and f['x']+12>gx and f['y']-18<gy+gh and f['y']+18>gy]
  bad=[f['frame']for f in body if next((v['gate_layer']for v in f.get('n10',[])if v['id']==latch['id']),1)!=0]
  crossing.append(dict(id=latch['id'],body_frames=[f['frame']for f in body],closed_overlap=bad))
  if not body or bad:why.append('actual_complete_body_open_gate_crossing_missing_'+latch['id'])
 owned=set(map(tuple,c['block_grid']['cells']));outside=[f['frame']for f in fs if not raster([f['x']-12,f['y']-18,24,36])<=owned]
 if outside:why.append('actual_body_outside_frozen_ownership')
 return dict(ok=not why,reasons=why,causal=dict(actual_hits=events,actual_M_renewal_frames=[f['frame']for f in staged],near_state_when_far_hit=nfar,near_hit_to_far_hit=farhit-nearhit if nearhit is not None and farhit is not None else None,configured_near_ticks=108,gate_crossings=crossing,outside_count=len(outside),outside_frames=outside[:12]),behavior={k:r.get(k)for k in ['shots','jumps','ticks']})
