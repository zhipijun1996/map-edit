"""N12 actual Block-native resource fork, no inherited shifted physics."""
import copy,math
from pathlib import Path
from pcg.prototype.creative_batches.plains50_ports import recipes_v2 as parent
from pcg.prototype.workshop.rules import cmd,wait_x,settle
from pcg.prototype.workshop.evaluate import purpose as original_purpose
from pcg.prototype.creative_batches.batch30_blockpilot.rules_v1 import block_port
from pcg.map_directed.block_grid.contracts import declare,raster,validate
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=('investment-fork',)
RUNNER_SCRIPT=HERE.parents[1]/'workshop/runner.gd'
NATIVE_SCENE=HERE/'main_v1.tscn'
SOURCE_DEPENDENCIES=[Path(parent.__file__),Path(__file__),HERE/'protocol-v1.json',HERE/'main_v1.gd',HERE/'main_v1.tscn',HERE.parent/'batch30_blockpilot/rules_v1.py',HERE.parent/'batch30_runtime/block_draw_v1.gd',HERE.parents[2]/'map_directed/block_grid/contracts.py',HERE.parents[2]/'creative-production/batch30/map-constraint-source-v3/source-index.json',HERE.parents[2]/'creative-production/batch30/block-next-ideas-v3.json']
HIGH=[(16,.94),(20,math.sqrt(.75)),(24,.94)]
LOW=[(8,8,.15),(8,16,.1),(8,24,.1)]

def candidate(target='B',control=0):
 if target not in ['B','C']or control not in range(3):raise ValueError('outsideN12registered3portcontrols')
 c=parent.layouts(RECIPES[0],0)[0];c['platforms']=[[-128,480,368,100],[320,224,192,24],[520,608,504,100],[-200,822,1300,60]]
 a=[-104,462];b=[488,206];low=[1000,590];end=b if target=='B'else low
 c['ports']=[dict(id='A',position=a,normal=[-1,0],support_index=0),dict(id='B',position=b,normal=[1,0],support_index=1),dict(id='C',position=low,normal=[1,0],support_index=2)]
 c['block_ports']={'A':block_port('A',[-1,3],'W',a),'B':block_port('B',[3,1],'E',b),'C':block_port('C',[7,4],'E',low)}
 cells={(x,y)for x in range(-1,9)for y in range(8)}-{(4,1),(8,4)};cells|={(-2,6)}|{(x,-1)for x in range(2,7)}
 c['block_reservations']=[];proj=declare(dict(case=c,ports=c['block_ports'],action_clearance=[]),cells);assert not validate(proj),validate(proj);c['block_grid']=proj['block_grid']
 c['spawn']=a[:];c['entry_port']=a[:];c['exit_port']=end[:];c['goal']=[end[0]-7,end[1]-4,14,8];c['world_bounds']=[-512,-512,2304,1792]
 c['reward_sites']=[dict(id='upper-cache',position=b[:],region=[458,200,60,12],amount=12)];c['expected_reward']=12 if target=='B'else 0;c['required_rewards']=['upper-cache']if target=='B'else[]
 if target=='B':hold,dy=HIGH[control];takeoff=140;after=0
 else:hold,after,dy=LOW[control];takeoff=205
 c['control_plan']=[cmd('axis',value=1),wait_x(takeoff),cmd('jump'),cmd('jump_release',hold),cmd('shoot',after,direction=[-math.sqrt(1-dy*dy),dy]),settle(end[0]),dict(op='wait',trigger=dict(state='grounded',timeout=240)),cmd('wait',20)]
 c['id']=f'b31-blockn12-v1-i0-{target}-c{control}';c.update(interface=0,max_frames=1000,trace_all=False,production_recipe=RECIPES[0],family='one-shot-two-routes',challenge_route=True,layout_title='一空中资源，两种落岸 / 三侧口',idea_ids=['B31-N12'],native_scene='res://prototype/creative_batches/batch30_blockn12/main_v1.tscn',native_block_scene=str(NATIVE_SCENE.relative_to(HERE.parents[3])))
 c['route_spec']=dict(id='high-investment'if target=='B'else'far-low',from_port='A',to_port=target,role='reward'if target=='B'else'main',via_ports=[],require_bell=False,required_rewards=c['required_rewards'])
 c['rule_parameters']=dict(control=control,target=target,hold=hold,shot_after_release=after,shot_dy=dy,source_family='A5investment-fork',new_family=False,native_rule=True)
 c['layout_uid']=digest({k:c.get(k)for k in ['platforms','ports','reward_sites','block_grid','block_ports']})
 c['generation_rule']=dict(id='B31-N12/Block-native-investment-fork',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),source_map_contract='862b736c491502ae9934265bc7415805b4c122b9',parameters=c['rule_parameters'])
 c['map_specification']=dict(schema='map-notes/challenge-specification/v1',id='B31-N12/three-side-port-interface0',source_type='explicit_model_authored_interface_demand',region='plains',required_family=c['family'],objective=dict(recipe=RECIPES[0],physical_layout_sha256=c['layout_uid'],roles=['fork','reward'],resource='Oneoriginalairshot choosesupperinvestmentorfarlowerbank',new_family=False),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=3,required_normals=[[-1,0],[1,0],[1,0]]),relations=[dict(from_port='A',to_port=t,role='reward'if t=='B'else'main')for t in ['B','C']],space=dict(block_size=128,max_width=1408,max_height=1152,max_port_span_x=1280,port_profiles=['ground64/v1']),boundary_policy='open',enclosing_walls=False,risk_reward=dict(mandatory_damage=False,reward_sites=c['reward_sites']),difficulty=dict(intent='regular',human_score=None),resource_state=dict(reset_between_components=False,entry='ActualsupportedAinternalstageoriginalfullresources, oneairshot only',exit='Observedactualhighorlowgroundstage; no seam/return guaranteed'),return_conditions='OnlyA->B/A->C; other4pairs/oldrejoin/fourthport/floortoretryUNKNOWN',budget=dict(generator_candidates=6,director_revisions=0))
 return c


def purpose(c,r):
 q=original_purpose(c,r);fs=r.get('frames',[]);owned=set(map(tuple,c['block_grid']['cells']));outside=[]
 for a,b in zip(fs,fs[1:]):
  if not raster([min(a['x'],b['x'])-12,min(a['y'],b['y'])-18,abs(a['x']-b['x'])+24,abs(a['y']-b['y'])+36])<=owned:outside.append(b['frame'])
 if outside:q['reasons'].append('actual_body_left_frozen_Block_ownership')
 shots=[f for f in fs if any(e.get('type')=='shot'for e in f.get('accepted',[]))];first=next((f for f in fs if shots and f['frame']>shots[0]['frame']and f.get('grounded')),None)
 q['causal'].update(first_post_shot_landing=({k:first.get(k)for k in ['frame','x','y','support_id','shot_charges','jumps_used']}if first else None),actual_shots=r.get('shots'),outside_body_sweep_frames=outside[:20])
 q['ok']=not q['reasons'];return q


def margin(c,r):
 fs=r.get('frames',[]);index=1 if c['route_spec']['to_port']=='B'else 2;rect=c['platforms'][index];f=next((f for f in fs if f.get('grounded')and f.get('support_id')=='Platform'+str(index)),None)
 if not f:return dict(eligible=False,score=None)
 score=min(f['x']-12-rect[0],rect[0]+rect[2]-f['x']-12)
 return dict(eligible=purpose(c,r)['ok']and score>=0,score=score,first_target_support={k:f.get(k)for k in ['frame','x','y','support_id']})
