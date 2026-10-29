import copy,inspect,sys
from pcg.migration import core,physics,godot_package
from pcg.prototype.workshop.rules import cmd
from .continue_revision060_v1 import rows,label,AUTH
from . import prepare_ideas_v1 as base
from .revision060_content_v1 import decode
from .prepare_review045_v1 import at,end,axis
from .prepare_ideas_v1 import settle
from .prepare_revision058_v2 import jump
from .finalize_revision059_v1 import folder_for as old_folder
CURRENT=None

def dock(p):
 d=core.read(CURRENT['designFile']);o=next(o for o in d['visualObjects']if o['id']==p['supportObjectId']);return[p['position'][0]-p['normal'][0]*24,o['y']-18]
def enrich(d):
 d=base.enrich(d);objects={o['id']:o for o in d['visualObjects']}
 for o in d['visualObjects']:
  if o.get('designMotion'):
   v=o['designMotion'];o.update(duration=v.get('period',v.get('travel_duration')),dwell=v.get('dwell_duration',0),initialPhase=v['initial_phase'])
  if o['type']in ['triggerZone','hitTurret','projectileBarrier']:o.setdefault('mechanics',{})['approvedCellType']=o['type'];o['type']='switch'
  if o.get('surfaceBinding'):
   v=o['surfaceBinding'];o.update(type='spike',sourceId=o['id'],hostId=v['ownerObjectId'])
  if o['type']=='enemy':o['definition']='plains_charger'if 'charger'in o['id']else'plains_sentry'
 if label(CURRENT)=='hq07':
  for k in ['gate-A','gate-B','pair-bell']:objects[k].setdefault('mechanics',{}).update(kind='complementary_gates',initialOpen='B',gateA='gate-A',gateB='gate-B')
  objects['pair-bell'].update(targetId='gate-A',sourceId='pair-bell');objects['return-bell'].update(targetId='gate-A',sourceId='pair-bell/return');objects['return-bell']['mechanics']=dict(returnSideOnly=True)
 if label(CURRENT)=='hq09':
  objects['motion-bell'].update(targetId='P',sourceId='motion-bell');objects['motion-bell'].setdefault('mechanics',{})['runtimeParameters']=dict(inactiveGate=[-4096,-4096,8,8])
 return d

def wait(state,timeout=1800,**kw):return dict(op='wait',trigger=dict(after=1,state=state,timeout=timeout),**kw)
def supported(p):return wait('carrier_supported',carrier=p,timeout=360)
def follow(p,offset=0,ring=False):return dict(op='settle',target_x=0,revision_follow=p,carrier_offset=offset,ring_follow=ring,deadband=.6,source_native_gain=5.5,trigger=dict(after=0))
def aim(x,y,after=1):return dict(op='shoot',native_aim_point=[x,y],trigger=dict(after=after))
def ring(running,carrier=None):return dict(op='shoot',group_command=running,group_carrier=carrier,trigger=dict(after=1,state='r060_ring_ready',timeout=600))
def group_wait(running):return wait('r060_group_running',running=running,timeout=240)
def group_plan(a,z):
 if a=='L':p=at(96,334)+[ring(True),group_wait(True)]+at(96,334)+[wait('r060_group_board'),follow('P'),cmd('jump'),cmd('jump_release',1),cmd('shoot',4,direction=[-.8,.6]),supported('P'),follow('P',ring=True),ring(False,'P'),group_wait(False),follow('P'),supported('P')]+jump(368,8,[0,1])+[supported('Q')]
 elif a=='R':p=at(584,78)+[ring(True),group_wait(True),wait('r060_carrier_height',carrier='Q',ymin=210,ymax=240),ring(False),group_wait(False)]+at(550,78)+[settle(368),wait('observed_height',observed_y=dict(direction='gte',value=100),timeout=120),cmd('shoot',1,direction=[1,0]),settle(368),supported('Q')]
 else:p=[axis(0),cmd('drop_through',1),wait('observed_height',observed_y=dict(direction='gte',value=70),timeout=120),settle(368),dict(op='wait',trigger=dict(after=1,state='airborne',dynamic=dict(kind='actor_x',direction='gte',value=226),timeout=120)),cmd('shoot',1,direction=[-.916515139,.4]),supported('Q')]
 p +=[follow('Q',32,ring=True),ring(True,'Q'),group_wait(True),wait('r060_carrier_height',carrier='Q',supported=True,ymin=199,ymax=204),ring(False,'Q'),group_wait(False),follow('Q'),supported('Q')]
 if z=='R':p+=jump(580,8,[-.98,.1989974874])+at(580,78)+end(616,78)
 elif z=='T':p+=jump(192,24)+[dict(op='shoot',direction=[0,1],trigger=dict(after=1,state='r060_top_aligned',timeout=120))]+end(192,14)
 else:p+=jump(256,24)+[follow('P'),supported('P'),follow('P',ring=True),ring(True,'P'),group_wait(True),wait('r060_group_left'),ring(False,'P'),group_wait(False),settle(24),wait('observed_height',observed_y=dict(direction='gte',value=290),timeout=180),cmd('shoot',1,direction=[1,0])]+end(24,334)
 return p

