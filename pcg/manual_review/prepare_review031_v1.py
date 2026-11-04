"""Materialize the four exact approvals without changing design geometry."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy,inspect
from pcg.migration import core,physics,godot_package
from pcg.prototype.workshop.rules import cmd
from . import prepare_first40_v1 as shared,prepare_review_refresh_v1 as refresh
AUTH=core.REPO/'feedback/manual-review/implementation-results/review-031-v1/authorization'
OUT=AUTH.parent
CURRENT=None
def rows():return core.read(AUTH/'handoff.json')['rows']
def axis(v):return dict(op='axis',value=v,cancel_settle=True,trigger=dict(after=0))
def dock(p):
 x,y=p['position'];nx,ny=p['normal']
 return [x-24*nx,y+14]if nx else [x,-288 if p['id']=='entry'else y-24]
def decode(doc):
 refresh.CURRENT=CURRENT;refresh.NOTES=[]
 return refresh.decode(doc)
def plan_for(n,target,source,design):
 p=copy.deepcopy(source[0]['control_plan']);z=next(v for v in design['ports']if v['id']==target['to']);x,y=dock(z)
 if n=='197':p=refresh.at(180,168)+p+refresh.at(430,552)
 if n=='198':p=refresh.at(190,420)+p+refresh.at(1370,420)
 if n=='200':
  if target['from']=='entry':p=refresh.at(80,484)+p+refresh.at(30,100)
  else:p=refresh.at(30,100)+[axis(1),dict(op='wait',trigger=dict(dynamic=dict(kind='actor_x',direction='gte',value=160),timeout=180)),axis(0),cmd('wait',50)]
 if n=='196':
  if target['from']=='entry':p=[cmd('drop_through'),axis(1)]+p[1:]
  else:p=[axis(1),cmd('wait',10)]
  if target['to']=='bottom':p=[axis(1),cmd('drop_through'),cmd('wait',90),axis(0)]
 for v in p:
  if v['op']=='axis':v['cancel_settle']=True
 return p+refresh.end(x,y),source[0]
def prepare(row):
 global CURRENT
 CURRENT=row
 source=inspect.getsource(shared.prepare).replace("'pcg/manual_review/first40_r'+n+'_v1.py'","'pcg/manual_review/review031_author_v1.py'")
 source=source.replace("match['generation_rule']['registration_source']","match.get('generation_rule',{}).get('registration_source',row['sourceModule']['file'])")
 source=source.replace("c['generation_rule']['registration_source']=","c.setdefault('generation_rule',{})['registration_source']=")
 source=source.replace("target['role']={'ingress':'main','air_exit':'main'}", "target['role']={'ingress':'main','air_exit':'main','branch_or_return':'return'}")
 scope={**shared.__dict__,'AUTH':AUTH,'dock':dock,'plan_for':plan_for,'decode':decode}
 exec(compile(source,__file__,'exec'),scope);scope['prepare'](row)
 f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];doc=core.read(f/'module.mapnote.json')
 for c in cs:
  c['id']=c['id'].replace('approved-first30','approved-review031-v1');c['max_frames']=3300 if row['reviewId']=='198'else 2700;c['trace_all']=False
  c['route_spec']['require_bell']=row['reviewId']=='197'
  for k in list(c):
   if k.startswith('migration_')or k in ('decoder_pending_behavior','validation_summary','review_alias','source_module','source_case','actions','axes'):c.pop(k,None)
  if row['reviewId']=='200'and c['route_spec']['from_port']=='exit':c['required_rewards']=[];c['expected_reward']=0
  if row['reviewId']=='196':
   if c['route_spec']['to_port']!='exit':c['required_rewards']=[];c['expected_reward']=0
   if c['route_spec']['from_port']=='bottom':c['review031_ingress_velocity']=[0,-600];c['warmup_frames']=0
 doc=godot_package.bind_case_behavior(doc,cs)
 core.write(f/'module.mapnote.json',doc);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
 core.write(f/'parameters.json',dict(designVersion=row['designVersion'],content=decode(doc),controls=[dict(route=c['route_spec'],control_plan=c['control_plan'],max_frames=c['max_frames'])for c in cs],notes=['Geometry, hazards, enemies, tracks and authored dwell unchanged; parameters and input policy only.','196 bottom AIR ingress is conditional on an incoming upward velocity, not a grounded recovery.']))
if __name__=='__main__':
 import sys
 for r in rows():
  if not sys.argv[1:]or r['reviewId']in sys.argv[1:]:prepare(r)
