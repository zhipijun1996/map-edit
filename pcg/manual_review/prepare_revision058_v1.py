"""Materialize twelve exact designs; explicit authorized42 adjustment kept separate."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy,inspect,sys
from pcg.migration import core,physics,godot_package,corners
from pcg.prototype.workshop.rules import cmd
from .continue_revision058_v1 import rows,label,AUTH
from . import prepare_ideas_v1 as base
from .revision058_content_v1 import decode
from .prepare_review045_v1 import at,end,axis
CURRENT=None

def dock(p):
 d=core.read(CURRENT['designFile']);o=next(o for o in d['visualObjects']if o['id']==p['supportObjectId']);x=p['position'][0]if not p['normal'][0]else p['position'][0]-p['normal'][0]*24
 return[x,o['y']-18]
def enrich(d):
 d=base.enrich(d)
 for o in d['visualObjects']:
  m=o.setdefault('mechanics',{})if o['type']in ['gate','bell']else{}
  if o['id']=='timed-gate':m.update(kind='timed_gate',openSeconds=3.0)
  if o['type']=='bell'and o.get('targetIds'):
   o['targetId']=o['targetIds'][0]
   if o['id']=='return-bell':o.update(sourceId='low-bell/return');m.update(returnSideOnly=True)
  if o['id']in ['gate-A','gate-B']:
   m.update(kind='complementary_gates',initialOpen='B',gateA='gate-A',gateB='gate-B')
  if o['id']=='common-bell':m.update(kind='complementary_gates',initialOpen='B',gateA='gate-A',gateB='gate-B')
  if o['id']=='right-access':o.update(sourceId='common-bell/return',targetId='gate-A');m.update(returnSideOnly=True)
  if o['id']=='bottom-access':m.update(returnSideOnly=True,extraPairAccess=True,groupSourceId='common-bell')
 return d

def jump(x,hold=24,shot=None):
 p=[base.settle(x),cmd('jump'),cmd('jump_release',hold)]
 if shot:p+=[cmd('shoot',4,direction=shot)]
 return p

def choose(which,direction):return dict(op='wait',pair_desired=which,direction=direction,trigger=dict(after=1,state='pair_desired',timeout=240))
def plan_for(n,t,source,d):
 lab=label(CURRENT);a,z=t['from'],t['to'];ps={p['id']:dock(p)for p in d['ports']};goal=ps[z]
 if '-left-'in n:
  delta=goal[1]-ps[a][1]
  if delta<-155:p=at(100,ps[a][1])+jump(goal[0],24,[0,1])if lab=='lt-2x2'else jump(goal[0],24,[0,1])
  elif lab=='lt-2x1'and a=='A':p=at(104,78)+jump(192,1)+[dict(op='wait',trigger=dict(after=1,state='airborne',dynamic=dict(kind='actor_x',direction='gte',value=180),timeout=90)),dict(op='shoot',direction=[0,1],height_threshold=64,trigger=dict(after=1,state='descending_height',timeout=90))]
  elif delta<0:p=jump(goal[0])
  elif a=='B'and next(p for p in d['ports']if p['id']=='B')['face']=='TOP':
   p=[cmd('drop_through',1)]
   if lab=='lt-2x1':p +=[dict(op='shoot',direction=[1,0],height_threshold=42,trigger=dict(after=1,state='descending_height',timeout=120))]
   p +=[base.settle(goal[0])]
  elif abs(delta)<1:p=jump(goal[0],12)
  else:p=[cmd('drop_through',1),base.settle(goal[0])]
 elif lab=='S15':p=at(90,ps[a][1])+jump(goal[0],24,[-.6,.8])if a=='L'else[base.settle(goal[0])]
 elif lab=='S09':
  if a=='L':p=at(76,78)+jump(208,8)+at(208,206)+[cmd('drop_through',1),base.settle(320)]
  else:p=at(292,462)+jump(96,24,[.65,.7599342077])+at(96,334)+jump(208,24,[-.4,.916515139])+at(208,206)+jump(64,24,[.4,.916515139])
 elif lab=='S07':
  if a=='L':p=at(90,206)+jump(256,24,[-1,0])+at(256,190)+at(300,190)+jump(376,4)+[dict(op='shoot',direction=[-.4,.916515139],aim_point=[336,272],height_threshold=180,trigger=dict(after=1,state='descending_height',timeout=120)),base.settle(448),dict(op='wait',trigger=dict(after=1,state='grounded',migration_goal=[416,88,64,12],timeout=240))]+jump(448)
  else:p=[dict(op='shoot',direction=[0,1],trigger=dict(after=1,state='grounded_shot_ready',timeout=120)),cmd('wait',12),cmd('drop_through',1),base.settle(256)]+at(256,190)+jump(24,8)
 elif lab=='S11':
  if a=='L':p=at(90,334)+jump(264)+at(264,302)
  elif a=='R':p=at(584,78)+[choose('A',[0,-1]),base.settle(264),dict(op='wait',trigger=dict(after=1,state='airborne',dynamic=dict(kind='actor_x',direction='lte',value=525),timeout=120)),cmd('shoot',direction=[1,0])]+at(264,302)
  else:p=[axis(0),cmd('jump'),dict(op='wait',observed_y=dict(direction='lte',value=390),trigger=dict(after=1,state='observed_height',timeout=90)),base.settle(264),cmd('jump_release',16),cmd('shoot',4,direction=[.6,.8])]+at(264,302)
  if z=='R':p+=at(300,302)+[choose('A',[.85,-.5267826876])]+at(300,302)+jump(584,24,[-.6,.8])
  elif z=='B':p+=at(300,302)+[choose('B',[.85,-.5267826876]),base.settle(448)]
  else:p+=jump(24)
 elif lab=='S02':
  if a=='T':p=[cmd('drop_through',1),base.settle(350)]
  else:p=[dict(op='wait',trigger=dict(after=1,state='carrier_board',timeout=1200),carrier='P'),base.settle(272),cmd('jump'),cmd('jump_release',24),dict(op='wait',trigger=dict(after=1,state='carrier_supported',timeout=240),carrier='P'),dict(op='settle',target_x=272,follow_carrier='P',trigger=dict(after=0)),dict(op='wait',trigger=dict(after=1,state='carrier_exit',timeout=1200),carrier='P',exit_y=200),*jump(64,24,[0,1])]
 else:
  p=[dict(op='wait',trigger=dict(after=1,state='route_carrier_ready',timeout=2200)),base.settle(goal[0])]
 return p+end(*goal),source[0]

def prepare42(row):
 from .continue_revision053_v1 import rows as oldrows,label as oldlabel
 old=next(r for r in oldrows()if oldlabel(r)=='42');src=core.REPO/'pcg/manual_review/implementation/revision-053-final-v1'/row['moduleId'];f=core.REPO/row['outputDirectory'];d=core.read(src/'module.mapnote.json');cs=core.read(src/'physics-input-cases.json')['cases'];o=next(o for o in d['objects']if o['id'].endswith('/platform-4'));o.update(x=304,w=208)
 g=d['generationContract'];g['validations']=[];g['generation']['approvedImplementation'].update(authorization=physics.artifact(AUTH/'request.json'),designFile=physics.artifact(core.REPO/row['designFile']),designVersion=row['designVersion']);g['generation']['approvedImplementation'].pop('boundaryInputs',None)
 for c in cs:
  c['platforms'][1]=[304,0,208,24];c['generation_rule']['registration_source']='pcg/manual_review/revision058_forest_author_v1.py';c['approved_implementation']['designVersion']=row['designVersion'];c['id']='approved-r058-42-'+c['route_spec']['id'];c.pop('block_ports',None)
  for v in c['control_plan']:
   if v['op']=='jump_release'and v['trigger'].get('after')==8:v['trigger']['after']=12
 core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(d,cs));core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs));core.write(f/'migration.json',core.read(src/'migration.json'));core.write(f/'parameters.json',dict(designVersion=row['designVersion'],authorizedShoreExtension=32,source=physics.artifact(src/'module.mapnote.json')))

def prepare(row):
 global CURRENT
 CURRENT=row
 if label(row)=='42':return prepare42(row)
 source=inspect.getsource(base.prepare).replace("'pcg/manual_review/ideas_author_v1.py'","'pcg/manual_review/revision058_author_v1.py'").replace("family='orbit-choice'if label(row)=='orbit'else'recoil-chain'","family='approved-interface'")
 scope={**base.__dict__,'AUTH':AUTH,'label':label,'decode':decode,'dock':dock,'enrich':enrich,'plan_for':plan_for};exec(compile(source,__file__,'exec'),scope);scope['prepare'](row)
 f=core.REPO/row['outputDirectory'];doc=core.read(f/'module.mapnote.json');cs=core.read(f/'cases.json')['cases']
 for c in cs:
  c['id']='approved-r058-'+label(row)+'-'+c['route_spec']['id'];c['max_frames']=3600;c['generation_rule']['registration_source']='pcg/manual_review/revision058_author_v1.py'
 core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(doc,cs));core.contract(f/'module.mapnote.json',refresh=True)
 m=core.read(f/'migration.json');m['sourceVersion']=row['designVersion'];m['sourcePath']=row['designFile'];core.write(f/'migration.json',m)
if __name__=='__main__':
 for r in rows():
  if not sys.argv[1:]or label(r)in sys.argv[1:]:prepare(r)