def hq02_plan(a,z):
 if a=='B':p=[wait('r060_carrier_height',carrier='P',ymax=250)]+at(300,462)+jump(144,24)+at(144,338)+[axis(0)]
 else:p=[axis(0),cmd('drop_through',1),settle(144)]+at(144,338)
 if a=='B':
  for i in range(6):
   loop=[wait('r060_seed',timeout=600),cmd('jump'),cmd('jump_release',24)]+at(144,338)
   for v in loop:v['interception_loop']=True
   loop[0]['interception_loop_start']=True;p+=loop
  p +=[wait('r060_intercepted',timeout=60)]
 p +=[wait('revision_clear',enemy='sentry',guard_x=144,high_shore=False,timeout=1200),wait('r060_carrier_height',carrier='P',ymin=385),follow('P',-24),cmd('jump'),cmd('jump_release',8),supported('P'),follow('P',-24)]
 if z=='T':p +=[wait('r060_carrier_height',carrier='P',supported=True,ymax=165)]+jump(64,24)+end(64,14)
 else:p +=[wait('r060_carrier_height',carrier='P',supported=True,ymin=405),settle(300),wait('observed_height',observed_y=dict(direction='gte',value=365),timeout=180),settle(320)]+end(320,462)
 return p

def plan_for(n,t,source,d):
 a,z=t['from'],t['to'];n=label(CURRENT);g=dock(next(p for p in d['ports']if p['id']==z))
 if n=='hq03':
  if a=='L':p=at(84,206)+[settle(224),cmd('jump'),cmd('jump_release',1)]+at(224,238)
  elif a=='R':p=at(460,206)+[settle(320),cmd('jump'),cmd('jump_release',1)]+at(320,238)
  else:p=[axis(0),cmd('drop_through',1),settle(320)]+at(320,238)
  p +=[wait('revision_clear',enemy='charger',guard_x=224 if a=='L'else 320,high_shore=False,timeout=1200)]
  if z=='T':p+=at(300,238)+jump(320,8,[0,1])
  elif z=='L':p+=jump(24,1)
  else:p+=jump(488,1)
 elif n=='hq07':
  if a=='L':p=at(110,334)+jump(330,24)+[wait('descending_height',height_threshold=310,timeout=120),aim(240,344),settle(500)]+at(500,334)+jump(672,24)+at(672,334)+[wait('revision_clear',enemy='charger',guard_x=672,high_shore=False,timeout=1200)]
  else:p=at(800,334)+[wait('revision_clear',enemy='charger',guard_x=800,high_shore=False,timeout=1200),dict(op='shoot',aim_cell=dict(kind='bell',id='pair-bell',receiver='access'),trigger=dict(after=1,state='grounded_shot_ready',timeout=180)),settle(500)]+at(500,334)+jump(110,24,[-1,0])
 elif n=='hq08':
  if a=='L':p=at(90,334)+jump(320,8,[-.75,.6614378278])+[supported('P'),follow('P'),wait('r060_08_exit')]+jump(320,24,[0,1])
  else:p=[axis(0),cmd('drop_through',1),settle(100)]+at(100,334)
 else:
  if a=='L':p=at(90,334)+jump(184,8)+at(184,270)+[aim(176,352),wait('r060_bell_open',bell_id='target-bell',timeout=180),settle(176)]+jump(176,24)+at(176,142)+jump(192,24)
  else:p=[axis(0),aim(272,16),wait('r060_bell_open',bell_id='target-bell',timeout=180),cmd('drop_through',1),settle(176)]+at(176,142)+[cmd('drop_through',1),settle(100)]+at(100,334)
 return p+end(*g),source[0]

