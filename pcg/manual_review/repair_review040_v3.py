"""Observe which side the real air enemy is on; retain the actual refund."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .prepare_review040_v3 import rows,height,at,end,jump
from .prepare_review_refresh_v1 import kill
def apply(row):
 n=row['reviewId'];f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v3-cases.json',dict(cases=cs))
 for c in cs:
  a,z=c['route_spec']['from_port'],c['route_spec']['to_port']
  if n=='220'and a=='C':
   if z=='B':c['control_plan']=at(770,446)+jump(435,632,hold=8)+kill('design-ground-enemy',435,632,8)+kill('design-air-enemy',400,632,8)+end(*c['exit_port'])
   else:
    p=c['control_plan'];i=next(i for i,v in enumerate(p)if v.get('enemy_window'));tail=p[i-3:];c['control_plan']=at(770,446)+jump(435,632,hold=8)+kill('design-ground-enemy',435,632,8)+jump(500,562,hold=10)+tail
  if n in ['220','225']:
   p=c['control_plan'];i=next((i for i,v in enumerate(p)if v.get('enemy_window')),None)
   if i is not None:
    p[i]['enemy_window']['required_side']=1
    j=next(j for j in range(i+1,len(p))if p[j]['op']=='shoot')
    p[i+1:j]=[dict(op='wait',trigger=dict(state='descending',timeout=180)),height(280 if n=='220' else 270,'gte')]
    if n=='220':p[i+3]['direction']=[.6,.8]
  c['generation_rule']['registration_source']='pcg/manual_review/review040_author_v3.py';c['id']=c['id'].replace('review040-v2','review040-v3').replace('review040-v1','review040-v3')
 d=godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs);core.write(f/'module.mapnote.json',d);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':
 import sys
 for r in rows():
  if r['reviewId']in sys.argv[1:]:apply(r)
