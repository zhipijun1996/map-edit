import copy,inspect,sys
from pcg.migration import core,physics,godot_package
from pcg.prototype.workshop.rules import cmd
from . import prepare_ideas_v1 as base
from .continue_revision059_v1 import rows,label,AUTH
from .revision059_hq_content_v1 import decode
from .prepare_review045_v1 import at,end,axis
from .prepare_revision058_v2 import jump
CURRENT=None

def dock(p):
 d=core.read(CURRENT['designFile']);o=next(o for o in d['visualObjects']if o['id']==p['supportObjectId']);return[p['position'][0]-p['normal'][0]*24,o['y']-18]
def enrich(d):
 d=base.enrich(d)
 for route in d['intendedRoutes']:
  if route['role']=='reward_return':route['role']='reward'
 for o in d['visualObjects']:
  if o.get('designMotion'):
   v=o['designMotion'];o.update(duration=v.get('period',v.get('travel_duration')),dwell=v.get('dwell_duration',0),initialPhase=v['initial_phase'])
  if o['id']=='timed-gate':o['mechanics'].update(kind='timed_gate',openSeconds=4.)
  if o['type']in ['triggerZone','hitTurret']:o.setdefault('mechanics',{})['approvedCellType']=o['type'];o['type']='switch'
  if o['id']=='turret-target-bell':o.update(targetId='timed-gate',sourceId=o['id'])
  if o['id']=='return-bell':o.update(targetId='timed-gate',sourceId='turret-target-bell/return');o['mechanics']=dict(returnSideOnly=True)
 return d

def supported(p,timeout=360):return dict(op='wait',carrier=p,trigger=dict(after=1,state='carrier_supported',timeout=timeout))
def follow(p,offset=0):return dict(op='settle',target_x=0,revision_follow=p,carrier_offset=offset,deadband=.6,source_native_gain=5.5,trigger=dict(after=0))
def wait(state,**kw):return dict(op='wait',trigger=dict(after=1,state=state,timeout=1800),**kw)
def aim(x,y,after=4):return dict(op='shoot',native_aim_point=[x,y],trigger=dict(after=after))
def plan_for(n,t,source,d):
 a,z=t['from'],t['to'];goal=dock(next(p for p in d['ports']if p['id']==z));lab=label(CURRENT)
 if lab=='hq01':
  if a=='L':p=at(96,334)+jump(256,1)+[cmd('shoot',4,direction=[-.65,.7599342077]),supported('P'),follow('P'),wait('hq_group_park_window'),aim(136,368),supported('P')]+jump(368)+[supported('Q')]
  elif a=='R':p=at(556,78)+jump(368,8)+[supported('Q')]
  else:p=[cmd('drop_through',1),base.settle(368),supported('Q')]
  if z=='R':p+=jump(616,24,[-1,0])
  elif z=='T':p+=jump(192,24,[.6,.8])
  else:p+=jump(24,8)
 elif lab=='hq02':
  if a=='B':p=[wait('hq_board'),base.settle(224),cmd('jump'),cmd('jump_release',8),supported('P'),follow('P',-24),wait('hq_upper')]+jump(64,24)
  else:p=[cmd('drop_through',1),base.settle(288)]
 elif lab=='hq04':
  p=at(90,334)+jump(216)+at(216,286)+at(248,286)+[wait('hq_saw_low')]+jump(576,24,[-.95,.3122498999])+at(576,126)+[cmd('drop_through',1),base.settle(512)]+at(512,366)+at(480,366)+[wait('hq_saw_high')]+jump(432,1)+[dict(op='wait',height_threshold=350,trigger=dict(after=1,state='descending_height',timeout=120)),cmd('shoot',1,direction=[.98,.1989974874]),base.settle(288)]+at(288,398)+at(240,398)+jump(24)
 else:
  if a=='L':p=at(90,206)+jump(336,24,[-1,0])+at(336,270)+[axis(0),cmd('jump'),cmd('jump_release',4),aim(280,256,4),base.settle(448)]+at(448,190)+jump(448,8,[0,1])
  else:p=[cmd('shoot',1,direction=[0,1]),cmd('wait',20),cmd('drop_through',1),base.settle(336)]+at(336,270)+at(270,270)+jump(24)
 return p+end(*goal),source[0]
def prepare(row):
 global CURRENT
 CURRENT=row;s=inspect.getsource(base.prepare).replace('pcg/manual_review/ideas_author_v1.py','pcg/manual_review/revision059_hq_author_v1.py');ns={**base.__dict__,'AUTH':AUTH,'label':label,'decode':decode,'dock':dock,'enrich':enrich,'plan_for':plan_for};exec(compile(s,__file__,'exec'),ns);ns['prepare'](row)
 f=core.REPO/row['outputDirectory'];d=core.read(f/'module.mapnote.json');cs=core.read(f/'cases.json')['cases']
 for c in cs:
  c['id']='approved-r059-'+label(row)+'-'+c['route_spec']['id'];c['max_frames']=3600;c['generation_rule']['registration_source']='pcg/manual_review/revision059_hq_author_v1.py'
  if label(row)=='hq04':c.update(required_rewards=['reward'],expected_reward=4)
 core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(d,cs));core.contract(f/'module.mapnote.json',refresh=True)
if __name__=='__main__':
 for r in rows():
  if label(r)in sys.argv[1:]:prepare(r)
