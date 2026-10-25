"""Pure placement: exact Module objects plus declared shared-landing dedup.

No floor, platform, corridor, shell or navigation object can be created here.
"""
import copy,json
from pathlib import Path
from pcg.prototype.factory.core.quality import digest
from pcg.prototype.plains.room_modules import generate,routes
from .director import requests


def compile_map(layout_path, library_modules=None):
 graph,specs,seams=requests(layout_path)
 modules=library_modules if library_modules is not None else [routes(generate(s))for s in specs]
 if {m['id']for m in modules}!={s['node_id']for s in specs}:raise ValueError('module_catalog_does_not_cover_map_demands')
 for m in modules:
  if m['spec']!=next(s for s in specs if s['node_id']==m['id']):raise ValueError('stale_module_demand_binding/'+m['id'])
 return assemble_modules(graph,modules,seams)


def assemble_modules(graph,modules,seams):
 """Shared exact-object placer; bounding boxes need not form closed rooms."""
 by={m['id']:m for m in modules};platforms=[];oneway=[];origin=[];lookup={};localmap={};other={k:[]for k in ['saws','moving_platforms','latches','thorns','hooks','enemies','hazards','reward_sites','shop_sites']}
 shared={}
 for seam in seams:
  if seam['kind']=='vertical':
   shared[seam['id']]=seam
 def translated_target(t,m):
  result=copy.deepcopy(t);dx,dy=m['spec']['placement']
  result['position']=[t['position'][0]+dx,t['position'][1]+dy];result['region']=[t['region'][0]+dx,t['region'][1]+dy,*t['region'][2:]]
  result['support_indices']=[localmap[m['id']][int(i)]for i in t['support_indices']]
  return result
 for m in modules:
  key=m['id'];dx,dy=m['spec']['placement'];localmap[key]={}
  for i,p in enumerate(m['case']['platforms']):
   rect=[p[0]+dx,p[1]+dy,*p[2:]];tag=next((eid for eid,port in m['ports'].items()if port.get('shared_landing_index')==i),None)
   identity=(tag,tuple(rect))if tag else(None,key,i)
   if tag and identity in lookup:
    idx=lookup[identity];origin[idx].append(dict(module=key,object_index=i,content_version=m['content_version'],shared_seam=tag))
   else:
    idx=len(platforms);platforms.append(rect);lookup[identity]=idx
    origin.append([dict(module=key,object_index=i,content_version=m['content_version'],shared_seam=tag)])
    if i in m['case']['one_way_platform_indices']:oneway.append(idx)
   localmap[key][i]=idx
  for kind in other:
   for raw in m['case'].get(kind,[]):
    value=copy.deepcopy(raw)
    if kind=='saws':value['origin']=[raw['origin'][0]+dx,raw['origin'][1]+dy];value['source_id']=key+'/'+raw['source_id']
    if kind=='moving_platforms':
     for field in ['start','finish']:value[field]=[raw[field][0]+dx,raw[field][1]+dy]
     value['platform_id']=key+'/'+raw['platform_id']
    if kind=='latches':value['id']=key+'/'+raw['id'];value['bell']=[raw['bell'][0]+dx,raw['bell'][1]+dy];value['gate']=[raw['gate'][0]+dx,raw['gate'][1]+dy,*raw['gate'][2:]]
    if kind=='latches'and raw.get('starts_ferry'):value['starts_ferry']=key+'/'+raw['starts_ferry']
    if kind=='latches'and raw.get('ferry_id'):value['ferry_id']=key+'/'+raw['ferry_id']
    if kind=='latches'and raw.get('return_access'):value['return_access']=[raw['return_access'][0]+dx,raw['return_access'][1]+dy]
    if kind=='enemies':value['id']=key+'/'+raw['id'];value['position']=[raw['position'][0]+dx,raw['position'][1]+dy]
    if kind=='reward_sites':
     value['id']=key+'/'+raw['id'];value['target']=translated_target(raw['target'],m)
     for field in ['required_bell','required_enemy']:
      if raw.get(field):value[field]=key+'/'+raw[field]
    if kind=='shop_sites':value['id']=key+'/'+raw['id'];value['position']=[raw['position'][0]+dx,raw['position'][1]+dy]
    other[kind].append(value)
 # Validate every physical contact, including the coincident actor-center Port.
 nodes={};edges={};gates=[];seamproof=[]
 def legs(values,m):
  dx,dy=m['spec']['placement'];result=[]
  for raw in values:
   v=copy.deepcopy(raw);v['target']=translated_target(v['target'],m)
   for cmd in v.get('control_plan',[]):
    if 'target_x'in cmd:cmd['target_x']+=dx
    if cmd.get('aim_cell'):cmd['aim_cell']['id']=m['id']+'/'+cmd['aim_cell']['id']
    q=cmd.get('trigger',{}).get('dynamic',{})
    if q.get('kind')=='actor_x':q['value']+=dx
    elif 'id'in q:q['id']=m['id']+'/'+q['id']
   if 'carrier_transfer'in v:
    c=v['carrier_transfer'];c['id']=m['id']+'/'+c['id'];c['source_level']+=dy;c['destination_level']+=dy;c['target_x']+=dx
    if c.get('park_bell'):c['park_bell']=m['id']+'/'+c['park_bell']
   result.append(v)
  return result
 for m in modules:
  s=m['spec'];n=s['node'];nodes[m['id']]=dict(id=m['id'],center=translated_target(m['center'],m),
    ports={},center_to_port={eid:legs(v,m)for eid,v in m['center_to_port'].items()},port_to_center={eid:legs(v,m)for eid,v in m['port_to_center'].items()},
    role=n['role'],label=n.get('label',m['id']),opens=n.get('opens',[]),reward=n.get('reward',0),
    module_content_version=m['content_version'],core_visit_program=legs(m.get('core_visit_program',[]),m),
    core_reward_target=translated_target(m['core']['exit'],m)if m.get('core')else None)
 for e,s in zip(graph['edges'],seams):
  a,b=by[e['from']],by[e['to']];pa,pb=a['ports'][e['id']],b['ports'][e['id']]
  posa=[pa['position'][i]+a['spec']['placement'][i]for i in range(2)];posb=[pb['position'][i]+b['spec']['placement'][i]for i in range(2)]
  if posa!=posb or pa['normal']!=[-v for v in pb['normal']]:raise ValueError('modules_do_not_plug_exactly/'+e['id'])
  ta=translated_target(pa['dock'],a);tb=translated_target(pb['dock'],b)
  if s['kind']=='side':
   target=dict(id='seam/'+e['id'],position=posa,region=[posa[0]-4,posa[1]-5,8,10],grounded=True,support_indices=sorted(set(ta['support_indices']+tb['support_indices'])))
   forward=[dict(kind='walk',target=target),dict(kind='walk',target=tb)]
   reverse=[dict(kind='walk',target=target),dict(kind='walk',target=ta)]if e['bidirectional']else[]
  else:
   if ta['position']!=tb['position']or ta['support_indices']!=tb['support_indices']:raise ValueError('shared_landing_not_identical/'+e['id'])
   forward=[dict(kind='walk',target=tb)];reverse=[dict(kind='walk',target=ta)]if e['bidirectional']else[]
  edges[e['id']]={**e,'forward_waypoints':forward,'reverse_waypoints':reverse}
  for m,p,t in [(a,pa,ta),(b,pb,tb)]:nodes[m['id']]['ports'][e['id']]=dict(position=posa,normal=p['normal'],target=t)
  seamproof.append(dict(id=e['id'],from_module=e['from'],to_module=e['to'],from_position=posa,to_position=posb,
      gap=0,normals_opposed=True,interstitial_terrain_objects=0,shared_landing=s['kind']=='vertical'))
 for m in modules:
  dx,dy=m['spec']['placement']
  for raw in m['boundary_gates']:
   gate=copy.deepcopy(raw);gate['bounds']=[raw['bounds'][0]+dx,raw['bounds'][1]+dy,*raw['bounds'][2:]]
   gate['module_content_version']=m['content_version'];gates.append(gate)
 for owners in origin:
  for owner in owners:owner['content_version']=by[owner['module']]['content_version']
 for key,node in nodes.items():node['module_content_version']=by[key]['content_version']
 xs=[p[0]for p in platforms]+[p[0]+p[2]for p in platforms];ys=[p[1]for p in platforms]+[p[1]+p[3]for p in platforms]
 case=dict(id='direct-module-plains',family='direct_module_map',capabilities=['move','jump','shot_recoil'],platforms=platforms,one_way_platform_indices=oneway,
  wall_platform_indices=[],world_bounds=[min(xs)-32,min(ys)-96,max(xs)-min(xs)+64,max(ys)-min(ys)+192],spawn=nodes[graph['entry']]['center']['position'],
  entry_port=nodes[graph['entry']]['center']['position'],exit_port=nodes[graph['goal']]['center']['position'],goal=nodes[graph['goal']]['center']['region'],
  max_frames=3600,control_plan=[],trace_all=False,**other)
 return dict(schema='pcg/direct-joined-module-map/v1',case=case,nodes=nodes,edges=edges,gate_specs=gates,modules=modules,
  exploration_graph=graph,source={'graph_source':'existing region-network-v2/plains-R2-0','graph_sha256':digest(graph)},
  seams=seamproof,object_provenance=origin,status='exact contact assembly; physical validation pending',
  hard_checks={'modules':len(modules),'connections':len(seams),'all_ports_coincident':True,'map_added_platforms':0,'connector_modules':0,'inter_module_platform_chains':0,'all_platforms_bound_to_module_versions':len(origin)==len(platforms)})
