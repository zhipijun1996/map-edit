import copy,inspect
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from . import prepare_ideas_v1 as base
from .continue_revision061_v1 import rows,label,AUTH
from .revision061_content_v1 import decode
from .prepare_revision060_v1 import wait,follow,supported,aim
from .prepare_review045_v1 import at,end,axis
from .prepare_revision058_v2 import jump
from .prepare_ideas_v1 import settle
CURRENT=None
def dock(p):
 d=core.read(CURRENT['designFile']);o=next(o for o in d['visualObjects']if o['id']==p['supportObjectId']);return[p['position'][0]-p['normal'][0]*24,o['y']-18]
def enrich(d):
 d=base.enrich(d);obs={o['id']:o for o in d['visualObjects']}
 for o in d['visualObjects']:
  if o.get('designMotion')and 'initial_phase'in o['designMotion']:
   m=o['designMotion'];o.update(duration=m.get('period',m.get('travel_duration')),dwell=m.get('dwell_duration',0),initialPhase=m['initial_phase'])
 if label(CURRENT)=='s11':
  obs['orbit-rail']['designMotion'].update(period=8.,initial_phase=0.,trajectory_kind='clockwise_ellipse/v1');obs['orbit-rail'].update(duration=8.,dwell=0.,initialPhase=0.)
 if label(CURRENT)=='s07':
  for k in ['step-A','step-B','swap-bell']:obs[k].setdefault('mechanics',{}).update(kind='complementary_gates',initialOpen='B',gateA='step-A',gateB='step-B')
  obs['swap-bell'].update(targetId='step-A',sourceId='swap-bell');obs['return-access'].update(targetId='step-A',sourceId='swap-bell/return',mechanics=dict(returnSideOnly=True))
 return d
