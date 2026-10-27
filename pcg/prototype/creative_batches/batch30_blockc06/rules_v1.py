"""A real three-port falling choice with native Block terminal profiles."""
import copy
from pathlib import Path
from pcg.map_directed.block_grid.contracts import declare,raster,regions,validate
from pcg.prototype.creative_batches.batch30_blockpilot.rules_v1 import block_port
from pcg.prototype.creative_batches.batch30_c06 import rules_v2 as source
from pcg.prototype.factory.core.quality import digest

HERE=Path(__file__).parent
RECIPES=('block128-falling-choice',)
RUNNER_SCRIPT=source.RUNNER_SCRIPT
SOURCE_DEPENDENCIES=[Path(source.__file__),*source.SOURCE_DEPENDENCIES,HERE/'protocol-v1.json',HERE.parent/'batch30_blockpilot/rules_v1.py']
DX,DY=48,11

def adapted(old):
 c=copy.deepcopy(old)
 def point(p):return[p[0]+DX,p[1]+DY]
 def rect(r):return[*point(r),*r[2:]]
 for key in ['platforms','hazards']:c[key]=[rect(r)for r in c.get(key,[])]
 for key in ['spawn','entry_port','exit_port']:c[key]=point(c[key])
 c['goal']=rect(c['goal'])
 for l in c['latches']:
  for key in ['bell','return_access']:
   if key in l:l[key]=point(l[key])
  for key in ['gate','paired_gate']:l[key]=rect(l[key])
 for s in c['reward_sites']:
  s['position']=point(s['position']);s['region']=rect(s['region'])
 for q in c['control_plan']:
  if 'target_x'in q:q['target_x']+=DX
  d=q.get('trigger',{}).get('dynamic',{})
  if d.get('kind')=='actor_x':d['value']+=DX
 edits=[]
 for index,top in [(0,224),(1,480),(2,992)]:
  r=c['platforms'][index];before=r[:];bottom=r[1]+r[3];r[1]=top;r[3]=bottom-top
  if index==0:r[2]=r[0]+r[2]-256;r[0]=256
  else:r[2]=640-r[0]
  edits.append(dict(index=index,before=before,after=r[:],top_delta=top-before[1],horizontal_trim=28))
 assert max(abs(e['top_delta'])for e in edits)<=32
 docks={'A':[280,206],'B':[616,462],'C':[616,974]}
 ports={'A':block_port('A',[2,1],'W',docks['A']),
        'B':block_port('B',[4,3],'E',docks['B']),
        'C':block_port('C',[4,7],'E',docks['C'])}
 c['ports']=[dict(id=k,position=docks[k],normal=ports[k]['normal'],support_index=i)for i,k in enumerate(['A','B','C'])]
 target=docks[c['route_spec']['to_port']]
 c['spawn']=docks['A'][:];c['entry_port']=docks['A'][:];c['exit_port']=target[:];c['goal']=[target[0]-25,target[1]-4,50,8]
 for s,k in zip(c['reward_sites'],['B','C']):
  s['position']=docks[k][:];s['region']=[docks[k][0]-30,docks[k][1]-6,60,12]
 for q in c['control_plan']:
  if q.get('op')=='settle':q['target_x']=target[0]
 reservations=[[256,-512,384,1664]]
 projected=dict(case=c,ports=ports,action_clearance=reservations,functional_roles=['junction','fork'])
 physical=regions(projected)+[l['paired_gate']for l in c['latches']]
 physical += [[s['position'][0]-21,s['position'][1]-18,42,36]for s in c['reward_sites']]
 cells=set().union(*(raster(r)for r in physical))
 projected=declare(projected,cells);errors=validate(projected)
 if errors:raise ValueError('block_c06_static/'+','.join(errors))
 c['block_grid']=projected['block_grid'];c['block_ports']=ports;c['block_reservations']=reservations
 c['block_adaptation']=dict(source_case=old['id'],translation=[DX,DY],terminal_edits=edits,retained_recovery_platform_indices=[3],deleted_platform_indices=[],map_added_terrain=0,inherited_physics=False)
 c['id']=old['id'].replace('b30-c06-v2-i1','b30-block-c06-v1-i0');c['interface']=0;c['family']=RECIPES[0];c['production_recipe']=RECIPES[0]
 c['layout_title']='Block128 坠井择层 / 同侧双门'
 c['rule_parameters']['interface']=0
 c['layout_uid']=digest({k:c.get(k,[])for k in ['platforms','ports','latches','reward_sites','block_grid','block_ports']})
 c['generation_rule']=dict(id='batch30/block-native-C06',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['block_adaptation'])
 s=c['map_specification'];s['id']='batch30/block-C06/0';s['required_family']=RECIPES[0]
 s['objective'].update(recipe=RECIPES[0],interface=0,physical_layout_sha256=c['layout_uid'],junction_role='fork',junction_pattern='falling_layer_choice')
 s['ports']['required_normals']=[p['normal']for p in c['ports']]
 s['space'].update(max_width=1280,max_height=1920,max_port_span_x=512,block_size=128,port_profiles=['ground64/v1'])
 s['resource_state']['entry']='Same actual supported internal A dock, original Aclosed/Bopen, original resources; boundary ingress and arbitrary world state UNKNOWN'
 s['return_conditions']='Failure floor retained. New exact recovery, reverse, boundary crossing and full Map remain UNKNOWN.'
 return c

def layouts(recipe,interface):
 if recipe!=RECIPES[0]or interface!=0:raise ValueError('only registered Block C06 slender interface0')
 return[adapted(c)for c in source.layouts(source.RECIPES[0],1)]

def purpose(c,r):
 q=source.purpose(c,r);owned=set(map(tuple,c['block_grid']['cells']));outside=[]
 for f in r.get('frames',[]):
  if not raster([f['x']-12,f['y']-18,24,36])<=owned:outside.append(f['frame'])
 q['causal']['unreserved_body_frames']=outside[:12]
 if outside:q['reasons'].append('actual_body_left_frozen_block_reservation')
 q['ok']=not q['reasons'];return q

def alternatives(c):
 route=c['rule_parameters']['route'];control=source.CONTROL[(1,route)]
 return[adapted(v)for v in source.alternatives(source.materialize(1,route,control))]
