"""Exact approved 040 materialization, with explicit new native Cell bindings."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy,inspect
from pcg.migration import core,physics,godot_package
from pcg.prototype.workshop.rules import cmd
from . import prepare_first40_v1 as shared,prepare_review_refresh_v1 as refresh
from .refresh_review040_v1 import AUTH,OUT
CURRENT=None
def rows():return core.read(AUTH/'handoff.json')['rows']
def axis(v):return dict(op='axis',value=v,cancel_settle=True,trigger=dict(after=0))
def at(x,y):return refresh.at(x,y)
def end(x,y):return refresh.end(x,y)
def height(y,direction='lte'):return dict(op='wait',observed_y=dict(direction=direction,value=y),trigger=dict(state='observed_height',timeout=240))
def jump(x,y,hold=8,shot=None):
 p=[dict(op='settle',target_x=x,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),cmd('jump'),cmd('jump_release',hold)]
 if shot is not None:p+=[cmd('shoot',6,direction=shot)]
 return p+at(x,y)
def phase(id,window):return dict(op='wait',trigger=dict(dynamic=dict(kind='platform_phase',id=id,window=window),timeout=1600))
def dock(p):
 x,y=p['position'];nx,ny=p['normal']
 if nx:return[x-24*nx,y+14]
 if p['surface']=='AIR':return[x,y-24]
 design=core.read(CURRENT['designFile']);floors=[o for o in design['visualObjects']if o['type']=='platform'and not o.get('trackId')and o['x']+12<=x<=o['x']+o['w']-12]
 return[x,min(floors,key=lambda o:abs(o['y']-y))['y']-18]
def filtered(doc):
 d=copy.deepcopy(doc);release=[o for o in d['objects']if o.get('mechanics',{}).get('kind')=='reward_committed_release']
 for o in release:o.update(type='terrain',sourceIndex=sum(v['type']in('terrain','platform')and not v.get('trackId')for v in d['objects']))
 return d
def extension(doc):
 release=[o for o in doc['objects']if o.get('mechanics',{}).get('kind')=='reward_committed_release']
 if not release:return {}
 o=release[0];reward=next(v for v in doc['objects']if v['id']==o['mechanics']['triggerRewardId']);index=next(v['sourceIndex']for v in filtered(doc)['objects']if v['id']==o['id'])
 return dict(review040_release=dict(id=o['id'],platform_index=index,rect=[o[k]for k in ['x','y','w','h']],reward_id=reward['mechanics']['source']['id']))
def decode(doc):
 refresh.CURRENT=CURRENT;refresh.NOTES=[];d=filtered(doc);v=refresh.decode(d);v.update(extension(doc));return v
def plan_for(n,target,source,design):
 a,z=[next(p for p in design['ports']if p['id']==target[k])for k in ('from','to')];x,y=dock(z);p=[]
 if n=='202':
  if target['from']=='entry':p=at(180,164)+copy.deepcopy(source[0]['control_plan'])+at(105,420)+[cmd('shoot',aim_cell=dict(kind='bell',id='pocket-bell',receiver='return')),cmd('wait',8)]
  else:p=at(280,420)+[axis(0),cmd('jump'),cmd('shoot',18,direction=[.3,.9539392014]),cmd('jump_release',1)]+at(210,164)
 elif n=='204':p=copy.deepcopy(source[0]['control_plan'])[:-1]+at(860,548)
 elif n=='166':
  if target['from']=='entry':p=at(610,582)+[axis(1),cmd('jump'),cmd('shoot',18,direction=[0,1]),cmd('jump_release',1)]
 elif n=='167':
  if target['to'].startswith('exit_upper'):
   p=at(450,582)+jump(410,512,hold=4)
   if target['to']=='exit_upper_left':p+=at(270,512)+jump(220,454,hold=4)
   else:p+=jump(550,454,hold=4)
  elif target['from'].startswith('exit_upper'):p=at(450,582)
 elif n=='225':
  if target['to']=='C':
   if target['from']=='A':p=at(210,404)+jump(380,212,hold=24)
   else:p=at(540,532)+[axis(0),cmd('jump'),cmd('shoot',20,direction=[.45,.89302855]),cmd('jump_release',1)]+at(405,212)
   p+=jump(448,116,hold=10)
  elif target['to']=='A':p=at(380,212)+jump(200,404,hold=4)if target['from']=='C'else at(540,532)+[axis(0),cmd('jump'),cmd('shoot',20,direction=[.45,.89302855]),cmd('jump_release',1)]+at(405,212)+jump(200,404,hold=4)
  elif target['from']=='A':p=at(210,404)+jump(600,532,hold=8,shot=[-.98,.199])
 elif n=='223':
  if target['from']=='D':p=[cmd('drop_through')]+at(325,632)
  elif target['from']=='B':p=at(600,632)
  elif target['from']=='A':p=at(210,420)+jump(325,632,hold=4)
  elif target['from']=='C':p=at(640,420)+[axis(-1),cmd('jump'),cmd('jump_release',4)]+at(325,632)
  if target['to']=='A':p+=jump(200,420,hold=24,shot=[.3,.953939])
  elif target['to']=='C':p+=at(325,632)+jump(500,420,hold=24,shot=[-.3,.953939])+refresh.kill('design-hub-ground-enemy',500,420,8)
  elif target['to']=='D':p+=jump(200,420,hold=24,shot=[.3,.953939])+at(210,420)+jump(320,260,hold=24)
  elif target['to']=='B':p+=jump(600,632,hold=8,shot=[-.98,.199])+end(744,676)
 elif n=='220':
  if target['from']=='A':p=at(250,190)+at(285,702)
  elif target['from']=='C':p=at(770,446)
  if target['to']=='C'and target['from']!='C':
   p+=jump(335,632,hold=8)+at(435,632)+refresh.kill('design-ground-enemy',435,632,8)+jump(530,562,hold=8)+jump(680,492,hold=8)+jump(810,446,hold=8)
  elif target['to']=='A':
   if target['from']=='B':p+=jump(335,632,hold=8)+at(435,632)+refresh.kill('design-ground-enemy',435,632,8)+jump(500,562,hold=8)
   else:p+=at(650,492)+at(500,562)
   p +=[dict(op='settle',target_x=335,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),cmd('jump'),cmd('jump_release',24),cmd('shoot',aim_cell=dict(kind='enemy',id='design-air-enemy',body_offset=[0,12])),dict(op='shoot',direction=[.1,.994987],trigger=dict(state='shot_ready',timeout=120))]
  elif target['to']=='B'and target['from']=='C':p+=at(650,492)+at(500,562)+at(335,632)
 elif n=='115':
  if target['from']=='entry':p=refresh.kill('design-carrier-enemy',300,582,8)+at(325,582)+[phase('ferry',[0,.03])]+jump(425,542,hold=10)+[axis(0),phase('ferry',[.5,.52])]+jump(1060,582,hold=8)
  else:p=at(1050,582)+[phase('ferry',[.5,.52])]+jump(940,542,hold=10)+[axis(0),phase('ferry',[0,.03])]+jump(300,582,hold=8)
 elif n=='206':p=at(200,420)+copy.deepcopy(source[0]['control_plan'])[:-1]+[dict(op='settle',target_x=355,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),dict(op='wait',trigger=dict(state='reward_released',timeout=900)),dict(op='settle',target_x=320,deadband=.6,source_native_gain=5.5,trigger=dict(after=0))]
 for v in p:
  if v['op']=='axis':v['cancel_settle']=True
 return p+([]if n=='206'else end(x,y)),source[0]
def prepare(row):
 global CURRENT
 CURRENT=row;text=inspect.getsource(shared.prepare).replace("'pcg/manual_review/first40_r'+n+'_v1.py'","'pcg/manual_review/review040_author_v1.py'")
 text=text.replace("match['generation_rule']['registration_source']","match.get('generation_rule',{}).get('registration_source',row['sourceModule']['file'])").replace("c['generation_rule']['registration_source']=","c.setdefault('generation_rule',{})['registration_source']=")
 text=text.replace("target['role']={'ingress':'main','air_exit':'main'}","target['role']={'ingress':'main','air_exit':'main','branch_or_return':'return','branch':'main','return_to_high_port':'return','hub_connection':'main','return_or_hub':'return'}")
 scope={**shared.__dict__,'AUTH':AUTH,'dock':dock,'plan_for':plan_for,'decode':decode};exec(compile(text,__file__,'exec'),scope);scope['prepare'](row)
 f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];doc=core.read(f/'module.mapnote.json')
 for c in cs:
  n=row['reviewId'];c['id']=c['id'].replace('approved-first30','approved-review040-v1');c['max_frames']=3000;c['trace_all']=False
  for k in list(c):
   if k.startswith('migration_')or k in ['recorded_frames','decoder_pending_behavior','validation_summary','review_alias','actions','axes','factory_evidence','source_action_program','original_action_contract']:c.pop(k,None)
  if n=='202'and c['route_spec']['from_port']=='exit':c['required_rewards']=[];c['expected_reward']=0
  if n=='115':c['refresh_carried_enemies']=[dict(enemy='design-carrier-enemy',carrier='ferry')]
  if n=='206':c['approved_first30']=copy.deepcopy(c['approved_implementation']);c['settle_frames']=6
  assert len(c['control_plan'])<=384
 doc=godot_package.bind_case_behavior(doc,cs);core.write(f/'module.mapnote.json',doc);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs));core.write(f/'parameters.json',dict(designVersion=row['designVersion'],content=decode(doc),controls=[dict(route=c['route_spec'],control_plan=c['control_plan'])for c in cs],geometry='exact approved design; native enemy glyph decoding only'))
if __name__=='__main__':
 import sys
 for r in rows():
  if not sys.argv[1:]or r['reviewId']in sys.argv[1:]:prepare(r)