def ring(id,running):return dict(op='shoot',group_id=id+'-bell',running=running,trigger=dict(after=1,state='r061_ring_ready',timeout=600))
def state(id,running):return wait('r061_running',group_id=id+'-bell',running=running)
def step(x,y,hold=24,shot=None):return jump(x,hold,shot)+at(x,y)
def plan_for(n,t,source,d):
 n=label(CURRENT);a,z=t['from'],t['to'];goal=dock(next(p for p in d['ports']if p['id']==z))
 if n=='s02':
  if a=='B':p=at(304,590)+step(288,446)+step(80,318,24,[.94,.341174442])+step(288,190,24,[-.94,.341174442])+step(64,62,24,[.94,.341174442])+step(64,14,16)
  else:p=[axis(0),cmd('drop_through',1),settle(64)]+at(64,62)+[cmd('drop_through',1),settle(288)]+at(288,190)+[cmd('drop_through',1),settle(80)]+at(80,318)+[cmd('drop_through',1),settle(288)]+at(288,446)+[cmd('drop_through',1),settle(320)]
 elif n=='s07':
  if a=='L':p=at(90,206)+step(248,238,16)+jump(376,16)+[aim(160,272)]+at(376,126)+step(448,14,24)
  else:p=[axis(0),aim(464,64),cmd('wait',20),cmd('drop_through',1),settle(376)]+at(376,126)+jump(248,8)+[aim(464,64)]+at(248,238)+step(24,206,24)
 elif n=='s08':
  if a=='R':p=at(420,206)+[settle(304),wait('observed_height',observed_y=dict(direction='gte',value=210),timeout=120),cmd('shoot',1,direction=[.9682458366,.25])]+at(304,190)+at(300,190)+[axis(0),cmd('jump'),cmd('jump_release',24),wait('revision_actor',ymax=60,timeout=120),cmd('shoot',1,direction=[-.9539392014,.3]),settle(448)]
  else:p=[axis(0),cmd('drop_through',1),wait('observed_height',observed_y=dict(direction='gte',value=40),timeout=120),cmd('shoot',1,direction=[1,0]),settle(304)]+at(304,190)+[settle(488),cmd('jump'),cmd('shoot',1,direction=[-1,0]),cmd('jump_release',1)]
 elif n=='s10':
  if a=='B':p=at(304,590)+step(296,478,24)+step(112,350,24,[.94,.341174442])+step(336,206,24,[-.85,.5267826876])
  else:p=at(300,206)+[settle(200),wait('observed_height',observed_y=dict(direction='gte',value=300),timeout=180),settle(112)]+at(112,350)+[cmd('drop_through',1),settle(296)]+at(296,478)+[cmd('drop_through',1),settle(320)]
 elif n=='s11':
  if a=='L':p=at(92,334)+[wait('r061_ellipse_board',x=92,y=334),follow('P'),cmd('jump'),cmd('jump_release',16),supported('P')]
  elif a=='R':p=at(570,78)+[settle(480),wait('observed_height',observed_y=dict(direction='gte',value=125),timeout=120),follow('P'),supported('P')]
  else:p=at(440,462)+[wait('r061_ellipse_board',x=440,y=462),follow('P'),cmd('jump'),cmd('jump_release',16),supported('P')]
  p +=[follow('P'),wait('r061_ellipse_exit',target=goal)]
  p +=jump(goal[0],24,[0,1]if z=='R'else([1,0]if z=='L'else None))
 elif n=='s12':
  if a=='L':p=at(92,334)+[ring('P',True),state('P',True),wait('r061_p_board'),follow('P'),cmd('jump'),cmd('jump_release',8),supported('P')]
  elif a=='B':p=[ring('P',True),state('P',True),wait('r061_p_bottom'),follow('P'),cmd('jump'),cmd('jump_release',24),supported('P')]
  elif a=='R':p=at(584,78)+[ring('Q',True),state('Q',True),settle(368),wait('observed_height',observed_y=dict(direction='gte',value=100),timeout=120),cmd('shoot',1,direction=[1,0]),follow('Q'),supported('Q')]
  else:p=[axis(0),cmd('drop_through',1),wait('observed_height',observed_y=dict(direction='gte',value=40),timeout=120),settle(368),cmd('shoot',14,direction=[-.916515,.4]),follow('Q'),supported('Q')]
  if a in ['L','B']:
   p +=[follow('P'),wait('r061_p_transfer'),ring('P',False),state('P',False),follow('P'),supported('P')]
   if z=='B':p +=[settle(448)]
   else:p +=jump(368,24,[0,1])+[follow('Q'),supported('Q')]
  if z not in ['B']or a in ['R','T']:
   p +=[follow('Q'),ring('Q',True),state('Q',True),wait('r061_q_exit'),ring('Q',False),state('Q',False),follow('Q'),supported('Q')]
   if z=='T':p+=jump(224,24)+[dict(op='shoot',trigger=dict(after=1,state='r061_top_shot',timeout=120))]
   elif z=='R':p+=jump(580,24,[-.95,.3122499])+at(580,78)
   elif z=='B':p+=[settle(448)]
   else:p+=jump(280,24)+[follow('P'),supported('P'),ring('P',True),state('P',True),wait('r061_p_left'),ring('P',False),state('P',False),settle(24),cmd('shoot',20,direction=[1,0])]
 elif n=='s13':
  p=at(68,206)+[wait('r061_saw_window'),settle(336),cmd('jump'),cmd('jump_release',1),cmd('shoot',1,direction=[-1,0])]+at(336,142)+[wait('r061_saw_window'),settle(48),cmd('jump'),cmd('jump_release',1),cmd('shoot',1,direction=[1,0])]
 else:raise ValueError(n)
 return p+end(*goal),source[0]
def prepare(r):
 global CURRENT
 CURRENT=r;s=inspect.getsource(base.prepare).replace('pcg/manual_review/ideas_author_v1.py','pcg/manual_review/revision061_author_v1.py');ns={**base.__dict__,'AUTH':AUTH,'label':label,'decode':decode,'dock':dock,'enrich':enrich,'plan_for':plan_for};exec(compile(s,__file__,'exec'),ns);ns['prepare'](r)
 f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];doc=core.read(f/'module.mapnote.json')
 for c in cs:
  c.update(id='approved-r061-'+label(r)+'-'+c['route_spec']['id'],max_frames=3600);c['generation_rule']['registration_source']='pcg/manual_review/revision061_author_v1.py'
  if label(r)=='s13':c['required_rewards']=['reward'];c['expected_reward']=4
 core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(doc,cs));core.contract(f/'module.mapnote.json',refresh=True)
if __name__=='__main__':
 for r in rows():prepare(r)
