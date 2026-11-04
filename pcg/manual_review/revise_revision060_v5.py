if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core
from .continue_revision060_v1 import rows,label
from .revise_revision060_v2 import save
from .prepare_revision060_v1 import wait,follow,supported
from .prepare_review045_v1 import at,end,axis
from .prepare_ideas_v1 import settle
from pcg.prototype.workshop.rules import cmd

def main():
 for r in rows():
  n=label(r)
  if n not in ['hq02','hq03','hq07']:continue
  f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases']
  for c in cs:
   c['generation_rule']['registration_source']='pcg/manual_review/revision060_author_v5.py';a,z=c['route_spec']['from_port'],c['route_spec']['to_port'];p=c['control_plan']
   if n=='hq02':
    k=next(i for i,v in enumerate(p)if v.get('trigger',{}).get('state')=='revision_clear');cut=next(i for i in range(k+1,len(p))if p[i].get('trigger',{}).get('state')=='r060_carrier_height');p=p[:k+1]+at(80,338)+[wait('r060_hq02_board'),follow('P',-24)]+p[cut+2:]
    if a=='T':
     j=next(i for i,v in enumerate(p)if v.get('target_x')==148);p=[axis(0),cmd('drop_through',1),settle(80)]+at(80,338)+p[j:]
   if n=='hq03':
    if a=='T':k=next(i for i,v in enumerate(p)if v.get('trigger',{}).get('state')=='r060_fight');p=[axis(0),cmd('drop_through',1),settle(272)]+p[k:]
    if z=='L':
     for v in p:
      if v.get('target_x')==180:v['target_x']=172
      if v.get('trigger',{}).get('migration_goal')==[176,267,8,6]:v['trigger']['migration_goal']=[168,267,8,6]
   if n=='hq07'and a=='R':
    for v in p:
     if v.get('target_x')==800:v['target_x']=790
     if v.get('guard_x')==800:v['guard_x']=790
     if v.get('trigger',{}).get('migration_goal')==[796,331,8,6]:v['trigger']['migration_goal']=[786,331,8,6]
   c['control_plan']=p
  save(r,cs,'v5')
if __name__=='__main__':main()
