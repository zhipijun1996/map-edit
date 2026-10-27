"""Folded XOR airlock: withdraw floor, land, reopen lateral passage."""
import copy,math
from pathlib import Path
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.creative_batches.batch30_blockpilot.rules_v1 import block_port
from pcg.map_directed.block_grid.contracts import declare,raster,validate
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent;CELL=HERE.parent/'batch30_cell'
RECIPES=('folded-floor-side-XOR-airlock',)
RUNNER_SCRIPT=CELL/'runner_v3.gd';NATIVE_SCENE=HERE/'main_v1.tscn'
SOURCE_DEPENDENCIES=[HERE/'protocol-v1.json',HERE/'idea-source-v1.json',HERE/'main_v1.gd',NATIVE_SCENE,*[CELL/n for n in ['pair_latch_v1.gd','pair_latch_v2.gd','pair_latch_v3.gd','runtime_v3.gd','runner_v3.gd','main_v3.gd','main_v3.tscn','protocol-v1.json']],HERE.parent/'batch30_runtime/block_draw_v1.gd']
def candidate(control=0):
 if control not in [0,1]:raise ValueError('outside registered firsttiming controls')
 c=base('N19');c['family']=RECIPES[0];c['capabilities']=['move','jump','shot_recoil'];c['interface']=0
 c['platforms']=[[0,352,320,256],[576,0,128,480],[448,608,256,48],[832,736,192,80],[128,928,768,32],[320,800,192,40]]
 c['latches']=[dict(id='folded-pair',bell=[360,280],gate=[320,352,256,20],paired_gate=[784,0,24,736],return_access=[536,550],initial_open='B')]
 c['spawn']=[24,334];c['entry_port']=[24,334];c['exit_port']=[1000,718];c['goal']=[993,714,14,8]
 c['ports']=[dict(id='A',position=[24,334],normal=[-1,0],support_index=0),dict(id='B',position=[1000,718],normal=[1,0],support_index=3)]
 c['control_plan']=[cmd('axis',value=1),wait_x(448),cmd('axis',value=0),ground(),cmd('wait',8+control*4),cmd('shoot',aim_cell=dict(kind='bell',id='folded-pair')),cmd('wait',24),ground(),cmd('wait',8),cmd('shoot',aim_cell=dict(kind='bell',id='folded-pair',receiver='access')),cmd('wait',20),cmd('axis',value=1),wait_x(680),cmd('jump'),cmd('jump_release',20),settle(1000),ground(),cmd('wait',10)]
 c['reward_sites']=[dict(id='folded-cache',position=[1000,718],region=[982,710,36,16],amount=10)]
 ports={'A':block_port('A',[0,2],'W',[24,334]),'B':block_port('B',[7,5],'E',[1000,718])}
 reservations=[[0,0,1024,1024]]
 m=declare(dict(case=c,ports=ports,action_clearance=reservations),[(x,y)for x in range(8)for y in range(8)]);assert not validate(m),validate(m)
 c['block_grid']=m['block_grid'];c['block_ports']=ports;c['block_reservations']=reservations
 c.update(id=f'b30-blockn19-v1-i0-c{control}',route_spec=dict(id='A-to-B',from_port='A',to_port='B',role='main',via_ports=[],required_rewards=['folded-cache'],require_bell=True),max_frames=1600,trace_all=False,production_recipe=RECIPES[0],challenge_route=True,expected_reward=10,required_rewards=['folded-cache'],idea_ids=['B31-N19'],native_scene='res://prototype/creative_batches/batch30_blockn19/main_v1.tscn',native_block_scene=str(NATIVE_SCENE.relative_to(HERE.parents[3])),layout_title='开脚下，落稳，再开侧面')
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','latches','reward_sites','block_grid','block_ports']})
 c['rule_parameters']=dict(control=control,first_shot_delay=8+4*control,loweraccess=[536,550],original_concept_access_conflict=[672,560],reverse='UNKNOWN')
 c['generation_rule']=dict(id='batch30/N19',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 c['map_specification']=dict(schema='map-notes/challenge-specification/v1',id='batch30/N19/west-high-east-low',source_type='explicit_model_derived10coin_foldedairlock_demand',region='plains',required_family=RECIPES[0],objective=dict(recipe=RECIPES[0],interface=0,physical_layout_sha256=c['layout_uid'],core='Withdraw actual floor gate, land real M, swap to side passage; existing C02 adaptation, no new family claim'),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=2,required_normals=[[-1,0],[1,0]]),relations=[dict(from_port='A',to_port='B',role='main',route_id='A-to-B')],space=dict(block_size=128,max_width=1024,max_height=1024,max_port_span_x=1024,port_profiles=['ground64/v1']),boundary_policy='open',enclosing_walls=False,rewards=[dict(kind='currency',amount=10,status='explicitderivedallocationnotMapbudget')],difficulty=dict(intent='regular',human_score=None),risk_reward=dict(mandatory_damage=False,reward_sites=c['reward_sites']),resource_state=dict(reset_between_components=False,entry='OriginalsupportedA; floorAclosed/sideBopen; nofreeMspawn',exit='ObservedB/10coins only; arbitraryworldstatetransferUNKNOWN'),return_conditions='FreshB-A, continuousreturn, arbitraryphase/recovery/seam/wholeMap UNKNOWN unless separately verified',budget=dict(generator_candidates=2,director_revisions=0))
 return c
