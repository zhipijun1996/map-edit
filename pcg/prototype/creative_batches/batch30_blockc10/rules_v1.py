"""Block128 input and output of a real internal recovery detour."""
import copy
from pathlib import Path
from pcg.prototype.creative_batches.batch30_c10 import api_v2 as source
from pcg.prototype.creative_batches.batch30_blockpilot.rules_v1 import block_port
from pcg.map_directed.block_grid.contracts import declare,raster,regions,validate
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=('block128-retained-shot-recovery',)
RUNNER_SCRIPT=source.RUNNER_SCRIPT
SOURCE_DEPENDENCIES=[Path(source.__file__),*source.SOURCE_DEPENDENCIES,HERE/'protocol-v1.json',HERE.parent/'batch30_blockpilot/rules_v1.py']
DX,DY=0,-112

def adapted(old):
 c=copy.deepcopy(old)
 def point(p):return[p[0]+DX,p[1]+DY]
 def rect(r):return[*point(r),*r[2:]]
 for key in ['platforms','hazards']:c[key]=[rect(r)for r in c.get(key,[])]
 for key in ['spawn','entry_port','exit_port']:c[key]=point(c[key])
 c['goal']=rect(c['goal']);c['world_bounds']=rect(c['world_bounds'])
 for l in c['latches']:
  for key in ['bell','return_access']:l[key]=point(l[key])
  for key in ['gate','paired_gate']:l[key]=rect(l[key])
 for s in c['reward_sites']:s['position']=point(s['position']);s['region']=rect(s['region'])
 edits=[]
 for index,top in [(0,352),(1,224)]:
  r=c['platforms'][index];before=r[:];bottom=r[1]+r[3];r[1]=top;r[3]=bottom-top
  if index==0:r[2]=r[0]+r[2]+128;r[0]=-128
  else:r[2]=768-r[0]
  edits.append(dict(index=index,before=before,after=r[:],top_delta=top-before[1],outward_extension=28))
 assert max(abs(e['top_delta'])for e in edits)<=32
 a=[-104,334];b=[744,206]
 c['spawn']=a[:];c['entry_port']=a[:];c['exit_port']=b[:];c['goal']=[b[0]-25,b[1]-4,50,8]
 c['ports']=[dict(id='A',position=a,normal=[-1,0],support_index=0),dict(id='B',position=b,normal=[1,0],support_index=1)]
 ports={'A':block_port('A',[-1,2],'W',a),'B':block_port('B',[5,1],'E',b)}
 for s in c['reward_sites']:s['position']=b[:];s['region']=[b[0]-30,b[1]-6,60,12]
 for q in c['control_plan']:
  if q.get('op')=='settle'and q.get('target_x')==650:q['target_x']=b[0]
  elif q.get('op')=='settle'and q.get('target_x')==80:q['target_x']=a[0]
 reservations=[[-128,-512,896,1280]]
 projected=dict(case=c,ports=ports,action_clearance=reservations,functional_roles=['traversal','conditional_recovery'])
 physical=regions(projected)+[l['paired_gate']for l in c['latches']]+[[s['position'][0]-21,s['position'][1]-18,42,36]for s in c['reward_sites']]
 cells=set().union(*(raster(r)for r in physical));projected=declare(projected,cells);errors=validate(projected)
 if errors:raise ValueError('block_C10_static/'+','.join(errors))
 c['block_grid']=projected['block_grid'];c['block_ports']=ports;c['block_reservations']=reservations
 c['block_adaptation']=dict(source_case=old['id'],translation=[DX,DY],terminal_edits=edits,retained_internal_recovery_indices=[2,3,4],deleted_platform_indices=[],map_added_terrain=0,inherited_physics=False,actual_return_settle_x=a[0])
 c['id']=old['id'].replace('b30-c10-v3','b30-block-c10-v1');c['family']=RECIPES[0];c['production_recipe']=RECIPES[0]
 c['layout_title']='Block128 留枪入洞，再返岸重试'
 c['layout_uid']=digest({k:c.get(k,[])for k in ['platforms','ports','latches','reward_sites','block_grid','block_ports']})
 c['generation_rule']=dict(id='batch30/block-native-C10',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['block_adaptation'])
 s=c['map_specification'];s['id']='batch30/block-C10/0';s['required_family']=RECIPES[0]
 s['objective'].update(recipe=RECIPES[0],physical_layout_sha256=c['layout_uid'],block_contract='map-notes/block-grid/v1')
 s['space'].update(max_width=1024,max_height=1280,max_port_span_x=896,block_size=128,port_profiles=['ground64/v1'])
 s['resource_state']['entry']='Actual supported A internal dock, original Aopen/Bclosed, real single air shot; boundary ingress/unknown state entailment not proven'
 s['return_conditions']='Both canonical witnesses required: nominal plus real miss->internal cavity->restore->newA dock->retryB. Generic recovery, B->A and boundary crossing remain UNKNOWN.'
 return c

def layouts(recipe,interface):
 if recipe!=RECIPES[0]or interface!=0:raise ValueError('Only original successful under-pocket interface is registered')
 return[adapted(c)for c in source.layouts(source.RECIPES[0],0)]

def purpose(c,r):
 q=source.purpose(c,r);owned=set(map(tuple,c['block_grid']['cells']));outside=[f['frame']for f in r.get('frames',[])if not raster([f['x']-12,f['y']-18,24,36])<=owned]
 q['causal']['unreserved_body_frames']=outside[:12]
 if outside:q['reasons'].append('actual_body_left_frozen_block_reservation')
 if not c.get('counterexample_kind')and c['rule_parameters']['route']=='retry':
  fs=r.get('frames',[]);cavity=q['causal'].get('cavity_grounded_frames',[])
  returned=[f['frame']for f in fs if cavity and f['frame']>min(cavity)and f.get('grounded')and f.get('support_id')=='Platform0'and abs(f['x']+104)<7]
  q['causal']['actual_new_A_dock_return_frames']=returned
  if not returned:q['reasons'].append('no_actual_new_A_staging_return')
 q['ok']=not q['reasons'];return q

def alternatives(c):
 old=next(v for v in source.layouts(source.RECIPES[0],0)if v['rule_parameters']['route']==c['rule_parameters']['route'])
 return[adapted(v)for v in source.alternatives(old)]
