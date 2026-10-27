"""Same auto occluder, two actual receiver rays and two exit destinations."""
import math
from pathlib import Path
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.creative_batches.batch30_blockpilot.rules_v1 import block_port
from pcg.map_directed.block_grid.contracts import declare,raster,validate
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=('dual-ray-window-fork',)
RUNNER_SCRIPT=HERE.parents[1]/'workshop/runner.gd'
NATIVE_SCENE=HERE/'main_v1.tscn'
SOURCE_DEPENDENCIES=[HERE/'protocol-v1.json',HERE/'idea-source-v1.json',HERE/'main_v1.gd',NATIVE_SCENE,HERE.parent/'batch30_runtime/block_draw_v1.gd']
def phase(lo):return dict(op='wait',trigger=dict(dynamic=dict(kind='platform_phase',id='ray-shutter',window=[lo,lo+.02]),timeout=360))
def prefix():
 return[cmd('axis',value=1),wait_x(230),cmd('jump'),cmd('jump_release',20),ground(),wait_x(968),cmd('axis',value=-1),cmd('jump'),cmd('jump_release',20),wait_x(800,-1),cmd('axis',value=0),ground(),cmd('axis',value=-1),wait_x(736,-1),cmd('axis',value=0),ground(),cmd('wait',8)]
def tail(target,lo=None):
 if target=='B':return[phase(.82 if lo is None else lo),cmd('jump'),cmd('jump_release',20),cmd('shoot',aim_cell=dict(kind='bell',id='low-B')),cmd('axis',value=1),wait_x(1024),cmd('axis',value=0),ground(),cmd('wait',8),cmd('axis',value=1),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[-.5,math.sqrt(.75)]),settle(1256),ground(),cmd('wait',10)]
 return[cmd('axis',value=1),wait_x(800),cmd('axis',value=0),ground(),phase(.1 if lo is None else lo),cmd('axis',value=1),cmd('jump'),cmd('jump_release',20),cmd('shoot',aim_cell=dict(kind='bell',id='high-C')),settle(1256),ground(),cmd('wait',10)]