def outcome(c,r):
 why=[];fs=r.get('frames',[])
 if not r.get('ok'):why.append(r.get('reason','unstable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
 if r.get('returns'):why.append('world_reset')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 if r.get('workshop',{}).get('coins')!=10:why.append('actual_reward_missing')
 owned=set(map(tuple,c['block_grid']['cells']));outside=[f['frame']for f in fs if not raster([f['x']-12,f['y']-18,24,36])<=owned]
 if outside:why.append('actual_body_outside_ownership')
 return dict(ok=not why,reasons=why,causal=dict(body_outside_frames=outside[:12]),behavior={k:r.get(k)for k in ['shots','jumps','ticks']})
def purpose(c,r):
 q=outcome(c,r);fs=r.get('frames',[]);pairs=r.get('workshop',{}).get('paired_gates',[]);state=pairs[0]if pairs else{}
 switches=[e for e in state.get('events',[])if e['type']=='pair_switch'];down=next((e for e in switches if e['open']=='A'),None);side=next((e for e in switches if down and e['frame']>down['frame']and e['open']=='B'),None)
 underfoot=[f for f in fs if down and down['frame']-12<=f['frame']<=down['frame']and f.get('grounded')and 332<=f['x']<=564 and abs(f['y']+18-352)<.3]
 middle=[f for f in fs if down and side and down['frame']<f['frame']<side['frame']and f.get('grounded')and f.get('support_id')=='Platform2'and abs(f['y']+18-608)<.3]
 clear=[f for f in fs if side and f['frame']==side['frame']and f['y']-18>=378]
 crossed=[f for f in fs if side and f['frame']>side['frame']and f['x']-12>=808 and f['y']+18<=736 and any(p.get('open_b')and p.get('gate_b_layer')==0 and p.get('gate_b_disabled')for p in f.get('workshop',{}).get('paired_gates',[]))]
 if not down or not underfoot:q['reasons'].append('actual_withdraw_underfoot_missing')
 if not middle or max((f.get('shot_charges',0)for f in middle),default=0)<1:q['reasons'].append('actual_M_landing_and_resource_missing')
 if not side or not clear:q['reasons'].append('actual_body_clear_second_swap_missing')
 if not crossed:q['reasons'].append('actual_open_side_fullbody_crossing_missing')
 q['causal'].update(actual_switches=switches,bridge_support_before_withdraw=[f['frame']for f in underfoot],M_landing={k:middle[0].get(k)for k in ['frame','x','y','support_id','shot_charges']}if middle else None,body_clear_second_swap=bool(clear),side_crossing_frames=[f['frame']for f in crossed],pair_final=state)
 q['ok']=not q['reasons'];return q
