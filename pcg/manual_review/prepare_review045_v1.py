"""Exact final drawings, original native hooks/region choice, bounded controls."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy,inspect,shutil
from pcg.migration import core,physics,godot_package,godot_package_v5
from pcg.prototype.workshop.rules import cmd
from . import prepare_first40_v1 as shared
from .first30_content_v2 import decode as ordinary_decode
from .refresh_review045_v1 import AUTH,OUT,rows,RETRIES
from .repair_review040_v9 import board
from .prepare_review040_v3 import axis,phase
CURRENT=None
def at(x,y):return [dict(op='settle',target_x=x,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),dict(op='wait',trigger=dict(after=1,state='grounded',migration_goal=[x-4,y-3,8,6],timeout=600))]
def end(x,y):return at(x,y)+[cmd('wait',24)]
def height(y,side='gte'):return dict(op='wait',observed_y=dict(value=y,direction=side),trigger=dict(state='observed_height',timeout=240))
def jump(x,y,hold=10,shot=None):
 p=[dict(op='settle',target_x=x,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),cmd('jump'),cmd('jump_release',hold)]
 if shot:p.append(cmd('shoot',1,direction=shot))
 return p+at(x,y)
def hook(target,delay=1):return [cmd('grapple',delay,aim_target=target),dict(op='wait',trigger=dict(after=21,state='free',timeout=240))]
def dock(p):
 x,y=p['position'];nx,ny=p['normal']
 if nx:return[x-24*nx,y+14]
 d=core.read(CURRENT['designFile']);support=[o for o in d['visualObjects']if o['type']in('terrain','platform')and not o.get('trackId')and o['x']<=x<=o['x']+o['w']]
 return[x,min(support,key=lambda o:abs(o['y']-y))['y']-18]
def decode(doc):
 d=copy.deepcopy(doc);chests=[]
 for o in doc['objects']:
  if o.get('mechanics',{}).get('service')==godot_package_v5.SERVICE:
   o['mechanics']['source']['position']=[o['x']+o['w']/2,o['y']+o['h']/2];chests.append(copy.deepcopy(o['mechanics']['source']))
 d['objects']=[o for o in d['objects']if o.get('mechanics',{}).get('service')!=godot_package_v5.SERVICE]
 content=ordinary_decode(d)
 if chests:content['original_region_chests']=chests
 return content
def plan_for(n,target,source,design):
 a,z=target['from'],target['to'];ports={p['id']:dock(p)for p in design['ports']};goal=ports[z];s=source[0];p=[]
 if n=='169':
  for x,t in ([(190,365),(410,560)]if a=='entry'else[(520,395),(350,170)]):
   p+=at(x,382)+[axis(0),dict(op='shoot',direction=[-.8 if a=='entry'else .8,.6],trigger=dict(state='grounded_shot_ready',timeout=180))]+at(t,382)
 elif n in {'41','61'}:p=at(0,-42)+copy.deepcopy(s['control_plan'][2:10])
 elif n=='55':p=at(108,-42)+copy.deepcopy(s['control_plan'][2:8])
 elif n=='57':p=at(0,0)+copy.deepcopy(s['control_plan'][2:10])
 elif n=='62':p=jump(-245,0,hold=12)+at(0,0)+copy.deepcopy(s['control_plan'][2:15])
 elif n in {'51','52'}:
  if a=='entry':p=jump(-245,-318,hold=4)+copy.deepcopy(s['control_plan'][2:(18 if n=='52'else 14)])
  elif n=='51':p=jump(360,-318,hold=4)+hook([330,-350],0)+[cmd('shoot',direction=[1,0])]+at(110,-318)+hook([-35,-350],0)+[cmd('shoot',direction=[1,0])]+at(-270,-318)+jump(-360,-318,hold=4)
  else:p=jump(360,-204,hold=4)+[cmd('jump')]+hook([310,-260],1)+[cmd('jump_release',5),cmd('shoot',direction=[1,0])]+at(110,-318)+hook([-35,-350],0)+[cmd('shoot',direction=[1,0])]+at(-270,-318)+jump(-360,-318,hold=4)
 elif n=='42':
  if a=='C':p=at(208,-178)
  else:
   launch=232 if a=='entry'else 350
   p=at(launch,-18)+[axis(0),cmd('jump'),cmd('grapple',1,aim_target=[304,-80]),cmd('jump_release',5),dict(op='wait',trigger=dict(after=21,state='free',timeout=240)),dict(op='settle',target_x=208,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),cmd('shoot',1,direction=[.25,.9682458366])]+at(208,-178)
  p+=[cmd('native_region_select',4,kind='coin'),cmd('wait',2)]
  if z!='C':p+=[cmd('drop_through')]+at(208,-18)+(jump(390,-18,hold=4)if z=='exit'else[])
 elif n=='50':
  if a=='C':p=jump(300,332,hold=8)+[cmd('jump'),cmd('grapple',1,aim_target=[120,155]),cmd('jump_release',5),dict(op='wait',trigger=dict(after=21,state='free',timeout=240))]+hook([200,-40],0)+[cmd('shoot',direction=[-1 if z=='exit'else 1,0])]
  elif a=='entry':p=at(0,-42)+copy.deepcopy(s['control_plan'][2:10])
  else:p=at(355,-42)+[cmd('jump'),cmd('grapple',1,aim_target=[200,-40]),cmd('jump_release',5),dict(op='wait',trigger=dict(after=21,state='free',timeout=240)),cmd('shoot',direction=[1,0])]+at(0,-42)
  if z=='C':p+=at(0,-42)+[dict(op='settle',target_x=195,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),height(160),cmd('shoot',direction=[-1,0])]+at(430,342)
 return p+end(*goal),s
def prepare(row):
 global CURRENT
 CURRENT=row;n=row['reviewId'];folder=core.REPO/row['outputDirectory']
 if n in RETRIES:
  assert not folder.exists();old=core.REPO/'pcg/manual_review/implementation/review-040-final-v1'/row['moduleId'];folder.mkdir(parents=True)
  for name in ['module.mapnote.json','cases.json','migration.json']:shutil.copy2(old/name,folder/name)
 else:
  text=inspect.getsource(shared.prepare).replace("'pcg/manual_review/first40_r'+n+'_v1.py'","'pcg/manual_review/review045_forest_author_v1.py'if n!='169'else'pcg/manual_review/review045_author_v1.py'")
  text=text.replace("if o['type']=='reward':","if o['type']=='reward'and 'region'in o.get('mechanics',{}).get('source',{}):")
  text=text.replace("target['role']={'ingress':'main','air_exit':'main'}","target['role']={'ingress':'main','air_exit':'main','return_or_branch':'return','return_or_hub':'return'}")
  scope={**shared.__dict__,'AUTH':AUTH,'dock':dock,'decode':decode,'plan_for':plan_for};exec(compile(text,__file__,'exec'),scope);scope['prepare'](row)
 cs=core.read(folder/'cases.json')['cases'];doc=core.read(folder/'module.mapnote.json')
 for c in cs:
  c['generation_rule']['registration_source']='pcg/manual_review/review045_forest_author_v1.py'if n in {'41','42','50','51','52','55','57','61','62'}else'pcg/manual_review/review045_author_v1.py';c['id']='approved-review045-v1-'+n+'-'+c['route_spec']['id'];c['max_frames']=3000;c['trace_all']=False
  for k in list(c):
   if k.startswith('migration_')or k in ['recorded_frames','factory_evidence','module_sha256','noise','decoder_pending_behavior','original_action_contract','source_action_program','actions','axes','source_native_steps','validation_summary']:c.pop(k,None)
  # A completed wait must observe a post-input physics frame, even at zero noise.
  for command in c['control_plan']:
   if command.get('trigger',{}).get('migration_goal'):command['trigger']['after']=max(1,command['trigger'].get('after',0))
  if n=='42':c['original_region_chests']=decode(doc)['original_region_chests'];c['required_region_chest_choices']=[dict(id='source_cache',kind='coin')]
  if n in {'41','61','55','57','62'}:c['expected_hook_sequence']={'41':['side_ring'],'61':['side_ring'],'55':['upper_window_ring'],'57':['relay_a','relay_b'],'62':['spiral_lower','spiral_middle','spiral_crown']}[n]
  if n in {'51','52'}:c['expected_hook_sequence']=['cavity_ring_a','cavity_ring_b']if c['route_spec']['from_port']=='entry'else['cavity_ring_b','cavity_ring_a']
  if n=='50':c['expected_hook_sequence']=['lower_window_ring','upper_window_ring']if c['route_spec']['from_port']=='C'else['upper_window_ring']
  if n=='42'and c['route_spec']['from_port']!='C':c['expected_hook_sequence']=['fruit']
 doc=godot_package.bind_case_behavior(doc,cs);core.write(folder/'module.mapnote.json',doc);core.contract(folder/'module.mapnote.json',refresh=True);core.write(folder/'cases.json',dict(cases=cs));core.write(folder/'parameters.json',dict(designVersion=row['designVersion'],geometry='exact approved design',controls=[dict(route=c['route_spec'],control_plan=c['control_plan'])for c in cs]))
 print(n,'READY',len(cs),flush=True)
if __name__=='__main__':
 import sys
 for r in rows():
  if not sys.argv[1:]or r['reviewId']in sys.argv[1:]:prepare(r)