def candidate(target='B',local=False,lo=None):
 if target not in ['B','C']:raise ValueError('onlytwoactualrequestedforkdestinations')
 c=base('N18');c['family']=RECIPES[0];c['capabilities']=['move','jump','shot_recoil'];c['interface']=0
 c['platforms']=[[0,736,256,64],[320,736,704,40],[704,608,192,48],[928,384,160,48],[1152,224,128,64],[992,608,288,80],[1088,384,192,64],[128,928,1024,32],[352,800,192,40],[688,0,12,338],[688,372,12,98],[688,504,12,152]]
 c['moving_platforms']=[dict(platform_id='ray-shutter',start=[664,400],finish=[664,640],size=[20,96],travel_duration=1.4,dwell_duration=.15,initial_phase=0)]
 c['latches']=[dict(id='low-B',bell=[624,570],gate=[1136,0,24,384],open_seconds=0),dict(id='high-C',bell=[640,352],gate=[1136,448,24,160],open_seconds=0)]
 docks={'A':[24,718],'B':[1256,206],'C':[1256,590]};cells={'A':([0,5],'W'),'B':([9,1],'E'),'C':([9,4],'E')}
 c['spawn']=[736,590]if local else docks['A'][:];c['entry_port']=docks['A'][:];c['exit_port']=docks[target][:];c['goal']=[1249,docks[target][1]-4,14,8]
 ports={k:block_port(k,*cells[k],docks[k])for k in cells}
 c['ports']=[dict(id=k,position=docks[k][:],normal=ports[k]['normal'],support_index={'A':0,'B':4,'C':5}[k])for k in cells]
 c['control_plan']=([]if local else prefix())+tail(target,lo)
 reservations=[[0,0,1280,1024]];m=declare(dict(case=c,ports=ports,action_clearance=reservations),[(x,y)for x in range(10)for y in range(8)]);assert not validate(m),validate(m)
 c['block_grid']=m['block_grid'];c['block_ports']=ports;c['block_reservations']=reservations
 c.update(id='b30-blockn18-v1-'+target+('-local'if local else'-A'),route_spec=dict(id='A-to-'+target,from_port='A',to_port=target,role='main',via_ports=[],required_rewards=[],require_bell=True),max_frames=2000,trace_all=False,production_recipe=RECIPES[0],challenge_route=True,expected_reward=0,required_rewards=[],idea_ids=['B31-N18'],native_scene='res://prototype/creative_batches/batch30_blockn18/main_v1.tscn',native_block_scene=str(NATIVE_SCENE.relative_to(HERE.parents[3])),layout_title='一块挡板，两扇射窗')
 if local:c['validation_fixture']=dict(kind='actual_supported_M_localcore',no_module_enrollment=True,no_A_ingress_claim=True)
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','moving_platforms','latches','reward_sites','block_grid','block_ports']})
 c['rule_parameters']=dict(target=target,initial_auto_phase=0,phase_wait=(.82 if target=='B'else .1)if lo is None else lo,local_core=local)
 c['generation_rule']=dict(id='batch30/N18',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 c['map_specification']=dict(schema='map-notes/challenge-specification/v1',id='batch30/N18/three-right-fan',source_type='explicit_model_derived_no_reward_threeportfork',region='plains',required_family=RECIPES[0],objective=dict(recipe=RECIPES[0],physical_layout_sha256=c['layout_uid'],core='Oneautooccluder/tworealreceiverwindows/differentoriginalrecoilandgateexit; notnewbasicfamily'),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=3,required_normals=[[-1,0],[1,0],[1,0]]),relations=[dict(from_port='A',to_port=k,role='main',route_id='A-to-'+k)for k in ['B','C']],space=dict(block_size=128,max_width=1280,max_height=1024,max_port_span_x=1280,port_profiles=['ground64/v1']),boundary_policy='open',enclosing_walls=False,rewards=[],difficulty=dict(intent='regular',human_score=None),risk_reward=dict(mandatory_damage=False),resource_state=dict(reset_between_components=False,entry='OriginalAshore; autoPphase0, bothindependentgatesclosed; first8localMfixturedoesnotclaimingress',exit='Onlyactualdestinationstate; noforcedexclusivity'),return_conditions='Other4directedpairs/fourthport/recovery/seam/wholeMapUNKNOWN',budget=dict(generator_candidates=2,director_revisions=0))
 return c
def purpose(c,r):
 why=[];fs=r.get('frames',[]);events=r.get('plains',{}).get('events',[]);target=c['route_spec']['to_port'];bell='low-B'if target=='B'else'high-C'
 if not r.get('ok'):why.append(r.get('reason','unstable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
 if r.get('returns'):why.append('world_reset')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 opened=[e for e in events if e.get('type')=='bell_open'and e.get('id')==bell]
 if not opened:why.append('actual_corresponding_receiver_not_hit')
 support=[f['frame']for f in fs if f.get('support_id')=='ray-shutter']
 if support:why.append('shutter_used_as_carriage')
 relay=[f for f in fs if f.get('grounded')and f.get('support_id')=='Platform3']
 if target=='B'and not relay:why.append('actual_high_relay_landing_missing')
 owned=set(map(tuple,c['block_grid']['cells']));outside=[f['frame']for f in fs if not raster([f['x']-12,f['y']-18,24,36])<=owned]
 if outside:why.append('actual_body_outside_ownership')
 return dict(ok=not why,reasons=why,causal=dict(actual_bell_open=opened,shutter_support=support,relay_first=({k:relay[0].get(k)for k in ['frame','x','y','support_id','shot_charges']}if relay else None),actual_projectile_impacts=[e for e in events if e['type']=='projectile_impact'],shots=[e for e in events if e['type']=='shot_origin'],outside_body_frames=outside[:12]),behavior={k:r.get(k)for k in ['shots','jumps','ticks']})
