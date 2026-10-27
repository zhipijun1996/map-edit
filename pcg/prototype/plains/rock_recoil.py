"""Rock-bank adaptation of verified open landforms, not a room-floor grammar.

Every collider is Module owned. Travel has no decorative latch gates: shot recoil
must earn real height/distance. Bells protect the two sealed reward chambers.
"""
import copy
from .synthesis import command
from ..factory.core.quality import digest

def adapt(source,spec):
 m=copy.deepcopy(source);m['spec']=copy.deepcopy(spec);m.pop('canonical_document',None)
 c=m['case'];key=m['id'];dx,dy=spec['placement']
 def rock(x,y,w,h):
  c['platforms'].append([x-dx,y-dy,w,h]);return len(c['platforms'])-1
 def target(x,y,label,support):
  return dict(id=key+'/'+label,position=[x-dx,y-dy],region=[x-dx-8,y-dy-4,16,8],support_indices=[support],grounded=True)
 def module(plan,dest):return dict(kind='module',target=dest,control_plan=copy.deepcopy(plan),budget_ticks=720)
 if key in ['west','ridge']:
  # These doors could be avoided by taking the deliberate lower route. Remove
  # the misleading gate/bell pair; keep the real recoil crossing itself.
  c['latches']=[]
  idx=m['core']['exit']['support_indices'][0];p=c['platforms'][idx]
  if key=='west':
   c['platforms'][idx]=[150-dx,658-dy,80,90]
   old=m['core']['exit']['position'][0];new=176-dx
   def patch(v):
    if isinstance(v,dict):
     if v.get('position')==[old,640-dy]:v.update(position=[new,640-dy],region=[new-8,636-dy,16,8])
     if v.get('target_x')==old:v['target_x']=new
     for item in v.values():patch(item)
    elif isinstance(v,list):
     for item in v:patch(item)
   patch(m['core']);patch(m['center_to_port']);patch(m['port_to_center'])
   # No return shot is required to open a travel door that no longer exists.
   m['port_to_center']['e0']=m['port_to_center']['e0'][1:]
   for leg in m['port_to_center']['e0']:
    if leg['target']['position']==[160-dx,640-dy]:leg['target']=target(176,640,'receiver',idx)
  else:
   c['platforms'][idx]=[p[0],p[1],p[2],80]
  c['one_way_platform_indices'].remove(idx)
 if key=='ridge':
  rock(460,750,110,100);rock(570,750,80,70)
 if key=='lookout':
  rock(920,580,180,180);rock(960,760,128,160);rock(1000,920,80,40)
 if key=='arch':
  rock(1655.317182305169,394,64.682817694831,120);rock(1690,514,50,44)
  # Direct main crosses the bridge. The upper chime/recoil chamber is a true
  # optional excursion from the hub, with its own explicit return program.
  old=copy.deepcopy(m['port_to_center']['e2'])
  m['port_to_center']['e2']=[dict(kind='walk',target=target(1440,520,'bridge-takeoff',m['core']['entry']['support_indices'][0])),dict(kind='jump',target=m['center'],hold_ticks=12)]
  m['core_visit_program']=copy.deepcopy(m['center_to_port']['e2'])+old
 if key=='bell':
  c['moving_platforms']=[]
  c['latches']=[v for v in c['latches']if v['id']!='parking-bell']
  for latch in c['latches']:
   latch.pop('starts_ferry',None);latch.pop('ferry_id',None)
  first=rock(1460,878,100,50);second=rock(1280,698,120,80)
  a=target(1500,860,'recoil-bank-1',first);b=target(1350,680,'recoil-bank-2',second)
  def recoil(t,axis):
   return module([command('axis',value=axis),command('jump'),command('jump_release',12),command('shoot',6,direction=[-.5*axis,.8660254037844386]),command('settle',6,target_x=t['position'][0],deadband=4)],t)
  dock=m['ports']['e7']['dock']
  m['center_to_port']['e7']=[m['center_to_port']['e7'][0],recoil(a,1),recoil(b,-1),recoil(copy.deepcopy(dock),1)]
 if key=='bell':
  before=c['platforms'];old_one=set(c['one_way_platform_indices']);after=[];mapping={};new_one=[]
  for i,p in enumerate(before):
   x,y,w,h=p;wx=x+dx;wy=y+dy;pieces=[p]
   if wy>=1058:
    pieces=[]
    if wx<1330:pieces.append([x,y,min(wx+w,1330)-wx,h])
    if wx+w>1510:pieces.append([max(wx,1510)-dx,y,wx+w-max(wx,1510),h])
   mapping[i]=[]
   for rect in pieces:
    if rect[2]<=0:continue
    mapping[i].append(len(after))
    if i in old_one:new_one.append(len(after))
    after.append(rect)
  m['center_to_port']['e6']=[];m['port_to_center']['e6']=[];m['port_to_center']['e7']=[]
  seen=set()
  def remap(v):
   if isinstance(v,dict):
    if id(v)in seen:return
    seen.add(id(v))
    if 'support_indices'in v:
     indices=[j for i in v['support_indices']for j in mapping[i]]
     x,y=v['position'];v['support_indices']=[j for j in indices if after[j][0]+12<=x<=after[j][0]+after[j][2]-12 and abs(after[j][1]-(y+18))<.01]
     if not v['support_indices']:raise ValueError('rock_canyon_invalidated_target/'+str(v.get('id')))
    if 'shared_landing_index'in v:v['shared_landing_index']=mapping[v['shared_landing_index']][0]
    for value in v.values():remap(value)
   elif isinstance(v,list):
    for value in v:remap(value)
  for group in ['ports','center','core','center_to_port','port_to_center','core_visit_program']:remap(m[group])
  remap(c['reward_sites'])
  c['platforms']=after;c['one_way_platform_indices']=new_one
  def ground(x,y,label):
   support=[i for i,p in enumerate(after)if abs(p[1]+dy-(y+18))<.01 and p[0]+dx+12<=x<=p[0]+dx+p[2]-12]
   if not support:raise ValueError('rock_canyon_missing_landing/'+label)
   t=target(x,y,label,support[0]);t['support_indices']=support;return t
  left=ground(1316,1040,'canyon-west-bank');right=ground(1526,1040,'canyon-east-bank')
  def cross(dest,direction):
   return module([command('axis',value=direction),command('jump'),command('jump_release',8),command('shoot',2,direction=[-direction,0]),command('settle',6,target_x=dest['position'][0],deadband=4)],dest)
  m['center_to_port']['e6']=[dict(kind='walk',target=left),cross(right,1),dict(kind='walk',target=m['ports']['e6']['dock'])]
  m['port_to_center']['e6']=[dict(kind='walk',target=right),cross(left,-1),dict(kind='walk',target=m['center'])]
  # Fast descent lands outside the recoil banks; return crosses the same
  # canyon in the opposite direction with the actual remaining state.
  m['port_to_center']['e7']=[dict(kind='drop',target=m['ports']['e6']['dock']),dict(kind='walk',target=right),cross(left,-1),dict(kind='walk',target=m['center'])]
 if key=='arch':
  # Lower bridge: walk under the high gear phase; on return, jump while the
  # same original gear is low. Waiting concerns a hazard window, not a lift.
  def gear_wait():return dict(op='wait',trigger=dict(dynamic=dict(kind='saw_phase',id='bridge-gear',window=[.20,.25]),timeout=190))
  dest=m['ports']['e3']['dock']
  m['center_to_port']['e3']=[module([command('axis',value=0),gear_wait(),command('settle',target_x=dest['position'][0],deadband=4)],dest)]
  approach=target(1672,600,'under-rock-takeoff',m['ports']['e3']['dock']['support_indices'][0])
  m['port_to_center']['e3']=[module([command('axis',value=0),gear_wait(),command('settle',target_x=approach['position'][0],deadband=3)],approach),module([command('axis',value=0),dict(op='wait',trigger=dict(dynamic=dict(kind='saw_phase',id='bridge-gear',window=[.60,.65]),timeout=190))],approach),dict(kind='jump',target=m['center'],hold_ticks=12)]
 if key=='relay':
  rock(2400,848,150,150);rock(2550,1078,230,130);rock(2780,1078,320,80)
 m['origin']='Map demand: exposed rock banks, recoil ascent, optional sealed treasure and separate fast descent; verified source adapted, never inherited pass'
 m['content_version']='sha256:'+digest({k:m[k]for k in ['case','ports','core','boundary_gates']})
 return m
