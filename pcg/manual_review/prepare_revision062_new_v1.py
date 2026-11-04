if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import inspect
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from . import prepare_ideas_v1 as base
from .continue_revision062_v1 import rows,label,AUTH
from .revision062_content_v1 import decode
from .prepare_revision060_v1 import wait,follow,supported,aim
from .prepare_review045_v1 import at,end,axis
from .prepare_revision058_v2 import jump
from .prepare_ideas_v1 import settle
CURRENT=None

def dock(p):
 d=core.read(CURRENT['designFile']);o=next(o for o in d['visualObjects']if o['id']==p['supportObjectId']);return[p['position'][0]-p['normal'][0]*24,o['y']-18]
def enrich(d):
 d=base.enrich(d)
 for o in d['visualObjects']:
  if o.get('designMotion')and'initial_phase'in o['designMotion']:
   m=o['designMotion'];o.update(duration=m.get('period',m.get('travel_duration')),dwell=m.get('dwell_duration',0),initialPhase=m['initial_phase'])
  if o['type']=='bell'and o['id']=='under-bell':o.update(targetId='P',hostId='P',mechanics={**o['mechanics'],'localReceiverOffset':[0,64],'runtimeParameters':dict(inactiveGate=[-4096,-4096,8,8],carrier_mount='P')})
  if o.get('surfaceBinding'):
   b=o['surfaceBinding'];o.update(type='spike',hostId=b['ownerObjectId'],sourceId=o['id'])
  if o['id']=='window-saw':o['type']='gear'
 return d

def ring(p,v):return dict(op='shoot',group_id=p+'-bell',running=v,trigger=dict(after=1,state='r062_ring',timeout=600))
def state(p,v):return wait('r062_running',group_id=p+'-bell',running=v)
def height(p,lo,hi,**kw):return wait('r062_height',carrier=p,ymin=lo,ymax=hi,**kw)
def clear(id,x):return[settle(x),dict(op='wait',fight_enemy=id,trigger=dict(after=1,state='revision_clear',timeout=1200))]
def plan_for(n,t,source,d):
 n=label(CURRENT);a,z=t['from'],t['to'];goal=dock(next(p for p in d['ports']if p['id']==z))
 if n=='s04':
  if a=='B':
   p=at(288,846)+clear('lower-air-enemy',288)+[ring('P',True),state('P',True),height('P',780,805),settle(348),cmd('jump'),settle(272),cmd('jump_release',24),follow('P'),supported('P'),height('P',448,470,up=True,supported=True),ring('P',False),state('P',False),follow('P',-32),supported('P'),ring('Q',True),state('Q',True),height('Q',420,450,up=False)]+jump(112,24)+[follow('Q'),supported('Q'),height('Q',380,430,up=True,supported=True),follow('Q',56),supported('Q'),ring('Q',False),state('Q',False)]+clear('upper-air-enemy',144)+[ring('Q',True),state('Q',True),follow('Q'),height('Q',160,178,up=True,supported=True)]+jump(64,24)
  else:p=[axis(0),cmd('drop_through'),settle(112),follow('Q'),supported('Q')]+clear('upper-air-enemy',144)+[follow('Q',56),supported('Q'),ring('Q',True),state('Q',True),follow('Q'),height('Q',550,576,up=False,supported=True)]+jump(272,24)+[follow('P'),supported('P')]+clear('lower-air-enemy',248)+[follow('P',56),supported('P'),ring('P',True),state('P',True),follow('P'),height('P',780,805,up=False,supported=True),settle(340)]
 elif n=='s06':
  if a=='B':p=at(416,718)+[dict(op='shoot',trigger=dict(after=1,state='r062_mount_shot',timeout=180)),settle(492),cmd('jump'),settle(416),cmd('jump_release',24),cmd('shoot',1,direction=[0,1]),follow('P'),supported('P'),follow('P'),height('P',160,178,up=True,supported=True)]+jump(64,24)
  else:p=[axis(0),cmd('drop_through'),settle(112),cmd('shoot',22,direction=[0,1]),follow('P'),supported('P'),settle(348),dict(op='shoot',air_only=True,trigger=dict(after=1,state='r062_mount_shot',timeout=600)),follow('P'),supported('P'),height('P',620,642,up=False,supported=True),settle(496)]
 elif n=='s09':
  if a=='L':p=at(90,206)+[wait('r062_saw_low'),settle(300),wait('observed_height',observed_y=dict(direction='gte',value=242),timeout=180),cmd('shoot',0,direction=[-1,0])]+at(320,398)+clear('middle-air-enemy',320)+[cmd('drop_through'),settle(320)]
  else:p=[axis(0),cmd('jump'),cmd('jump_release',24),cmd('shoot',1,direction=[0,1])]+at(320,398)+clear('middle-air-enemy',320)+[wait('r062_saw_low'),settle(232),cmd('jump'),cmd('jump_release',24),cmd('shoot',1,direction=[.6,.8]),settle(80)]+at(24,206)
 else:raise ValueError(n)
 return p+end(*goal),source[0]
def main():
 global CURRENT
 for r in rows():
  if r['implementationMode']!='new_exact_approved_design':continue
  CURRENT=r;s=inspect.getsource(base.prepare).replace('pcg/manual_review/ideas_author_v1.py','pcg/manual_review/revision062_new_author_v1.py');ns={**base.__dict__,'AUTH':AUTH,'label':label,'decode':decode,'dock':dock,'enrich':enrich,'plan_for':plan_for};exec(compile(s,__file__,'exec'),ns);ns['prepare'](r)
  f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];doc=core.read(f/'module.mapnote.json')
  for c in cs:c.update(id='approved-r062-'+label(r)+'-'+c['route_spec']['id'],max_frames=3600);c['generation_rule']['registration_source']='pcg/manual_review/revision062_new_author_v1.py'
  core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(doc,cs));core.contract(f/'module.mapnote.json',refresh=True);print(label(r),'PREPARED',flush=True)
if __name__=='__main__':main()
