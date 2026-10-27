"""Block128 adaptation of the user's real mounted-bell interception."""
import copy
from pathlib import Path
from pcg.prototype.creative_batches.batch30_d05 import api_v3 as source
from pcg.prototype.creative_batches.batch30_blockpilot.rules_v1 import block_port
from pcg.map_directed.block_grid.contracts import declare,raster,regions,validate
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=('block128-bell-carrier-catch',)
RUNNER_SCRIPT=source.RUNNER_SCRIPT
SOURCE_DEPENDENCIES=[Path(source.__file__),*source.SOURCE_DEPENDENCIES,HERE/'protocol-v1.json',HERE.parent/'batch30_blockpilot/rules_v1.py']
DX,DY=32,-86

def adapted(old):
 c=copy.deepcopy(old)
 def point(p):return[p[0]+DX,p[1]+DY]
 def rect(r):return[*point(r),*r[2:]]
 for key in ['platforms','hazards']:c[key]=[rect(r)for r in c.get(key,[])]
 for key in ['spawn','entry_port','exit_port']:c[key]=point(c[key])
 c['goal']=rect(c['goal']);c['world_bounds']=rect(c['world_bounds'])
 for m in c['moving_platforms']:m['start']=point(m['start']);m['finish']=point(m['finish'])
 for l in c['latches']:
  l['bell']=point(l['bell']);l['gate']=rect(l['gate'])
 for s in c['reward_sites']:s['position']=point(s['position']);s['region']=rect(s['region'])
 for q in c['control_plan']:
  if 'target_x'in q:q['target_x']+=DX
  d=q.get('trigger',{}).get('dynamic',{})
  if d.get('kind')=='actor_x':d['value']+=DX
 r=c['platforms'][1];before=r[:];bottom=r[1]+r[3];r[1]=224;r[3]=bottom-224;r[2]=1536-r[0]
 assert abs(r[1]-before[1])<=32 and before[0]+before[2]-1536==16
 a=[-104,334];b=[1512,206]
 c['spawn']=a[:];c['entry_port']=a[:];c['exit_port']=b[:];c['goal']=[b[0]-25,b[1]-4,50,8]
 c['ports']=[dict(id='A',position=a,normal=[-1,0],support_index=0),dict(id='B',position=b,normal=[1,0],support_index=1)]
 ports={'A':block_port('A',[-1,2],'W',a),'B':block_port('B',[11,1],'E',b)}
 for s in c['reward_sites']:s['position']=b[:];s['region']=[b[0]-30,b[1]-6,60,12]
 for q in c['control_plan']:
  if q.get('op')=='settle':q['target_x']=b[0]
 reservations=[[-128,-512,1664,1152],[-640,384,768,384]]
 projected=dict(case=c,ports=ports,action_clearance=reservations,functional_roles=['traversal'])
 physical=regions(projected)
 for l in c['latches']:
  m=next(m for m in c['moving_platforms']if m['platform_id']==l['carrier_mount'])
  offset=[l['bell'][j]-m['start'][j]for j in [0,1]];xs=[m['start'][0]+offset[0],m['finish'][0]+offset[0]];ys=[m['start'][1]+offset[1],m['finish'][1]+offset[1]]
  assert offset==[80,-120]
  physical.append([min(xs)-14,min(ys)-17,max(xs)-min(xs)+28,max(ys)-min(ys)+34])
 physical += [[s['position'][0]-21,s['position'][1]-18,42,36]for s in c['reward_sites']]
 cells=set().union(*(raster(r)for r in physical));projected=declare(projected,cells);errors=validate(projected)
 if errors:raise ValueError('block_D05_static/'+','.join(errors))
 c['block_grid']=projected['block_grid'];c['block_ports']=ports;c['block_reservations']=reservations
 c['block_adaptation']=dict(source_case=old['id'],translation=[DX,DY],terminal_edit=dict(index=1,before=before,after=r[:],top_delta=r[1]-before[1],right_trim=16),entry_rebound_to_original_bank=True,retained_recovery_platform_indices=[3,4,5,6],deleted_platform_indices=[],mounted_bell_full_envelope=True,map_added_terrain=0,inherited_physics=False)
 c['id']='b30-block-d05-v1-i'+str(c['interface'])+'-c1'
 if old.get('counterexample_kind'):c['id']+='-counter-'+old['id'].split('-counter-',1)[-1]
 c['family']=RECIPES[0];c['production_recipe']=RECIPES[0]
 c['layout_title']='Block128 风铃台追接 / '+('窄接收岸'if c['interface']==0 else'向内扩40接收岸')
 c['layout_uid']=digest({k:c.get(k,[])for k in ['platforms','ports','moving_platforms','latches','reward_sites','block_grid','block_ports']})
 c['generation_rule']=dict(id='human-d05/block128-bell-carrier-catch',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['block_adaptation'])
 for k in ['first_departure_x','second_departure_x']:
  if k in c['rule_parameters']:c['rule_parameters'][k]+=DX
 s=c['map_specification'];s['id']='batch30/block-D05/'+str(c['interface']);s['required_family']=RECIPES[0]
 s['objective'].update(recipe=RECIPES[0],physical_layout_sha256=c['layout_uid'],block_contract='map-notes/block-grid/v1')
 s['space'].update(max_width=2560,max_height=1536,max_port_span_x=1664,block_size=128,port_profiles=['ground64/v1'])
 s['resource_state']['entry']='Supported internal A dock and initially parked original carrier; boundary ingress/phase entailment UNKNOWN'
 s['return_conditions']='All original failure floor/stairs retained; exact new same-world retry, reverse and boundaries UNKNOWN until separately verified'
 return c

def layouts(recipe,interface):
 if recipe!=RECIPES[0]or interface not in [0,1]:raise ValueError('outside two registered Block D05 demands')
 return[adapted(c)for c in source.layouts(source.RECIPES[0],interface)]

def purpose(c,r):
 q=source.purpose(c,r);outside=[];owned=set(map(tuple,c['block_grid']['cells']))
 for f in r.get('frames',[]):
  if not raster([f['x']-12,f['y']-18,24,36])<=owned:outside.append(f['frame'])
 q['causal']['unreserved_body_frames']=outside[:12]
 if outside:q['reasons'].append('actual_body_left_frozen_block_reservation')
 q['ok']=not q['reasons'];return q

def alternatives(c):
 old=source.layouts(source.RECIPES[0],c['interface'])[0]
 return[adapted(v)for v in source.alternatives(old)]
