"""Bounded Block terminal adaptation of repaired (not withdrawn) A2."""
import copy,json,math
from pathlib import Path
from pcg.prototype.workshop import rules as original
from pcg.prototype.workshop.evaluate import purpose as original_purpose
from pcg.prototype.creative_batches.batch30_blockpilot.rules_v1 import block_port
from pcg.map_directed.block_grid.contracts import declare,raster,regions,validate
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=('block128-active-chase-bidirectional',)
RUNNER_SCRIPT=HERE.parents[1]/'workshop/runner.gd'
# HERE.parents[1] is prototype.
SOURCE_DEPENDENCIES=[Path(original.__file__),HERE/'protocol-v1.json',HERE/'source-map-demand-v1.json',HERE.parent/'batch30_blockpilot/rules_v1.py',HERE.parents[2]/'map_directed/block_grid/contracts.py']
SOURCE_IDS=['26544bbf5c94d81a45bc1953800c97cbe0a62a42f0971aa1b0a59e67094972b0','6b9d2d9858dbb646b119182e597096264618d7e907588f6ee63ac99545016b63']

def reverse_plan(c,hold=20):
 left=c['platforms'][1][0];end=c['ports'][0]['position'][0]
 return [original.cmd('axis',value=-1),original.wait_x(left+24,-1),original.cmd('jump'),original.cmd('jump_release',hold),original.cmd('shoot',6,direction=[.9,math.sqrt(1-.9**2)]),dict(op='wait',trigger=dict(dynamic=dict(kind='on_platform',id='chase-carrier'),timeout=240)),original.cmd('jump'),original.cmd('jump_release',12),original.settle(end,6)]

def candidate(interface=0,direction='out',hold=20):
 if interface not in [0,1]:raise ValueError('only two registered interfaces')
 c=original.chase(interface);c['interface']=interface;dx=[32,6][interface];dy=42
 def pt(p):return[p[0]+dx,p[1]+dy]
 def rect(r):return[*pt(r),*r[2:]]
 c['platforms']=[rect(r)for r in c['platforms']]
 c['platforms'][0][2]=c['platforms'][0][0]+c['platforms'][0][2]+128;c['platforms'][0][0]=-128
 r=c['platforms'][1];bottom=r[1]+r[3];r[1]=352;r[3]=bottom-352;r[2]=1024-r[0]
 for m in c['moving_platforms']:m['start']=pt(m['start']);m['finish']=pt(m['finish'])
 for l in c['latches']:l['bell']=pt(l['bell']);l['gate']=rect(l['gate']);l['return_access']=pt(l['return_access'])
 plan=copy.deepcopy(c['control_plan'])
 for op in plan:
  if 'target_x'in op:op['target_x']+=dx
  d=op.get('trigger',{}).get('dynamic',{})
  if d.get('kind')=='actor_x':d['value']+=dx
 plan[-1]['target_x']=1000
 prefix=[original.cmd('axis',value=1),original.wait_x(80+dx),original.cmd('axis',value=0),original.ground(),original.cmd('wait',6)]
 a=[-104,462];b=[1000,334]
 c['ports']=[dict(id='A',position=a,normal=[-1,0],support_index=0),dict(id='B',position=b,normal=[1,0],support_index=1)]
 c['block_ports']={'A':block_port('A',[-1,3],'W',a),'B':block_port('B',[7,2],'E',b)}
 c['block_reservations']=[[-128,0,1152,768]]
 c['reward_sites']=[];c['expected_reward']=0;c['required_rewards']=[]
 c['family']=RECIPES[0];c['production_recipe']=RECIPES[0]
 c['route_spec']=dict(id='chase'if direction=='out'else'return',from_port='A'if direction=='out'else'B',to_port='B'if direction=='out'else'A',role='main',required_rewards=[])
 c['spawn']=(a if direction=='out'else b)[:];c['entry_port']=c['spawn'][:];c['exit_port']=(b if direction=='out'else a)[:]
 c['goal']=[c['exit_port'][0]-25,c['exit_port'][1]-4,50,8];c['world_bounds']=[-1024,-1024,4096,3072]
 c['control_plan']=prefix+plan if direction=='out'else reverse_plan(c,hold)
 c['max_frames']=1000;c['trace_all']=True
 c['rule_parameters'].update(interface=interface,direction=direction,reverse_hold=hold,translation=[dx,dy],reward_removed_for_explicit_map_request=True)
 c['block_adaptation']=dict(source_candidate=SOURCE_IDS[interface],translation=[dx,dy],shore_top_delta=[0,22],shore_outer_trim=[32-dx,18 if interface==0 else 27],retained_recovery_platform_indices=[2],deleted_platform_indices=[],map_added_terrain=0,inherited_physics=False)
 project=dict(case=c,ports=c['block_ports'],action_clearance=c['block_reservations'])
 physical=regions(project);owned=set().union(*(raster(r)for r in physical));project=declare(project,owned)
 errors=validate(project)
 if errors:raise ValueError(errors)
 c['block_grid']=project['block_grid']
 c['layout_uid']=digest({k:c.get(k)for k in ['platforms','moving_platforms','latches','ports','reward_sites','block_grid','block_ports']})
 c['id']=f'b30-block-a2-v1-i{interface}-{direction}-h{hold}'
 c['layout_title']='Block128 主动追台与逆向接台'
 c['generation_rule']=dict(id='A2/repaired-chase/block128',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['block_adaptation'])
 spec=copy.deepcopy(json.loads((HERE/'source-map-demand-v1.json').read_text())['original_request']);spec['required_family']=RECIPES[0]
 spec['resolved_local_interfaces']=dict(ports=c['block_ports'],relations=[['A','B'],['B','A']],source='Actual Map incident edges bidirectional, exact staging resolved locally; all fields of original_request otherwise retained',initial_carrier='original parked start for both directions')
 c['map_specification']=spec
 return c

def layouts(recipe,interface):
 if recipe!=RECIPES[0]:raise ValueError('unsupported recipe')
 return[candidate(interface,d)for d in ['out','back']]

def purpose(c,r):
 v=copy.deepcopy(c);v['family']='chase-landing'if c['route_spec']['from_port']=='A'else'block-return';q=original_purpose(v,r)
 owned=set(map(tuple,c['block_grid']['cells']));outside=[]
 fs=r.get('frames',[])
 for a,b in zip(fs,fs[1:]):
  body=[min(a['x'],b['x'])-12,min(a['y'],b['y'])-18,abs(a['x']-b['x'])+24,abs(a['y']-b['y'])+36]
  if not raster(body)<=owned:outside.append(b['frame'])
 q['causal']['outside_body_sweep_frames']=outside[:20]
 if outside:q['reasons'].append('actual_body_left_frozen_block_reservation')
 if c['route_spec']['from_port']=='B':
  supports=[f for f in fs if f.get('support_id')=='chase-carrier'];q['causal']['actual_return_carrier_support_frames']=len(supports)
  # Reverse reachability is the hard requirement. Actual intermediate supports are reported, not prescribed as necessity.
 q['ok']=not q['reasons'];return q