def prepare_new(r):
 global CURRENT
 CURRENT=r;s=inspect.getsource(base.prepare).replace('pcg/manual_review/ideas_author_v1.py','pcg/manual_review/revision060_author_v1.py');ns={**base.__dict__,'AUTH':AUTH,'label':label,'decode':decode,'dock':dock,'enrich':enrich,'plan_for':plan_for};exec(compile(s,__file__,'exec'),ns);ns['prepare'](r)
 f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];doc=core.read(f/'module.mapnote.json')
 for c in cs:c.update(id='approved-r060-'+label(r)+'-'+c['route_spec']['id'],max_frames=3600);c['generation_rule']['registration_source']='pcg/manual_review/revision060_author_v1.py'
 core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(doc,cs));core.contract(f/'module.mapnote.json',refresh=True)

def prepare_repair(r):
 f=core.REPO/r['outputDirectory'];assert not f.exists();old=old_folder(r);doc=core.read(old/'module.mapnote.json');cs=core.read(old/'physics-input-cases.json')['cases'];m=core.read(old/'migration.json');m.pop('holdoutPool',None);m['status']='prepared_unverified';impl=doc['generationContract']['generation']['approvedImplementation'];impl.update(authorization=physics.artifact(AUTH/'request.json'),priorImplementation=physics.artifact(old/'module.mapnote.json'));doc['generationContract']['validations']=[]
 for k in ['runtimeSource','decoderSource','observerSource','boundaryInputs']:impl.pop(k,None)
 if label(r)=='hq02':next(o for o in doc['objects']if o['id']=='middle')['w']=112
 if label(r)=='s12':
  for o in doc['objects']:
   if o['id']in ['P','Q']:o.setdefault('mechanics',{})['nativeOneWaySupport']=True
 content=decode(doc)
 for c in cs:
  c.update(content);c.update(id='approved-r060-'+label(r)+'-'+c['route_spec']['id'],max_frames=3600);c['generation_rule']['registration_source']='pcg/manual_review/revision060_author_v1.py'
  for k in ['recorded_frames','factory_evidence','noise','module_sha256']:c.pop(k,None)
  a,z=c['route_spec']['from_port'],c['route_spec']['to_port']
  if label(r)=='hq01':c['control_plan']=group_plan(a,z)
  if label(r)=='hq02':c['control_plan']=hq02_plan(a,z);c['require_original_interception']=a=='B'
 core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(doc,cs));core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs));core.write(f/'migration.json',m);core.write(f/'parameters.json',dict(designVersion=r['designVersion'],authorization=physics.artifact(AUTH/'request.json'),content=content,prior=physics.artifact(old/'parameters.json'),authorizedGeometryChange=label(r)=='hq02',authorizedCollisionChange=label(r)=='s12',controls=[dict(route=c['route_spec'],control_plan=c['control_plan'])for c in cs]))
if __name__=='__main__':
 for r in rows():
  if label(r)in sys.argv[1:]:(prepare_repair(r)if label(r)in ['hq01','hq02','s12']else prepare_new(r))
