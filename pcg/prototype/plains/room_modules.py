"""Demand-driven direct-contact Macro rooms, using original Plains Cells.

Geometry is completely created here, before Map assembly. The Map cannot append
platforms or navigation stairs. Large continuous floors, timed carriers and
existing recoil/bell challenges are independent room content, not inter-room fill.
"""
import copy,heapq,json
from pathlib import Path
from .synthesis import command
from .three_port import gear_cross
from ..factory.core.quality import digest
ROOT=Path(__file__).resolve().parents[2]


def generate(spec):
 key=spec['node_id'];W,H=spec['space']['core_bounds'][2:];base=H-spec.get('floor_margin',64)
 ports={p['id']:copy.deepcopy(p)for p in spec['ports']}
 platforms=[];one_way=[];saws=[];latches=[];carriers=[];floors={};columns=[]
 def platform(rect,one=False):
  i=len(platforms);platforms.append(rect)
  if one:one_way.append(i)
  return i
 def target(x,y,supports,label,width=128):
  return dict(id=key+'/'+label,position=[float(x),float(y)],region=[x-10,y-5,20,10],support_indices=supports,
              support_width=width,grounded=True)
 for p in ports.values():
  if p['kind']=='vertical'and p['normal'][1]<0:
   columns.append(dict(id='lift-'+p['id'],x=p['column_x'],level=0,port=p['id'],bearing=p['bearing']))
 galleries={p['position'][1]for p in ports.values()if p['kind']=='side'and p['position'][1]!=base}
 gallery_counts={-1:0,1:0}
 for level in sorted(galleries,reverse=True):
  relevant=[p for p in ports.values()if p['kind']=='side'and p['position'][1]==level]
  sides={p['normal'][0]for p in relevant}
  x=128+256*gallery_counts[-1] if sides=={-1}else W-128-256*gallery_counts[1] if sides=={1}else W/2
  if len(sides)==1:gallery_counts[next(iter(sides))]+=1
  columns.append(dict(id='lift-gallery-'+str(level),x=x,level=level,port=None,bearing=-1 if sides=={-1}else 1))
 if any(abs(a['x']-b['x'])<256 for i,a in enumerate(columns)for b in columns[i+1:]):raise ValueError('room_generator_column_clearance/'+key)
 def slices(level):
  spans=[(0,W)]
  # Only carriers whose real envelope crosses this floor need a shaft cut.
  for c in columns:
   if c['level']>level:continue
   new=[]
   for lo,hi in spans:
    if hi<=c['x']-80 or lo>=c['x']+80:new.append((lo,hi));continue
    if lo<c['x']-80:new.append((lo,c['x']-80))
    if hi>c['x']+80:new.append((c['x']+80,hi))
   spans=new
  return spans
 for level in [base,*sorted(galleries)]:
  floors[level]=[]
  for lo,hi in slices(level):
   if hi-lo<40:raise ValueError('module_would_need_tiny_navigation_pad/'+key)
   index=platform([lo,level+18,hi-lo,16 if level==base else 32],True)
   floors[level].append((lo,hi,index))
 def floor_target(x,level,label):
  candidates=[(lo,hi,i)for lo,hi,i in floors[level]if lo+12<=x<=hi-12]
  if not candidates:raise ValueError('no_actual_module_support/'+key+'/'+label+'/'+str((x,level)))
  lo,hi,i=candidates[0];return target(x,level,[i],label,hi-lo)
 for c in columns:
  # The carrier stops 16wu below the static destination. The final original
  # jump transfers onto a stationary landing; actor motion is never assigned.
  c['definition']=dict(platform_id=c['id'],start=[c['x'],base+18+12],finish=[c['x'],c['level']+18+12+16],
       size=[128,24],travel_duration=2.4,dwell_duration=1.2,initial_phase=0.)
  carriers.append(c['definition'])
  c['left']=floor_target(c['x']-96,base,c['id']+'/base-left')
  c['right']=floor_target(c['x']+96,base,c['id']+'/base-right')
 for p in ports.values():
  x,y=p['position']
  if p['kind']=='vertical':
   cx=p['column_x'];index=platform([cx-80,y+18,160,16],True)
   p['dock']=target(x,y,[index],'port/'+p['id'],160);p['shared_landing_index']=index
  else:p['dock']=floor_target(32 if p['normal'][0]<0 else W-32,y,'dock/'+p['id'])
 # Portals are cut in the Module's own walls, never patched by the Map.
 def boundary(side,length,holes):
  spans=[(0,length)]
  for lo,hi in sorted(holes):
   result=[]
   for a,b in spans:
    if b<=lo or a>=hi:result.append((a,b));continue
    if a<lo:result.append((a,lo))
    if b>hi:result.append((hi,b))
   spans=result
  for lo,hi in spans:
   if hi<=lo:continue
   rect={'left':[0,lo,16,hi-lo],'right':[W-16,lo,16,hi-lo],
         'top':[lo,0,hi-lo,16],'bottom':[lo,H-16,hi-lo,16]}[side]
   platform(rect)
 for side in ([] if spec.get('boundary_policy')=='open' else ['left','right','top','bottom']):
  relevant=[p for p in ports.values()if (side=='left'and p['normal']==[-1,0])or(side=='right'and p['normal']==[1,0])or(side=='top'and p['normal']==[0,-1])or(side=='bottom'and p['normal']==[0,1])]
  holes=[(p['position'][1]-96,p['position'][1]+40)if side in ['left','right']else(p['column_x']-96,p['column_x']+96)for p in relevant]
  boundary(side,H if side in ['left','right']else W,holes)
 # Reuse the measured latest-main fork core on selected roles. It becomes an
 # explicit L2 child of this newly validated Macro, no old pass is inherited.
 core=None
 if spec.get('include_optional_core',True) and key in {'r5','r10','r14','r12','r7','r6'}:
  free=slices(base);slot=next(((a,b)for a,b in free if b-a>=600),None)
  if slot:
   source=ROOT/'results/plains-three-port-production-v1/review_cases.json'
   old=json.loads(source.read_text())['cases'][0];dx=slot[0]+136;dy=base-420
   upper=old['platforms'][1];pi=platform([upper[0]+dx,upper[1]+dy,*upper[2:]])
   for raw in old['saws']:
    saw=copy.deepcopy(raw);saw['origin']=[raw['origin'][0]+dx,raw['origin'][1]+dy];saw['source_id']='core-gear';saw['initial_phase']=0.;saws.append(saw)
   for raw in old['latches']:
    value=copy.deepcopy(raw);value['id']='core-bell';value['bell']=[raw['bell'][0]+dx,raw['bell'][1]+dy];value['gate']=[raw['gate'][0]+dx,raw['gate'][1]+dy,*raw['gate'][2:]];latches.append(value)
   # Same A→C measured input; the enclosing Macro is always tested afresh.
   upper_case=next(c for c in json.loads(source.read_text())['cases']if c.get('route_spec',{}).get('id')=='upper')
   plan=copy.deepcopy(upper_case['control_plan'])
   for op in plan:
    if 'target_x'in op:op['target_x']+=dx
   core=dict(source=str(source.relative_to(ROOT)),source_geometry='same recoil/bell/receiver; room floor and boundary are a new Macro version',
     entry=floor_target(80+dx,base,'core/entry'),exit=target(old['ports'][2]['position'][0]+dx,old['ports'][2]['position'][1]+dy,[pi],'core/reward',192),
     control_plan=plan)
 if spec.get('include_optional_core',True) and core is None and not any(base-230 < level < base-20 for level in galleries):
  slot=next(((a,b)for a,b in slices(base)if b-a>=240),None)
  selected=ROOT/'results/direct-vertical-bell-v2/selected.json'
  if slot and selected.exists() and H>=384:
   old=json.loads(selected.read_text())['case'];dx=slot[0]+16;dy=base-420
   upper=old['platforms'][1];pi=platform([upper[0]+dx,upper[1]+dy,*upper[2:]],True)
   for raw in old['latches']:
    value=copy.deepcopy(raw);value['id']='core-bell';value['bell']=[raw['bell'][0]+dx,raw['bell'][1]+dy];value['gate']=[raw['gate'][0]+dx,raw['gate'][1]+dy,*raw['gate'][2:]];latches.append(value)
   plan=copy.deepcopy(old['control_plan'])
   for op in plan:
    if 'target_x'in op:op['target_x']+=dx
   core=dict(source=str(selected.relative_to(ROOT)),source_geometry='measured vertical recoil180 + bell; new enclosing Macro always revalidated',
    entry=floor_target(old['entry_port'][0]+dx,base,'core/entry'),exit=target(old['exit_port'][0]+dx,old['exit_port'][1]+dy,[pi],'core/reward',192),control_plan=plan)
 if not saws and key in {'r0','r3','r4','r9','r11','r15','r17','exp0_1','exp1_0','exp1_1'}:
  slot=max(slices(base),key=lambda p:p[1]-p[0])
  if slot[1]-slot[0]>=260:saws=[dict(source_id='gallery-gear',origin=[(slot[0]+slot[1])/2,base-12],travel=[0,-115],radius=16,period=2.4,initial_phase=0.)]
 # Dynamic envelopes must remain in this Module and clear vertical seams.
 # The old fork gear swept 55wu into the next room; it cannot be reused there.
 for saw in saws:
  saw['travel']=[0,-40]
  excluded=[p['column_x'] for p in ports.values()if p['kind']=='vertical']
  safe=[x for lo,hi in slices(base)for x in range(int(lo+96),int(hi-95),32)
        if all(abs(x-c)>=144 for c in excluded)]
  if not safe:
   saw['omit_due_to_port_clearance']=True;continue
  saw['origin'][0]=min(safe,key=lambda x:abs(x-saw['origin'][0]))
 saws[:]=[s for s in saws if not s.get('omit_due_to_port_clearance')]
 left=next((a,b,i)for a,b,i in floors[base]if b-a>=48)
 center_x=left[0]+min(64,(left[1]-left[0])/2)
 if left[0]==0:center_x=max(32,center_x)
 center=floor_target(center_x,base,'center')
 case=dict(id='module-'+key,family='plains_direct_room_macro',capabilities=['move','jump','shot_recoil'],platforms=platforms,
    one_way_platform_indices=one_way,wall_platform_indices=[],world_bounds=[-24,-96,W+48,H+240],spawn=center['position'],entry_port=center['position'],
    exit_port=[center['position'][0]+32,base],goal=[center['position'][0]+20,base-5,24,10],control_plan=[],max_frames=3600,
    trace_all=False,hazards=[],thorns=[],saws=saws,moving_platforms=carriers,latches=latches,hooks=[],enemies=[])
 module=dict(schema='pcg/direct-room-module-payload/v1',id=key,spec=copy.deepcopy(spec),case=case,ports=ports,
   center=center,columns=columns,floors=floors,core=core,assembly_created_geometry=False,
   quality={'human_fun':'unverified','production_admitted':False},origin='existing Plains cells + measured fork child, generated before placement')
 module['boundary_gates']=[]
 for need in spec.get('boundary_gate_requirements',[]):
  p=ports[need['edge_id']];x,y=p['position']
  bounds=[x-5,y-64,10,82]if p['kind']=='side'else[p['column_x']-96,y+(40 if p['normal'][1]<0 else -29),192,10]
  module['boundary_gates'].append(dict(id='gate/'+need['edge_id'],edge_id=need['edge_id'],bounds=bounds,
   direction=p['normal'],switch=need['switch'],one_way=need['one_way'],owner_module=key,
   source='module-generated boundary gate',from_module=key,to_module=need['peer']))
 module['content_version']='sha256:'+digest({k:module[k]for k in ['case','ports','core','boundary_gates']})
 return module


