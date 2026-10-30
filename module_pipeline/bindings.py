"""Declarative native-data bindings to authoritative Mapnote objects.

This is a data compiler, not a physics model. Imported parameter recipes are
checked against the existing native compiler before any old source is removed.
"""
import copy,math
PHYSICAL_KEYS={'position','bell','access','return_access','additional_pair_access','gate','paired_gate','rect','region','origin','start','finish','muzzle','sequence_gate','spawn','trigger','ellipse_center','points','loop_points','bands','hazards'}
META={'schema','source_sha256','stable_id','ports','world_bounds','entry_port','exit_port'}
def center(o):return[o['x']+o['w']/2,o['y']+o['h']/2]
def rect(o):return[o[k]for k in ['x','y','w','h']]
def equal(a,b):
 if isinstance(a,(int,float))and not isinstance(a,bool)and isinstance(b,(int,float)):return abs(a-b)<1e-7
 if isinstance(a,list)and isinstance(b,list):return len(a)==len(b)and all(equal(x,y)for x,y in zip(a,b))
 if isinstance(a,dict)and isinstance(b,dict):return a.keys()==b.keys()and all(equal(a[k],b[k])for k in a)
 return a==b
def evaluate(value,doc):
 objects={o['id']:o for o in doc['objects']}
 def visit(v):
  if isinstance(v,list):return[visit(x)for x in v]
  if not isinstance(v,dict):return copy.deepcopy(v)
  op=v.get('$bind')
  if op:
   o=objects[v['object']]
   if op=='rect':return rect(o)
   if op=='center':return center(o)
   if op=='size':return[o['w'],o['h']]
   if op=='field':
    result=o
    for key in v['path']:result=result[key]
    return copy.deepcopy(result)
   if op=='points':return[[p['x'],p['y']]for p in o['points']]
   if op=='relative_point':return[a+b for a,b in zip(center(o),v['offset'])]
   if op=='relative_rect':return[o['x']+v['offset'][0],o['y']+v['offset'][1],o['w']+v['sizeDelta'][0],o['h']+v['sizeDelta'][1]]
   if op=='thorn':
    host=objects[o['hostId']];face=v['metric']
    if face=='start_offset':return o['x']-host['x']if v['face']in ['top','bottom']else o['y']-host['y']
    if face=='length':return o['w']if v['face']in ['top','bottom']else o['h']
    if face=='depth':return o['h']if v['face']in ['top','bottom']else o['w']
   raise ValueError('unknown_binding_operator:'+str(op))
  return{k:visit(x)for k,x in v.items()}
 return visit(value)
def recipe_for(doc,content):
 objects=doc['objects'];byid={o['id']:o for o in objects}
 def resolve(identifier):
  if identifier in byid:return byid[identifier]
  return next((o for o in objects if o.get('sourceId')==identifier),None)
 def props(o):
  if o is None:return[]
  values=[]
  for path in [[],['mechanics'],['mechanics','runtimeParameters'],['mechanics','source']]:
   item=o
   try:
    for k in path:item=item[k]
   except (KeyError,TypeError):continue
   if isinstance(item,dict):values.extend((o['id'],path+[k],k,v)for k,v in item.items())
  if o.get('trackId')in byid:values+=props(byid[o['trackId']])
  if isinstance(o.get('designMotion'),dict):values.extend((o['id'],['designMotion',k],k,v)for k,v in o['designMotion'].items())
  return values
 def bind(v,path,hint=None):
  key=str(path[-1])if path else''
  if isinstance(v,dict):
   ident=v.get('id',v.get('source_id',v.get('platform_id')));hint=resolve(ident)or hint
   return{k:bind(x,path+[k],hint)for k,x in v.items()}
  if isinstance(v,list):
   if path and path[0]=='platforms'and len(path)==2:
    o=next((o for o in objects if o.get('sourceIndex')==path[-1]and o['type']in ['terrain','platform']and not o.get('trackId')),None)
    if o is None:o=next(o for o in objects if equal(rect(o),v)and o['type']not in ['route','entry','exit','note','trackLine','trackArc'])
    return{'$bind':'rect','object':o['id']}
   if key=='size'and hint and equal(v,[hint['w'],hint['h']]):return{'$bind':'size','object':hint['id']}
   for oid,p,k,value in props(hint):
    if k==key and equal(v,value):return{'$bind':'field','object':oid,'path':p}
   if key=='loop_points'and hint and hint.get('trackId')in byid:
    track=byid[hint['trackId']]
    if equal(v,[[p['x'],p['y']]for p in track.get('points',[])]):return{'$bind':'points','object':track['id']}
   spatial=key in PHYSICAL_KEYS or(len(path)>=2 and str(path[-2])in ['access','hazards','bands','platforms'])
   if spatial and len(v)in [2,4]and all(isinstance(x,(int,float))for x in v):
    candidates=([hint]if hint else[])+[o for o in objects if o is not hint and o['type']not in ['route','entry','exit','note','anchor','trackLine','trackArc']]
    # Prefer exact referenced Cell geometry. Relative offsets express native
    # receiver regions without another absolute geometry source.
    for o in candidates:
     if len(v)==4 and equal(v,rect(o)):return{'$bind':'rect','object':o['id']}
     if len(v)==2 and equal(v,center(o)):return{'$bind':'center','object':o['id']}
    if candidates:
     o=hint or min(candidates,key=lambda o:math.dist(v[:2],center(o)))
     if len(v)==2:return{'$bind':'relative_point','object':o['id'],'offset':[v[i]-center(o)[i]for i in range(2)]}
     return{'$bind':'relative_rect','object':o['id'],'offset':[v[0]-o['x'],v[1]-o['y']],'sizeDelta':[v[2]-o['w'],v[3]-o['h']]}
   return[bind(x,path+[i],hint)for i,x in enumerate(v)]
  if hint is not None:
   aliases={'travel_duration':['travel_duration','duration'],'dwell_duration':['dwell_duration','dwell'],'initial_phase':['initial_phase','initialPhase'],'period':['period','duration'],'ellipse_period':['ellipse_period','period','duration']}.get(key,[key])
   for oid,p,k,value in props(hint):
    if k in aliases and equal(v,value):return{'$bind':'field','object':oid,'path':p}
   if key in ['start_offset','length','depth']and hint.get('hostId')and path[0]=='thorns':
    host=byid[hint['hostId']];face='top'if abs(hint['y']+hint['h']-host['y'])<1e-5 else'bottom'if abs(hint['y']-host['y']-host['h'])<1e-5 else'left'if abs(hint['x']+hint['w']-host['x'])<1e-5 else'right'
    return{'$bind':'thorn','object':hint['id'],'metric':key,'face':face}
  return copy.deepcopy(v)
 result={k:bind(v,[k])for k,v in content.items()if k not in META}
 if not equal(evaluate(result,doc),{k:v for k,v in content.items()if k not in META}):raise ValueError('native_binding_roundtrip_mismatch:'+doc['id'])
 return result
