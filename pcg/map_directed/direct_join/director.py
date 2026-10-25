"""Preserved mission/exploration graph → contact faces → Module requests."""
import copy,itertools,json
from pathlib import Path
from pcg.map_directed.director import REPO

UNIT=(512,288)
def requests(layout_path):
 raw=json.loads(Path(layout_path).read_text());unit=raw.get('units',UNIT);g=copy.deepcopy(raw['source_graph'])
 axis=raw.get('column_widths',[unit[0]]*40);prefix=[0]
 for value in axis:prefix.append(prefix[-1]+value)
 rs={k:{'x':prefix[v['x']],'y':v['y']*unit[1],'w':prefix[v['x']+v['w']]-prefix[v['x']],'h':v['h']*unit[1]}for k,v in raw['rooms'].items()}
 ports={k:{}for k in rs};seams=[];top_edges={k:[]for k in rs}
 for e in g['edges']:
  a,b=rs[e['from']],rs[e['to']];fr,to=e['from'],e['to']
  if a['x']+a['w']==b['x']or b['x']+b['w']==a['x']:
   normal=[1,0]if a['x']<b['x']else[-1,0];point=[max(a['x'],b['x']),min(a['y']+a['h'],b['y']+b['h'])-64]
   seam=dict(id=e['id'],a=fr,b=to,position=point,normal=normal,kind='side',aperture=[point[0]-24,point[1]-96,48,136])
  elif a['y']+a['h']==b['y']or b['y']+b['h']==a['y']:
   normal=[0,1]if a['y']<b['y']else[0,-1];low=max(a['x'],b['x']);high=min(a['x']+a['w'],b['x']+b['w'])
   bottom=to if normal[1]>0 else fr
   seam=dict(id=e['id'],a=fr,b=to,normal=normal,kind='vertical',cut_y=max(a['y'],b['y']),overlap=[low,high],lower_module=bottom)
   top_edges[bottom].append(seam)
  else:raise ValueError('input_edge_is_not_a_direct_contact/'+e['id'])
  seams.append(seam)
 # Choose carrier columns using the Module's actual other ports, avoiding
 # lift wells through another gallery. No geometry is authored here.
 issues=[];group_options={}
 for node,edges in top_edges.items():
  if not edges:continue
  room=rs[node];gallery_by_level={}
  for s in seams:
   if s['kind']!='side'or node not in [s['a'],s['b']]:continue
   level=s['position'][1]-room['y']
   if level!=room['h']-64:gallery_by_level.setdefault(level,set()).add(-1 if s['position'][0]==room['x']else 1)
  own=[];counts={-1:0,1:0}
  for level,sides in sorted(gallery_by_level.items(),reverse=True):
   if sides=={-1}:own.append(room['x']+128+256*counts[-1]);counts[-1]+=1
   elif sides=={1}:own.append(room['x']+room['w']-128-256*counts[1]);counts[1]+=1
   else:own.append(room['x']+room['w']/2)
  options=[]
  for s in edges:
   lo,hi=s['overlap'];options.append(sorted(set([lo+128,(lo+hi)//2,hi-128])))
  candidates=[]
  for values in itertools.product(*options):
   allx=list(values)+own
   distances=[abs(a-b)for i,a in enumerate(allx)for b in allx[i+1:]]
   if distances and min(distances)<256:continue
   candidates.append((-(min(distances)if distances else 9999),values))
  if not candidates:
   issues.append(node);chosen=tuple(o[0]for o in options)
  else:chosen=min(candidates)[1]
  if raw.get('physical_port_clearance'):
   group_options[node]=[v for _,v in sorted(candidates)]
   continue
  for s,c in zip(edges,chosen):
   lo,hi=s['overlap'];bearing=1 if c<=(lo+hi)/2 else-1
   point=[c+bearing*62,s['cut_y']]
   s.update(position=point,column_x=c,bearing=bearing,aperture=[c-96,s['cut_y']-80,192,160])
 if raw.get('physical_port_clearance'):
  # The old per-room greedy columns can put a bottom export directly under
  # another lift's parked body. Search the SAME finite candidate columns
  # jointly; no corridor/terrain/physics is synthesized here.
  assigned={};expanded=0;order=sorted(group_options,key=lambda n:(len(group_options[n]),n))
  vertical={s['id']:s for s in seams if s['kind']=='vertical'}
  def compatible(s,x,t,y):
   if not {s['a'],s['b']}&{t['a'],t['b']}:return True
   return abs(x-y)>=256 if s['lower_module']==t['lower_module'] else abs(x-y)>=192
  def search(index):
   nonlocal expanded
   expanded+=1
   if expanded>25000:return False
   if index==len(order):return True
   node=order[index];edges=top_edges[node]
   for values in group_options[node]:
    if any(not compatible(s,x,vertical[eid],other)for s,x in zip(edges,values)for eid,other in assigned.items()):continue
    assigned.update({s['id']:x for s,x in zip(edges,values)})
    if search(index+1):return True
    for s in edges:assigned.pop(s['id'])
   return False
  if not search(0):raise ValueError('module_lift_and_bottom_port_clearance_unsatisfied/'+','.join(order))
  for s in vertical.values():
   c=assigned[s['id']];lo,hi=s['overlap'];bearing=1 if c<=(lo+hi)/2 else-1
   s.update(position=[c+bearing*62,s['cut_y']],column_x=c,bearing=bearing,aperture=[c-96,s['cut_y']-80,192,160])
 if issues:raise ValueError('module_columns_need_local_shape_revision/'+','.join(issues))
 for s in seams:
  for node,normal in [(s['a'],s['normal']),(s['b'],[-n for n in s['normal']])]:
   room=rs[node];p=[s['position'][0]-room['x'],s['position'][1]-room['y']]
   ports[node][s['id']]=dict(id=s['id'],position=p,normal=normal,kind=s['kind'],
     column_x=s.get('column_x',0)-room['x']if s['kind']=='vertical'else None,bearing=s.get('bearing'),
     aperture=[s['aperture'][0]-room['x'],s['aperture'][1]-room['y'],*s['aperture'][2:]])
 nodes={n['id']:n for n in g['nodes']}
 result=[]
 for key,r in rs.items():
  result.append(dict(schema='map-notes/challenge-specification/v1',id='direct-room/'+key,node_id=key,region='plains',
   objective='A complete multiport action room; every boundary face plugs directly into a peer Module',
   node=nodes[key],placement=[r['x'],r['y']],space={'core_bounds':[0,0,r['w'],r['h']],'allowed_external_overlap':'declared seam landing only'},
   ports=list(ports[key].values()),boundary_gate_requirements=[dict(edge_id=e['id'],switch=e.get('switch'),one_way=not e['bidirectional'],peer=e['to'])for e in g['edges']if e['from']==key and(e.get('switch')or not e['bidirectional'])],
   capabilities={'version':1,'status':'defined','allOf':['move','jump','shot_recoil'],'anyOfGroups':[]},
   forbidden=['L4 connector terrain','stair-pad chain','undeclared ports','post-placement navigation fill'],
   budget={'generator_candidates':1,'unbounded_retry':False}))
 return g,result,seams