def routes(module):
 """Build input policies over the Module's existing landforms, never geometry."""
 base=module['spec']['space']['core_bounds'][3]-module['spec'].get('floor_margin',64);cols=module['columns'];case=module['case'];floors=module['floors']
 def target_at(x,y,label):
  for lo,hi,i in floors[y]:
   if lo+12<=x<=hi-12:return dict(id=module['id']+'/'+label,position=[x,y],region=[x-10,y-5,20,10],support_indices=[i],grounded=True)
  raise ValueError('route_has_no_module_owned_landing/'+module['id']+'/'+str((x,y)))
 def walk(a,b):
  if a['position']==b['position']:return []
  result=dict(kind='walk',target=copy.deepcopy(b))
  if a['position'][1]==base==b['position'][1]:
   saw=next((s for s in case['saws']if min(a['position'][0],b['position'][0])<s['origin'][0]<max(a['position'][0],b['position'][0])),None)
   if saw:
    d=1 if b['position'][0]>a['position'][0]else-1
    plan=gear_cross(b['position'][0],saw['origin'][0],d)
    for op in plan:
     q=op.get('trigger',{}).get('dynamic',{})
     if q.get('kind')=='saw_phase':q['id']=saw['source_id']
    result.update(kind='module',control_plan=plan,budget_ticks=720)
  return [result]
 def carrier(c,target,level,mode,bearing):
  return dict(kind='module',target=copy.deepcopy(target),control_plan=[command('wait')],budget_ticks=1000,
   carrier_transfer={'id':c['id'],'mode':mode,'source_level':level,'destination_level':target['position'][1],
                      'bearing':bearing,'target_x':target['position'][0]})
 def along(a,b,level):
  result=[];x=a['position'][0];d=1 if b['position'][0]>x else-1
  current=a
  for c in sorted(cols,key=lambda c:c['x'],reverse=d<0):
   if c['level']>level or not min(x,b['position'][0])<c['x']<max(x,b['position'][0]):continue
   serving=level in [base,c['level']]
   if not serving and module['spec'].get('boundary_policy')!='open':raise ValueError('gallery_requires_crossing_nonserving_shaft/'+module['id'])
   take=target_at(c['x']-d*96,level,'board/'+c['id']+'/'+str(d));end=target_at(c['x']+d*96,level,'cross/'+c['id']+'/'+str(d))
   result+=walk(current,take)
   result.append(carrier(c,end,level,'cross',d) if serving else dict(kind='jump',target=end,hold_ticks=20))
   current=end
  result+=walk(current,b);return result
 outbound={};inbound={};center=module['center']
 for eid,p in module['ports'].items():
  dock=p['dock'];y=dock['position'][1]
  if p['kind']=='side'and y==base:
   outbound[eid]=along(center,dock,base);inbound[eid]=along(dock,center,base)
  elif p['kind']=='vertical'and p['normal'][1]>0:
   options=[min(max(dock['position'][0],lo+24),hi-24)for lo,hi,_ in floors[base]if hi-lo>=48]
   safe=target_at(min(options,key=lambda x:abs(x-dock['position'][0])),base,'bottom-approach/'+eid)
   outbound[eid]=along(center,safe,base)+[dict(kind='drop',target=dock)]
   inbound[eid]=[dict(kind='jump',target=safe,hold_ticks=12)]+along(safe,center,base)
  else:
   c=next(c for c in cols if c['port']==eid)if p['kind']=='vertical'else next(c for c in cols if c['port']is None and c['level']==y)
   bearing=p['bearing']if p['kind']=='vertical'else p['normal'][0]
   landing=dock if p['kind']=='vertical'else target_at(c['x']+bearing*96,y,'gallery-exit/'+eid)
   approach=c['right']if bearing>0 else c['left']
   outbound[eid]=along(center,approach,base)+[carrier(c,landing,base,'ascend',bearing)]
   if p['kind']=='side':outbound[eid]+=along(landing,dock,y)
   drop_start=dock
   return_x=c['x']+bearing*96
   safe=target_at(return_x,base,'descending-return/'+eid)
   # A drop input steers away from the carrier and reissues only on real
   # one-way intermediate landings, never resetting or moving the actor.
   inbound[eid]=([*along(dock,landing,y)]if p['kind']=='side'else[])+[dict(kind='drop',target=safe)]+along(safe,center,base)
 module['center_to_port']=outbound;module['port_to_center']=inbound
 # Optional measured action remains inside the Module. Returning uses the
 # same phase-aware floor policies as the actual exported ports.
 module['core_visit_program']=[]
 core=module.get('core')
 if core and all(i in case['one_way_platform_indices']for i in core['exit']['support_indices']):
  safe=target_at(core['exit']['position'][0],base,'core/returned')
  module['core_visit_program']=along(center,core['entry'],base)+[
   dict(kind='module',target=copy.deepcopy(core['exit']),control_plan=copy.deepcopy(core['control_plan']),budget_ticks=720),
   dict(kind='drop',target=safe)]+along(safe,center,base)
 return module
