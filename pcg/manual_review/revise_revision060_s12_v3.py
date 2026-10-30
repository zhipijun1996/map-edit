import copy
from pcg.migration import core
from .continue_revision060_v1 import rows,label
from .revise_revision060_v2 import save
from .prepare_revision060_v1 import wait
from .prepare_review045_v1 import at,end
from .prepare_ideas_v1 import settle

def main():
 r=next(r for r in rows()if label(r)=='s12');f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases']
 for c in cs:
  c['generation_rule']['registration_source']='pcg/manual_review/revision060_author_v3.py';a,z=c['route_spec']['from_port'],c['route_spec']['to_port'];p=c['control_plan']
  if z=='R':
   k=next(i for i,v in enumerate(p)if v.get('windows')and v['windows'][0].get('id')=='Q'and v['windows'][0].get('ymin')==185)
   p[k]=wait('r060_s12_right')
   for v in p[k:]:
    if v.get('target_x')==616:v['target_x']=580
    if v.get('direction')==[-1,0]:v['adaptive_right_shot']=True
   # Preserve real landing at the conservative interior580 dock before walking to616.
   for v in p[k:]:
    if v.get('trigger',{}).get('migration_goal')==[612,75,8,6]:v['trigger']['migration_goal']=[576,75,8,6]
   p+=end(*c['exit_port'])
  if a=='B'and z=='L':
   for v in p:
    if v.get('target_x')==24:v['target_x']=64
    if v.get('trigger',{}).get('migration_goal')==[20,331,8,6]:v['trigger']['migration_goal']=[60,331,8,6]
   p+=end(*c['exit_port'])
  c['control_plan']=p
 bygoal={c['route_spec']['to_port']:c for c in cs if c['route_spec']['from_port']=='B'}
 for c in cs:
  if c['route_spec']['from_port']!='R':continue
  z=c['route_spec']['to_port'];prefix=[settle(500)]+at(500,462)
  if z=='B':c['control_plan']=prefix+copy.deepcopy(bygoal['L']['control_plan'][:3])+end(*c['exit_port'])
  else:c['control_plan']=prefix+copy.deepcopy(bygoal[z]['control_plan'])
 save(r,cs,'v3')
if __name__=='__main__':main()
