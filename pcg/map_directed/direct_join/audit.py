"""Fail closed on any Map-authored terrain or altered Module geometry."""
from pcg.prototype.factory.core.quality import digest

def audit(c):
 modules={m['id']:m for m in c['modules']};platforms=c['case']['platforms'];origins=c['object_provenance']
 if len(platforms)!=len(origins):raise ValueError('orphan_map_platform')
 used=set()
 for rect,owners in zip(platforms,origins):
  if not owners:raise ValueError('map_platform_without_module')
  for owner in owners:
   m=modules[owner['module']];p=m['case']['platforms'][owner['object_index']];dx,dy=m['spec']['placement']
   if rect!=[p[0]+dx,p[1]+dy,*p[2:]]:raise ValueError('map_changed_module_geometry')
   if owner['content_version']!=m['content_version']:raise ValueError('stale_module_instance_version')
   used.add((m['id'],owner['object_index']))
  if len(owners)>1 and(len(owners)!=2 or not owners[0]['shared_seam']or owners[0]['shared_seam']!=owners[1]['shared_seam']):raise ValueError('undeclared_deduplicated_geometry')
 expected={(m['id'],i)for m in modules.values()for i in range(len(m['case']['platforms']))}
 if used!=expected:raise ValueError('module_geometry_was_omitted')
 for seam in c['seams']:
  positions=[];normals=[]
  for node in [seam['from_module'],seam['to_module']]:
   m=modules[node];p=m['ports'][seam['id']];dx,dy=m['spec']['placement']
   positions.append([p['position'][0]+dx,p['position'][1]+dy]);normals.append(p['normal'])
  if positions[0]!=positions[1]or normals[0]!=[-v for v in normals[1]]:raise ValueError('module_ports_are_not_flush')
 overlaps=[]
 for i,a in enumerate(platforms):
  own={p['module']for p in origins[i]}
  for j,b in enumerate(platforms[:i]):
   if own&{p['module']for p in origins[j]}:continue
   if min(a[0]+a[2],b[0]+b[2])-max(a[0],b[0])>1e-5 and min(a[1]+a[3],b[1]+b[3])-max(a[1],b[1])>1e-5:overlaps.append([i,j])
 if overlaps:raise ValueError('undeclared_inter_module_solid_overlap/'+str(overlaps))
 for m in modules.values():
  W,H=m['spec']['space']['core_bounds'][2:]
  for s in m['case']['saws']:
   x,y=s['origin'];tx,ty=s['travel'];r=s['radius']
   if x-abs(tx)-r<0 or x+abs(tx)+r>W or y-abs(ty)-r<0 or y+abs(ty)+r>H:raise ValueError('module_saw_sweeps_into_neighbor/'+m['id'])
 return dict(schema='pcg/direct-module-assembly-audit/v1',modules=len(modules),seams=len(c['seams']),
  map_created_terrain_objects=0,omitted_module_objects=0,orphan_platforms=0,port_gaps=0,
  undeclared_inter_module_solid_overlaps=0,all_instance_geometry_exact=True,
  unique_platforms=len(platforms),module_source_platforms=len(expected),shared_landing_duplicates_deduplicated=len(expected)-len(platforms),
  geometry_sha256=digest({k:c['case'][k]for k in ['platforms','one_way_platform_indices','saws','moving_platforms','latches']}),
  scope='Exact source/shape/static-envelope audit; not actual physical traversal or fun')
